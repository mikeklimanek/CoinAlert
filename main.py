import requests
import json

def fetch_crypto_data(crypto_id):
    """
    Fetches the real-time price data of a cryptocurrency using CoinGecko API.
    
    :param crypto_id: str, the ID of the cryptocurrency as per CoinGecko. For example, 'bitcoin'.
    :return: dict, containing the price information.
    """
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd'
    response = requests.get(url)
    data = json.loads(response.text)  
    return data


crypto_id = 'bitcoin'
data = fetch_crypto_data(crypto_id)
print(f"Current price of {crypto_id.capitalize()} is ${data[crypto_id]['usd']}")
