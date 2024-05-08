# /home/dthxsu/workspace/github.com/dthxsu/CoinAlert/v1_crypto/crypto.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from v1_crypto.utils.auth import get_database_connection


conn = get_database_connection()


def all_price_changes(conn, symbol):
    id_patterns = {
        'BTC': 'B%',
        'ETH': 'E%',
        'ADA': 'C%',
        'BNB': 'N%',
        'USDT': 'T%',
        'XRP': 'X%',
        'DOGE': 'D%',
        'DOT': 'P%',
        'SOL': 'S%',
        'UNI': 'U%'
    }

    id_pattern = id_patterns.get(symbol)

    if not id_pattern:
        print(f"No pattern found for {symbol}")
        return

    query = f"""
    SELECT id, price FROM cryptocurrencies
    WHERE symbol = ? AND id LIKE ?
    ORDER BY CAST(SUBSTR(id, 2) AS INTEGER) DESC
    LIMIT 6
    """
    
    results = conn.execute(query, (symbol, id_pattern)).fetchall()

    if len(results) < 6:
        print(f"Insufficient data for {symbol}")
        return
    
    results.reverse()
    
    prices = [row[1] for row in results]
    ids = [row[0] for row in results]
    print("_______________________________________________________________")
    print(f"Price changes for {symbol} from last day:\n_______________________________________________________________")
    first_price = prices[0]
    last_price = prices[-1]
    
    total_change_percent = ((last_price - first_price) / first_price) * 100
    print(f"Total change from -24h till now === {total_change_percent:.2f}%   ||   from ${first_price} to ${last_price}")
    
    hours = 24
    for i in range(len(prices) - 1):
        current_price = prices[i]
        next_price = prices[i + 1]
        change_percent = ((next_price - current_price) / current_price) * 100
        print(f"Change from -{hours}h to -{hours-4}h === {change_percent:.2f}%   ||   from ${current_price} to ${next_price}")
        hours -= 4
        
        
for i in ['BTC', 'ETH', 'ADA', 'BNB', 'USDT', 'XRP', 'DOGE', 'DOT', 'SOL', 'UNI']:
    all_price_changes(conn, i)