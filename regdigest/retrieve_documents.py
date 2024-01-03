# -*- coding: utf-8 -*-
"""
Mark Febrizio

Created: 2022-06-13

Last modified: 2023-12-14
"""
# dependencies
from copy import deepcopy
from datetime import date, timedelta
import json
from pathlib import Path
import re

from pandas import DataFrame, read_csv, read_excel
import requests

try:  # for use as module: python -m regdigest
    from .preprocessing import (
        clean_agency_names, 
        get_parent_agency, 
        filter_corrections, 
        filter_actions, 
        extract_rin_info, 
        create_rin_keys, 
        AgencyMetadata, 
        )
    from .regex_filters import FILTER_ROUTINE
    from .duplicates import identify_duplicates, remove_duplicates
except ImportError:
    # hacky but allows alternate script to work
    from preprocessing import (
        clean_agency_names, 
        get_parent_agency, 
        filter_corrections, 
        filter_actions, 
        extract_rin_info, 
        create_rin_keys, 
        AgencyMetadata, 
        )
    from regex_filters import FILTER_ROUTINE
    from duplicates import identify_duplicates, remove_duplicates


BASE_PARAMS = {
    'per_page': 1000, 
    "page": 0, 
    'order': "oldest"
    }
BASE_URL = r'https://www.federalregister.gov/api/v1/documents.json?'


class QueryError(Exception):
    pass


def extract_year(string: str):
    """Extract date from a string in a format similar to `datetime.datetime` or `datetime.date`.

    Args:
        string (str): Date represented as a string.

    Returns:
        int: Year attribute of `datetime.date` object.
    """
    res = re.compile("\d{4}-\d{2}-\d{2}", re.I).match(string)
    
    if isinstance(res, re.Match):
        return date.fromisoformat(res[0]).year
    else:
        return None


def convert_to_datetime_date(input_date: date| str):
    if isinstance(input_date, date):
        return input_date
    elif isinstance(input_date, str):
        return date.fromisoformat(input_date)
    else:
        raise TypeError(f"Inappropriate argument type {type(input_date)} for parameter 'input_date'.")


def date_in_quarter(input_date: date | str, year: str, quarter: tuple, return_quarter_end: bool = True):
    """Checks if given date falls within a year's quarter. 
    Returns input date if True, otherwise returns first or last day of quarter.

    Args:
        input_date (date | str): Date to check.
        year (str): Year to check against.
        quarter (tuple): Quarter to check against.
        return_quarter_end (bool, optional): Return end date of quarter when input not in range. Defaults to True.

    Raises:
        TypeError: Inappropriate argument type for 'input_date'.

    Returns:
        datetime.date: Returns input_date when it falls within range; otherwise returns boundary date of quarter.
    """    
    check_date = convert_to_datetime_date(input_date)
    range_start = date.fromisoformat(f"{year}-{quarter[0]}")
    range_end = date.fromisoformat(f"{year}-{quarter[1]}")
    in_range = (check_date >= range_start) and (check_date <= range_end)
    #return in_range
    if in_range:
        return check_date
    elif (not in_range) and return_quarter_end:
        return range_end
    elif (not in_range) and (not return_quarter_end):
        return range_start


def greater_than_date(date_a: date | str, date_b: date | str):
    """Compare whether a date A occurs after date B.

    Args:
        date_a (date | str): The first given date.
        date_b (date | str): The second given date.

    Returns:
        bool: True if date A occurs after date B.
    """    
    return convert_to_datetime_date(date_a) > convert_to_datetime_date(date_b)


