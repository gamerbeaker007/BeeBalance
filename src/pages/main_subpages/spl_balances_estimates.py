import logging

import streamlit as st

from src.api import spl, peakmonsters
from src.util import spl_util

log = logging.getLogger('SPL Estimates')


def add_estimations(row, list_prices_df, market_prices_df, placeholder):
    account_name = row['name']
    if not spl.player_exist(account_name):
        logging.info(f'Not a splinterlands account skip {account_name}')
        return row

    estimates = spl_util.get_portfolio_value(account_name, list_prices_df, market_prices_df, placeholder)
    if estimates.empty:
        return row

    for col in estimates.columns:
        if col in row.index:
            # Add the value if the column exists in the row
            row[col] += estimates[col].iloc[0]
        else:
            # Add the column to the row if it doesn't exist
            row[col] = estimates[col].iloc[0]
    return row


def get_page(df, max_number_of_account):
    st.title('Splinterlands \'Estimated\' Value ($)')

    if df.index.size <= max_number_of_account:
        loading_placeholder = st.empty()

        with st.spinner('Loading data... Please wait.'):
            list_prices_df = spl.get_all_cards_for_sale_df()
            market_prices_df = peakmonsters.get_market_prices_df()

            spl_estimates = df.apply(lambda row:
                                     add_estimations(row,
                                                     list_prices_df,
                                                     market_prices_df,
                                                     loading_placeholder), axis=1)

        loading_placeholder.empty()
        st.dataframe(df, hide_index=True)
        return spl_estimates
    else:
        st.write(f'Skip SPL estimate more then {max_number_of_account} accounts requested')
        return df
