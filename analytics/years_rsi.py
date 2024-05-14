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

def calculate_ma(prices, period=14):
    return prices.rolling(window=period).mean()

def calculate_sma(prices, period=14):
    return calculate_ma(prices, period)

def calculate_ema(prices, period=14):
    return prices.ewm(span=period, adjust=False).mean()

def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    ema_fast = calculate_ema(prices, fast_period)
    ema_slow = calculate_ema(prices, slow_period)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    macd_histogram = macd_line - signal_line

    return macd_line, signal_line, macd_histogram

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

def add_columns_if_not_exist(ticker):
    table_name = f"{ticker.lower()}_historical"
    columns_to_add = ["RSI REAL", "MA REAL", "SMA REAL", "EMA REAL", "MACD REAL", "Signal REAL", "MACD_Histogram REAL"]
    for column in columns_to_add:
        try:
            alter_table_sql = f"ALTER TABLE {table_name} ADD COLUMN {column.split()[0]} {column.split()[1]};"
            conn.execute(alter_table_sql)
        except Exception as e:
            if "duplicate column name" not in str(e):
                print(f"Error adding column {column.split()[0]} to {table_name}: {e}")

def calculate_and_store_indicators(ticker, rsi_period=14, ma_period=14, sma_period=14, ema_period=14, macd_fast=12, macd_slow=26, macd_signal=9):
    df = get_full_stock_data(ticker)
    if df is not None:
        add_columns_if_not_exist(ticker)
        df['RSI'] = calculate_rsi(df['close'], rsi_period)
        df['MA'] = calculate_ma(df['close'], ma_period)
        df['SMA'] = calculate_sma(df['close'], sma_period)
        df['EMA'] = calculate_ema(df['close'], ema_period)
        df['MACD'], df['Signal'], df['MACD_Histogram'] = calculate_macd(df['close'], macd_fast, macd_slow, macd_signal)

        table_name = f"{ticker.lower()}_historical"
        update_sql = f"UPDATE {table_name} SET RSI = ?, MA = ?, SMA = ?, EMA = ?, MACD = ?, Signal = ?, MACD_Histogram = ? WHERE timestamp = ?;"

        for index, row in df.iterrows():
            conn.execute(update_sql, (
                row['RSI'], row['MA'], row['SMA'], row['EMA'], row['MACD'], row['Signal'], row['MACD_Histogram'],
                index.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()

        print(f"Indicators calculated and stored for {ticker}.")
    else:
        print(f"Unable to calculate indicators for {ticker} due to missing data.")

def load_stock_symbols(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

symbols_file = 'utils/symbols.txt'
stock_symbols = load_stock_symbols(symbols_file)

for ticker in stock_symbols:
    calculate_and_store_indicators(ticker)
