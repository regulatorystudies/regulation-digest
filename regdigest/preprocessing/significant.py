# gather details on rule significance
# retrieve FR tracking data
# isolate significance columns
# merge with retrieved documents (on document_number)


from datetime import date
import polars as pl
from pandas import DataFrame as pd_DataFrame


class ImportError(Exception):
    pass


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
    
    # read csv; try lossy encoding if raises error
    try:
        df = pl.read_csv(url, columns=cols)
    except pl.ComputeError:
        df = pl.read_csv(url, columns=cols, encoding="utf8-lossy")
    
    if df.shape[1] == len(cols):
        return df, cols
    else:
        #print(f"Shape of imported df: {df.shape}")
        #raise ImportError("Error importing DataFrame from GitHub.")
        return None, cols


def clean_data(df: pl.DataFrame, 
               document_numbers: list, 
               clean_columns: list | tuple, 
               return_optimized_plan = False
               ):
    
    # start a lazy query
    lf = (
        df.lazy()
        # strip whitespace
        .with_columns(pl.col("document_number").str.strip_chars())
        # only keep document_numbers from input
        .filter(pl.col("document_number").is_in(document_numbers))
        # cast to nullable int dtype
        .with_columns(pl.col(c for c in clean_columns if c != "document_number").cast(pl.Int64, strict=False))
        )
    
    # return optimized query plan instead of df
    if return_optimized_plan:
        return lf.explain(optimized=True)
    
    # call collect to return df
    return lf.collect()


def merge_with_api_results(pd_df: pd_DataFrame, 
                           pl_df: pl.DataFrame
                           ):
    
    main_df = pl.from_pandas(pd_df)
    df = main_df.join(pl_df, on="document_number", how="left", validate="1:1")
    return df.to_pandas()


def get_significant_info(input_df, start_date, document_numbers):
    
    pl_df, clean_cols = read_csv_data(start_date)
    if pl_df is None:
        print("Failed to integrate significance tracking data with retrieved documents.")
        return input_df
    pl_df = clean_data(pl_df, document_numbers, clean_cols)
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
    df_a, clean_cols = read_csv_data(date_a)
    #df_a = clean_data(df_a, numbers, clean_cols)
    
    # test for dates after EO 14094
    df_b, clean_cols = read_csv_data(date_b)
    #df_b = clean_data(df_b, numbers, clean_cols)
    
    #print(df_a.shape, df_b.shape)
