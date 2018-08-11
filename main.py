from stockcrawler.fetch_data import FetchData

if __name__ == '__main__':
    fetch = FetchData(120)  # 10 years
    # execute batch
    fetch.execute()
