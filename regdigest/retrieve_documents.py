# -*- coding: utf-8 -*-
"""
Mark Febrizio

Created: 2022-06-13

Last modified: 2023-05-25
"""

#%% Init
#import json
from datetime import date
#import webbrowser
from pathlib import Path
import re

from pandas import DataFrame, read_csv, read_excel
import requests

from preprocessing import clean_agency_names, filter_corrections, extract_rin_info, create_rin_keys


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
    
    if end_date:
        dict_params.update({'conditions[publication_date][lte]': f"{end_date}"})

    results, count = query_documents_endpoint(endpoint_url, dict_params)
    
    return results, count


def get_documents_by_number(document_numbers: list, 
                            fields: tuple = ('document_number', 
                                             'publication_date', 
                                             'agency_names', 
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
        #document_numbers = []
        #for u in urls:
        #    m = re.search(pattern, u)
        #    doc_number = m.group(0)
        #    document_numbers.append(doc_number)
    
    return document_numbers


def export_data(df: DataFrame, 
                path: Path, 
                file_name: str = f"federal_register_clips_{date.today()}.csv"):
    
    with open(path / file_name, "w") as f:
        df.to_csv(f, lineterminator="\n")
    
    print("Exported data as csv!")


def main(input_path: Path = None):
    
    if not input_path:
        start_date = input("Input start date [yyyy-mm-dd]: ")
        end_date = input("Input end date [yyyy-mm-dd]: ")
        results, _ = get_documents_by_date(start_date, end_date=end_date)
    else:
        # https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists
        #document_numbers = [item for sublist in kwargs.values for item in sublist if type(sublist)==list]
        #get_documents_by_number(list(document_numbers))
        document_numbers = parse_document_numbers(input_path) 
        results, _ = get_documents_by_number(document_numbers)
    
    results_with_rin_info = (create_rin_keys(doc, extract_rin_info(doc)) for doc in results)

    df = DataFrame(list(results_with_rin_info))
    df, _ = filter_corrections(df)
    df = clean_agency_names(df).set_index("document_number")
    df = df.drop(columns=["regulation_id_number_info", "correction_of"])
    return df

    
if __name__ == "__main__":
    
    p = Path(__file__)
    data_dir = p.parents[1].joinpath("data")
    input_dir = p.parents[1].joinpath("input")
    
    if not (data_dir.exists() or input_dir.exists()):
        data_dir.mkdir(parents=True, exist_ok=True)
        input_dir.mkdir(parents=True, exist_ok=True)
    
    get_input = input("Using input file? [y/n]")
    
    if get_input=="y":
        df2 = main(input_path=input_dir)
        export_data(df2, data_dir)
    else:
        df = main()
        export_data(df, data_dir)

