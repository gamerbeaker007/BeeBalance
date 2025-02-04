import streamlit as st

spl_list = st.secrets.get("general", {}).get("spl_gray_list", [])


def check(account_names):
    matching_accounts = list(set(account_names) & set(spl_list))
    return "❗" if matching_accounts else ""
