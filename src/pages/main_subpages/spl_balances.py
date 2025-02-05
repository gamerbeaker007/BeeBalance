import streamlit as st

from src.api import spl
from src.graphs import ke_ratio_graph
from src.static import icons
from src.util.card import create_card

token_columns = [
        'SPS',
        'SPSP',
        'DEC',
        'DEC-B',
        'LICENSE',
        'PLOT',
        'TRACT',
        'REGION',
        'VOUCHER',
        'CREDITS'
    ]


def add_token_balances(row, placeholder):
    placeholder.text(f"Loading SPL Balances for account: {row['name']}")

    # Specify tokens to filter

    spl_balances = spl.get_balances(row["name"], filter_tokens=token_columns)

    # Pivot the balances DataFrame
    if spl_balances.empty:
        # Return the original row if no balances are found
        return row

    pivoted_df = spl_balances.pivot(index="player", columns="token", values="balance")

    # Convert the row to a single-row DataFrame for merging
    row_df = row.to_frame().T
    merged_row = row_df.merge(pivoted_df, left_on="name", right_on="player", how="left")

    # Reorder the columns to ensure original columns are followed by the new ones
    for col in pivoted_df.columns:
        if col not in row_df.columns:
            row_df[col] = pivoted_df[col].iloc[0] if col in pivoted_df.columns else 0

    return row_df.iloc[0]  # Return as a Series


def prepare_date(df):
    # Create a dynamic placeholder for loading text
    loading_placeholder = st.empty()

    with st.spinner('Loading data... Please wait.'):
        # Use a custom merge to ensure column order is preserved
        sps_balances = df.apply(lambda row: add_token_balances(row, loading_placeholder), axis=1)

    loading_placeholder.empty()

    for col in token_columns:
        if col not in sps_balances.columns:
            sps_balances[col] = 0

    # Ensure original columns appear first
    sps_balances = sps_balances[list(df.columns) + token_columns]
    return sps_balances


def get_page(df):
    st.title('Splinterlands Balances')

    add_cards(df)

    if df.name.index.size > 1:
        ke_ratio_graph.add(df[['name', 'ke_ratio', 'hp', 'SPSP']])


def add_cards(sps_balances):
    # Display the cards in a row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            create_card(
                "SPS + Staked SPS",
                f"{sps_balances['SPS'].sum() + sps_balances['SPSP'].sum()} SPS",
                icons.sps_icon_url,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            create_card(
                "VOUCHERS",
                f"{sps_balances['VOUCHER'].sum()} VOUCHERS",
                icons.voucher_icon_url,
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            create_card(
                "DEC + DEC-B",
                f"{sps_balances['DEC'].sum() + sps_balances['DEC-B'].sum()} DEC",
                icons.dec_icon_url,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            create_card(
                "Validator License",
                f"{sps_balances['LICENSE'].sum()} #",
                icons.license_icon_url,
            ),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            create_card(
                "Credits",
                f"{sps_balances['CREDITS'].sum()} CREDITS",
                icons.credits_icon_url,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            create_card(
                "Land Claims",
                f"{sps_balances['PLOT'].sum() + sps_balances['TRACT'].sum() + sps_balances['REGION'].sum()} #",
                icons.land_icon_url_svg,
            ),
            unsafe_allow_html=True,
        )
