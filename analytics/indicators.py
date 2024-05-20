import os
import libsql_experimental as libsql
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")


conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)


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
        

def print_latest_indicators_report(stock_symbols):
    """
    This function prints the latest indicators report for the given stock symbols.
    It assumes that the indicators have already been calculated and stored.
    """
    for ticker in stock_symbols:
        indicators = get_latest_indicators(ticker)
        
        print(f"Ticker: {ticker}")
        for indicator, value in indicators.items():
            print(f"  {indicator}: {value}")
        print()
        
        
def get_latest_indicators(ticker):
    """
    Dummy function to simulate retrieving the latest indicators for a given ticker.
    Replace this with actual logic to fetch the latest indicators from your data store.
    """
    return {
        "RSI": 45.2,
        "Moving Average": 150.3,
        "MACD": -1.5
    }