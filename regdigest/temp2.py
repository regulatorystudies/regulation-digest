from pandas import DataFrame

from retrieve_documents import (
    BASE_PARAMS, 
    BASE_URL, 
    query_documents_endpoint, 
    get_documents_by_date, 
    get_missing_documents, 
    )

these_params = BASE_PARAMS.copy()

these_params = {"conditions[publication_date][gte]": "2023-01-01", 
                "conditions[publication_date][lte]": "2023-06-30", 
                "conditions[type][]": "NOTICE",  #"RULE"
                "per_page": 1000, 
                "order": "oldest"
                }

how = ["document_number", "publication_date", "title"]

results0, count = query_documents_endpoint(BASE_URL, these_params)
print(f"Num. documents to retrieve: {len(results0)}")
print(these_params)
#these_params.pop("conditions[publication_date][gte]")
#these_params.pop("conditions[publication_date][lte]")
#these_params.update({"conditions[publication_date][year]": 2023})
#results1 = get_missing_documents(results0, len(results0), BASE_URL, these_params)
df_1 = DataFrame(results0)
bool_1 = df_1.duplicated(how)
counts1 = bool_1.value_counts()
print(counts1)
