from retrieve_documents import retrieve_documents

if __name__ == "__main__":
    
    start = input("Start date [yyyy-mm-dd]: ")
    end = input("End date [yyyy-mm-dd]: ")

    df = retrieve_documents(start_date=start, end_date=end, test_filters=True)
    print(df.head())