def query_documents_endpoint(endpoint_url: str, dict_params: dict):
    """GET request for documents endpoint.

    Args:
        endpoint_url (str): URL for API endpoint.
        dict_params (dict): Paramters to pass in GET request.

    Returns:
        tuple[list, int]: Tuple of API results, count of documents retrieved.
    """    
    results, count = [], 0
    response = requests.get(endpoint_url, params=dict_params).json()
    max_documents_threshold = 10000
    
    # handles queries returning no documents
    if response["count"] == 0:
        pass
    
    # handles queries that need multiple requests
    elif response["count"] > max_documents_threshold:
        
        # get range of dates
        start_date = dict_params.get("conditions[publication_date][gte]")
        end_date = dict_params.get("conditions[publication_date][lte]")
        
        # set range of years
        start_year = extract_year(start_date)
        if end_date is None:
            end_date = date.today()
            end_year = end_date.year
        else:
            end_year = extract_year(end_date)
        years = range(start_year, end_year + 1)
        
        # format: YYYY-MM-DD
        quarter_tuples = (
            ("01-01", "03-31"), ("04-01", "06-30"), 
            ("07-01", "09-30"), ("10-01", "12-31")
            )
        
        # retrieve documents
        dict_params_qrt = deepcopy(dict_params)
        for year in years:
            for quarter in quarter_tuples:            
                results_qrt = []
                
                # set start and end dates based on input date
                gte = date_in_quarter(start_date, year, quarter, return_quarter_end=False)
                lte = date_in_quarter(end_date, year, quarter)
                if greater_than_date(start_date, lte):
                    # skip quarters where start_date is later than last day of quarter
                    continue
                elif greater_than_date(gte, end_date):
                    # skip quarters where end_date is ealier than first day of quarter
                    break
                
                # update parameters by quarter
                dict_params_qrt.update({
                    "conditions[publication_date][gte]": f"{gte}", 
                    "conditions[publication_date][lte]": f"{lte}"
                                        })
                
                # get documents
                results_qrt = retrieve_results_by_next_page(endpoint_url, dict_params_qrt)
                results.extend(results_qrt)
                count += response["count"]
    
    # handles normal queries
    elif response["count"] in range(max_documents_threshold + 1):
        count += response["count"]
        results.extend(retrieve_results_by_next_page(endpoint_url, dict_params))
    
    # otherwise something went wrong
    else:
        raise QueryError(f"Query returned document count of {response['count']}.")

    duplicates = identify_duplicates(results, key="document_number")
    count_dups = len(duplicates)
    if count_dups > 0:
        raise QueryError(f"API request returned {count_dups} duplicate values.")
    
    return results, count


def retrieve_results_by_page_range(num_pages: int, endpoint_url: str, dict_params: dict) -> list:
    """Retrieve documents by looping over a given number of pages.

    Args:
        num_pages (int): Number of pages to retrieve documents from.
        endpoint_url (str): URL for API endpoint.
        dict_params (dict): Paramters to pass in GET request.

    Returns:
        list: Documents retrieved from the API.
    """
    results, tally = [], 0
    for page in range(1, num_pages + 1):  # grab results from each page
        dict_params.update({"page": page})
        response = requests.get(endpoint_url, params=dict_params)
        results_this_page = response.json()["results"]
        results.extend(results_this_page)
        tally += len(results_this_page)
    count = response.json()["count"]
    print(count, tally)
    return results, count


def retrieve_results_by_next_page(endpoint_url: str, dict_params: dict) -> list:
    """Retrieve documents by accessing "next_page_url" returned by each request.

    Args:
        endpoint_url (str): url for documents.{format} endpoint.
        dict_params (dict): Paramters to pass in GET request.

    Raises:
        QueryError: Failed to retrieve documents from all pages.

    Returns:
        list: Documents retrieved from the API.
    """
    results = []
    response = requests.get(endpoint_url, params=dict_params).json()
    pages = response.get("total_pages")
    next_page_url = response.get("next_page_url")
    counter = 0
    while next_page_url is not None:
        counter += 1
        results_this_page = response["results"]
        results.extend(results_this_page)
        response = requests.get(next_page_url).json()
        next_page_url = response.get("next_page_url")
    else:
        counter += 1
        results_this_page = response["results"]
        results.extend(results_this_page)
    
    # raise exception if failed to access all pages
    if counter != pages:
        raise QueryError(f"Failed to retrieve documents from all {pages} pages.")
    
    return results


def get_documents_surrounding_date(data: list, 
                                   date_str: str, 
                                   date_padding: int, 
                                   document_count: int, 
                                   endpoint_url: str, 
                                   dict_params: dict, 
                                   unique_id: str):
    # update params to get documents surrounding missing dates
    center = date.fromisoformat(date_str)
    delta = timedelta(days=date_padding)
    date_range = (center - delta, center + delta)
    dict_params.update({
        "conditions[publication_date][gte]": f"{date_range[0]}", 
        "conditions[publication_date][lte]": f"{date_range[1]}"
        })
    
    # retrieve documents and add to existing results
    response = requests.get(endpoint_url, params=dict_params).json()
    data.extend(response["results"])
    
    # filter out new duplicates; update validate
    data, _ = remove_duplicates(data, key=unique_id)
    print(f"Running total unique: {len(data)}")
    validate = document_count - len(data)
    
    return data, validate


