import pandas as pd
import streamlit as st

from src.api import spl
from src.static import icons
from src.util.card import create_card

extra_columns = [
    'collection_power',
    'deeds',
]


def add_assets(row):
    """
    Add assets (collection power and deeds) to a player's row.

    :param row: A row from a DataFrame.
    :return: A DataFrame containing the modified row.
    """
    # Fetch player card collection and calculate collection power
    player_card_collection = spl.get_player_collection_df(row["name"])
    row = row.copy()  # Ensure modification does not affect cached data

    row["collection_power"] = player_card_collection[
        "collection_power"].sum() if not player_card_collection.empty else 0

    # Fetch player deeds collection and count
    player_deeds = spl.get_deeds_collection(row["name"])
    row["deeds"] = len(player_deeds) if not player_deeds.empty else 0

    return pd.DataFrame([row])  # Always return as DataFrame for easy concatenation


def prepare_data(df):
    """
    Process each player's data, adding asset information.
    Uses a Streamlit status update for user feedback.
    """
    status = st.status("Loading SPL Assets...", expanded=True)

    processed_rows = []  # List to store processed rows

    for index, row in df.iterrows():
        status.update(label=f"Fetching assets for: {row['name']}...", state="running")

        updated_row = add_assets(row)  # Process row
        processed_rows.append(updated_row)  # Append result

        status.update(label=f"Completed {row['name']}", state="complete")

    # Combine processed rows into a DataFrame
    result_df = pd.concat(processed_rows, ignore_index=True) if processed_rows else pd.DataFrame(columns=df.columns)

    status.update(label="All assets loaded!", state="complete")

    return result_df


def get_page(df):
    st.title('Splinterlands Assets')
    add_cards(df)


def add_cards(spl_assets):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            create_card(
                "Collection Power",
                f"{spl_assets['collection_power'].sum()} CP",
                icons.cards_icon_url,
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            create_card(
                "Deeds",
                f"{spl_assets['deeds'].sum()} #",
                icons.land_icon_url_svg,
            ),
            unsafe_allow_html=True,
        )
