import streamlit as st

from src.pages.main_subpages import spl_balances, hivesql_balances, spl_balances_extra, spl_assets
from src.util.card import card_style


def get_page():
    # Get the input from the user
    account_names = st.text_input('Enter account names (space separated)')

    # Split the input into a list of account names
    account_names = [name.strip() for name in account_names.split(" ") if name.strip()]
    if account_names:
        st.markdown(card_style, unsafe_allow_html=True)
        df = hivesql_balances.get_page(account_names)
        df = spl_balances.get_page(df)
        df = spl_assets.get_page(df)
        if len(account_names) == 1:
            spl_balances_extra.get_page(account_names[0])

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
