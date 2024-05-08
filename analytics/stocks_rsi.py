import libsql_experimental as libsql
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

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

def get_recent_stock_data(ticker, days=20):
    table_name = f"{ticker.lower()}_historical"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    query = f"""
    SELECT timestamp, open, close, high, low, volume 
    FROM {table_name} 
    WHERE timestamp >= '{start_date.strftime('%Y-%m-%d %H:%M:%S')}' 
    ORDER BY timestamp ASC;
    """
    rows = conn.execute(query).fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=['timestamp', 'open', 'close', 'high', 'low', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df
    else:
        print(f"No recent data found for {ticker}.")
        return None

def calculate_and_store_current_day_rsi(ticker, period=14):
    df = get_recent_stock_data(ticker, days=period + 1)
    if df is not None:
        df['RSI'] = calculate_rsi(df['close'], period)
        table_name = f"{ticker.lower()}_historical"
        update_sql = f"UPDATE {table_name} SET RSI = ? WHERE timestamp = ? AND (RSI IS NULL OR RSI = '');"

        for index, row in df.iterrows():
            conn.execute(update_sql, (row['RSI'], index.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()

        print(f"RSI calculated and stored for the current day of {ticker}.")
    else:
        print(f"Unable to calculate RSI for {ticker} due to missing recent data.")

def load_stock_symbols(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def update_rsi_for_all_symbols(symbols_file='utils/symbols.txt'):
    stock_symbols = load_stock_symbols(symbols_file)
    for ticker in stock_symbols:
        calculate_and_store_current_day_rsi(ticker)
