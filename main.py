from dotenv import load_dotenv
import logging
load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from analytics.results_rsi import print_latest_rsi_report
from analytics.stocks_rsi import update_rsi_for_all_symbols

update_rsi_for_all_symbols()

print_latest_rsi_report()
