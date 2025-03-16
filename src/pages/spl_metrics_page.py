import logging

import pandas as pd
import streamlit as st
import plotly.express as px

from src.api import spl

log = logging.getLogger("SPL Metrics")


def get_page():
    st.title("SPL Metrics")
    df = spl.get_metrics("mkt_cap_usd", "2000-01-01")
    df["date"] = pd.to_datetime(df["date"])  # Convert to datetime format

    # Streamlit App
    st.title("Market Cap USD Over Time")

    # Date Range Slider
    min_date = df["date"].min().to_pydatetime()  # Convert to Python datetime object
    max_date = df["date"].max().to_pydatetime()  # Convert to Python datetime object

    selected_range = st.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),  # Default to full range
        format="YYYY-MM-DD",
    )

    # Ensure selected_range values are converted to pandas timestamps
    start_date = pd.Timestamp(selected_range[0])
    end_date = pd.Timestamp(selected_range[1])

    # Filter Data Based on Slider Selection
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    # Create a Plotly figure
    fig = px.line(
        filtered_df,
        x="date",
        y="value",
        title="Market Cap USD Over Time",
        labels={"date": "Date", "value": "Market CAP USD"},
    )

    # Add fill below the line with 50% transparency
    fig.update_traces(line=dict(color="green", width=2), fill="tozeroy", fillcolor="rgba(0,128,0,0.5)")

    # Format x-axis to display dates as YYYY-MM-DD
    fig.update_layout(
        xaxis=dict(tickformat="%Y-%m-%d"),
        yaxis_title="Market CAP USD",
        xaxis_title="Date",
        height=800,
    )

    # Display the filtered plot
    st.plotly_chart(fig)
    with st.expander(f'Data', expanded=False):
        st.dataframe(filtered_df)
