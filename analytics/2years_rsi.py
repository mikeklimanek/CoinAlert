import libsql_experimental as libsql
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gains = (delta.where(delta > 0, 0)).fillna(0)
    losses = (-delta.where(delta < 0, 0)).fillna(0)

    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def get_full_stock_data(ticker):
    table_name = f"{ticker.lower()}_historical"
    query = f"""
    SELECT timestamp, open, close, high, low, volume 
    FROM {table_name} 
    ORDER BY timestamp ASC;
    """
    rows = conn.execute(query).fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=['timestamp', 'open', 'close', 'high', 'low', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df
    else:
        print(f"No data found for {ticker}.")
        return None

def add_rsi_column(ticker):
    table_name = f"{ticker.lower()}_historical"
    alter_table_sql = f"ALTER TABLE {table_name} ADD COLUMN RSI REAL;"
    try:
        conn.execute(alter_table_sql)
    except Exception as e:
        if "duplicate column name: RSI" not in str(e):
            print(f"Error adding RSI column to {table_name}: {e}")

def calculate_and_store_rsi(ticker, period=14):
    df = get_full_stock_data(ticker)
    if df is not None:
        add_rsi_column(ticker)
        df['RSI'] = calculate_rsi(df['close'], period)

        table_name = f"{ticker.lower()}_historical"
        update_sql = f"UPDATE {table_name} SET RSI = ? WHERE timestamp = ?;"

        for index, row in df.iterrows():
            conn.execute(update_sql, (row['RSI'], index.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()

        print(f"RSI calculated and stored for {ticker}.")
    else:
        print(f"Unable to calculate RSI for {ticker} due to missing data.")

def load_stock_symbols(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

symbols_file = 'utils/symbols.txt'
stock_symbols = load_stock_symbols(symbols_file)

for ticker in stock_symbols:
    calculate_and_store_rsi(ticker)
