import plotly.graph_objects as go
import streamlit as st
from streamlit_theme import st_theme


def is_dark_theme_enabled():
    """
    Determine if the current Streamlit theme is dark or light.
    Returns True if dark theme is enabled, False otherwise.
    """
    theme = st_theme()
    if theme:
        return theme['base'] == "dark"
    else:
        return True  # Default to dark theme if theme information is unavailable


def determine_label(row):
    name = row['name']
    spsp = round(row['SPSP'],2)
    hp = round(row['hp'],2)
    ke_ratio = round(row['ke_ratio'],2)
    return f"Name: {name}<br>SPSP: {spsp}<br>HP: {hp}<br>KE Ratio: {ke_ratio}"


def add_ke_ratio_graph(df):
    df = df.fillna(0)

    # Create a Plotly scatter plot
    fig = go.Figure()

    # Add scatter plot for the bubbles
    fig.add_trace(
        go.Scatter(
            x=df['hp'],
            y=df['ke_ratio'],
            mode='markers',
            marker=dict(
                size=df['SPSP'],  # Bubble size based on SPSP
                sizemode='area',
                sizeref=2. * max(df['SPSP']) / (40.**2),  # Normalize bubble size
                color=df['ke_ratio'],  # Color by ke_ratio (optional gradient)
                colorscale='Viridis',  # Adjust to preferred color scale
                showscale=True,
                line=dict(
                    color='white',  # Border color
                    width=2  # Border width
                )
            ),
            text=[determine_label(row) for _, row in df.iterrows()],  # Hover text
            hoverinfo='text',  # Show custom hover text
            name='Bubbles'
        )
    )

    # Add vertical blue line for ke_ratio = 1
    fig.add_shape(
        type="line",
        x0=min(df['hp']), x1=max(df['hp']),
        y0=1, y1=1,
        line=dict(color="blue", width=2, dash="dash"),
        name="ke_ratio = 1"
    )

    # Add vertical red line for ke_ratio = 3
    fig.add_shape(
        type="line",
        x0=min(df['hp']), x1=max(df['hp']),
        y0=3, y1=3,
        line=dict(color="red", width=2, dash="dash"),
        name="ke_ratio = 3"
    )

    # Update layout
    fig.update_layout(
        title="KE Ratio vs HP with SPSP Bubble Size",
        xaxis_title="HP",
        yaxis_title="KE Ratio (Log Scale)",
        yaxis=dict(type="log"),  # Set y-axis to log scale
        # template="plotly_white" if not is_dark_theme else "plotly_dark",
        # plot_bgcolor=background_color,
        # paper_bgcolor=background_color,
        # font=dict(color=text_color),
        height=800,
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, theme="streamlit")


def add_spsp_vs_hp_graph(df):
    df = df.fillna(0)

    fig = go.Figure()

    # Add scatter plot for SPS vs HP
    fig.add_trace(
        go.Scatter(
            x=df['hp'],
            y=df['SPSP'],
            mode='markers',
            marker=dict(
                size=10,  # Fixed bubble size for simplicity
                color=df['SPSP'],  # Color by SPS
                colorscale='Viridis',  # Use a color scale
                showscale=True,  # Show color scale on the side
                line=dict(
                    color='white',  # Bubble border color
                    width=2  # Bubble border width
                )
            ),
            text=[f"Name: {row['name']}<br>SPSP: {round(row['SPSP'], 2)}<br>HP: {round(row['hp'], 2)}"
                  for _, row in df.iterrows()],  # Custom hover text
            hoverinfo='text',  # Show custom hover text
            name='SPS vs HP'
        )
    )

    # Update layout
    fig.update_layout(
        title="SPSP vs HP",
        xaxis_title="HP",
        yaxis_title="SPSP",
        # template="plotly_white" if not is_dark_theme else "plotly_dark",
        # plot_bgcolor=background_color,
        # paper_bgcolor=background_color,
        # font=dict(color=text_color),
        height=800,
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, theme="streamlit")
