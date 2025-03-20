import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from src.graphs import graph_util

METRIC_NAMES = {
    'battles': 'Battles',
    'battles-modern': 'Battles Modern',
    'battles-survival': 'Battles Survival',
    'battles-wild': 'Battles Wild',
    'dau': 'Daily Active Users',
    'dec_rewards': 'DEC Rewards',
    'market_vol': 'Market Volume',
    'market_vol_usd': 'Market Volume USD',
    'mkt_cap_usd': 'Market CAP USD',
    'sign_ups': 'Signups',
    'spellbooks': 'Spellbooks',
    'tx_total': 'Total transactions',
}


def format_metric_name(metric):
    """Converts metric keys to human-readable titles."""
    return METRIC_NAMES.get(metric, metric.replace("-", " ").title())


def add_user_join_line(fig, username, join_date, y_max):
    fig.add_trace(
        go.Scatter(
            x=[join_date, join_date],
            y=[0, y_max],
            mode="lines",
            line=dict(color="red", width=4),
            name=f"Join date of {username}",
            yaxis='y'  # Assign y-axis
        )
    )
    return fig


def create_market_graph(df, username, join_date, show_join_date):
    # Filter DataFrame to include only the desired metrics
    filtered_df = df[df["metric"].isin(["market_vol", "market_vol_usd", "mkt_cap_usd"])]

    _, log_y = graph_util.get_chart_settings(y=True,
                                             default_value_y=False,
                                             widget_suffix="market_graph")
    y_axis_type = 'log' if log_y else 'linear'

    # Create a subplot figure with multiple y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Define colors for each metric
    metric_colors = {
        "market_vol": "blue",
        "market_vol_usd": "purple",
        "mkt_cap_usd": "orange"
    }

    max_mkt_cap = filtered_df[filtered_df["metric"] == "mkt_cap_usd"]["value"].max() * 1.10
    max_mkt_vol_usd = filtered_df[filtered_df["metric"] == "market_vol_usd"]["value"].max() * 1.10
    max_mkt_vol = filtered_df[filtered_df["metric"] == "market_vol"]["value"].max() * 1.10

    if join_date and show_join_date:
        fig = add_user_join_line(fig, username, join_date, max_mkt_cap)

    # Add traces for each metric
    for metric in filtered_df.metric.unique():
        metric_df = filtered_df[filtered_df["metric"] == metric]
        metric_name = METRIC_NAMES.get(metric, metric)

        # Determine which y-axis to use
        if metric == "market_vol":
            yaxis = "y3"  # Third y-axis
        elif metric == "market_vol_usd":
            yaxis = "y2"  # Secondary y-axis
        else:
            yaxis = "y"  # Primary y-axis

        fig.add_trace(
            go.Scatter(
                x=metric_df["date"],
                y=metric_df["value"],
                mode="lines+markers",
                marker=dict(size=5, color=metric_colors.get(metric, "red")),
                name=metric_name,
                yaxis=yaxis  # Assign y-axis
            )
        )

    # Update layout with three y-axes
    fig.update_layout(
        xaxis=dict(tickformat="%Y-%m-%d"),
        yaxis=dict(
            type=y_axis_type,
            title=METRIC_NAMES["mkt_cap_usd"],  # Primary Y-Axis
            titlefont=dict(color=metric_colors["mkt_cap_usd"]),
            tickfont=dict(color=metric_colors["mkt_cap_usd"]),
            range=None if log_y else [0, max_mkt_cap],
        ),
        yaxis2=dict(
            type=y_axis_type,
            title=METRIC_NAMES["market_vol_usd"],  # Second Y-Axis (right)
            titlefont=dict(color=metric_colors["market_vol_usd"]),
            tickfont=dict(color=metric_colors["market_vol_usd"]),
            overlaying="y",
            side="right",
            showgrid=False,
            range=None if log_y else [0, max_mkt_vol_usd],
        ),
        yaxis3=dict(
            type=y_axis_type,
            title=METRIC_NAMES["market_vol"],  # Third Y-Axis (far right)
            titlefont=dict(color=metric_colors["market_vol"]),
            tickfont=dict(color=metric_colors["market_vol"]),
            overlaying="y",
            side="right",
            position=1,  # Adjust position of third axis
            showgrid=False,
            range=None if log_y else [0, max_mkt_vol],
        ),
        xaxis_title="Date",
        height=800,
    )

    # Display the plot
    st.plotly_chart(fig)

    with st.expander("Data", expanded=False):
        st.dataframe(filtered_df)


def create_tx_graph(df, username, join_date, show_join_date):
    # Filter DataFrame to include only the desired metrics
    filtered_df = df[df["metric"].isin(["tx_total"])]

    _, log_y = graph_util.get_chart_settings(y=True,
                                             default_value_y=False,
                                             widget_suffix="tx_graph")
    y_axis_type = 'log' if log_y else 'linear'

    fig = go.Figure()

    max_tx = filtered_df["value"].max() * 1.10

    if join_date and show_join_date:
        fig = add_user_join_line(fig, username, join_date, max_tx)

    for metric in filtered_df.metric.unique().tolist():
        metric_df = filtered_df.loc[filtered_df.metric == metric]
        fig.add_trace(
            go.Scatter(
                x=metric_df["date"],
                y=metric_df["value"],
                mode="lines+markers",
                marker=dict(
                    size=5,
                    color='blue',
                    symbol="circle",
                ),
                name=METRIC_NAMES.get(metric),
            )
        )

    # Format x-axis
    fig.update_layout(
        xaxis=dict(tickformat="%Y-%m-%d"),
        yaxis=dict(
            type=y_axis_type
        ),
        yaxis_title="Transactions",
        xaxis_title="Date",
        height=800,
    )

    # Display the plot
    st.plotly_chart(fig)
    with st.expander("Data", expanded=False):
        st.dataframe(filtered_df)


