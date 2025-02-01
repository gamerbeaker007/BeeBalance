import logging

import streamlit as st

from src.api import spl, peakmonsters
from src.static import icons
from src.util import spl_util
from src.util.card import create_card

log = logging.getLogger('SPL Estimates')


def add_estimations(row, list_prices_df, market_prices_df, placeholder):
    account_name = row['name']
    if not spl.player_exist(account_name):
        log.info(f'Not a splinterlands account skip {account_name}')
        return row

    estimates = spl_util.get_portfolio_value(account_name, list_prices_df, market_prices_df, placeholder)
    if estimates.empty:
        return row

    row = row.copy()
    for col in estimates.columns:
        if col in row.index:
            # Add the value if the column exists in the row
            row[col] += estimates[col].iloc[0]
        else:
            # Add the column to the row if it doesn't exist
            row[col] = estimates[col].iloc[0]
    return row


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


def prepare_data(df, max_number_of_accounts):
    if df.index.size > max_number_of_accounts:
        return df

    loading_placeholder = st.empty()

    # Store the current column order
    initial_columns = df.columns.tolist()

    with st.spinner('Loading data... Please wait.'):
        list_prices_df = spl.get_all_cards_for_sale_df()
        market_prices_df = peakmonsters.get_market_prices_df()

        spl_estimates = df.apply(lambda row:
                                 add_estimations(row,
                                                 list_prices_df,
                                                 market_prices_df,
                                                 loading_placeholder), axis=1)

        # Reorder columns: put initial columns first, followed by any new columns
        new_columns = [col for col in spl_estimates.columns if col not in initial_columns]
        reordered_columns = initial_columns + new_columns
        spl_estimates = spl_estimates[reordered_columns]

    loading_placeholder.empty()
    return spl_estimates


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

        with st.expander("Estimated value data", expanded=False):
            st.dataframe(df, hide_index=True)
    else:
        st.write(f'Skip SPL estimate more then {max_number_of_accounts} accounts requested')
