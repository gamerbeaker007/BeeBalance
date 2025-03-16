import plotly.graph_objects as go
import streamlit as st

from src.graphs import graph_util


def add(df):
    log_x, log_y = graph_util.get_chart_settings(True, True, "ke_hp")

    df = df.sort_values(by="hp", ascending=False).reset_index(drop=True)

    # Assign hp_rank (0 for highest HP, increasing downwards)
    df["hp_rank"] = range(len(df))

    # Compute total rewards
    df["total_rewards"] = df["curation_rewards"] + df["posting_rewards"]

    fig = go.Figure()

    # Scatter plot for KE Ratio
    fig.add_trace(
        go.Scatter(
            x=df["hp_rank"],
            y=df["ke_ratio"],
            mode="markers",
            marker=dict(
                size=8,
                color="orange",
                symbol="circle",
            ),
            name="KE Ratio",
            hoverinfo="text",
            text=[
                f"Name: {row['name']}<br>KE Ratio: {row['ke_ratio']:.2f}<br>HP: {row['hp']}<br>"
                f"HP Rank: {row['hp_rank']}<br>Total Rewards: {row['total_rewards']:.2f}"
                for _, row in df.iterrows()
            ]
        )
    )

    # Scatter plot for Total Rewards (on secondary y-axis)
    fig.add_trace(
        go.Scatter(
            x=df["hp_rank"],  # Set HP as X-axis labels
            y=df["total_rewards"],
            mode="markers",
            marker=dict(
                size=8,
                color="blue",
                symbol="diamond",
            ),
            name="Total Rewards",
            hoverinfo="text",
            text=[
                f"Name: {row['name']}<br>KE Ratio: {row['ke_ratio']:.2f}<br>HP: {row['hp']:.2f}<br>"
                f"HP Rank: {row['hp_rank']}<br>Total Rewards: {row['total_rewards']:.2f}"
                for _, row in df.iterrows()
            ],
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["hp_rank"],
            y=df["hp"],
            mode="lines",
            line=dict(
                color="red",
            ),
            name="HP",
            hoverinfo="text",
            text=[
                f"Name: {row['name']}<br>KE Ratio: {row['ke_ratio']:.2f}<br>HP: {row['hp']:.2f}<br>"
                f"HP Rank: {row['hp_rank']}<br>Total Rewards: {row['total_rewards']:.2f}"
                for _, row in df.iterrows()
            ],
        )
    )

    # Decide whether to use log or linear scale
    x_axis_type = 'log' if log_x else 'linear'
    y_axis_type = 'log' if log_y else 'linear'

    # Update figure layout
    fig.update_layout(
        title="HP vs KE Ratio & Total Rewards",
        xaxis_title="HP (Log Scale)" if log_x else "HP Ratio",
        yaxis_title="KE Ratio (Log Scale)" if log_y else "KE Ratio",
        xaxis=dict(
            type=x_axis_type,
            tickformat=".0f"
        ),
        yaxis=dict(
            type=y_axis_type,
            tickformat=".0f",
            showgrid=True
        ),
        height=800,
    )

    st.plotly_chart(fig, theme="streamlit")