def create_user_graph(df, username, join_date, show_join_date):
    # Filter DataFrame to include only the desired metrics
    filtered_df = df[df["metric"].isin(["dau", "sign_ups", "spellbooks"])]

    _, log_y = graph_util.get_chart_settings(y=True,
                                             default_value_y=False,
                                             widget_suffix="user_graph")
    y_axis_type = 'log' if log_y else 'linear'

    # Create a subplot figure with multiple y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Define colors for each metric
    metric_colors = {
        "dau": "blue",
        "sign_ups": "purple",
        "spellbooks": "orange"
    }

    max_dau = filtered_df[filtered_df["metric"] == "dau"]["value"].max() * 1.10
    max_sing_ups = filtered_df[filtered_df["metric"] == "sign_ups"]["value"].max() * 1.10
    max_spellbooks = filtered_df[filtered_df["metric"] == "spellbooks"]["value"].max() * 1.10

    if join_date and show_join_date:
        fig = add_user_join_line(fig, username, join_date, max_spellbooks)

    # Add traces for each metric
    for metric in filtered_df.metric.unique():
        metric_df = filtered_df[filtered_df["metric"] == metric]
        metric_name = METRIC_NAMES.get(metric, metric)

        # Determine which y-axis to use
        if metric == "dau":
            yaxis = "y3"  # Third y-axis
        elif metric == "sign_ups":
            yaxis = "y2"  # Secondary y-axis
        else:
            yaxis = "y"  # Primary y-axis

        fig.add_trace(
            go.Scatter(
                x=metric_df["date"],
                y=metric_df["value"],
                mode="lines+markers",
                marker=dict(size=5, color=metric_colors.get(metric, "red")),
                name=metric_name,
                yaxis=yaxis  # Assign y-axis
            )
        )

    # Update layout with three y-axes
    fig.update_layout(
        xaxis=dict(tickformat="%Y-%m-%d"),
        yaxis=dict(
            type=y_axis_type,
            title=METRIC_NAMES["spellbooks"],  # Primary Y-Axis
            titlefont=dict(color=metric_colors["spellbooks"]),
            tickfont=dict(color=metric_colors["spellbooks"]),
            range=None if log_y else [0, max_spellbooks],
        ),
        yaxis2=dict(
            type=y_axis_type,
            title=METRIC_NAMES["sign_ups"],  # Second Y-Axis (right)
            titlefont=dict(color=metric_colors["sign_ups"]),
            tickfont=dict(color=metric_colors["sign_ups"]),
            overlaying="y",
            side="right",
            showgrid=False,
            range=None if log_y else [0, max_sing_ups],
        ),
        yaxis3=dict(
            type=y_axis_type,
            title=METRIC_NAMES["dau"],  # Third Y-Axis (far right)
            titlefont=dict(color=metric_colors["dau"]),
            tickfont=dict(color=metric_colors["dau"]),
            overlaying="y",
            side="right",
            position=1,  # Adjust position of third axis
            showgrid=False,
            range=None if log_y else [0, max_dau],
        ),
        xaxis_title="Date",
        height=800,
    )

    # Display the plot
    st.plotly_chart(fig)

    with st.expander("Data", expanded=False):
        st.dataframe(filtered_df)


def create_battle_graph(df):
    filtered_df = df[df["metric"].str.startswith("battles")]

    _, log_y = graph_util.get_chart_settings(y=True,
                                             default_value_y=False,
                                             widget_suffix="battle_graph")
    y_axis_type = 'log' if log_y else 'linear'

    fig = go.Figure()

    for metric in filtered_df.metric.unique().tolist():
        if metric == 'battles-modern':
            color = 'blue'
        elif metric == 'battles-wild':
            color = 'purple'
        elif metric == 'battles-survival':
            color = 'orange'
        else:
            color = 'red'

        metric_df = filtered_df.loc[filtered_df.metric == metric]
        fig.add_trace(
            go.Scatter(
                x=metric_df["date"],
                y=metric_df["value"],
                mode="lines+markers",
                marker=dict(
                    size=5,
                    color=color,
                    symbol="circle",
                ),
                name=METRIC_NAMES.get(metric),
            )
        )

    # Format x-axis
    fig.update_layout(
        xaxis=dict(tickformat="%Y-%m-%d"),
        yaxis=dict(
            type=y_axis_type
        ),
        yaxis_title="Amount of battles played",
        xaxis_title="Date",
        height=800,
    )

    # Display the plot
    st.plotly_chart(fig)
    with st.expander("Data", expanded=False):
        st.dataframe(filtered_df)
