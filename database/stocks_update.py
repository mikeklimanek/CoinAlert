import os
import requests
import time
import pandas as pd
import libsql_experimental as libsql
from datetime import datetime, timedelta
from dotenv import load_dotenv
from requests.exceptions import HTTPError, ConnectionError
from database.data_fetch import get_data_from_api

load_dotenv()
NEW_API_KEY = os.getenv('NEW_API_KEY')
BASE_URL = 'https://api.polygon.io'
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)
conn.sync()

def data_exists(ticker):
    from_day = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    table_name = f"{ticker.lower()}_historical"
    query = f"SELECT COUNT(*) FROM {table_name} WHERE timestamp LIKE '{from_day}%'"
    count = conn.execute(query).fetchone()[0]
    return count > 0

def fetch_stock_data(ticker, start_date, end_date):
    multiplier = 1
    timespan = 'day'
    endpoint = f'/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}'
    url = f'{BASE_URL}{endpoint}'
    params = {'apiKey': NEW_API_KEY}
    
    attempts = 0
    while attempts < 5:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get('results', [])
        except (HTTPError, ConnectionError) as e:
            print(f'Error: {e}. Retrying...')
            attempts += 1
            time.sleep(2 ** attempts)  # Exponential backoff
    print(f'Failed to fetch data for {ticker} after {attempts} attempts.')
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
        try:
            conn.executemany(insert_sql, batch)
            conn.commit()
            print(f"Inserted batch into {table_name}: {batch}")
        except Exception as e:
            print(f"Failed to insert into batch: {batch}: {e}")
        
for ticker in stock_symbols:
    if not data_exists(ticker):
        from_day = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        current_day = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        print(f'Fetching and updating data for {ticker} for {from_day}...')
        stock_data = fetch_stock_data(ticker, from_day, current_day)
        
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


result = conn.execute("SELECT * FROM aapl_historical").fetchall()



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
    
    