import requests
import pandas as pd
import os
import dotenv

dotenv.load_dotenv()

NEW_API_KEY = os.getenv('NEW_API_KEY')
BASE_URL = 'https://api.polygon.io'


# placeholder file for now