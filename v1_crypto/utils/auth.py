# /home/dthxsu/workspace/github.com/dthxsu/CoinAlert/v1_crypto/crypto.py
import dotenv
import os
import libsql_experimental as libsql
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

def get_database_connection():
    url = os.getenv("TURSO_DATABASE_URL")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")
    conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)
    conn.sync()
    return conn
