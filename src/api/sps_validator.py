import logging

import pandas as pd
import requests
from requests.adapters import HTTPAdapter

from src.api.logRetry import LogRetry

# API URLs
SPS_VALIDATOR_URL = 'https://validator.hive-engine.com/'

# API Configurations
DEFAULT_TIMEOUT = 10  # Configurable timeout for API requests

# Configure Logging
log = logging.getLogger("SPS Validator API")
log.setLevel(logging.INFO)


# Retry Strategy
def configure_http_session() -> requests.Session:
    retry_strategy = LogRetry(
        total=11,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=2,
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        logger_name="SPL Retry"
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.headers.update({
        "Accept": "application/json",
        "User-Agent": "BeeBalanced/1.0"
    })
    return session


http = configure_http_session()


def get_rich_list_spsp(number_of_accounts: int) -> pd.DataFrame:
    """
    Get the top SPSP holders.

    :param number_of_accounts: Number of top SPSP holders to fetch.
    :return: DataFrame containing SPSP balances, or empty DataFrame on failure.
    """
    address = f"{SPS_VALIDATOR_URL}/tokens/SPSP"
    params = {
        'limit': number_of_accounts,
        'systemAccounts': False,
    }

    try:
        response = http.get(address, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()

        response_json = response.json()

        # Validate API response structure
        if not isinstance(response_json, dict) or 'balances' not in response_json:
            log.error(f"Unexpected API response from {address}: {response_json}")
            return pd.DataFrame()

        return pd.DataFrame(response_json['balances'])

    except requests.exceptions.RequestException as e:
        log.error(f"Error fetching {address} (Status Code: {getattr(e.response, 'status_code', 'N/A')}): {e}")
        return pd.DataFrame()
