import logging

import pandas as pd
import streamlit as st

from src.api import spl, peakmonsters
from src.static import icons
from src.util import spl_util
from src.util.card import create_card

log = logging.getLogger('SPL Estimates')


def get_collection_card(df):
    list_value = df.filter(regex='list_value').sum(axis=1, numeric_only=True).sum()
    market_value = df.filter(regex='market_value').sum(axis=1, numeric_only=True).sum()

    return create_card(
        ' Collection',
        f'List: {round(float(list_value), 2)} $ <br>Market:{round(float(market_value), 2)} $',
        icons.cards_icon_url,
    )


def get_total_card(df):
    total_value = df.filter(regex='_value').filter(regex='.*(?<!_list_value)$').sum(axis=1, numeric_only=True).sum()
    return create_card(
        'Total',
        f'{round(float(total_value), 2)} $',
        icons.credits_icon_url,
    )


def get_dec_card(df):
    liquid_value = df.filter(regex='dec_value').sum(axis=1, numeric_only=True).sum()
    staked_value = df.filter(regex='dec_staked_value').sum(axis=1, numeric_only=True).sum()
    return create_card(
        'DEC',
        f'Liquid: {round(float(liquid_value), 2)} $ <br>Staked: {round(float(staked_value), 2)} $',
        icons.dec_icon_url,
    )


def get_sps_card(df):
    liquid_value = df.filter(regex='sps_value').sum(axis=1, numeric_only=True).sum()
    staked_value = df.filter(regex='spsp_value').sum(axis=1, numeric_only=True).sum()
    return create_card(
        'SPS',
        f'Liquid: {round(float(liquid_value), 2)} $ <br>Staked: {round(float(staked_value), 2)} $',
        icons.sps_icon_url,
    )


def get_license_card(df):
    value = df.filter(regex='license_value').sum(axis=1, numeric_only=True).sum()
    return create_card(
        'License',
        f'{round(float(value), 2)} $',
        icons.license_icon_url,
    )


def get_voucher_card(df):
    value = df.filter(regex='voucher_value').sum(axis=1, numeric_only=True).sum()
    return create_card(
        'Voucher',
        f'{round(float(value), 2)} $',
        icons.voucher_icon_url,
    )


def get_credits_card(df):
    value = df.filter(regex='credits_value').sum(axis=1, numeric_only=True).sum()
    return create_card(
        'Credits',
        f'{round(float(value), 2)} $',
        icons.credits_icon_url,
    )


def get_land_card(df):
    # Use df.columns to filter column names
    land_columns = df.columns[
        df.columns.str.startswith("deeds_value") |
        df.columns.str.startswith("plot_value") |
        df.columns.str.startswith("tract_value") |
        df.columns.str.startswith("region_value") |
        (df.columns.str.startswith("totem") & df.columns.str.endswith("_value"))
        ]

    # Sum the filtered columns
    land_value = df[land_columns].sum().sum()  # Sum all rows and columns

    # Create the card
    return create_card(
        'Land + Totem Claims',
        f'{round(float(land_value), 2)} $',
        icons.land_icon_url_svg,
    )


def get_other_values_card(df):
    # Filter for all `_value` columns
    value_columns = df.filter(regex='_value').columns

    # Exclude columns ending with `_list_value` or `_market_value`
    unused_value_columns = value_columns[
        ~value_columns.str.endswith('_list_value') &
        ~value_columns.str.endswith('_market_value') &
        ~value_columns.str.endswith('dec_value') &
        ~value_columns.str.endswith('dec_staked_value') &
        ~value_columns.str.endswith('sps_value') &
        ~value_columns.str.endswith('spsp_value') &
        ~value_columns.str.endswith('license_value') &
        ~value_columns.str.endswith('voucher_value') &
        ~value_columns.str.endswith('credits_value') &
        ~value_columns.str.startswith("deeds_value") &
        ~value_columns.str.startswith("plot_value") &
        ~value_columns.str.startswith("tract_value") &
        ~value_columns.str.startswith("region_value") &
        ~(value_columns.str.startswith("totem") & value_columns.str.endswith("_value"))
        ]

    # Sum the remaining columns across all rows
    unused_value_total = df[unused_value_columns].sum().sum()

    # Create the card
    return create_card(
        'Others',
        f'{round(float(unused_value_total), 2)} $',
        icons.credits_icon_url,  # Replace with an appropriate icon for this card
    )


