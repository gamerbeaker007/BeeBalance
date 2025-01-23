import streamlit as st

from src.pages import hive_balances, spl_balances


def get_page():
    account_name = st.text_input('account name')
    if account_name:
        hive_balances.get_page(account_name)
        spl_balances.get_page(account_name)
    else:
        st.write('Enter valid hive account name')