def get_missing_documents(existing_data: list, 
                          document_count: int, 
                          endpoint_url: str, 
                          dict_params: dict, 
                          date_padding: int = 3, 
                          unique_id: str = "document_number"):

    dups = identify_duplicates(existing_data, key=unique_id)    
    validate = len(dups)
    
    while validate > 0:
        data_alt = deepcopy(existing_data)
        dates = (d.get("publication_date") for d in dups)
        for dt in dates:
            # get documents surrounding missing dates
            data_alt, validate = get_documents_surrounding_date(
                data_alt, 
                dt, 
                date_padding, 
                document_count, 
                endpoint_url, 
                dict_params, 
                unique_id
                )
            
            # validate equals documents returned by initial query minus running total unique
            if validate == 0:
                # ends function before looping again or moving to else clauses
                return data_alt
        else:
            date_padding += 1
    else:
        print("No missing documents.")
        return existing_data


def get_documents_by_date(start_date: str, 
                          end_date: str | None = None, 
                          fields: tuple = ('document_number', 
                                           'publication_date', 
                                           'agency_names', 
                                           'agencies', 
                                           'citation', 
                                           'start_page', 
                                           'end_page', 
                                           'html_url', 
                                           'pdf_url', 
                                           'title', 
                                           'type', 
                                           'action', 
                                           'regulation_id_number_info', 
                                           #'significant', 
                                           'correction_of'),
                          endpoint_url: str = BASE_URL, 
                          dict_params: dict = BASE_PARAMS):
    """Retrieve Federal Register documents using a date range.

    Args:
        start_date (str): Start date when documents were published (inclusive; format must be 'yyyy-mm-dd').
        end_date (str | None, optional): End date (inclusive; format must be 'yyyy-mm-dd'). Defaults to None (implies end date is `datetime.date.today()`).
        fields (tuple, optional): Fields/columns to retrieve. Defaults to ('document_number', 'publication_date', 'agency_names', 'agencies', 'citation', 'start_page', 'end_page', 'html_url', 'pdf_url', 'title', 'type', 'action', 'regulation_id_number_info', 'correction_of').
        endpoint_url (_type_, optional): Endpoint url. Defaults to r'https://www.federalregister.gov/api/v1/documents.json?'.

    Returns:
        tuple[list, int]: Tuple of API results, count of documents retrieved.
    """
    # update dictionary of parameters
    dict_params.update({
        'conditions[publication_date][gte]': f'{start_date}', 
        'fields[]': fields
        })
    
    # relies on functionality that empty strings '' are falsey in Python: https://docs.python.org/3/library/stdtypes.html#truth-value-testing
    if end_date:
        dict_params.update({'conditions[publication_date][lte]': f"{end_date}"})
    
    results, count = query_documents_endpoint(endpoint_url, dict_params)
    return results, count


def get_documents_by_number(document_numbers: list, 
                            fields: tuple = ('document_number', 
                                             'publication_date', 
                                             'agency_names', 
                                             'agencies', 
                                             'citation', 
                                             'start_page', 
                                             'end_page', 
                                             'html_url', 
                                             'pdf_url', 
                                             'title', 
                                             'type', 
                                             'action', 
                                             'regulation_id_number_info', 
                                             #'significant', 
                                             'correction_of'), 
                            sort_data: bool = True
                            ):
    """Retrieve Federal Register documents using a list of document numbers.

    Args:
        document_numbers (list): Documents to retrieve based on 'document_number' field.
        fields (tuple, optional): Fields/columns to retrieve. Defaults to ('document_number', 'publication_date', 'agency_names', 'agencies', 'citation', 'start_page', 'end_page', 'html_url', 'pdf_url', 'title', 'type', 'action', 'regulation_id_number_info', 'correction_of').
        sort_data (bool, optional): Sort documents by 'document_number'. Defaults to True.

    Returns:
        tuple[list, int]: Tuple of API results, count of documents retrieved.
    """    
    if sort_data:
        document_numbers_str = ",".join(sorted(document_numbers))
    else:
        document_numbers_str = ",".join(document_numbers)
    
    endpoint_url = fr'https://www.federalregister.gov/api/v1/documents/{document_numbers_str}.json?'
    dict_params = {'fields[]': fields}
    results, count = query_documents_endpoint(endpoint_url, dict_params)
    return results, count


def parse_document_numbers(path: Path, 
                           pattern: str = r"[\w|\d]{2,4}-[\d]{5,}"):
    """Parse Federal Register document numbers from input data file.

    Args:
        path (Path): Path to input file.
        pattern (str, optional): Regex pattern to search for. Defaults to r"[\w|\d]{2,4}-[\d]{5,}".

    Raises:
        ValueError: Raises error when input file is not CSV or Excel spreadsheet.

    Returns:
        list: List of document numbers.
    """    
    file = next(p for p in path.iterdir() if (p.is_file() and p.name != ".gitignore"))
    if file.suffix in (".csv", ".txt", ".tsv"):
        with open(file, "r") as f:
            df = read_csv(f)
    elif file.suffix in (".xlsx", ".xls", ".xlsm"):
        with open(file, "rb") as f:
            df = read_excel(f)
    else:
        raise ValueError("Input file must be CSV or Excel spreadsheet.")    
    
    if 'document_number' in df.columns:
        document_numbers = df['document_number'].values.tolist()
    else:
        url_list = df['html_url'].values.tolist()
        document_numbers = [re.search(pattern, url).group(0) for url in url_list]
    
    return document_numbers


