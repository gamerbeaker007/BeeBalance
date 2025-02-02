import plotly.graph_objects as go
import streamlit as st


def add(df):
    df = df.fillna(0)
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


    fig.update_layout(
        title="HP vs KE Ratio & Total Rewards",
        yaxis=dict(
            title="KE Ratio (Log Scale)",
            type="log",
            showgrid=True
        ),
        height=600,
    )

    st.plotly_chart(fig, theme="streamlit")
