import os
from crypto import fetch_crypto_data, conn
from database.crypto_db import process_and_store_data

def job():
    api_url = os.getenv('API_URL') + '?limit=10'  
    data = fetch_crypto_data(api_url)
    if data:
        process_and_store_data(data, conn)

if __name__ == "__main__":
    job()