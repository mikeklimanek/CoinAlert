# project/analytics/rsi_report.py
import libsql_experimental as libsql
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)

def get_latest_rsi(stock_list):
    results = []
    latest_date = None
    for ticker in stock_list:
        table_name = f"{ticker.lower()}_historical"
        query = f"""
        SELECT timestamp, open, close, RSI 
        FROM {table_name} 
        ORDER BY timestamp DESC 
        LIMIT 1;
        """
        row = conn.execute(query).fetchone()
        if row:
            current_date = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
            latest_date = latest_date or current_date
            rsi_value = f"{row[3]:.3f}" if row[3] is not None else "N/A"
            results.append(f"{ticker.upper()} | open {row[1]:.3f} | close {row[2]:.3f} | RSI {rsi_value}")
        else:
            results.append(f"{ticker.upper()} | No data available")
    return latest_date, results

def format_date(date):
    return date.strftime('%d%b%y').upper()

def print_latest_rsi_report(stocks=None):
    if stocks is None:
        stocks = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']

    latest_date, latest_rsi = get_latest_rsi(stocks)

    if latest_date:
        formatted_date = format_date(latest_date)
        print(f"RSI for {formatted_date}")
        for rsi_data in latest_rsi:
            print(rsi_data)
    else:
        print("No data available for the selected stocks.")
