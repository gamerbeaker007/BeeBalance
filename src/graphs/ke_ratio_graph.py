import plotly.graph_objects as go
import streamlit as st

from src.graphs import graph_util


def determine_label(row):
    name = row['name']
    spsp = round(row['SPSP'], 2)
    hp = round(row['hp'], 2)
    ke_ratio = round(row['ke_ratio'], 2)
    return f"Name: {name}<br>SPSP: {spsp}<br>HP: {hp}<br>KE Ratio: {ke_ratio}"


def add(df):
    # SPSP can be None / NaN so make them 0
    df["SPSP"] = df["SPSP"].astype(float).fillna(0.0)

    log_x, log_y = graph_util.get_chart_settings(True, True, "ke_ratio")

    # Helper function for the labels
    def determine_label(row):
        # Provide your custom label logic here, e.g., return f"HP: {row['hp']}, KE Ratio: {row['ke_ratio']}"
        return f"HP: {round(row['hp'], 2)}, KE Ratio: {round(row['ke_ratio'], 2)}, SPSP: {round(row['SPSP'], 2)}"

    # Create a Plotly figure
    fig = go.Figure()

    # Add a scatter trace for the bubbles
    fig.add_trace(
        go.Scatter(
            x=df['hp'],
            y=df['ke_ratio'],
            mode='markers',
            marker=dict(
                size=df['SPSP'],  # Bubble size based on SPSP
                sizemode='area',
                sizeref=2. * max(df['SPSP']) / (40. ** 2),  # Normalize bubble size
                color=df['ke_ratio'],  # Color by ke_ratio
                colorscale='Viridis',  # Color scale
                showscale=True,
                line=dict(
                    color='white',  # Border color
                    width=2  # Border width
                )
            ),
            text=[determine_label(row) for _, row in df.iterrows()],  # Hover text
            hoverinfo='text',
            name='Bubbles'
        )
    )

    # Add a horizontal line for ke_ratio = 1 (blue)
    fig.add_shape(
        type="line",
        x0=min(df['hp']), x1=max(df['hp']),
        y0=1, y1=1,
        line=dict(color="blue", width=2, dash="dash"),
        name="ke_ratio = 1"
    )

    # Add a horizontal line for ke_ratio = 3 (red)
    fig.add_shape(
        type="line",
        x0=min(df['hp']), x1=max(df['hp']),
        y0=3, y1=3,
        line=dict(color="red", width=2, dash="dash"),
        name="ke_ratio = 3"
    )

    # Decide whether to use log or linear scale
    x_axis_type = 'log' if log_x else 'linear'
    y_axis_type = 'log' if log_y else 'linear'

    # Update figure layout
    fig.update_layout(
        title="KE Ratio vs HP with SPSP Bubble Size",
        xaxis_title="HP (Log Scale)" if log_x else "HP",
        yaxis_title="KE Ratio (Log Scale)" if log_y else "KE Ratio",
        xaxis=dict(type=x_axis_type, tickformat=".0f"),
        yaxis=dict(type=y_axis_type, tickformat=".0f"),
        height=800,
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, theme="streamlit")
