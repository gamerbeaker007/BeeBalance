import logging
import re
from datetime import datetime

import streamlit as st

from src.pages.main_subpages import hivesql_balances, spl_balances_estimates, spl_assets, spl_balances, \
    hive_engine_balances
from src.util.card import card_style

log = logging.getLogger("Main Page")


def get_page():
    # Get the input from the user
    account_names = st.text_input('Enter account names (space separated)', key="account_input")

    valid_pattern = re.compile(r'^[a-zA-Z0-9\- .]+$')
    valid = valid_pattern.match(account_names)

    if not valid and account_names:
        st.warning(f'Invalid input character. Should match [a-zA-Z0-9\\- .]')

    if valid:
        # Create an empty container to hold the results
        result_container = st.empty()

        if account_names:
            # Split the input into a list of account names
            account_names = [name.strip() for name in account_names.split(' ') if name.strip()]

            # **Check if input has changed, then clear the container**
            if "last_input" not in st.session_state or st.session_state.last_input != account_names:
                result_container.empty()  # **Clears the previous output**
                st.session_state.last_input = account_names  # **Store new input**

            log.info(f'Analysing account: {account_names}')

            with result_container.container():
                st.markdown(card_style, unsafe_allow_html=True)
                df = hivesql_balances.prepare_data(account_names)
                hivesql_balances.get_page(df)

                if not df.empty:
                    # Add date column
                    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    df.insert(0, 'date', current_datetime)

                    df = hive_engine_balances.prepare_date(df)
                    hive_engine_balances.get_page(df)

                    df = spl_balances.prepare_date(df)
                    spl_balances.get_page(df)

                    df = spl_assets.prepare_data(df)
                    spl_assets.get_page(df)

                    with st.expander("Hive + HE + SPL data", expanded=False):
                        st.dataframe(df, hide_index=True)

                    max_number_of_accounts = 5
                    df = spl_balances_estimates.prepare_data(df, max_number_of_accounts)
                    spl_balances_estimates.get_page(df, max_number_of_accounts)
                else:
                    st.write('Enter valid hive account names')
    else:
        st.write('Enter valid hive account names')
