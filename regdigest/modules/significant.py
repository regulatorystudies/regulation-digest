# gather details on rule significance from FR tracking document
# see: https://github.com/regulatorystudies/Reg-Stats/blob/main/data/fr_tracking/fr_tracking.csv

from datetime import date

import polars as pl
from pandas import (
    DataFrame as pd_DataFrame, 
    read_csv as pd_read_csv, 
    )


def read_csv_data(
    start_date: date | str, 
    retrieve_columns: list | tuple = (
        "document_number",
        "significant", 
        "econ_significant", 
        "3(f)(1) significant", 
        "Major"
        ), 
    url: str = r"https://raw.githubusercontent.com/regulatorystudies/Reg-Stats/main/data/fr_tracking/fr_tracking.csv"
    ):
    # handle dates formatted as str
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)
    
    # drop econ_significant column for dates on or after EO 14094 
    if start_date >= date.fromisoformat("2023-04-06"):
        cols = [col for col in retrieve_columns if col != "econ_significant"]
    else:
        cols = list(retrieve_columns)
    
    # read csv; try different encoding if raises error
    try:
        df_pd = pd_read_csv(url, usecols=cols)
    except UnicodeDecodeError:
        df_pd = pd_read_csv(url, usecols=cols, encoding="latin")
    df = pl.from_pandas(df_pd)
    
    if df.shape[1] == len(cols):
        # rename columns if they exist
        rename_cols = {"3(f)(1) significant": "3f1_significant", "Major": "major"}
        if all(True if rename in cols else False for rename in rename_cols.keys()):
            df = df.rename(rename_cols)
            cols = [rename_cols.get(col, col) for col in cols]
        
        # return unique documents to fix possible manual entry errors in fr-tracking.csv
        return df.unique(subset="document_number", keep="any")
    else:
        return None


def clean_data(df: pl.DataFrame, 
               document_numbers: list, 
               return_optimized_plan = False
               ):
    
    # start a lazy query
    lf = (
        df.lazy()
        # strip whitespace
        .with_columns(pl.col("document_number").str.strip_chars())
        # only keep document_numbers from input
        .filter(pl.col("document_number").is_in(document_numbers))
        )
    
    # return optimized query plan instead of df
    if return_optimized_plan:
        return lf.explain(optimized=True)
    
    # call collect to return df
    return lf.collect()


def merge_with_api_results(
        pd_df: pd_DataFrame, 
        pl_df: pl.DataFrame, 
    ):    
    main_df = pl.from_pandas(pd_df)
    df = main_df.join(pl_df, on="document_number", how="left", validate="1:1", coalesce=True)
    return df.to_pandas()


def get_significant_info(input_df, start_date, document_numbers):
    
    pl_df = read_csv_data(start_date)
    if pl_df is None:
        print("Failed to integrate significance tracking data with retrieved documents.")
        return input_df
    pl_df = clean_data(pl_df, document_numbers)
    pd_df = merge_with_api_results(input_df, pl_df)
    return pd_df


if __name__ == "__main__":
    
    date_a = "2023-04-05"
    date_b = "2023-04-06"
    numbers = [
        "2021-01303", 
        '2023-28006', 
        '2024-00149', 
        '2024-00089',
        '2023-28828',
        '2024-00300',
        '2024-00045',
        '2024-00192',
        '2024-00228',
        '2024-00187'
        ]

    # test for dates before EO 14094
    df_a = read_csv_data(date_a)
    df_a = clean_data(df_a, numbers)
    
    # test for dates after EO 14094
    df_b = read_csv_data(date_b)
    df_b = clean_data(df_b, numbers)
