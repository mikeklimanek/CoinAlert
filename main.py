import requests
import pandas as pd
import os
import dotenv

dotenv.load_dotenv()

NEW_API_KEY = os.getenv('NEW_API_KEY')
BASE_URL = 'https://api.polygon.io'

def fetch_crypto_data(from_symbol, to_symbol, multiplier, timespan, start_date, end_date):
    endpoint = f'/v2/aggs/ticker/X:{from_symbol}{to_symbol}/range/{multiplier}/{timespan}/{start_date}/{end_date}'
    url = f'{BASE_URL}{endpoint}'
    params = {'apiKey': NEW_API_KEY}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()['results']
    else:
        print(f'Error: {response.status_code}, {response.text}')
        return None

def calculate_rsi(prices, period=30):
    delta = prices.diff()
    gains = (delta.where(delta > 0, 0)).fillna(0)
    losses = (-delta.where(delta < 0, 0)).fillna(0)
    
    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


from_symbol = 'BTC'
to_symbol = 'USD'
multiplier = 1
timespan = 'day'
start_date = '2024-04-01'
end_date = '2024-04-30'

crypto_data = fetch_crypto_data(from_symbol, to_symbol, multiplier, timespan, start_date, end_date)

if crypto_data:
    df = pd.DataFrame(crypto_data)
    df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['close'] = df['c']

    # Calculate RSI
    df['RSI'] = calculate_rsi(df['close'])
    print(df[['close', 'RSI']])
