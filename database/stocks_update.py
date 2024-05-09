import os
import requests
import pandas as pd
import libsql_experimental as libsql
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
NEW_API_KEY = os.getenv('NEW_API_KEY')
BASE_URL = 'https://api.polygon.io'
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)
conn.sync()

def data_exists(ticker):
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    table_name = f"{ticker.lower()}_historical"
    query = f"SELECT COUNT(*) FROM {table_name} WHERE timestamp LIKE '{yesterday}%'"
    count = conn.execute(query).fetchone()[0]
    return count > 0

def fetch_stock_data(ticker, start_date, end_date):
    multiplier = 1
    timespan = 'day'
    endpoint = f'/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}'
    url = f'{BASE_URL}{endpoint}'
    params = {'apiKey': NEW_API_KEY}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f'Error: {response.status_code}, {response.text}')
        return None

def load_stock_symbols(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

stock_symbols = load_stock_symbols('utils/symbols.txt')

def insert_data_in_batches(df, table_name, batch_size=100):
    insert_sql = f"""
    INSERT OR IGNORE INTO {table_name} (timestamp, open, close, high, low, volume)
    VALUES (?, ?, ?, ?, ?, ?);
    """
    rows = [
        (index.strftime('%Y-%m-%d %H:%M:%S'), row['open'], row['close'], row['high'], row['low'], row['volume'])
        for index, row in df.iterrows()
    ]
    
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        conn.executemany(insert_sql, batch)
        conn.commit()
        print(f"Inserted batch into {table_name}: {batch}")
        
for ticker in stock_symbols:
    if not data_exists(ticker):
        print(f'Fetching and updating data for {ticker} for yesterday...')
        yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        stock_data = fetch_stock_data(ticker, yesterday, yesterday)
        
        if stock_data:
            df = pd.DataFrame(stock_data)
            df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df.rename(columns={'o': 'open', 'c': 'close', 'h': 'high', 'l': 'low', 'v': 'volume'})
            table_name = f"{ticker.lower()}_historical"
            insert_data_in_batches(df, table_name)
            print(f"Data for {ticker} updated successfully.")
        else:
            print(f"No new data available for {ticker}.")


result = conn.execute("SELECT * FROM aapl_historical WHERE timestamp LIKE '%2024-05-07%'").fetchall()
print(result)
