import re
from numpy import array
from pandas import DataFrame

from search_columns import search_columns


class FilterError(Exception):
    pass


def filter_corrections(df: DataFrame):
    """Filter out corrections from Federal Register documents. 
    Identifies corrections using `corrrection_of` field and regex searches of `document_number`, `title`, and `action` fields.

    Args:
        df (DataFrame): Federal Register data.

    Returns:
        tuple[DataFrame, DataFrame]: Tuple of data without corrections, data with corrections.
    """
    # get original column names
    cols = df.columns.tolist()
    
    # filter out corrections
    # 1. Using correction fields
    bool_na = array(df["correction_of"].isna())
    #df_filtered = df.loc[bool_na, :]  # keep when correction_of is missing
    #print(f"correction_of missing: {sum(bool_na)}")
    
    # 2. Searching other fields
    search_1 = search_columns(df, [r"^C[\d]"], ["document_number"], 
                                 return_column="indicator1")
    search_2 = search_columns(df, [r"(?:;\scorrection\b)|(?:\bcorrecting\samend[\w]+\b)"], ["title", "action"], 
                                 return_column="indicator2")
    bool_search = array(search_1["indicator1"] == 1) | array(search_2["indicator2"] == 1)
    #print(f"Flagged documents: {sum(bool_search)}")
    #bool_search = array(search_2["indicator2"] == 1)
    
    # separate corrections from non-corrections
    df_no_corrections = df.loc[(bool_na & ~bool_search), cols]  # remove flagged documents
    df_corrections = df.loc[(~bool_na | bool_search), cols]
    
    # return filtered results
    if len(df) != (len(df_no_corrections) + len(df_corrections)):
        raise FilterError(f"Non-corrections ({len(df_no_corrections)}) and corrections ({len(df_corrections)}) do no sum to total ({len(df)}).")

    else:
        return df_no_corrections, df_corrections


def filter_actions(df: DataFrame, pattern: str = None, filters: tuple[str] | list[str] = (), columns: tuple | list = ()):
    # get original column names
    cols = df.columns.tolist()
    
    if pattern:
        regex = pattern
        #print(f"used pattern: {regex}")
    else:
        filter_groups = (f"(?:{filter})" for filter in filters)
        regex = fr"{'|'.join(filter_groups)}"
        #print(f"used filters: {regex}")
    
    # Searching fields
    search = search_columns(df, [regex], list(columns), 
                                 return_column="indicator")
    bool_search = array(search["indicator"] == 1)
    print(f"{list(bool_search).count(True)} documents filtered out.")
    
    # filter out flagged documents
    df_filtered = df.loc[~bool_search, cols]
    
    # return filtered results
    return df_filtered

