import pandas as pd
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


def add_token_balances(row):
    """
    Fetch and process SPL balances for a given player row.
    Returns a DataFrame containing the updated balance information.
    """
    spl_balances = spl.get_balances(row["name"], filter_tokens=token_columns)

    if spl_balances.empty:
        return pd.DataFrame([row])  # Ensure we return a DataFrame, not a Series

    # Pivot balances for each token
    pivoted_df = spl_balances.pivot(index="player", columns="token", values="balance").reset_index()

    # Convert the row to a DataFrame
    row_df = pd.DataFrame([row])

    # Merge token balances with the original row
    merged_row = row_df.merge(pivoted_df, left_on="name", right_on="player", how="left").drop(columns=["player"])

    # Ensure all expected token columns exist
    for col in token_columns:
        if col not in merged_row.columns:
            merged_row[col] = 0  # Default missing tokens to 0

    return merged_row


def prepare_data(df):
    """
    Process all rows in df by fetching SPL balances and updating token columns.
    Uses Streamlit's status update for user feedback.
    """

    empty_space = st.empty()
    with empty_space.container():
        with st.status('Loading SPL Balances...', expanded=True) as status:
            processed_rows = []  # List to store processed rows

            for index, row in df.iterrows():
                status.update(label=f"Fetching balances for: {row['name']}...", state="running")

                updated_row = add_token_balances(row)  # Process each row
                processed_rows.append(updated_row)  # Append processed row

                status.update(label=f"Completed {row['name']}", state="complete")

            # Combine processed rows into a DataFrame
            if processed_rows:
                result_df = pd.concat(processed_rows, ignore_index=True)
            else:
                result_df = pd.DataFrame(columns=df.columns)  # Return an empty DataFrame if no data
    empty_space.empty()

    return result_df


def get_page(df):
    st.title('Splinterlands Balances')

    add_cards(df)

    if df.name.index.size > 1:
        ke_ratio_graph.add(df[['name', 'ke_ratio', 'hp', 'SPSP']])


def add_cards(sps_balances):
    # Define a safe sum function to handle missing columns
    def safe_sum(df, column):
        return df[column].sum() if column in df.columns else 0

    # Display the cards in a row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            create_card(
                "SPS + Staked SPS",
                f"{safe_sum(sps_balances, 'SPS') + safe_sum(sps_balances, 'SPSP')} SPS",
                icons.sps_icon_url,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            create_card(
                "VOUCHERS",
                f"{safe_sum(sps_balances, 'VOUCHER')} VOUCHERS",
                icons.voucher_icon_url,
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            create_card(
                "DEC + DEC-B",
                f"{safe_sum(sps_balances, 'DEC') + safe_sum(sps_balances, 'DEC-B')} DEC",
                icons.dec_icon_url,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            create_card(
                "Validator License",
                f"{safe_sum(sps_balances, 'LICENSE')} #",
                icons.license_icon_url,
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            create_card(
                "Credits",
                f"{safe_sum(sps_balances, 'CREDITS')} CREDITS",
                icons.credits_icon_url,
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            create_card(
                "Land Claims",
                f"{safe_sum(sps_balances, 'PLOT') + safe_sum(sps_balances, 'TRACT') + safe_sum(sps_balances, 'REGION')} #",
                icons.land_icon_url_svg,
            ),
            unsafe_allow_html=True,
        )
