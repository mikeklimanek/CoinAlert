import requests
from datetime import datetime
import dotenv
import pytz
import os
import libsql_experimental as libsql
dotenv.load_dotenv()
API_URL = os.getenv('API_URL')
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect("coin-alert.db", sync_url=url, auth_token=auth_token)
conn.sync()


api_result = requests.get(API_URL + '?limit=1')


api_result_json = api_result.json()


name = api_result_json['data']['1']['name']
usd_price = api_result_json['data']['1']['quotes']['USD']['price']
last_updated_unix = api_result_json['data']['1']['last_updated']

last_updated_utc = datetime.utcfromtimestamp(last_updated_unix)
cet_timezone = pytz.timezone('CET')
last_updated_cet = last_updated_utc.replace(tzinfo=pytz.utc).astimezone(cet_timezone)
formatted_date = last_updated_cet.strftime('%Y-%m-%d %H:%M:%S %Z')




print(f"Name: {name}")
print(f"USD Price: ${usd_price}")
print(f"Last Updated (CET): {formatted_date}")


# print(api_result.json())