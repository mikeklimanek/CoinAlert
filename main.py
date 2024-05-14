from dotenv import load_dotenv
import logging
load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
import libsql_experimental as libsql
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from analytics.indicators_report import print_latest_indicators_report

load_dotenv()
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")
api_url = os.getenv("STOCK_API_URL")
api_key = os.getenv("STOCK_API_KEY")

conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)

def get_data_from_api(ticker, start_date, end_date):
    params = {
        'symbol': ticker,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'apikey': api_key
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {ticker}: {response.status_code}")
        return None

def store_new_data(ticker, data):
    table_name = f"{ticker.lower()}_historical"
    insert_sql = f"""
    INSERT INTO {table_name} (timestamp, open, close, high, low, volume)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    for entry in data:
        timestamp = datetime.strptime(entry['date'], '%Y-%m-%d')
        conn.execute(insert_sql, (
            timestamp, entry['open'], entry['close'], entry['high'], entry['low'], entry['volume']
        ))
    conn.commit()

def check_and_update_data(ticker):
    table_name = f"{ticker.lower()}_historical"
    query = f"SELECT COUNT(*) FROM {table_name} WHERE timestamp >= ?;"
    two_years_ago = datetime.now() - timedelta(days=2*365)
    row = conn.execute(query, (two_years_ago.strftime('%Y-%m-%d %H:%M:%S'),)).fetchone()
    if row and row[0] >= 2*365:
        yesterday = datetime.now() - timedelta(days=1)
        api_data = get_data_from_api(ticker, yesterday, yesterday)
        if api_data:
            store_new_data(ticker, api_data)
            print(f"Data updated for {ticker}.")
        else:
            print(f"No new data available for {ticker}.")
    else:
        print(f"Not enough historical data for {ticker}.")

def calculate_and_store_indicators(ticker):
    from analytics.years_rsi import calculate_rsi, calculate_ma, calculate_sma, calculate_ema, calculate_macd, get_full_stock_data, add_columns_if_not_exist
    
    df = get_full_stock_data(ticker)
    if df is not None:
        add_columns_if_not_exist(ticker)
        df['RSI'] = calculate_rsi(df['close'])
        df['MA'] = calculate_ma(df['close'])
        df['SMA'] = calculate_sma(df['close'])
        df['EMA'] = calculate_ema(df['close'])
        df['MACD'], df['Signal'], df['MACD_Histogram'] = calculate_macd(df['close'])

        table_name = f"{ticker.lower()}_historical"
        update_sql = f"""
        UPDATE {table_name} SET RSI = ?, MA = ?, SMA = ?, EMA = ?, MACD = ?, Signal = ?, MACD_Histogram = ? 
        WHERE timestamp = ?;
        """

        for index, row in df.iterrows():
            conn.execute(update_sql, (
                row['RSI'], row['MA'], row['SMA'], row['EMA'], row['MACD'], row['Signal'], row['MACD_Histogram'],
                index.strftime('%Y-%m-%d %H:%M:%S')
            ))
        conn.commit()

        print(f"Indicators calculated and stored for {ticker}.")
    else:
        print(f"Unable to calculate indicators for {ticker} due to missing data.")

def load_stock_symbols(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    symbols_file = 'utils/symbols.txt'
    stock_symbols = load_stock_symbols(symbols_file)

    for ticker in stock_symbols:
        check_and_update_data(ticker)
        calculate_and_store_indicators(ticker)
    
    print_latest_indicators_report(stock_symbols)

if __name__ == "__main__":
    main()
