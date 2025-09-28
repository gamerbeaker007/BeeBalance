import logging
import streamlit as st

from src.api.hafsql import fetch_balance_history
from src.graphs import balance_history_graph

log = logging.getLogger("Balance History")


def get_page():
    account_input = st.text_input("Enter account name (space separated):")
    if account_input:
        account_list = account_input.split()
        with st.spinner("Fetching balance history..."):
            result_df = fetch_balance_history(account_list)
        if not result_df.empty:
            balance_history_graph.add(result_df)

            with st.expander("Data", expanded=False):
                st.dataframe(result_df, hide_index=True)

        else:
            st.warning("No data found for the given accounts.")
