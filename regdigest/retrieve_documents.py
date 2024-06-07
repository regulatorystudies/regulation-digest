# -*- coding: utf-8 -*-
"""
Mark Febrizio

Created: 2022-06-13

Last modified: 2024-01-12
"""
# dependencies
from copy import deepcopy
from datetime import date
import functools
import json
import logging
from pathlib import Path
import re

from fr_toolbelt.api_requests import (
    get_documents_by_date, 
    get_documents_by_number, 
    parse_document_numbers, 
    )
from fr_toolbelt.preprocessing import AgencyMetadata, AgencyData, RegInfoData
from pandas import DataFrame

try:  # for use as module: python -m regdigest
    from .modules import (
        filter_corrections, 
        filter_actions, 
        get_significant_info, 
        )
    from .regex_filters import FILTER_ROUTINE
except ImportError:
    # hacky but allows alternate script to work
    from modules import (
        filter_corrections, 
        filter_actions, 
        get_significant_info, 
        )
    from regex_filters import FILTER_ROUTINE

FIELDS = (
    'document_number', 
    'publication_date', 
    'agency_names', 
    'agencies', 
    'citation', 
    'start_page', 
    'end_page', 
    'html_url', 
    'pdf_url', 
    'title', 
    'type', 
    'action', 
    'regulation_id_number_info', 
    'correction_of', 
    )


# -- utils -- #


def export_data(df: DataFrame, 
                path: Path, 
                file_name: str = f"federal_register_clips_{date.today()}.csv"):
    """Save data to file in CSV format.

    Args:
        df (DataFrame): Data as a DataFrame.
        path (Path): Path to save directory.
        file_name (str, optional): File name. Defaults to f"federal_register_clips_{date.today()}.csv".
    """    
    with open(path / file_name, "w", encoding = "utf-8") as f:
        df.to_csv(f, lineterminator="\n")
    print(f"Exported data as csv to {path}.")


def create_paths(input_file: bool = False) -> list[Path]:
    """Create paths for input and output data.

    Args:
        input_file (bool, optional): True if using input file. Defaults to False.

    Returns:
        list[Path]: List of path-like objects.
    """    
    dirs = []
    p = Path(__file__)
    output_dir = p.parents[1].joinpath("output")
    dirs.append(output_dir)
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    
    if input_file:  # create input directory if using input file
        input_dir = p.parents[1].joinpath("input")
        input_dir.mkdir(parents=True, exist_ok=True)
        dirs.append(input_dir)
    
    return dirs


def log_errors(func, filepath: Path = Path(__file__).parents[1] / "error.log"):
    """Decorator for logging errors in given file.
    Supply a value for 'filepath' to change the default name or location of the error log.
    Defaults to filepath = Path(__file__).parents[1]/"error.log".
    """    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as err:
            logging.basicConfig(
                filename=filepath, 
                encoding="utf-8", 
                format= "-----\n%(asctime)s -- %(levelname)s", 
                datefmt="%Y-%m-%d %H:%M:%S"
                )
            logging.exception("\n")
            print(f"Logged error ({err}) in {filepath.name}. Exiting program.")
    return wrapper


# -- main functions -- #


def retrieve_documents(
        start_date: str | date = None, 
        end_date: str | date = None, 
        input_path: Path = None, 
    ):
    """Main pipeline for retrieving Federal Register documents.

    Args:
        metadata (dict): Agency metadata for cleaning agency names.
        input_path (Path, optional): Path to input with documents to retrieve. Defaults to None.

    Returns:
        DataFrame: Output data.
    """
    if input_path is None:  # date range
        if start_date is None:
            start_date = f"{date.today()}"
        results, count = get_documents_by_date(start_date, end_date=end_date, fields=FIELDS, handle_duplicates="drop")
    elif isinstance(input_path, (Path, str)):  # input file
        document_numbers = parse_document_numbers(input_path) 
        results, count = get_documents_by_number(document_numbers, fields=FIELDS)
        start_date = min(date.fromisoformat(d.get("publication_date", f"{date.today()}")) for d in results)
        print(start_date)
    else:
        raise TypeError
    
    if count == 0:
        print("No documents returned.")
        return None
    
    # create DataFrame; filter out documents; clean agency info; drop unneeded columns
    #results = process_documents(results, which=("agencies", "rin", ), return_format = "name")
    metadata, schema = AgencyMetadata().get_agency_metadata()
    results = AgencyData(results, metadata, schema, field_keys=("agencies", "agency_names")).process_data(return_format = "name")
    results = [r | {"agency_names": "; ".join([metadata.get(a).get("name", "") for a in r.get("agency_slugs", "")])} for r in results]
    results = RegInfoData(results).process_data()
    
    df = DataFrame(results)
    df, _ = filter_corrections(df)
    df = filter_actions(df, filters = FILTER_ROUTINE, columns = ["title"])
    document_numbers = df.loc[:, "document_number"].to_numpy().tolist()
    df = get_significant_info(df, start_date, document_numbers)
    df = df.astype({"independent_reg_agency": "int64"}, errors="ignore")
    df = df.sort_values(["publication_date", "document_number"])
    df = df.rename(columns={"parent_name": "parent_agency_names"}, errors="ignore")
    keep_cols = [
        "document_number", 
        "publication_date", 
        "agency_names", 
        "parent_agency_names",
        "citation", 
        "start_page", 
        "end_page", 
        "html_url", 
        "pdf_url", 
        "title", 
        "type",
        "action", 
        "rin", 
        "rin_priority", 
        "independent_reg_agency", 
        "significant", 
        "3f1_significant", 
        "major", 
        ]
    
    # return data
    return df.loc[:, [c for c in keep_cols if c in df.columns]].set_index("document_number")


@log_errors
def main():
    """Command-line interface for retrieving documents.
    """
    # loop for getting inputs, calling main pipeline function, and saving data
    # won't break until it receives valid input
    while True:
        # print prompt to console
        get_input = input("Use input file containing document numbers or urls? [yes/no]: ")
        
        # check user inputs
        if get_input.lower() in ("y", "yes"):
            output_dir, input_dir = create_paths(input_file=True)
            df = retrieve_documents(input_path=input_dir)
            break
        elif get_input.lower() in ("n", "no"):
            [output_dir] = create_paths()
            while True:  # doesn't exit until correctly formatted input received
                pattern = r"\d{4}-[0-1]\d{1}-[0-3]\d{1}"
                start_date = input("Input start date [yyyy-mm-dd]: ")
                match_1 = re.fullmatch(pattern, start_date, flags=re.I)
                end_date = input("Input end date [yyyy-mm-dd]. Or just press enter to use today as the end date: ")
                match_2 = re.fullmatch(pattern, end_date, flags=re.I)
                if match_1 and (match_2 or end_date==""):
                    #print(type(end_date), f"{end_date=}", len(end_date), sep=r" | ")
                    df = retrieve_documents(start_date=start_date, end_date=end_date)
                    break
                else:
                    print("Invalid input. Must enter dates in format 'yyyy-mm-dd'.")
            break
        else:
            print("Invalid input. Must enter 'y' or 'n'.")
    
    if df is not None:
        export_data(df, output_dir)


if __name__ == "__main__":
    
    main()
