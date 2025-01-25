import streamlit as st

from src.pages import spl_balances, hivesql_balances
from src.util.card import card_style


def get_page():
    # Get the input from the user
    account_names = st.text_input('Enter account names (comma-separated)')

    # Split the input into a list of account names
    account_names = [name.strip() for name in account_names.split(",") if name.strip()]
    if account_names:
        st.markdown(card_style, unsafe_allow_html=True)
        hivesql_balances.get_page(account_names)
        if len(account_names) == 1:
            spl_balances.get_page(account_names[0])

        # TODO combined data table with columns
        #     HP
        #     Rank
        #     Account
        #     Creation Date
        #     Hive Power(HP)
        #     Curation Rewards(HP)
        #     Author Rewards(HP)
        #     Total Rewards(HP)
        #     Author + Curation
        #     HP(Author + Curation) / HP
        #     SPSP Balance
        #     CP
        #     DEC + DEC - B
        #     Validator Nodes
        #     Plots
    else:
        st.write('Enter valid hive account name')
