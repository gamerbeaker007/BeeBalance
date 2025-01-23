import streamlit as st

from datetime import datetime

import pandas as pd
from beem import hive, Hive
from beem.market import Market


@st.cache_data(ttl="1h")
def get_hive_balances(account):
    _hive = Hive()
    current_date = datetime.now()
    formatted_date = current_date.strftime('%Y-%m-%d')


    # Calculate curation rewards, HP, and ratio
    curation_rewards = account['curation_rewards'] / 10 # not use
    vesting_shares = account.get_balance('total', 'VESTS').amount
    liquid_hive = account.get_balance('total', 'HIVE').amount
    hbd = account.get_balance('total', 'HBD').amount
    hp = _hive.vests_to_hp(vesting_shares)
    pure_ratio = curation_rewards / hp

    market = Market(hive_instance=_hive)
    price = float(market.ticker()["highest_bid"]['price'])  # HBD per HIVE

    # Calculate equivalent HIVE
    hp_in_hbd = hbd / price
    ratio_with_hbd = curation_rewards / (hp + hp_in_hbd)

    return pd.DataFrame({
        "Date": [formatted_date],
        "Account": [account['name']],
        "HIVE": [liquid_hive],
        "HP": [hp],
        "HBD": [hbd],
        "HBD in HP": [hp_in_hbd],
        "Curation Rewards": [curation_rewards],
        "Ratio": [pure_ratio],
        "Ratio w. HBD": [ratio_with_hbd]
    })
