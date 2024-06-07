from database.stocks_update import check_and_update_data, store_new_data, insert_data_in_batches
from database.data_fetch import get_data_from_api
from analytics.indicators import calculate_and_store_indicators
from utils.symbols import load_stock_symbols
from datetime import datetime, timedelta

def main():
    file_path = 'utils/symbols.txt'
    stock_symbols = load_stock_symbols(file_path)

    for ticker in stock_symbols:
        # yesterday = datetime.now() - timedelta(1)
        start_date = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
        end_date = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
        data = get_data_from_api(ticker, start_date, end_date)
        if data:
            # store_new_data(data)
            # insert_data_in_batches
            check_and_update_data(ticker)
            calculate_and_store_indicators(ticker)
        else:
            print(f"No new data available for {ticker}.")
            
    print("Data update process completed.")

if __name__ == "__main__":
    main()
