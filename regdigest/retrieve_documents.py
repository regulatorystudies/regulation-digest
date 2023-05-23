# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 12:19:24 2022

@author: mark
"""

#%% Init
import json
from datetime import date

import requests
import webbrowser



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
                          fields: tuple = ('publication_date', 
                                                 'agency_names', 
                                                 'citation', 
                                                 'start_page', 
                                                 'end_page', 
                                                 'html_url', 
                                                 'pdf_url', 
                                                 'title', 
                                                 'type', 
                                                 'action', 
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

    results, count = query_documents_endpoint(endpoint_url, dict_params)
    
    return results, count


def get_documents_by_number(document_numbers: list, 
                            fields: tuple = ('publication_date', 
                                             'agency_names', 
                                             'citation', 
                                             'start_page', 
                                             'end_page', 
                                             'html_url', 
                                             'pdf_url', 
                                             'title', 
                                             'type', 
                                             'action', 
                                             #'significant', 
                                             'correction_of'), 
                            sorted: bool = True
                            ):
    
    if sorted:
        document_numbers_str = ",".join(sorted(document_numbers))
    else:
        document_numbers_str = ",".join(document_numbers)
    
    # define endpoint url
    endpoint_url = fr'https://www.federalregister.gov/api/v1/documents/{document_numbers_str}.json?'
    
    # dictionary of parameters
    dict_params = {'fields[]': fields}
    results, count = query_documents_endpoint(endpoint_url, dict_params)
    
    return results, count


def save_json(results, count):
    pass
    # create dictionary of data with retrieval date
    dctsRules = {"source": "Federal Register API, https://www.federalregister.gov/reader-aids/developer-resources/rest-api",
    #            "endpoint": endpoint_url,
                "date_retrieved": f"{date.today()}",
    #            "timeframe": timeframe,
                "count": results,
                "results": count
                }



def main(by_date: bool = True, **kwargs):
    
    if by_date:
        start_date = input("Input start date [yyyy-mm-dd]: ")    
        results, count = get_documents_by_date(start_date)
    else:
        # https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists
        #document_numbers = [item for sublist in kwargs.values for item in sublist if type(sublist)==list]
        #get_documents_by_number(list(document_numbers))
        results, count = get_documents_by_number(list(kwargs))
    
    

