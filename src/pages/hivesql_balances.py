import streamlit as st

from src.api import hivesql
from src.util.card import create_card

hive_icon_url = "https://files.peakd.com/file/peakd-hive/beaker007/AJpkTfBdpYojJYRFeoMZWprXbLf1ZeNZo83HSpomKJEjr5QMZMjLXbxfm4bEhVr.png"
hbd_icon_url = "https://files.peakd.com/file/peakd-hive/beaker007/AJbhBb9Ev3i1cHKtjoxtsCAaXK9njP56dzMwBRwfZVZ21WseKsCa6bM1q79mqFg.svg"
curation_icon_url = "https://d36mxiodymuqjm.cloudfront.net/website/ui_elements/shop/img_credits.png"


def determine_emoji(ratio):
    print(ratio)
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


def get_page(account_names):
    st.title('Hive sql stats')
    result = hivesql.get_hive_balances(account_names)
    if not result.empty and result.index.size == 1:
        row = result.iloc[0]
        hive_balance = round(row['hive'] + row['hive_savings'], 2)
        hbd_balance = round(row['hbd'] + row['hbd_savings'], 2)
        hp_balance = round(row['hp'], 2)
        curation_rewards = round(row['curation_rewards'], 2)
        author_rewards = round(row['author_rewards'], 2)
        ke_ratio = round(row['ke_ratio'], 2)

        # Display the cards in a row
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.markdown(
                create_card(
                    "HIVE",
                    f"{hive_balance} HIVE",
                    hive_icon_url,
                ),
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                create_card(
                    "HP (Hive Powered Up)",
                    f"{hp_balance} HIVE",
                    hive_icon_url,
                ),
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                create_card(
                    "HBD",
                    f"{hbd_balance} $",
                    hbd_icon_url,
                ),
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                create_card(
                    "Author rewards",
                    f"{author_rewards} HIVE",
                    curation_icon_url,
                ),
                unsafe_allow_html=True,
            )
        with col5:
            st.markdown(
                create_card(
                    "Curation rewards",
                    f"{curation_rewards} HIVE",
                    curation_icon_url,
                ),
                unsafe_allow_html=True,
            )

        st.title(':blue[KE Ratio]: ' + str(round(ke_ratio, 2)) + ' ' + determine_emoji(ke_ratio))
        st.write('KE Ratio = (Author Rewards + Curation Rewards) / HP')
        st.write('As a reminder KE Ratio is not everything please read the following post: ')
        st.write('TODO add link')

    with st.expander("Hive balances data", expanded=False):
        st.dataframe(result, hide_index=True)
