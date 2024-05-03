import dotenv
import os
import libsql_experimental as libsql

dotenv.load_dotenv()

def get_database_connection():
    url = os.getenv("TURSO_DATABASE_URL")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")
    conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)
    conn.sync()
    return conn
