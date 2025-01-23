import streamlit as st
from beem.account import Account
from beem.exceptions import AccountDoesNotExistsException

from src.api import hive
from src.util.card import create_card, card_style

hive_icon_url = "https://files.peakd.com/file/peakd-hive/beaker007/AJpkTfBdpYojJYRFeoMZWprXbLf1ZeNZo83HSpomKJEjr5QMZMjLXbxfm4bEhVr.png"
hbd_icon_url = "https://files.peakd.com/file/peakd-hive/beaker007/AJbhBb9Ev3i1cHKtjoxtsCAaXK9njP56dzMwBRwfZVZ21WseKsCa6bM1q79mqFg.svg"
curation_icon_url = "https://d36mxiodymuqjm.cloudfront.net/website/ui_elements/shop/img_credits.png"


def determine_emoji(ratio):
    print(ratio)
    if ratio <= 1:
        return ':heart_eyes:'
    elif 1 < ratio <= 3:
        return ':sunglasses:'
    elif  3 < ratio <= 10:
        return ':confused:'
    elif 10 < ratio <= 20:
        return ':confounded:'
    elif ratio > 20:
        return ':scream:'
    else:
        return ':question:'


def get_page(account_name):
    st.title('Hive balances')
    try:
        account = Account(account_name)
        if account is not None:
            balances = hive.get_hive_balances(account)
            hive_balance = round(balances['HIVE'].iloc[0], 2)
            hp_balance = round(balances['HP'].iloc[0], 2)
            hbd_balance = round(balances['HBD'].iloc[0], 2)
            curation_reward_balance = round(balances['Curation Rewards'].iloc[0], 2)
            # Apply card CSS
            st.markdown(card_style, unsafe_allow_html=True)

            # Display the cards in a row
            col1, col2, col3, col4 = st.columns(4)

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
                        "Received Curation Rewards",
                        f"{curation_reward_balance} HIVE",
                        curation_icon_url,
                    ),
                    unsafe_allow_html=True,
                )

            st.title(':blue[KE Ratio]: ' + str(round(balances.Ratio.iloc[0], 2)) + ' ' + determine_emoji(balances.Ratio.iloc[0]))
            st.write('As a reminder KE Ratio is not everything please read the following post: ')
            st.write('TODO add link')
            with st.expander("Hive balances data", expanded=False):
                st.dataframe(balances, hide_index=True)
        else:
            st.write('Enter valid hive account name')
    except AccountDoesNotExistsException:
        st.warning('Invalid account name try again')
