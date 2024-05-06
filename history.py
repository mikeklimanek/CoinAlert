import os
import requests
import pandas as pd
import libsql_experimental as libsql
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
NEW_API_KEY = os.getenv('NEW_API_KEY')
BASE_URL = 'https://api.polygon.io'
API_URL = os.getenv('API_URL')
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

# Connect to the database
conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)
conn.sync()

# Fetch historical data for BTC over the past two years
def fetch_crypto_data(from_symbol, to_symbol, multiplier, timespan, start_date, end_date):
    endpoint = f'/v2/aggs/ticker/X:{from_symbol}{to_symbol}/range/{multiplier}/{timespan}/{start_date}/{end_date}'
    url = f'{BASE_URL}{endpoint}'
    params = {'apiKey': NEW_API_KEY}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()['results']
    else:
        print(f'Error: {response.status_code}, {response.text}')
        return None

# Get date two years ago from today
def get_two_years_ago():
    today = datetime.now()
    two_years_ago = today - timedelta(days=2 * 365)
    return two_years_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')

# Fetch data for the last two years
from_symbol = 'BTC'
to_symbol = 'USD'
multiplier = 1
timespan = 'day'
start_date, end_date = get_two_years_ago()

crypto_data = fetch_crypto_data(from_symbol, to_symbol, multiplier, timespan, start_date, end_date)

if crypto_data:
    # Create a DataFrame from the fetched data
    df = pd.DataFrame(crypto_data)
    df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df.rename(columns={'o': 'open', 'c': 'close', 'h': 'high', 'l': 'low', 'v': 'volume'})

    # Prepare the SQL table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS btc_historical (
        timestamp TEXT PRIMARY KEY,
        open REAL,
        close REAL,
        high REAL,
        low REAL,
        volume REAL
    );
    """
    conn.execute(create_table_sql)

    # Function to insert data in batches
    def insert_data_in_batches(df, batch_size=100):
        insert_sql = """
        INSERT OR IGNORE INTO btc_historical (timestamp, open, close, high, low, volume)
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
            print(f"Inserted batch: {batch}")

    # Insert the DataFrame into the SQL table in batches
    insert_data_in_batches(df)

    print("Data successfully written to the database.")
else:
    print("No data fetched.")
    
    
result = conn.execute("SELECT * FROM btc_historical LIMIT 5;").fetchall()
print(result)