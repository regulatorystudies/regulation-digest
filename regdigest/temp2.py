from pathlib import Path
import json

import requests
import pandas as pd


def get_documents(url, params):
    response = requests.get(url, params=params).json()
    counter = 1
    while True:    
        with open(download_path / f"documents_page{counter}.json", "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4)
        
        next_page_url = response.get("next_page_url")
        if next_page_url is None:
            break
        
        response = requests.get(next_page_url).json()
        counter += 1


def load_results(files):
    results = []
    for file in files:
        with open(download_path / file, "r", encoding="utf-8") as f:
            data = json.load(f)["results"]
            results.extend(data)
    return results


def report(results):
    print(len(results))
    df_1 = pd.DataFrame(results)
    how = ["document_number", "publication_date", "title"]
    bool_1 = df_1.duplicated(how, keep=False)
    print("Duplicate counts:", bool_1.value_counts(), sep="\n")
    print(df_1.loc[bool_1, "document_number"])


if __name__ == "__main__":
    
    download_path = Path(__file__).parents[6].joinpath("mark", "Downloads")
    endpoint_url = r"https://www.federalregister.gov/api/v1/documents.json?"
    dict_params = {"conditions[publication_date][year]": 2023, 
                    "conditions[type][]": "NOTICE",  #"RULE"
                    "per_page": 1000, 
                    "order": "oldest"
                    }
    
    get_documents(endpoint_url, dict_params)
    files = [f"documents_page{n}.json" for n in range(1, 11)]
    results = load_results(files)
    report(results)
