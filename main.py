from database.stocks_update import check_and_update_data, store_new_data
from database.data_fetch import get_data_from_api
from analytics.indicators import calculate_and_store_indicators, print_latest_indicators_report
from utils.symbols import load_stock_symbols
from datetime import datetime, timedelta

def main():
    file_path = 'utils/symbols.txt'
    stock_symbols = load_stock_symbols(file_path)

    for ticker in stock_symbols:
        yesterday = datetime.now() - timedelta(1)
        start_date = yesterday.strftime('%Y-%m-%d')
        end_date = start_date
        data = get_data_from_api(ticker, start_date, end_date)
        if data:
            store_new_data(data)
            check_and_update_data(ticker)
            calculate_and_store_indicators(ticker)
        else:
            print(f"No new data available for {ticker}.")

    print_latest_indicators_report(stock_symbols)

if __name__ == "__main__":
    main()
