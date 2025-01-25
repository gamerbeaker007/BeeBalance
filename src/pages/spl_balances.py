from time import sleep

import streamlit as st

from src.api import spl
from src.static import icons
from src.util.card import create_card


def add_token_balances(row, placeholder):
    placeholder.text(f"Loading SPL Balances for account: {row['name']}")

    # Specify tokens to filter
    tokens = [
        'SPS',
        'SPSP',
        'DEC',
        'DEC-B',
        'LICENSE',
        'PLOT',
        'TRACT',
        'REGION',
        'VOUCHER',
        'CREDIT'
    ]

    spl_balances = spl.get_balances(row["name"], filter_tokens=tokens)

    # Pivot the balances DataFrame
    if spl_balances.empty:
        # Return the original row if no balances are found
        return row

    pivoted_df = spl_balances.pivot(index="player", columns="token", values="balance")

    # Convert the row to a single-row DataFrame for merging
    row_df = row.to_frame().T
    merged_row = row_df.merge(pivoted_df, left_on="name", right_on="player", how="left")

    return merged_row.iloc[0]  # Return as a Series


def get_page(df):
    st.title('Splinterlands Balances')

    # Create a dynamic placeholder for loading text
    loading_placeholder = st.empty()

    with st.spinner('Loading data... Please wait.'):
        sps_balances = df.apply(lambda row: add_token_balances(row, loading_placeholder), axis=1)

    loading_placeholder.empty()

    sps_balance = sps_balances.iloc[0]
    # Display the cards in a row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            create_card(
                "SPS + Staked SPS",
                f"{sps_balance['SPS'].sum() + sps_balance['SPSP'].sum()} SPS",
                icons.sps_icon_url,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            create_card(
                "VOUCHERS",
                f"{sps_balance['VOUCHER'].sum()} VOUCHERS",
                icons.voucher_icon_url,
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            create_card(
                "DEC + DEC-B",
                f"{sps_balance['DEC'].sum() + sps_balance['DEC-B'].sum()} DEC",
                icons.dec_icon_url,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            create_card(
                "Validator License",
                f"{sps_balance['LICENSE'].sum()} #",
                icons.license_icon_url,
            ),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            create_card(
                "Credits",
                f"{sps_balance['CREDIT'].sum()} CREDITS",
                icons.license_icon_url,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            create_card(
                "Land plots (PLOT+TRACT+REGION)",
                f"{sps_balance['PLOT'].sum() + sps_balance['TRACT'].sum() + sps_balance['REGION'].sum()} #",
                icons.land_icon_url_svg,
            ),
            unsafe_allow_html=True,
        )

    with st.expander("Hive+SPL balances data", expanded=False):
        st.dataframe(sps_balances, hide_index=True)

    return df
