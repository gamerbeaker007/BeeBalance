import streamlit as st


def get_chart_settings(x=False, y=False, default_value_x=False, default_value_y=True, widget_suffix=""):
    log_x = x
    log_y = y

    with st.container(border=True):
        st.markdown("#### Graph Settings")
        if x:
            log_x = st.checkbox(
                "Log scale for X-axis?",
                value=default_value_x,
                key=f"log_x_{widget_suffix}"
            )
        if y:
            log_y = st.checkbox(
                "Log scale for Y-axis?",
                value=default_value_y,
                key=f"log_y_{widget_suffix}"
            )

    return log_x, log_y
