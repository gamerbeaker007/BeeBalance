import logging

import pandas as pd
import requests
from requests.adapters import HTTPAdapter

from src.api.logRetry import LogRetry

# Configure retry strategy
retry_strategy = LogRetry(
    total=10,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=2,  # wait will be [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    allowed_methods=["HEAD", "GET", "OPTIONS"],
    logger_name="Peakmonster Retry"
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)

peak_monsters_url = "https://peakmonsters.com/api/market/cards/prices"

log = logging.getLogger("Peakmonsters API")

def get_market_prices_df():
    try:
        response = http.get(peak_monsters_url)
        result = response.json()  # Validate JSON response

        if isinstance(result, dict) and 'prices' in result:
            return pd.DataFrame(result["prices"])

    except (ValueError, requests.exceptions.RequestException) as e:
        log.error(f"Error fetching market prices: {e}")

    return pd.DataFrame()  # Return empty DataFrame on failure