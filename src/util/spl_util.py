from src.api import spl, peakmonsters
from src.util import collection_util, token_util, land_util
import streamlit as st


def get_portfolio_value(account_name):
    loading_placeholder = st.empty()

    with st.spinner("Loading data... Please wait."):

        list_prices_df = spl.get_all_cards_for_sale_df()
        market_prices_df = peakmonsters.get_market_prices_df()

        loading_placeholder.text(f"Determining card values")
        df1 = collection_util.get_card_edition_value(account_name, list_prices_df, market_prices_df)

        loading_placeholder.text(f"Determining token values")
        df2 = token_util.get_token_value(account_name)
        total_df = df1.merge(df2)

        loading_placeholder.text(f"Determining deeds value")
        df3 = land_util.get_deeds_value(account_name)
        total_df = total_df.merge(df3)

        loading_placeholder.text(f"Determining DEC values")
        df4 = land_util.get_staked_dec_value(account_name)
        total_df = total_df.merge(df4)

        loading_placeholder.text(f"Determining Land resource values")
        df5 = land_util.get_resources_value(account_name)
        total_df = total_df.merge(df5)

    loading_placeholder.empty()

    return total_df
