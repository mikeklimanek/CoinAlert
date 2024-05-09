# project/analytics/indicators_report.py
import libsql_experimental as libsql
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)

def get_latest_indicators(stock_list):
    results = []
    latest_date = None
    for ticker in stock_list:
        table_name = f"{ticker.lower()}_historical"
        query = f"""
        SELECT timestamp, open, close, RSI, MA, SMA, EMA, MACD, Signal, MACD_Histogram
        FROM {table_name}
        ORDER BY timestamp DESC
        LIMIT 1;
        """
        row = conn.execute(query).fetchone()
        if row:
            current_date = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
            latest_date = latest_date or current_date
            rsi_value = f"{row[3]:.3f}" if row[3] is not None else "N/A"
            ma_value = f"{row[4]:.3f}" if row[4] is not None else "N/A"
            sma_value = f"{row[5]:.3f}" if row[5] is not None else "N/A"
            ema_value = f"{row[6]:.3f}" if row[6] is not None else "N/A"
            macd_value = f"{row[7]:.3f}" if row[7] is not None else "N/A"
            signal_value = f"{row[8]:.3f}" if row[8] is not None else "N/A"
            histogram_value = f"{row[9]:.3f}" if row[9] is not None else "N/A"

            results.append(
                f"{ticker.upper()} | open {row[1]:.3f} | close {row[2]:.3f} | RSI {rsi_value} | MA {ma_value} | SMA {sma_value} | EMA {ema_value} | MACD {macd_value} | Signal {signal_value} | Histogram {histogram_value}"
            )
        else:
            results.append(f"{ticker.upper()} | No data available")
    return latest_date, results

def format_date(date):
    return date.strftime('%d%b%y').upper()

def print_latest_indicators_report(stocks=None):
    if stocks is None:
        stocks = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']

    latest_date, latest_indicators = get_latest_indicators(stocks)

    if latest_date:
        formatted_date = format_date(latest_date)
        print(f"Indicators for {formatted_date}")
        for indicator_data in latest_indicators:
            print(indicator_data)
    else:
        print("No data available for the selected stocks.")

if __name__ == "__main__":
    print_latest_indicators_report()
