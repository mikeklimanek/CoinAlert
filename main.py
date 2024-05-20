from database.stocks_update import check_and_update_data, store_new_data
from database.data_fetch import get_data_from_api
from analytics.indicators import calculate_and_store_indicators, print_latest_indicators_report
from utils.symbols import load_stock_symbols

def main():
    symbols_file = 'utils/symbols.txt'
    stock_symbols = load_stock_symbols(symbols_file)

    for ticker in stock_symbols:
        data = get_data_from_api(ticker)
        store_new_data(data)
        check_and_update_data(ticker)
        calculate_and_store_indicators(ticker)
    
    print_latest_indicators_report(stock_symbols)

if __name__ == "__main__":
    main()
