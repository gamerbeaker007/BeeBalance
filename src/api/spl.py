import pandas as pd
import requests
from requests.adapters import HTTPAdapter
import streamlit as st

from src.api.logRetry import LogRetry

base_url = 'https://api2.splinterlands.com/'
land_url = 'https://vapi.splinterlands.com/'
prices_url = 'https://prices.splinterlands.com/'

retry_strategy = LogRetry(
    total=10,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=2,  # wait will be [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    allowed_methods=['HEAD', 'GET', 'OPTIONS']
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount('https://', adapter)


@st.cache_data(ttl="1h")
def get_player_collection_df(username):
    address = base_url + 'cards/collection/' + username
    collection = http.get(address).json()['cards']
    df = pd.DataFrame(sorted(collection, key=lambda card: card['card_detail_id']))
    details = get_card_details()
    df.loc[:, 'card_name'] = df.apply(lambda row: details.loc[row['card_detail_id']]['name'], axis=1)
    return df[['player', 'uid', 'card_detail_id', 'card_name', 'xp', 'gold', 'edition', 'level', 'bcx', 'bcx_unbound']]


@st.cache_data(ttl="24h")
def get_card_details():
    address = base_url + 'cards/get_details'
    return pd.DataFrame(http.get(address).json()).set_index('id')


@st.cache_data(ttl="24h")
def get_settings():
    address = base_url + 'settings'
    return http.get(address).json()


@st.cache_data(ttl="1h")
def get_balances(username):
    address = base_url + 'players/balances'
    params = {'username': username}
    return http.get(address, params=params).json()


@st.cache_data(ttl="1h")
def get_prices():
    address = prices_url + 'prices'
    return http.get(address).json()

@st.cache_data(ttl="1h")
def get_all_cards_for_sale_df():
    address = base_url + 'market/for_sale_grouped'
    all_cards_for_sale = requests.get(address).json()
    return pd.DataFrame(sorted(all_cards_for_sale, key=lambda card: card['card_detail_id']))


@st.cache_data(ttl="1h")
def get_staked_dec_df(account_name):
    address = land_url + 'land/stake/decstaked'
    params = {'player': account_name}
    return pd.DataFrame(http.get(address, params=params).json()['data'])


@st.cache_data(ttl="1h")
def get_deeds_collection(username):
    address = land_url + 'land/deeds'
    params = {
        'status': 'collection',
        'player': username,
    }
    collection = http.get(address, params=params)
    return collection.json()['data']['deeds']


@st.cache_data(ttl="1h")
def get_deeds_market():
    address = land_url + 'land/deeds'
    params = {'status': 'market'}
    market = http.get(address, params=params)
    return market.json()['data']['deeds']


@st.cache_data(ttl="1h")
def spl_get_pools():
    address = land_url + 'land/liquidity/pools'

    result = http.get(address).json()
    if result and 'data' in result:
        return pd.DataFrame(result['data'])
    return pd.DataFrame()


@st.cache_data(ttl="1h")
def get_liquidity(account, resource):
    address = land_url + 'land/liquidity/pools/' + str(account) + '/' + resource

    result = http.get(address).json()
    if result and 'data' in result:
        return pd.DataFrame(result['data'])
    return pd.DataFrame()


@st.cache_data(ttl="1h")
def get_owned_resource_sum(account, resource):
    address = land_url + 'land/resources/owned'
    params = {'player': account, 'resource': resource}

    result = http.get(address, params=params).json()
    if result and 'data' in result:
        df = pd.DataFrame(result['data'])
        if 'amount' in df.columns.tolist():
            return df.amount.sum()
    return None


@st.cache_data(ttl="1h")
def player_exist(account_name):
    address = base_url + 'players/details'
    params = {'name': account_name}
    result = http.get(address, params=params)
    if result.status_code == 200 and 'error' not in result.json():
        return True
    else:
        return False
