import logging
from typing import Dict, Any, Optional, List

import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter

from src.api.logRetry import LogRetry

# API URLs
SPS_VALIDATOR_URL = 'https://validator.hive-engine.com/'

# Configure Logging
log = logging.getLogger("SPS Validator api")
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
        "accept": "application/json",
        "User-Agent": "BeeBalanced/1.0"
    })
    return session


http = configure_http_session()


def get_rich_list_spsp(number_of_accounts) -> pd.DataFrame:
    """
    Get the top SPSP holders
    :param number_of_accounts: top x of spsp holders
    :return: DataFrame with requested data or empty DataFrame on failure.
    """
    # https://validator.hive-engine.com/tokens/SPSP?limit=2000&systemAccounts=false'
    address = SPS_VALIDATOR_URL + '/tokens/SPSP'
    params = {
        'limit': number_of_accounts,
        'systemAccounts': False,
    }
    try:
        response = http.get(address, params=params, timeout=10)
        response.raise_for_status()

        response_json = response.json()

        # Handle API errors
        if isinstance(response_json, dict) and "error" in response_json:
            log.error(f"API error from {address}: {response_json['error']}")
            return pd.DataFrame()

        return pd.DataFrame(response_json['balances'])

    except requests.exceptions.RequestException as e:
        log.error(f"Error fetching {address}: {e}")
        return pd.DataFrame()
