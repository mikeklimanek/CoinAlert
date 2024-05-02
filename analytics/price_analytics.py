import dotenv
import os
import libsql_experimental as libsql
dotenv.load_dotenv()
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)
conn.sync()

def print_price_changes(conn, symbol):
    query = """
    SELECT id, price FROM cryptocurrencies
    WHERE symbol = ? AND id LIKE 'B%'
    ORDER BY CAST(SUBSTR(id, 2) AS INTEGER) DESC
    LIMIT 6
    """
    
    results = conn.execute(query, [symbol]).fetchall()

    if len(results) < 6:
        print(f"Insufficient data for {symbol}")
        return
    
    results.reverse()
    
    prices = [row[1] for row in results]
    ids = [row[0] for row in results]
    print(f"Price changes for {symbol} from last day:")
    first_price = prices[0]
    last_price = prices[-1]
    
    total_change_percent = ((last_price - first_price) / first_price) * 100
    print(f"Total change from {ids[0]} to {ids[-1]}: {total_change_percent:.2f}%")
    
    for i in range(len(prices) - 1):
        current_price = prices[i]
        next_price = prices[i + 1]
        change_percent = ((next_price - current_price) / current_price) * 100
        print(f"Change from {ids[i]} to {ids[i + 1]}: {change_percent:.2f}%")
        
print_price_changes(conn, 'Bitcoin')
    