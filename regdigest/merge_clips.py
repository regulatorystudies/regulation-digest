"""
Mark Febrizio
"""

# %% initialize
from pathlib import Path

import pandas as pd


p = Path(__file__)
data_dir = p.parents[1].joinpath("data", "clips")
if data_dir.exists() and data_dir.is_dir():
    pass
else:
    data_dir.mkdir(parents=True, exist_ok=True)


# %% Load data

people = ["MF", "NT", "ZX"]

mark = data_dir / r"Federal_Register_Clips - 2022-08-30.xlsx"
nate = data_dir / r"Nates_FR_Clips_2022-08-30.xlsx"
zoey = data_dir / r"federal_register 8.30.2022.xlsx"

df_list = []
keep_cols = ['publication_date', 'agency_names', 'citation', 'html_url', 'title', 'type', 'cat']
for x, p in zip([mark, nate, zoey], people):
    with open(x, "rb") as f:
        df = pd.read_excel(f, header=0)
    
    df = df.loc[:, keep_cols]
    df["person"] = p
    df_list.append(df)

print(f"Imported {len(df_list)} dataframes.")

# concatenate
df_combo = pd.concat(df_list, axis=0, ignore_index=True, verify_integrity=True)
print(f"Combined into one dataframe with {len(df_combo)} rows.")


# %% Compare selections

# logic: compare duplicated columns for each df
#df_dup = df_combo.duplicated(subset=["citation", "type", "html_url"], keep=False)
#df_combo.loc[~df_dup, "dup_number"] = 0
#df_combo.loc[df_dup, 'dup_number'] = df_combo.groupby(['html_url']).cumcount() + 1

# https://stackoverflow.com/questions/39481609/number-duplicates-sequentially-in-pandas-dataframe
df_combo.loc[:, "dup_number"] = df_combo.groupby(["html_url", "cat"]).cumcount() + 1
df_combo = df_combo.sort_values(by=["html_url", "cat", "dup_number"], ascending=True)
df_dup = df_combo.duplicated(subset=["html_url", "cat"], keep="last")
df_unique = df_combo.loc[~df_dup, :].reset_index(drop=True)
df_sorted = df_unique.sort_values(by=["agency_names", "citation", "html_url", "cat"], kind="stable", ignore_index=True)


# %% Export

file = data_dir / "combined_Federal_Register_Clips_2022-08-30.csv"
with open(file, "w") as f:
    df_sorted.to_csv(f, line_terminator="\n", index=False)

print("saved as csv!")

