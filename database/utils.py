from utils.auth import get_database_connection

conn = get_database_connection()


def generate_new_id(symbol, conn):
    letter_map = {
        "Bitcoin": "B", "Ethereum": "E", "Cardano": "C", "Binance Coin": "N",
        "Tether": "T", "XRP": "X", "Dogecoin": "D", "Polkadot": "P",
        "Solana": "S", "Uniswap": "U"
    }
    letter = letter_map.get(symbol)
    if not letter:
        raise ValueError("Symbol not recognized")

    query = f"SELECT id FROM cryptocurrencies WHERE id LIKE '{letter}%'"
    results = conn.execute(query).fetchall()
    max_number = 0


    for row in results:
        num = int(row[0][1:])
        if num > max_number:
            max_number = num

    new_id = f"{letter}{max_number + 1}"

    return new_id

