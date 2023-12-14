from pathlib import Path
import pandas as pd

from retrieve_documents import *

out_path = Path(__file__).parents[1].joinpath("output")
file = "federal_register_clips_2023-12-14.csv"

with open(out_path / file, "r", encoding="utf-8") as f:
    df = pd.read_csv(f, index_col=False)

bool_dup = df.duplicated("document_number", keep=False)
df_dup = df.loc[bool_dup, :]


these_params = BASE_PARAMS.copy()
these_params.update({
    "conditions[publication_date][year]": 2023
        })

these_params = {"conditions[publication_date][year]": 2023, 
                "conditions[type][]": "NOTICE",  #"RULE"
                "per_page": 1000, 
                "order": "oldest"
                }

how = ["document_number", "publication_date", "title"]

results1 = retrieve_results_by_next_page(BASE_URL, these_params)
df_1 = pd.DataFrame(results1)
bool_1 = df_1.duplicated(how)
counts1 = bool_1.value_counts()
#print(df_1.loc[bool_1])

results2 = retrieve_results_by_page_range(10, BASE_URL, these_params)
df_2 = pd.DataFrame(results2[0])
bool_2 = df_2.duplicated(how)
counts2 = bool_2.value_counts()
#print(df_2.loc[bool_2])

print(counts1, counts2, sep="\n")

common = set([r.get("document_number") for r in results1 if r in results2] + [r.get("document_number") for r in results2 if r in results1])
uncommon = set([r.get("document_number") for r in results1 if r not in results2] + [r.get("document_number") for r in results2 if r not in results1])

missing1, missing2 = [], []
for u in uncommon:
    #print(u)
    missing2.extend([n for n, r in enumerate(results1) if r.get("document_number") == u])
    missing1.extend([n for n, r in enumerate(results2) if r.get("document_number") == u])
