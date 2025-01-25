import streamlit as st

from src.api import spl
from src.util import spl_util


def get_page(account_name):
    st.title('Splinterlands "Estimated" Balances ALL')
    if spl.player_exist(account_name):
        spl_balances = spl_util.get_portfolio_value(account_name)
        st.dataframe(spl_balances, hide_index=True)
    else:
        st.warning('Invalid account name try again')
