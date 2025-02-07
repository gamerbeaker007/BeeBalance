import logging
import re
from datetime import datetime

import streamlit as st

from src.pages.main_subpages import hivesql_balances, spl_balances_estimates, spl_assets, spl_balances, \
    hive_engine_balances
from src.util.card import card_style

log = logging.getLogger("Main Page")

max_number_of_accounts = 5


def get_page():
    # Get the input from the user
    account_names = st.text_input('Enter account names (space separated)', key="account_input")

    valid_pattern = re.compile(r'^[a-zA-Z0-9\- .]+$')
    valid = valid_pattern.match(account_names)

    if not valid and account_names:
        st.warning(f'Invalid input character. Should match [a-zA-Z0-9\\- .]')

    if valid:
        if account_names:
            # Split the input into a list of account names
            account_names = [name.strip() for name in account_names.split(' ') if name.strip()]

            # Check if input has changed, then reset stored data
            if "last_input" not in st.session_state or st.session_state.last_input != account_names:
                st.session_state.last_input = account_names  # Store new input
                st.session_state.hive_data = None  # Reset Hive data
                st.session_state.spl_data = None  # Reset SPL data

            log.info(f'Analyzing account: {account_names}')

            title = ''
            # **Fetch Hive and Hive Engine Data (if not already loaded)**
            st.markdown(card_style, unsafe_allow_html=True)
            if st.session_state.hive_data is None:
                df = hivesql_balances.prepare_data(account_names)

                if not df.empty:
                    # Add date column
                    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    df.insert(0, 'date', current_datetime)

                    df = hive_engine_balances.prepare_data(df)

                    # Store the fetched data
                    st.session_state.hive_data = df
                    st.rerun()
                else:
                    st.write('Enter valid hive account names')
                    return
            else:
                df = st.session_state.hive_data  # Load existing data
                hivesql_balances.get_page(df)
                hive_engine_balances.get_page(df)
                title += 'HIVE + HE'

            if st.session_state.spl_data is None:
                # **Button to Attach SPL Data**
                if st.button("Attach SPL Data"):
                    df = spl_balances.prepare_data(df)
                    df = spl_assets.prepare_data(df)
                    df = spl_balances_estimates.prepare_data(df, max_number_of_accounts)

                    # Store SPL data to prevent reloading
                    st.session_state.spl_data = df
                    st.rerun()
            else:
                df = st.session_state.spl_data
                spl_balances.get_page(df)
                spl_assets.get_page(df)
                spl_balances_estimates.get_page(df, max_number_of_accounts)
                title += " + SPL data"

            with st.expander(f'{title}', expanded=False):
                st.dataframe(df, hide_index=True)

    else:
        st.write('Enter valid hive account names')
