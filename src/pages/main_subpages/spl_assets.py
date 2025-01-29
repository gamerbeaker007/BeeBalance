import streamlit as st

from src.api import spl
from src.static import icons
from src.util.card import create_card

extra_columns = [
    'collection_power',
    'deeds',
]


def add_assets(row, placeholder):
    placeholder.text(f"Loading SPL Balances for account: {row['name']}")

    player_details = spl.get_player_details(row["name"])
    if not player_details:
        return row
    row['collection_power'] = player_details['collection_power']

    player_deeds = spl.get_deeds_collection(row['name'])
    if not player_deeds:
        return row

    row['deeds'] = len(player_deeds)
    return row


def prepare_data(df):
    loading_placeholder = st.empty()

    with st.spinner('Loading data... Please wait.'):
        spl_assets = df.apply(lambda row: add_assets(row, loading_placeholder), axis=1)

    loading_placeholder.empty()

    for col in extra_columns:
        if col not in spl_assets.columns:
            spl_assets[col] = 0

    # Ensure original columns appear first
    spl_assets = spl_assets[list(df.columns) + extra_columns]
    return spl_assets


def get_page(df):
    st.title('Splinterlands Assets')

    add_cards(df)

    with st.expander("Hive+SPL balances + SPL Assets data", expanded=False):
        st.dataframe(df, hide_index=True)


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
