import logging
import pandas as pd
import streamlit as st
import plotly.express as px

from src.api import spl

log = logging.getLogger("SPL Metrics")


METRIC_NAMES = {
    'battles': 'Battles',
    'battles-modern': 'Battles Modern',
    'battles-survival': 'Battles Survival',
    'battles-wild': 'Battles Wild',
    'dau': 'Daily Active Users',
    'dec_rewards': 'DEC Rewards',
    'market_vol': 'Market Volume',
    'market_vol_usd': 'Market Volume USD',
    'mkt_cap_usd': 'Market CAP USD (Cards)',
    'sign_ups': 'Signups',
    'spellbooks': 'Spellbooks',
    'tx_total': 'Total transactions',
}


def format_metric_name(metric):
    """Converts metric keys to human-readable titles."""
    return METRIC_NAMES.get(metric, metric.replace("-", " ").title())


def add_chart(df, title, slider_key):
    df["date"] = pd.to_datetime(df["date"])  # Convert to datetime format

    # Set default min/max date
    min_date = df["date"].min().to_pydatetime()
    max_date = df["date"].max().to_pydatetime()

    # Store each slider's state separately
    if slider_key not in st.session_state:
        st.session_state[slider_key] = (min_date, max_date)

    selected_range = st.slider(
        f"Select Date Range for '{title}'",
        min_value=min_date,
        max_value=max_date,
        value=st.session_state[slider_key],  # Use stored value
        format="YYYY-MM-DD",
        key=slider_key,  # Unique key to prevent re-rendering all sliders
    )

    # Convert selected range to timestamps
    start_date = pd.Timestamp(selected_range[0])
    end_date = pd.Timestamp(selected_range[1])

    # Filter Data
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    # Create Plotly Figure
    fig = px.line(
        filtered_df,
        x="date",
        y="value",
        title=f"{title}",
        labels={"date": "Date", "value": title},
    )

    # Add fill below the line with 50% transparency
    fig.update_traces(line=dict(color="green", width=2), fill="tozeroy", fillcolor="rgba(0,128,0,0.5)")

    # Format x-axis
    fig.update_layout(
        xaxis=dict(tickformat="%Y-%m-%d"),
        yaxis_title=title,
        xaxis_title="Date",
        height=800,
    )

    # Display the plot
    st.plotly_chart(fig)
    with st.expander("Data", expanded=False):
        st.dataframe(filtered_df)


def get_page():
    st.title("SPL Metrics")

    df = spl.get_metrics()
    unique_metrics = df["metric"].unique()  # Get unique metric names

    metric_mapping = {metric: format_metric_name(metric) for metric in unique_metrics}
    selected_metric_friendly = st.selectbox("Select a Metric to Display", list(metric_mapping.values()))
    selected_metric = next(k for k, v in metric_mapping.items() if v == selected_metric_friendly)
    metric_df = pd.DataFrame(df[df.metric == selected_metric]["values"].iloc[0])

    # Unique slider key per metric
    slider_key = f"slider_{selected_metric}"

    # Render the selected metric's chart
    add_chart(metric_df, selected_metric_friendly, slider_key)
