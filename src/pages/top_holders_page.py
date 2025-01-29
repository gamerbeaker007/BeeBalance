import logging
from datetime import datetime

import pandas as pd
import streamlit as st

from src.api import hive_sql, spl
from src.graphs import graphs
from src.pages.main_subpages import hivesql_balances, spl_balances

log = logging.getLogger('Top Holders')


def analyse_accounts(accounts):
    df = hivesql_balances.prepare_data(accounts)

    # Add date column
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df.insert(0, 'date', current_datetime)

    df = spl_balances.prepare_date(df)
    # df = spl_assets.prepare_data(df)

    return df


def create_page(account_list):
    result = analyse_accounts(account_list)

    # Display results if available
    if not result.empty:
        graphs.add_ke_ratio_graph(result)
        graphs.add_spsp_vs_hp_graph(result)
        st.dataframe(result, hide_index=True)


def get_page():
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 4])
    result = pd.DataFrame()

    # Create a container for execution results
    results_container = st.container()

    account_limit = 100
    posting_reward = 500
    comments = 10
    months = 6
    with col1:
        if st.button(f'TOP {account_limit} HP holders with author rewards >{posting_reward}'):
            # Store parameters for use in the results container
            st.session_state.button_clicked = 'top authors'
    with col2:
        if st.button(f'TOP 100 Staked SPS Holders'):
            # Store parameters for use in the results container
            st.session_state.button_clicked = 'top spsp'
    with col3:
        if st.session_state.authenticated:
            if st.button('Top active authors'):
                # Store parameters for use in the results container
                st.session_state.button_clicked = 'top active authors'
    with col4:
        if st.session_state.authenticated:
            if st.button(f'TOP 200 Staked SPS Holders'):
                # Store parameters for use in the results container
                st.session_state.button_clicked = 'top 200 spsp'

    # Handle execution based on which button was clicked
    with results_container:
        button_clicked = st.session_state.get('button_clicked')
        if button_clicked:
            log.info(f'Analysing top holders: {button_clicked}')

        if button_clicked == 'top active authors':
            if st.session_state.authenticated:
                active_authors = hive_sql.get_active_hivers(posting_reward, comments, months)
                st.write(f'account found: {active_authors.index.size}, '
                         f'with params '
                         f'total posting_reward >{posting_reward}, '
                         f'comments >{comments}, months -{months}')
                st.dataframe(active_authors, hide_index=True)

                st.warning('TODO scaled down to 10 for now')
                account_list = active_authors.head(10).name.to_list()
                create_page(account_list)

        elif button_clicked == 'top authors':
            top_authors = hive_sql.get_top_posting_rewards(account_limit, posting_reward)
            account_list = top_authors.name.to_list()
            create_page(account_list)

        elif button_clicked == 'top spsp':
            rich_list = spl.get_spsp_richlist()
            rich_list = rich_list.sort_values(by="balance", ascending=False)
            account_list = rich_list.player.head(100).to_list()
            create_page(account_list)

        elif button_clicked == 'top 200 spsp':
            rich_list = spl.get_spsp_richlist()
            rich_list = rich_list.sort_values(by="balance", ascending=False)
            account_list = rich_list.player.to_list()
            create_page(account_list)
