import plotly.graph_objects as go
import streamlit as st


def add(df):
    # SPSP can be None / NaN so make them 0
    df["SPSP"] = df["SPSP"].astype(float).fillna(0.0)

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

    # Update layout
    fig.update_layout(
        title="SPSP Holdings",
        xaxis_title="name",
        yaxis_title="SPSP",
        height=800,
        # yaxis=dict(type="log"),
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, theme="streamlit")
