# gather details on rule significance
# retrieve FR tracking data
# isolate significance columns
# merge with retrieved documents (on document_number)


from datetime import date
import polars as pl


def read_csv_data(start_date: date | str, 
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
    
    return df


def clean_data(df: pl.DataFrame, 
               document_numbers: list, 
               clean_columns: list | tuple = (
                   "document_number",
                   "significant", 
                   "econ_significant", 
                   "3(f)(1) significant", 
                   "Major"
                   )):
    # strip whitespace
    df = df.with_columns(pl.col("document_number").str.strip_chars())
    
    # remove null values
    df = df.filter(pl.col("document_number").is_not_null())
    
    # cast to nullable int dtype    
    df = df.with_columns(pl.col(clean_columns)).cast(pl.Int64, strict=False)
    
    return df.filter(
            pl.col("document_number").is_in(document_numbers)
                )


if __name__ == "__main__":
    
    start = "2023-04-01"
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
    
    df = read_csv_data(start)
    df = clean_data(df, numbers)
    print(len(df))


#schema = df.schema
#schema.update({""})