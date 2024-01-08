"""
Note:
This was developed to handle an error with the Federal Register API 
where it was returning duplicate documents, 
which also meant that some results were missing.
That issue was patched, so this code isn't essential at the moment.
"""

from copy import deepcopy
from datetime import date, timedelta
import requests
from duplicates import remove_duplicates, identify_duplicates


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
