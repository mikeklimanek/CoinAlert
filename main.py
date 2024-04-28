import requests
import dotenv
import os

dotenv.load_dotenv()
API_Key = os.getenv('API_KEY')

params = {
  'access_key': API_Key
}

api_result = requests.get('http://api.marketstack.com/v1/tickers/aapl/eod/latest', params)

api_response = api_result.json()
print(api_response)

for stock_data in api_response['data']:
    print(u'Ticker %s has a day high of  %s on %s' % (
      stock_data['symbol'],
      stock_data['high'],
      stock_data['date']
    ))
