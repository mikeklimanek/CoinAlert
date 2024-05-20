import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
api_url = os.getenv("API_URL")
api_key = os.getenv("API_KEY")




def get_data_from_api(ticker, start_date, end_date):
    params = {
        'symbol': ticker,
        'start_date': start_date,
        'end_date': end_date,
        'apikey': api_key
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {ticker}: {response.status_code}")
        return None