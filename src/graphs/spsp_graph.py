import plotly.graph_objects as go
import streamlit as st

from src.graphs import graph_util


def add(df):
    # SPSP can be None / NaN so make them 0
    df["SPSP"] = df["SPSP"].astype(float).fillna(0.0)

    log_x, log_y = graph_util.get_chart_settings(False, True, widget_suffix="spsp")

    df = df.sort_values(by="SPSP", ascending=False)

    fig = go.Figure()

    # Add scatter plot for SPS vs HP
    fig.add_trace(
        go.Bar(
            x=df['name'],
            y=df['SPSP'],
            name='SPS vs HP with posting rewards bubble size)'
        )
    )

    y_axis_type = 'log' if log_y else 'linear'

    # Update layout
    fig.update_layout(
        title="SPSP Holdings",
        xaxis_title="name",
        yaxis_title="SPSP (Log Scale)" if log_y else "SPSP",
        yaxis=dict(type=y_axis_type, tickformat=".0f"),
        height=800,
        # yaxis=dict(type="log"),
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, theme="streamlit")
