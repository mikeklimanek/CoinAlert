import os
from dotenv import load_dotenv
import json
import requests
from pandas import json_normalize
from urllib.parse import urlencode

from typing import Dict, List, Union, Optional, Any
import warnings

warnings.filterwarnings("ignore")

load_dotenv()
APIkey = os.getenv('API_KEY')

def tm_API(endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Obtain data from the Token Metrics Data API."""
    try:
        if payload:
            url = 'https://alpha.data-api.tokenmetrics.com/v1/' + endpoint + '?' + urlencode(payload)
        else:
            url = 'https://alpha.data-api.tokenmetrics.com/v1/' + endpoint

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'api_key': APIkey
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Connection Error: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
    return {}

endpoint = 'tokens'
params = {}
response = tm_API(endpoint, params)
if response:
    coins = json_normalize(response['data'])
    coins = coins.sort_values(by='TOKEN_ID').reset_index(drop=True)
    filtered_coins = coins[coins.NAME.isin(['Bitcoin', 'Ethereum', 'Litecoin'])].reset_index(drop=True)
    print(filtered_coins)
