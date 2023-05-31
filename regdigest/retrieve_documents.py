# -*- coding: utf-8 -*-
"""
Mark Febrizio

Created: 2022-06-13

Last modified: 2023-05-30
"""
# import dependencies
from datetime import date
import json
#import os
from pathlib import Path
import re
#import sys

from pandas import DataFrame, read_csv, read_excel
import requests

from preprocessing import (
    clean_agency_names, get_parent_agency, 
    filter_corrections, filter_actions, 
    extract_rin_info, create_rin_keys, 
    )


# constants
FILTER_ROUTINE = [  # title filters for routine actions
    r"^Privacy\sAct\sof\s1974", 
    r"^Airworthiness\sDirectives", 
    r"^Airworthiness\sCriteria", 
    r"^Fisheries\sof\sthe\s[\w]+;", 
    r"^Submission\sfor\sOMB\sReview;", 
    r"^Sunshine\sAct\sMeetings", 
    r"^Agency\sInformation\sCollection\sActivit[\w]+", 
    r"Notice\sof\sClosed\sMeetings$", 
    r"^Environmental\sImpact\sStatements;\sNotice\sof\sAvailability", 
    r"^Combined\sNotice\sof\sFilings", 
    r"Coastwise\sEndorsement\sEligibility\sDetermination\s[.]+\sVessel", 
    r"^Safety\sZone[\w]*", 
    r"^Air\sPlan\sApproval", 
    r"^Drawbridge\sOperation\sRegulation", 
    ]


def query_documents_endpoint(endpoint_url: str, dict_params: dict):
    """_summary_

    Args:
        endpoint_url (str): _description_
        dict_params (dict): _description_

    Returns:
        tuple[list, int]: _description_
    """    
    results, count = [], 0
    response = requests.get(endpoint_url, params=dict_params)
    if response.json()["count"] != 0:
        
        # set variables
        count += response.json()["count"]
        
        try:  # for days with multiple pages of results
            pages = response.json()["total_pages"]  # number of pages to retrieve all results
            
            # for loop for grabbing results from each page
            for page in range(1, pages + 1):
                dict_params.update({"page": page})
                response = requests.get(endpoint_url, params=dict_params)
                results_this_page = response.json()["results"]
                results.extend(results_this_page)
        
        except:  # when only one page of results
            results_this_page = response.json()["results"]
            results.extend(results_this_page)
    return results, count


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
                          endpoint_url: str = r'https://www.federalregister.gov/api/v1/documents.json?'
                          ):
    
    # define parameters
    res_per_page = 1000
    page_offset = 0
    sort_order = 'oldest'
    
    # dictionary of parameters
    dict_params = {'per_page': res_per_page, 
                   "page": page_offset,
                   'order': sort_order, 
                   'fields[]': fields, 
                   'conditions[publication_date][gte]': f"{start_date}"
                   }
    
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
    
    if sort_data:
        document_numbers_str = ",".join(sorted(document_numbers))
    else:
        document_numbers_str = ",".join(document_numbers)
    
    # define endpoint url
    endpoint_url = fr'https://www.federalregister.gov/api/v1/documents/{document_numbers_str}.json?'
    
    # dictionary of parameters
    dict_params = {'fields[]': fields}
    results, count = query_documents_endpoint(endpoint_url, dict_params)
    
    return results, count


def parse_document_numbers(path: Path, 
                           pattern: str = r"[\w|\d]{2,4}-[\d]{5,}"):
    
    file = next(p for p in path.iterdir() if p.is_file())
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
    
    with open(path / file_name, "w") as f:
        df.to_csv(f, lineterminator="\n")
    
    print(f"Exported data as csv to {path}.")


def main(metadata: dict, input_path: Path = None):
    
    if not input_path:
        
        while True:
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
        
    else:
        # https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists
        #document_numbers = [item for sublist in kwargs.values for item in sublist if type(sublist)==list]
        #get_documents_by_number(list(document_numbers))
        document_numbers = parse_document_numbers(input_path) 
        results, _ = get_documents_by_number(document_numbers)
    
    results_with_rin_info = (create_rin_keys(doc, extract_rin_info(doc)) for doc in results)

    df = DataFrame(list(results_with_rin_info))
    df, _ = filter_corrections(df)
    df = filter_actions(df, filters = FILTER_ROUTINE, columns = ["title"])
    df = clean_agency_names(df).set_index("document_number")
    df = get_parent_agency(df, metadata)
    df = df.drop(columns=["regulation_id_number_info", "correction_of", "agencies"])
    return df


def create_paths(input_file: bool = False):
    
    dirs = []
    p = Path(__file__)
    output_dir = p.parents[1].joinpath("output")
    dirs.append(output_dir)
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    
    if input_file:
        input_dir = p.parents[1].joinpath("input")
        input_dir.mkdir(parents=True, exist_ok=True)
        dirs.append(input_dir)
    
    return dirs


if __name__ == "__main__":
    
    # import metadata
    metadata_dir = Path(__file__).parent.joinpath("data")
    with open(metadata_dir / "agencies_endpoint_metadata.json", "r") as f:
        agency_metadata = json.load(f)["results"]
    
    while True:
        # print prompt to console
        get_input = input("Use input file? [yes/no]: ")
        
        if get_input.lower() in ("y", "yes"):
            output_dir, input_dir = create_paths(input_file=True)
            df2 = main(agency_metadata, input_path=input_dir)
            export_data(df2, output_dir)
            break
        elif get_input.lower() in ("n", "no"):
            output_dir = create_paths()[0]
            df = main(agency_metadata)
            export_data(df, output_dir)
            break
        else:
            print("Invalid input. Must enter 'y' or 'n'.")

