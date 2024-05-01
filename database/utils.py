import os
import libsql_experimental as libsql


url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)
conn.sync()

def generate_new_id(symbol, conn):
    letter_map = {
        "Bitcoin": "B", "Ethereum": "E", "Cardano": "C", "Binance Coin": "N",
        "Tether": "T", "XRP": "X", "Dogecoin": "D", "Polkadot": "P",
        "Solana": "S", "Uniswap": "U"
    }
    letter = letter_map.get(symbol)
    if not letter:
        raise ValueError("Symbol not recognized")


    result = conn.execute(f"SELECT id FROM cryptocurrencies WHERE id LIKE '{letter}%' ORDER BY id DESC LIMIT 1")
    last_id = result.fetchone()
    if last_id is None:
        new_id = f"{letter}1"
    else:
        number = int(last_id[0][1:]) + 1
        new_id = f"{letter}{number}"
    return new_id
