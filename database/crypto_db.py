from datetime import datetime
import pytz
from .utils import generate_new_id
from utils.auth import get_database_connection

conn = get_database_connection()



def initialize_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cryptocurrencies (
            id TEXT,
            name TEXT,
            symbol TEXT,
            website_slug TEXT,
            rank INTEGER,
            circulating_supply REAL,
            total_supply REAL,
            max_supply REAL,
            price REAL,
            volume_24h REAL,
            market_cap REAL,
            percent_change_1h REAL,
            percent_change_24h REAL,
            percent_change_7d REAL,
            last_updated INTEGER,
            entry_datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        );
    """)
    conn.commit()
    
initialize_db(conn)



def process_and_store_data(data, conn):
    for key, value in data['data'].items():
        new_id = generate_new_id(value['name'], conn)
        last_updated_utc = datetime.utcfromtimestamp(value['last_updated'])
        cet_timezone = pytz.timezone('CET')
        last_updated_cet = last_updated_utc.replace(tzinfo=pytz.utc).astimezone(cet_timezone)

        usd_quotes = value['quotes']['USD']
        conn.execute("""
            INSERT INTO cryptocurrencies (
                id, name, symbol, website_slug, rank, circulating_supply, total_supply, max_supply,
                price, volume_24h, market_cap, percent_change_1h, percent_change_24h, percent_change_7d, last_updated
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            new_id, value['name'], value['symbol'], value['website_slug'], value['rank'],
            value['circulating_supply'], value['total_supply'], value['max_supply'],
            usd_quotes['price'], usd_quotes['volume_24h'], usd_quotes['market_cap'],
            usd_quotes['percent_change_1h'], usd_quotes['percent_change_24h'], usd_quotes['percent_change_7d'],
            last_updated_cet.timestamp()
        ))

    conn.commit()