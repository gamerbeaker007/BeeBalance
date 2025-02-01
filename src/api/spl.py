import logging

import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter

from src.api.logRetry import LogRetry

base_url = 'https://api2.splinterlands.com/'
land_url = 'https://vapi.splinterlands.com/'
prices_url = 'https://prices.splinterlands.com/'

retry_strategy = LogRetry(
    total=11,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=2,  # wait will be [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    allowed_methods=['HEAD', 'GET', 'OPTIONS'],
    logger_name = "SPL Retry"
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount('https://', adapter)

http.headers.update({
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "User-Agent": "BeeBalanced/1.0"
})

log = logging.getLogger("SPL API")


@st.cache_data(ttl="1h")
def get_player_collection_df(username):
    """
    Fetch player card collection and add card names.
    """
    df = fetch_api_data(f'{base_url}cards/collection/{username}', data_key='cards')

    if not df.empty:
        return df[
            ['player', 'uid', 'card_detail_id', 'collection_power', 'xp', 'gold', 'edition', 'level', 'bcx', 'bcx_unbound']]

    return df  # Returns empty DataFrame if no data


@st.cache_data(ttl="24h")
def get_card_details():
    """
    Fetch all card details and store them with an index.
    """
    log.info("FETCHING CARD DETAIL")
    df = fetch_api_data(f'{base_url}cards/get_details')
    return df.set_index('id') if not df.empty else df


@st.cache_data(ttl="24h")
def get_settings():
    """
    Fetch Splinterlands game settings.
    """
    return fetch_api_data(f'{base_url}settings')


@st.cache_data(ttl="1h")
def get_balances(username, filter_tokens=None):
    """
    Fetch player balances. Optionally filter for specific tokens.
    """
    df = fetch_api_data(f'{base_url}players/balances', params={'username': username})

    if filter_tokens and not df.empty:
        df = df[df["token"].isin(filter_tokens)]

        # Identify missing tokens
        existing_tokens = df["token"].unique()
        missing_tokens = [token for token in filter_tokens if token not in existing_tokens]

        # Create rows for missing tokens with default values
        missing_rows = pd.DataFrame({
            "player": [username] * len(missing_tokens),
            "token": missing_tokens,
            "balance": [0] * len(missing_tokens),
        })

        # Combine the existing and missing rows
        df = pd.concat([df, missing_rows], ignore_index=True)
        df = df[['player', 'token', 'balance']]

    return df


@st.cache_data(ttl="1h")
def get_prices():
    """
    Fetch current prices for assets.

    TODO use fetch_api_data different response structure
    """
    address = prices_url + 'prices'
    return http.get(address).json()


@st.cache_data(ttl="1h")
def get_all_cards_for_sale_df():
    """
    Fetch all cards currently for sale on the Splinterlands market.
    Returns a DataFrame sorted by card_detail_id.
    """
    df = fetch_api_data(f'{base_url}market/for_sale_grouped')

    # Sort by 'card_detail_id' if the DataFrame is not empty
    return df.sort_values(by='card_detail_id') if not df.empty else df


@st.cache_data(ttl="1h")
def get_staked_dec_df(account_name):
    """
    Fetch staked DEC for land.
    """
    return fetch_api_data(f'{land_url}land/stake/decstaked', params= {'player': account_name}, data_key='data')


@st.cache_data(ttl="1h")
def get_deeds_collection(username):
    """
    Fetch land deeds from a player.
    """
    params = {
        'status': 'collection',
        'player': username,
    }
    return fetch_api_data(f'{land_url}land/deeds', params=params, data_key='data.deeds')


@st.cache_data(ttl="1h")
def get_deeds_market():
    """
    Fetch land deeds currently on the market.
    """
    return fetch_api_data(f'{land_url}land/deeds', params={'status': 'market'}, data_key='data.deeds')


@st.cache_data(ttl="1h")
def spl_get_pools():
    """
    Fetch liquidity pools data.
    """
    return fetch_api_data(f'{land_url}land/liquidity/pools', data_key='data')


@st.cache_data(ttl="1h")
def get_owned_resource_sum(account, resource):
    """
    Fetch the total owned amount of a specific resource for a player.
    Returns the sum of the "amount" column.
    """
    df = fetch_api_data(f'{land_url}land/resources/owned', params={'player': account, 'resource': resource}, data_key='data')
    return df['amount'].sum() if 'amount' in df.columns else 0  # Return 0 instead of None if missing


@st.cache_data(ttl="1h")
def player_exist(account_name):
    """
    Check if a player exists in the Splinterlands API.
    Returns True if player balances exist, False otherwise.
    """
    player_data = fetch_api_data(f'{base_url}players/balances', params={'players': account_name})

    # If the DataFrame is not empty, the player exists
    return not player_data.empty


@st.cache_data(ttl="1h")
def get_player_details(account_name):
    """
    Fetch player details from the API.
    """
    return fetch_api_data(f'{base_url}players/details', params={'name': account_name})


@st.cache_data(ttl="1h")
def get_spsp_richlist():
    """
    Fetch the SPSP rich list from the API.
    """
    return fetch_api_data(f'{base_url}players/richlist', params={'token_type': 'SPSP'}, data_key='richlist')


def get_nested_value(dictionary, key_path, default=None):
    """
    Retrieve a nested value from a dictionary using dot-separated keys.

    :param dictionary: The dictionary to search
    :param key_path: A dot-separated string indicating the key path (e.g., "data.deeds")
    :param default: The default value to return if the key path doesn't exist
    :return: The value at the specified key path or the default value
    """
    keys = key_path.split(".")
    for key in keys:
        if isinstance(dictionary, dict) and key in dictionary:
            dictionary = dictionary[key]
        else:
            return default  # Return default if any key is missing
    return dictionary


def fetch_api_data(address, params=None, data_key=None):
    """
    Generic function to fetch data from the Splinterlands API.

    :param endpoint: API endpoint (relative to base_url)
    :param params: Query parameters for the request
    :param data_key: Key to extract data from JSON response (optional)
    :return: DataFrame with requested data or empty DataFrame on failure
    """
    try:
        response = http.get(address, params=params)
        response.raise_for_status()

        # Parse JSON response
        response_json = response.json()

        # Check if an error exists in the response
        if isinstance(response_json, dict) and "error" in response_json:
            log.error(f"API responded with an error: {response_json['error']}")
            return pd.DataFrame()

        # If a specific data key is provided, extract that key's value
        if data_key and isinstance(response_json, dict):
            response_json = get_nested_value(response_json, data_key, [])

        return pd.DataFrame(response_json)  # Default return

    except requests.exceptions.RequestException as e:
        log.error(f"Error fetching data from {address}: {e}")
        return pd.DataFrame()
