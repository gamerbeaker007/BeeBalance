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
    spsp = round(row['SPSP'], 2)
    hp = round(row['hp'], 2)
    ke_ratio = round(row['ke_ratio'], 2)
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
                sizeref=2. * max(df['SPSP']) / (40. ** 2),  # Normalize bubble size
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
                size=df['posting_rewards'],
                sizemode='area',
                sizeref=2. * max(df['posting_rewards']) / (40. ** 2),  # Normalize bubble size
                color=df['SPSP'],
                colorscale='Viridis',
                # showscale=True,  # Show color scale on the side
                line=dict(
                    color='white',  # Bubble border color
                    width=2  # Bubble border width
                )
            ),
            text=[f"Name: {row['name']}<br>SPSP: {round(row['SPSP'], 2)}<br>"
                  f"HP: {round(row['hp'], 2)}<br>"
                  f"Posting rewards: {round(row['posting_rewards'] + row['curation_rewards'], 2)}"
                  for _, row in df.iterrows()],
            hoverinfo='text',
            name='SPS vs HP with posting rewards bubble size)'
        )
    )

    # Update layout
    fig.update_layout(
        title="SPSP vs HP with Posting Rewards Bubble size",
        xaxis_title="HP",
        yaxis_title="SPSP",
        height=800,
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, theme="streamlit")


def add_spsp_graph(df):
    df = df.fillna(0)
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


def add_ke_hp_graph(df):
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
            x=df["hp_rank"],  # Set HP as X-axis labels
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
            # yaxis="y2"
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
