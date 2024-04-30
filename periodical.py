import schedule
import time

def job():
    api_url = os.getenv('API_URL') + '?limit=1'  # Adjust the limit as needed
    data = fetch_crypto_data(api_url)
    if data:
        conn = libsql.connect("coin-alert.db", sync_url=os.getenv("TURSO_DATABASE_URL"), auth_token=os.getenv("TURSO_AUTH_TOKEN"))
        initialize_db(conn)
        process_and_store_data(data, conn)
        conn.close()

schedule.every(4).hours.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
