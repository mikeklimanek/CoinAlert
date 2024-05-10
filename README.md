# CoinAlert
Version 1 calls API through pipeline, fetches data to DB and alerts with an email notification on changes over 4-5% in 4hour cycles with top10 crypto coins.

## Version 2 under development
API data source migration and DB injection with historical data. Working on new pipelines and live pipelines calculating indicators for stocks and crypto. Preparation for data visualization with Jupyter Notebook.

## Overview
This Crypto Price Alert System is designed to monitor cryptocurrency prices, updating every 4 hours via an API pipeline that interacts with a live database. The system cleans and processes the incoming data, calculates changes between each update, and sends email notifications for any price changes in cryptocurrencies that exceed a 5% threshold, either positive or negative.

## Installation

### Prerequisites
- Python 3.x
- pip (Python package installer)

### Dependencies
To install the required Python libraries, run the following command:

```bash
pip install requests==2.31.0 python-dotenv==1.0.1 pytz==2024.1 libsql-experimental==0.0.34 sendgrid==6.11.0 pandas==2.2.2
```


Make sure to adjust paths and other placeholders (`YOUR_SENDGRID_API_KEY`, `YOUR_DATABASE_CONNECTION_STRING`, `path/to/your_script.py`) to match your actual project setup.
