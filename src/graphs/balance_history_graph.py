import plotly.graph_objects as go
import streamlit as st

BALANCE_TYPES_PRIMARY = ["hive", "hp", "hive_savings"]
BALANCE_TYPES_SECONDARY = ["hbd", "hbd_savings"]

def add(df):
    df = df.sort_values("block_timestamp")
    df.rename(columns={"hp_equivalent": "hp"}, inplace=True)

    account_names = df["account_name"].unique()
    isOne = len(account_names) == 1

    fig = go.Figure()
    for account_name in account_names:
        account_df = df[df["account_name"] == account_name]
        filtered_df2 = account_df.groupby(account_df["block_timestamp"].dt.to_period("M")).first().reset_index(drop=True)
        for balance_type in BALANCE_TYPES_PRIMARY:
            fig.add_trace(
                go.Scatter(
                    x=filtered_df2["block_timestamp"].astype(str),
                    y=filtered_df2[balance_type],
                    mode="lines+markers",
                    name=balance_type if isOne else f"{account_name} - {balance_type}",
                    yaxis="y"
                )
            )
        for balance_type in BALANCE_TYPES_SECONDARY:
            fig.add_trace(
                go.Scatter(
                    x=filtered_df2["block_timestamp"].astype(str),
                    y=filtered_df2[balance_type],
                    mode="lines+markers",
                    name=balance_type if isOne else f"{account_name} - {balance_type}",
                    yaxis="y2"
                )
            )

    fig.update_layout(
        title="Balance history over time",
        xaxis_title="Block Timestamp",
        yaxis=dict(
            title="Hive / HP / Hive Savings",
            side="left",
            showgrid=True
        ),
        yaxis2=dict(
            title="HBD / HBD Savings",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        height=600,
        legend=dict(
            title="Balance Type",
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig, theme="streamlit")