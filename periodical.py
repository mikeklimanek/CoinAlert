import schedule
import time
import os
from crypto import fetch_crypto_data, conn
from database.crypto_db import process_and_store_data





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