def add_estimations(row, list_prices_df, market_prices_df):
    """
    Add estimated portfolio value to a player's row based on market data.
    Returns a DataFrame containing the updated row.
    """
    account_name = row['name']

    if not spl.player_exist(account_name):
        log.info(f'Not a Splinterlands account, skipping {account_name}')
        return pd.DataFrame([row])  # Ensure function always returns a DataFrame

    # Fetch portfolio estimates
    estimates = spl_util.get_portfolio_value(account_name, list_prices_df, market_prices_df)

    if estimates.empty:
        return pd.DataFrame([row])

    row = row.copy()  # Ensure modification does not affect cached data

    for col in estimates.columns:
        if col in row.index:
            row[col] += estimates[col].iloc[0]  # Add value if column exists
        else:
            row[col] = estimates[col].iloc[0]  # Add new column if missing

    return pd.DataFrame([row])  # Return as DataFrame for easy concatenation


def prepare_data(df, max_number_of_accounts):
    """
    Process all accounts by adding estimated values based on market prices.
    Uses Streamlit status updates for real-time feedback.
    """
    if df.index.size > max_number_of_accounts:
        return df  # Return unchanged if too many accounts

    empty_space = st.empty()
    with empty_space.container():
        with st.status('Loading SPL Estimates...', expanded=True) as status:
            # Store the current column order
            initial_columns = df.columns.tolist()

            # Fetch market data **before** iterating over accounts
            status.update(label="Fetching market data...", state="running")
            list_prices_df = spl.get_all_cards_for_sale_df()
            market_prices_df = peakmonsters.get_market_prices_df()
            status.update(label="Market data loaded!", state="complete")

            processed_rows = []  # Store processed data

            # Iterate over each row while updating progress
            for index, row in df.iterrows():
                status.update(label=f"Processing estimations for: {row['name']}...", state="running")

                updated_row = add_estimations(row, list_prices_df, market_prices_df)  # Process row
                processed_rows.append(updated_row)

                status.update(label=f"Completed {row['name']}", state="complete")

            # Combine processed rows into a DataFrame
            result_df = pd.concat(processed_rows, ignore_index=True) if processed_rows else pd.DataFrame(columns=df.columns)

            # Reorder columns: original columns first, then new ones
            new_columns = [col for col in result_df.columns if col not in initial_columns]
            result_df = result_df[initial_columns + new_columns]

            status.update(label="All estimations completed!", state="complete")
    empty_space.empty()

    return result_df


def get_page(df, max_number_of_accounts):
    st.title('Splinterlands \'Estimated\' Value ($)')

    if df.index.size <= max_number_of_accounts:
        total_card = get_total_card(df)
        collection_card = get_collection_card(df)
        dec_card = get_dec_card(df)
        sps_card = get_sps_card(df)
        land_card = get_land_card(df)
        others_card = get_other_values_card(df)
        license_card = get_license_card(df)
        voucher_card = get_voucher_card(df)
        credits_card = get_credits_card(df)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(total_card, unsafe_allow_html=True)
            st.markdown(land_card, unsafe_allow_html=True)
            st.markdown(others_card, unsafe_allow_html=True)
        with col2:
            st.markdown(collection_card, unsafe_allow_html=True)
            st.markdown(license_card, unsafe_allow_html=True)
        with col3:
            st.markdown(dec_card, unsafe_allow_html=True)
            st.markdown(voucher_card, unsafe_allow_html=True)
        with col4:
            st.markdown(sps_card, unsafe_allow_html=True)
            st.markdown(credits_card, unsafe_allow_html=True)
    else:
        st.write(f'Skipped SPL estimate more then {max_number_of_accounts} accounts requested')
