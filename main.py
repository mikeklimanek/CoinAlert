from dotenv import load_dotenv
import requests
from flask import Flask
from pandas import json_normalize
import pandas as pd
from urllib.parse import urlencode
import os

from typing import Dict, List, Union, Optional, Any
import warnings

warnings.filterwarnings("ignore")

app = Flask(__name__)

@app.route('/')
def home():
    return tm_API('tokens')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)  
load_dotenv()
API_key = os.getenv('API_KEY')


def tm_API(endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
	"""Obtain data from the Token Metrics Data API

	Args:
		endpoint (str): The endpoint of the API
		payload (Optional[Dict[str, Any]], optional): The parameters to send to the API. Defaults to None.

	Returns:
		Dict[str, Any]: The response from the API
	"""

	if payload:
		url = 'https://api.tokenmetrics.com/' + endpoint + '?' + urlencode(payload)
	else:
		url = 'https://api.tokenmetrics.com/' + endpoint 
	headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'api_key': API_key}
	response = requests.get(url, headers=headers)
	print(response.json())
	return response.json()

endpoint = 'tokens'
params = {}
response = tm_API(endpoint,params)
coins = json_normalize(response['data'])
coins = coins.sort_values(by = 'TOKEN_ID').reset_index(drop = True)
coins[coins.NAME.isin(['Bitcoin','Ethereum','Litecoin'])]


# Obtain data from the Binance US API
r = requests.get('https://api.binance.us/api/v3/klines', params = {'symbol': 'BTCUSDT', 'interval': '1d', 'limit': 1000}).json()

# Convert to pandas dataframe
col = ['Open time','Open','High','Low','Close','Volume','Close time','Quote asset volume','Number of trades',
       'Taker buy volume','Taker buy quote asset volume','Ignore']
btcusdt = pd.DataFrame(r, columns = col)

# Clean up the data
btcusdt['Close time'] = pd.to_datetime(btcusdt['Open time'], unit='ms')
btcusdt['Close time'] = btcusdt['Close time'].dt.strftime('%Y-%m-%d')
btcusdt.rename(columns = {'Close time': 'Date'}, inplace = True)
btcusdt[['Open', 'High', 'Low', 'Close', 'Volume']] = btcusdt[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
btcusdt = btcusdt[['Date','Open', 'High', 'Low', 'Close', 'Volume']]


