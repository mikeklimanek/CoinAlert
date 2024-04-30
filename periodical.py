import schedule
import time
import requests
from datetime import datetime
import dotenv
import pytz
import os
import libsql_experimental as libsql
from crypto import fetch_crypto_data, initialize_db, process_and_store_data, conn

dotenv.load_dotenv()
API_URL = os.getenv('API_URL')
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")




def job():
    api_url = os.getenv('API_URL') + '?limit=10'  
    data = fetch_crypto_data(api_url)
    if data:
        process_and_store_data(data, conn)

schedule.every(4).hours.do(job)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down the scheduler...")
    # Optionally, here you can add conn.close() if it's supported and necessary.
except Exception as e:
    print(f"An error occurred: {e}")
