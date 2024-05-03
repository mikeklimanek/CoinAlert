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

    message_lines = []
    message_lines.append(f"Total change for {symbol} in last 24 hours === {total_change_percent:.2f}% from ${first_price} to ${last_price}")


    hours = 24
    for i in range(len(prices) - 1):
        current_price = prices[i]
        next_price = prices[i + 1]
        change_percent = ((next_price - current_price) / current_price) * 100
        if abs(change_percent) >= 4:                # settings for percentage change
            message_lines.append(f"{symbol} Changed from -{hours}h to -{hours-4}h === {change_percent:.2f}% || from ${current_price} to ${next_price}")
        hours -= 4

    
    return None, message_lines if message_lines else None

def send_notification(changes):
    if changes:
        subject = "Significant Crypto Price Changes"
        body = "<strong>Here are the significant changes:</strong><br><br>" + "<br><br>".join(changes)
        send_email(subject, body)

significant_changes = []
for symbol in ['BTC', 'ETH', 'ADA', 'BNB', 'USDT', 'XRP', 'DOGE', 'DOT', 'SOL', 'UNI']:
    error, changes = all_price_changes(conn, symbol)
    if error:
        print(error)
    if changes:
        
        significant_changes.extend(['<br>'.join(changes)])

if significant_changes:
    send_notification(significant_changes)
