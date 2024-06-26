# /home/dthxsu/workspace/github.com/dthxsu/CoinAlert/v1_crypto/crypto.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
import requests
import dotenv
import libsql_experimental as libsql
from v1_crypto.database.crypto_db import process_and_store_data
from v1_crypto.analytics.changes_alert import all_price_changes
from v1_crypto.utils.email_setup import send_email


dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

API_URL = os.getenv('API_URL')
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)
conn.sync()


    
def fetch_crypto_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

api_result = requests.get(API_URL + '?limit=10')
api_result_json = api_result.json()
process_and_store_data(api_result_json, conn)

conn.sync()

def send_notification(changes):
    if changes:
        subject = "Significant Crypto Price Changes"
        body = "<strong>Here are the significant changes:</strong><br><br>" + "<br><br>".join(changes)
        try:
            send_email(subject, body)
            print("Email sent successfully!")
        except Exception as e:
            print("Error sending email:", str(e))
            print("Retrying one more time...")
            try:
                send_email(subject, body)
                print("Email sent successfully after retry!")
            except Exception as e:
                print("Error sending email after retry:", str(e))

significant_changes = []
for symbol in ['BTC', 'ETH', 'ADA', 'BNB', 'USDT', 'XRP', 'DOGE', 'DOT', 'SOL', 'UNI']:
    error, changes = all_price_changes(conn, symbol)
    if error:
        print(error)
    if changes:
        
        significant_changes.extend(['<br>'.join(changes)])

if significant_changes:
    send_notification(significant_changes)
else:
    print("No significant changes found.")





