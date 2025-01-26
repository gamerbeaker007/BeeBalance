import logging
from datetime import datetime

import streamlit as st

from src.pages.main_subpages import hivesql_balances, spl_balances_estimates, spl_assets, spl_balances
from src.util.card import card_style

log = logging.getLogger("Main Page")


def get_page():
    # Get the input from the user
    account_names = st.text_input('Enter account names (space separated)')
    log.info(f'Analysing account: {account_names}')

    # Split the input into a list of account names
    account_names = [name.strip() for name in account_names.split(' ') if name.strip()]
    if account_names:
        st.markdown(card_style, unsafe_allow_html=True)
        df = hivesql_balances.get_page(account_names)

        # Add date column
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df.insert(0, 'date', current_datetime)

        df = spl_balances.get_page(df)
        df = spl_assets.get_page(df)

        df = spl_balances_estimates.get_page(df, 5)
    else:
        st.write('Enter valid hive account name')
