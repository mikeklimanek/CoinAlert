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

def get_latest_rsi_date(ticker):
    table_name = f"{ticker.lower()}_historical"
    query = f"""
    SELECT timestamp 
    FROM {table_name} 
    WHERE RSI IS NOT NULL
    ORDER BY timestamp DESC
    LIMIT 1;
    """
    result = conn.execute(query).fetchone()
    return pd.to_datetime(result[0]) if result else None

def get_partial_stock_data(ticker, start_date=None):
    table_name = f"{ticker.lower()}_historical"
    if start_date:
        query = f"""
        SELECT timestamp, open, close, high, low, volume 
        FROM {table_name} 
        WHERE timestamp >= '{start_date.strftime('%Y-%m-%d %H:%M:%S')}'
        ORDER BY timestamp ASC;
        """
    else:
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

def calculate_and_store_rsi_incrementally(ticker, period=14):
    latest_rsi_date = get_latest_rsi_date(ticker)
    df_new_data = get_partial_stock_data(ticker, latest_rsi_date)

    if df_new_data is not None:
        df_existing_data = get_partial_stock_data(ticker)
        df_combined = pd.concat([df_existing_data, df_new_data]).drop_duplicates()

        df_combined['RSI'] = calculate_rsi(df_combined['close'], period)
        df_updated = df_combined.loc[df_new_data.index]

        table_name = f"{ticker.lower()}_historical"
        update_sql = f"UPDATE {table_name} SET RSI = ? WHERE timestamp = ?;"

        for index, row in df_updated.iterrows():
            conn.execute(update_sql, (row['RSI'], index.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()

        print(f"RSI incrementally calculated and stored for {ticker}.")
    else:
        print(f"Unable to calculate RSI for {ticker} due to missing data.")

def load_stock_symbols(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

symbols_file = 'utils/symbols.txt'
stock_symbols = load_stock_symbols(symbols_file)

for ticker in stock_symbols:
    calculate_and_store_rsi_incrementally(ticker)
