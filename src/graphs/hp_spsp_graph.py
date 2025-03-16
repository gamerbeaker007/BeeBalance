import plotly.graph_objects as go
import streamlit as st


def add(df, log_x, log_y):
    # SPSP can be None / NaN so make them 0
    df["SPSP"] = df["SPSP"].fillna(0).infer_objects(copy=False)

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

    # Decide whether to use log or linear scale
    x_axis_type = 'log' if log_x else 'linear'
    y_axis_type = 'log' if log_y else 'linear'

    # Update layout
    fig.update_layout(
        title="SPSP vs HP with Posting Rewards Bubble size",
        xaxis_title="HP",
        yaxis_title="SPSP",
        xaxis=dict(type=x_axis_type, tickformat=".0f"),
        yaxis=dict(type=y_axis_type, tickformat=".0f"),
        height=800,
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, theme="streamlit")
