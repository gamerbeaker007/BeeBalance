import  streamlit as st
from src.api.logRetry import LogRetry
import pandas as pd
import requests
from requests.adapters import HTTPAdapter

retry_strategy = LogRetry(
    total=10,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=2,  # wait will be [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)

api_url = 'https://hivebuzz.me/api/stats/'


@st.cache_data(ttl="1h")
def get_stats(account_name):
    address = api_url + account_name

    result = http.get(address).json()
    if result:
        return pd.DataFrame([result])
    return None
