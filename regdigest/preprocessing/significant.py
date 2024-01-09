# gather details on rule significance
# retrieve FR tracking data
# isolate significance columns
# merge with retrieved documents (on document_number)


from pandas import DataFrame, read_excel


def retrieve_fr_tracking_data(url: str = r"https://github.com/regulatorystudies/Reg-Stats/raw/main/data/fr_tracking/fr_tracking.xlsx"):
    
    df = read_excel(url)
    
    return df


if __name__ == "__main__":
    
    df = retrieve_fr_tracking_data()
