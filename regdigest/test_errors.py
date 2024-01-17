import polars as pl
import pandas as pd

url_old = "https://raw.githubusercontent.com/regulatorystudies/Reg-Stats/1e4455d69b756fd3ae0c87bc5baf56c00760e13c/data/fr_tracking/fr_tracking.csv"
url_new = "https://raw.githubusercontent.com/regulatorystudies/Reg-Stats/main/data/fr_tracking/fr_tracking.csv"

df_pl_old = pl.read_csv(url_old, encoding="utf8-lossy")
df_pl_new = pl.read_csv(url_new, encoding="utf8-lossy")

df_pd_old = pd.read_csv(url_old, encoding="latin")
df_pd_new = pd.read_csv(url_new, encoding="latin")

df_pl_old_from_pd = pl.from_pandas(df_pd_old)

for df in (
    df_pl_old, 
    df_pl_new, 
    df_pd_old, df_pd_new, 
    df_pl_old_from_pd
    ):
    print(df.shape)
