import streamlit as st

from src.api import hive_sql
from src.static import icons
from src.util.card import create_card


def determine_emoji(ratio):
    if ratio <= 1:
        return ':heart_eyes:'
    elif 1 < ratio <= 3:
        return ':sunglasses:'
    elif 3 < ratio <= 10:
        return ':confused:'
    elif 10 < ratio <= 20:
        return ':confounded:'
    elif ratio > 20:
        return ':scream:'
    else:
        return ':question:'


def prepare_data(account_names):
    return hive_sql.get_hive_balances(account_names)


def get_page(df):
    st.title('Hive Balances')
    if not df.empty:
        ke_ratio = round(df['ke_ratio'].max(), 2)

        add_cards(df)

        if df.index.size == 1:
            st.title(':blue[KE Ratio]: ' + str(round(ke_ratio, 2)) + ' ' + determine_emoji(ke_ratio))
            st.write('KE Ratio = (Author Rewards + Curation Rewards) / HP')
            st.write('As a reminder KE Ratio is not everything please read the following post: ')
            st.write('TODO add link')
        else:
            st.title(':blue[KE Ratio]: N/A')
            st.write('KE Ratio is not determined for multiple accounts')
            st.write('KE Ratio = (Author Rewards + Curation Rewards) / HP')

    with st.expander("Hive balances data", expanded=False):
        st.dataframe(df, hide_index=True)


def add_cards(result):
    hive_balance = round(result['hive'].sum() + result['hive_savings'].sum(), 2)
    hbd_balance = round(result['hbd'].sum() + result['hbd_savings'].sum(), 2)
    hp_balance = round(result['hp'].sum(), 2)
    curation_rewards = round(result['curation_rewards'].sum(), 2)
    author_rewards = round(result['author_rewards'].sum(), 2)
    # Display the cards in a row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            create_card(
                "HIVE",
                f"{hive_balance} HIVE",
                icons.hive_icon_url,
            ),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            create_card(
                "HP (Hive Powered Up)",
                f"{hp_balance} HIVE",
                icons.hive_icon_url,
            ),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            create_card(
                "HBD",
                f"{hbd_balance} $",
                icons.hbd_icon_url,
            ),
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            create_card(
                "Author rewards",
                f"{author_rewards} HIVE",
                icons.credits_icon_url,
            ),
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            create_card(
                "Curation rewards",
                f"{curation_rewards} HIVE",
                icons.credits_icon_url,
            ),
            unsafe_allow_html=True,
        )
