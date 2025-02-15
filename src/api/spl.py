import logging
from typing import Dict, Any, Optional, List

import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter

from src.api.logRetry import LogRetry

# API URLs
API_URLS = {
    "base": "https://api2.splinterlands.com/",
    "land": "https://vapi.splinterlands.com/",
    "prices": "https://prices.splinterlands.com/",
}

# Configure Logging
log = logging.getLogger("SPL API")
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
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "User-Agent": "BeeBalanced/1.0"
    })
    return session


http = configure_http_session()


def fetch_api_data(address: str, params: Optional[Dict[str, Any]] = None,
                   data_key: Optional[str] = None) -> pd.DataFrame:
    """
    Generic function to fetch data from the Splinterlands API.

    :param address: API endpoint URL.
    :param params: Query parameters for the request.
    :param data_key: Key to extract data from JSON response (optional).
    :return: DataFrame with requested data or empty DataFrame on failure.
    """
    try:
        response = http.get(address, params=params, timeout=10)
        response.raise_for_status()

        response_json = response.json()

        # Handle API errors
        if isinstance(response_json, dict) and "error" in response_json:
            log.error(f"API error from {address}: {response_json['error']}")
            return pd.DataFrame()

        if data_key and isinstance(response_json, dict):
            response_json = get_nested_value(response_json, data_key)

        if isinstance(response_json, list):
            return pd.DataFrame(response_json)
        else:
            return pd.DataFrame(response_json, index=[0])

    except requests.exceptions.RequestException as e:
        log.error(f"Error fetching {address}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl="1h")
def get_player_collection_df(username: str) -> pd.DataFrame:
    """
    Fetch player card collection and return filtered DataFrame.
    """
    df = fetch_api_data(f"{API_URLS['base']}cards/collection/{username}", data_key="cards")
    return df[["player", "uid", "card_detail_id", "collection_power", "xp", "gold", "edition", "level", "bcx",
               "bcx_unbound"]] if not df.empty else df


@st.cache_data(ttl="24h")
def get_card_details() -> pd.DataFrame:
    """
    Fetch and index all card details.
    """
    log.info("Fetching card details...")
    df = fetch_api_data(f"{API_URLS['base']}cards/get_details")
    return df.set_index("id") if not df.empty else df


@st.cache_data(ttl="1h")
def get_balances(username: str, filter_tokens: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Fetch player balances and optionally filter by tokens.
    """
    df = fetch_api_data(f"{API_URLS['base']}players/balances", params={"username": username})

    if filter_tokens and not df.empty:
        df = df[df["token"].isin(filter_tokens)]
        missing_tokens = [token for token in filter_tokens if token not in df["token"].unique()]
        missing_rows = pd.DataFrame(
            {"player": [username] * len(missing_tokens), "token": missing_tokens, "balance": [0] * len(missing_tokens)})
        df = pd.concat([df, missing_rows], ignore_index=True)
        df = df[["player", "token", "balance"]]

    return df


@st.cache_data(ttl="1h")
def get_prices() -> Dict:
    """
    Fetch current asset prices.
    """
    return http.get(f"{API_URLS['prices']}prices").json()


@st.cache_data(ttl="1h")
def get_all_cards_for_sale_df() -> pd.DataFrame:
    """
    Fetch all cards currently for sale.
    """
    df = fetch_api_data(f"{API_URLS['base']}market/for_sale_grouped")
    return df.sort_values(by="card_detail_id") if not df.empty else df


@st.cache_data(ttl="1h")
def get_staked_dec_df(account_name: str) -> pd.DataFrame:
    """
    Fetch staked DEC for land.
    """
    return fetch_api_data(f"{API_URLS['land']}land/stake/decstaked", params={"player": account_name}, data_key="data")


@st.cache_data(ttl="1h")
def get_deeds_collection(username):
    """
    Fetch land deeds from a player.
    """
    params = {
        'status': 'collection',
        'player': username,
    }
    return fetch_api_data(f'{API_URLS['land']}land/deeds', params=params, data_key='data.deeds')


@st.cache_data(ttl="1h")
def get_deeds_market():
    """
    Fetch land deeds currently on the market.
    """
    return fetch_api_data(f'{API_URLS['land']}land/deeds', params={'status': 'market'}, data_key='data.deeds')


@st.cache_data(ttl="1h")
def spl_get_pools():
    """
    Fetch liquidity pools data.
    """
    return fetch_api_data(f'{API_URLS['land']}land/liquidity/pools', data_key='data')


@st.cache_data(ttl="1h")
def get_owned_resource_sum(account, resource):
    """
    Fetch the total owned amount of a specific resource for a player.
    Returns the sum of the "amount" column.
    """
    df = fetch_api_data(f'{API_URLS['land']}land/resources/owned', params={'player': account, 'resource': resource},
                        data_key='data')
    return df['amount'].sum() if 'amount' in df.columns else 0  # Return 0 instead of None if missing


@st.cache_data(ttl="1h")
def player_exist(account_name: str) -> bool:
    """
    Check if a player exists in the Splinterlands API.
    """
    player_data = fetch_api_data(f"{API_URLS['base']}players/balances", params={"players": account_name})
    return not player_data.empty


@st.cache_data(ttl="1h")
def get_player_details(account_name: str) -> pd.DataFrame:
    """
    Fetch player details.
    """
    return fetch_api_data(f"{API_URLS['base']}players/details", params={"name": account_name})


@st.cache_data(ttl="1h")
def get_spsp_richlist() -> pd.DataFrame:
    """
    Fetch the SPSP rich list.
    """
    return fetch_api_data(f"{API_URLS['base']}players/richlist", params={"token_type": "SPSP"}, data_key="richlist")


def get_nested_value(response_dict: dict, key_path: str) -> Any:
    """
    Retrieve a nested value from a dictionary using dot-separated keys.
    """
    keys = key_path.split(".")
    for key in keys:
        if isinstance(response_dict, dict) and key in response_dict:
            response_dict = response_dict[key]
        else:
            log.error(f"Invalid key requested {key_path}.. Fix api call or check response changed {response_dict}")
            return {}  # Return empty if any key is missing
    return response_dict