def export_data(df: DataFrame, 
                path: Path, 
                file_name: str = f"federal_register_clips_{date.today()}.csv"):
    """Save data to file in CSV format.

    Args:
        df (DataFrame): Data as a DataFrame.
        path (Path): Path to save directory.
        file_name (str, optional): File name. Defaults to f"federal_register_clips_{date.today()}.csv".
    """    
    with open(path / file_name, "w", encoding = "utf-8") as f:
        df.to_csv(f, lineterminator="\n")
    print(f"Exported data as csv to {path}.")


def pipeline(metadata: dict, input_path: Path = None):
    """Main pipeline for retrieving Federal Register documents.

    Args:
        metadata (dict): Agency metadata for cleaning agency names.
        input_path (Path, optional): Path to input with documents to retrieve. Defaults to None.

    Returns:
        DataFrame: Output data.
    """    
    if not input_path:  # date range        
        while True:  # doesn't exit until correctly formatted input received
            pattern = r"\d{4}-[0-1]\d{1}-[0-3]\d{1}"
            start_date = input("Input start date [yyyy-mm-dd]: ")
            match_1 = re.fullmatch(pattern, start_date, flags=re.I)
            end_date = input("Input end date [yyyy-mm-dd]. Or just press enter to use today as the end date: ")
            match_2 = re.fullmatch(pattern, end_date, flags=re.I)
            if match_1 and (match_2 or end_date==""):
                results, _ = get_documents_by_date(start_date, end_date=end_date)
                break
            else:
                print("Invalid input. Must enter dates in format 'yyyy-mm-dd'.")
    
    else:  # input file
        document_numbers = parse_document_numbers(input_path) 
        results, _ = get_documents_by_number(document_numbers)
    
    # get rin info for documents; returns generator of dict
    results_with_rin_info = (create_rin_keys(doc, extract_rin_info(doc)) for doc in results)

    # create DataFrame; filter out documents; clean agency info; drop unneeded columns
    df = DataFrame(list(results_with_rin_info))
    df, _ = filter_corrections(df)
    df = filter_actions(df, filters = FILTER_ROUTINE, columns = ["title"])
    df = clean_agency_names(df).set_index("document_number")
    df = get_parent_agency(df, metadata)
    df = df.drop(columns=["regulation_id_number_info", "correction_of", "agencies"])
    
    # return data
    return df


def create_paths(input_file: bool = False) -> list[Path]:
    """Create paths for input and output data.

    Args:
        input_file (bool, optional): True if using input file. Defaults to False.

    Returns:
        list[Path]: List of path-like objects.
    """    
    dirs = []
    p = Path(__file__)
    output_dir = p.parents[1].joinpath("output")
    dirs.append(output_dir)
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    
    if input_file:  # create input directory if using input file
        input_dir = p.parents[1].joinpath("input")
        input_dir.mkdir(parents=True, exist_ok=True)
        dirs.append(input_dir)
    
    return dirs


def retrieve_documents():
    # get agency metadata
    try:  # import metadata from local JSON
        metadata_dir = Path(__file__).parent.joinpath("data")
        with open(metadata_dir / "agencies_endpoint_metadata.json", "r") as f:
            metadata = json.load(f)["results"]
    except:  # retrieve from API
        agency_metadata = AgencyMetadata()
        agency_metadata.get_metadata()
        agency_metadata.transform()
        metadata = agency_metadata.transformed_data
    
    # loop for getting inputs, calling main pipeline function, and saving data
    # won't break until it receives valid input
    while True:
        # print prompt to console
        get_input = input("Use input file? [yes/no]: ")
        
        # check user inputs
        if get_input.lower() in ("y", "yes"):
            output_dir, input_dir = create_paths(input_file=True)
            df2 = pipeline(metadata, input_path=input_dir)
            export_data(df2, output_dir)
            break
        elif get_input.lower() in ("n", "no"):
            output_dir = create_paths()[0]
            df = pipeline(metadata)
            export_data(df, output_dir)
            break
        else:
            print("Invalid input. Must enter 'y' or 'n'.")


if __name__ == "__main__":
    
    retrieve_documents()
