import os
import requests
import pandas as pd
import libsql_experimental as libsql
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
NEW_API_KEY = os.getenv('NEW_API_KEY')
BASE_URL = 'https://api.polygon.io'
API_URL = os.getenv('API_URL')
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)
conn.sync()

def fetch_stock_data(ticker, multiplier, timespan, start_date, end_date):
    endpoint = f'/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}'
    url = f'{BASE_URL}{endpoint}'
    params = {'apiKey': NEW_API_KEY}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f'Error: {response.status_code}, {response.text}')
        return None

def get_two_years_ago():
    today = datetime.now()
    two_years_ago = today - timedelta(days=2 * 365)
    return two_years_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')

def create_table(ticker):
    table_name = f"{ticker.lower()}_historical"
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        timestamp TEXT PRIMARY KEY,
        open REAL,
        close REAL,
        high REAL,
        low REAL,
        volume REAL
    );
    """
    conn.execute(create_table_sql)

def insert_data_in_batches(df, table_name, batch_size=100):
    insert_sql = f"""
    INSERT OR IGNORE INTO {table_name} (timestamp, open, close, high, low, volume)
    VALUES (?, ?, ?, ?, ?, ?);
    """
    rows = [
        (
            index.strftime('%Y-%m-%d %H:%M:%S'),
            row['open'], row['close'], row['high'], row['low'], row['volume']
        )
        for index, row in df.iterrows()
    ]

    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        conn.executemany(insert_sql, batch)
        conn.commit()
        print(f"Inserted batch into {table_name}: {batch}")

def load_stock_symbols(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

start_date, end_date = get_two_years_ago()
multiplier = 1
timespan = 'day'
symbols_file = 'utils/symbols.txt'

stock_symbols = load_stock_symbols(symbols_file)

for ticker in stock_symbols:
    print(f'Fetching data for {ticker}...')
    stock_data = fetch_stock_data(ticker, multiplier, timespan, start_date, end_date)

    if stock_data:
        df = pd.DataFrame(stock_data)
        df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df.rename(columns={'o': 'open', 'c': 'close', 'h': 'high', 'l': 'low', 'v': 'volume'})

        table_name = f"{ticker.lower()}_historical"
        create_table(ticker)
        insert_data_in_batches(df, table_name)

        print(f"Data successfully written to the {table_name} table.")
    else:
        print(f"No data fetched for {ticker}.")

result = conn.execute("SELECT * FROM aapl_historical LIMIT 5;").fetchall()
print(result)
