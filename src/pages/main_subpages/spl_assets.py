import streamlit as st

from src.api import spl
from src.static import icons
from src.util.card import create_card

extra_columns = [
    'collection_power',
    'deeds',
]


def add_assets(row, placeholder):
    """
    Add assets (collection power and deeds) to a player's row.

    :param row: A row from a DataFrame.
    :param placeholder: Streamlit placeholder to display status messages.
    :return: A modified row with added asset values.
    """
    placeholder.text(f"Loading SPL Balances for account: {row['name']}")

    # Ensure we modify a copy of row
    row = row.copy()

    # Fetch player card collection and calculate collection power
    player_card_collection = spl.get_player_collection_df(row["name"])
    if not player_card_collection.empty:
        row["collection_power"] = player_card_collection["collection_power"].sum()
    else:
        row["collection_power"] = 0  # Default value if empty

    # Fetch player deeds collection and count
    player_deeds = spl.get_deeds_collection(row["name"])
    if not player_deeds.empty:
        row["deeds"] = len(player_deeds)
    else:
        row["deeds"] = 0  # Default value if empty

    return row


def prepare_data(df):
    loading_placeholder = st.empty()

    with st.spinner('Loading data... Please wait.'):
        spl_assets = df.apply(lambda row: add_assets(row, loading_placeholder), axis=1)

    loading_placeholder.empty()

    return spl_assets


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
