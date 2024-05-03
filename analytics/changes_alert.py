from utils.auth import get_database_connection
from utils.email_setup import send_email


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
        return f"No pattern found for {symbol}", None

    query = """
    SELECT id, price FROM cryptocurrencies
    WHERE symbol = ? AND id LIKE ?
    ORDER BY CAST(SUBSTR(id, 2) AS INTEGER) DESC
    LIMIT 6
    """
    results = conn.execute(query, (symbol, id_pattern)).fetchall()
    if len(results) < 6:
        return f"Insufficient data for {symbol}", None

    results.reverse()
    prices = [row[1] for row in results]
    first_price = prices[0]
    last_price = prices[-1]
    total_change_percent = ((last_price - first_price) / first_price) * 100

    message = f"<br>Total change for {symbol} from -24h till now === {total_change_percent:.2f}% from ${first_price} to ${last_price}"
    significant_changes = []

    if abs(total_change_percent) >= 2:
        significant_changes.append(message)
    
    return None, significant_changes

def send_notification(changes):
    if changes:
        subject = "Significant Crypto Price Changes"
        body = "Here are the significant changes:\n" + "\n".join(changes)
        send_email(subject, body)

significant_changes = []
for symbol in ['BTC', 'ETH', 'ADA', 'BNB', 'USDT', 'XRP', 'DOGE', 'DOT', 'SOL', 'UNI']:
    error, changes = all_price_changes(conn, symbol)
    if error:
        print(error)
    if changes:
        significant_changes.extend(changes)

if significant_changes:
    send_notification(significant_changes)
