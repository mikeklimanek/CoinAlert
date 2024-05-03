# CoinAlert
# Crypto Price Alert System

## Overview
This project is designed to monitor cryptocurrency prices, updating every 4 hours via an API pipeline that interacts with a live database. The system cleans and processes the incoming data, calculates changes between each update, and sends email notifications for any price changes in cryptocurrencies that exceed a 5% threshold, either positive or negative.

## Installation

### Prerequisites
- Python 3.x
- pip (Python package installer)

### Dependencies
To install the required Python libraries, run the following command:

```bash
pip install requests==2.31.0 python-dotenv==1.0.1 pytz==2024.1 libsql-experimental==0.0.34
```


Make sure to adjust paths and other placeholders (`YOUR_SENDGRID_API_KEY`, `YOUR_DATABASE_CONNECTION_STRING`, `path/to/your_script.py`) to match your actual project setup.