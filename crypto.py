import requests
import dotenv
import os
import libsql_experimental as libsql
from database.crypto_db import initialize_db, process_and_store_data
dotenv.load_dotenv()
API_URL = os.getenv('API_URL')
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)
conn.sync()

initialize_db(conn)

    
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





