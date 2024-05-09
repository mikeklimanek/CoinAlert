from dotenv import load_dotenv
import logging
load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from analytics.results_rsi import print_latest_rsi_report
from analytics.indicators_report import print_latest_indicators_report
# from analytics.stocks_rsi import calculate_and_store_rsi_incrementally

# calculate_and_store_rsi_incrementally()

# print_latest_rsi_report()

print_latest_indicators_report()