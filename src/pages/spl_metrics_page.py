import streamlit as st
import logging
from datetime import datetime, timedelta

import pandas as pd
import pytz

from src.api import spl
from src.graphs import spl_metrics_graphs

log = logging.getLogger("SPL Metrics")


def display_period_buttons():
    # Define filter options
    options = {
        "All": None,
        "12 Months": 365,
        "6 Months": 180,
        "1 Month": 30,
        "2 Weeks": 14,
        "7 Days": 7
    }

    # Create the toggle buttons
    # Initialize session state for toggle buttons
    if "selected_option" not in st.session_state:
        st.session_state.selected_option = 7
        number_of_days_label = '7 Days'
    else:
        value = st.session_state.selected_option
        number_of_days_label = next((key for key, val in options.items() if val == value), None)

    # Layout for toggle buttons
    cols = st.columns(len(options))

    for i, (label, days) in enumerate(options.items()):
        if cols[i].button(label, use_container_width=True):
            st.session_state.selected_option = days
            number_of_days_label = label

    st.subheader(f"SPL Metrics for the last {number_of_days_label}")

    return st.session_state.selected_option


def filter_on_days(df, number_of_days):
    df["date"] = pd.to_datetime(df["date"])
    now_utc = datetime.now(pytz.utc)
    # Convert to datetime format
    if number_of_days is not None:
        filtered_df = df[df["date"] >= now_utc - timedelta(days=number_of_days)]
    else:
        filtered_df = df
    return filtered_df


def create_one_dataframe(df, number_of_days):
    df_exploded = df.explode("values")
    # Normalize the dictionary column into separate columns
    df_transformed = pd.json_normalize(df_exploded.to_dict("records"))
    # Rename columns for clarity
    df_transformed = df_transformed.rename(columns={"values.date": "date", "values.value": "value"})
    # Convert date column to datetime format
    df_transformed["date"] = pd.to_datetime(df_transformed["date"])
    # Select final columns
    df_transformed = df_transformed[["date", "metric", "value"]]
    # Filtered asked number of days
    filtered_df = filter_on_days(df_transformed, number_of_days)
    return filtered_df


def get_page():

    df = spl.get_metrics()

    number_of_days = display_period_buttons()

    df = create_one_dataframe(df, number_of_days)

    username = st.text_input("Enter SPL user name (determine join date)")
    show_join_date = st.checkbox("Show join date")

    join_date = None
    if username:
        user_df = spl.get_player_details(username)
        if user_df.empty:
            st.warning("Incorrect username")
        else:
            join_date = pd.to_datetime(user_df["join_date"]).iloc[0]

    tab1, tab2, tab3, tab4 = st.tabs(["Battle Metrics", "Card Market Metrics", "User Metrics", "Transactions"])

    with tab1:
        st.subheader("Battle Metrics")
        spl_metrics_graphs.create_battle_graph(df)

    with tab2:
        st.subheader("Card Market Metrics")
        spl_metrics_graphs.create_market_graph(df, username, join_date, show_join_date)

    with tab3:
        st.subheader("User Metrics")
        spl_metrics_graphs.create_user_graph(df, username, join_date, show_join_date)

    with tab4:
        st.subheader("Transactions")
        spl_metrics_graphs.create_tx_graph(df, username, join_date, show_join_date)
