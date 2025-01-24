import streamlit as st

from src.pages import hive_balances, spl_balances, hive_balances
from src.util.card import card_style


def get_page():
    account_name = st.text_input('account name')
    if account_name:
        st.markdown(card_style, unsafe_allow_html=True)
        hive_balances.get_page(account_name)
        spl_balances.get_page(account_name)

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
