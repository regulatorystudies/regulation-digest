from pathlib import Path
from datetime import date

from retrieve_documents import retrieve_documents


if __name__ == "__main__":
    
    start = input("Start date [yyyy-mm-dd]: ")
    end = input("End date [yyyy-mm-dd]: ")
    download = input("Download? [yes/no]: ")

    df = retrieve_documents(start_date=start, end_date=end, test_filters=True)
    print(df.head())
    if download.lower() in ("yes", "y"):
        outpath = Path(__file__).parents[1].joinpath("output")
        df.to_csv(outpath / f"removed_documents_{date.today()}.csv", index=False)
