import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer

from src.api import hive_sql
from src.pages.main_subpages import spl_balances

query_options = {
    "HIVE": {
        "hp": ("hp_min", "hp_max", 0, 1000000000000),  # Min default 0, Max default 1000
        "reputation": ("reputation_min", "reputation_max", 0, 100),  # Default 25-75
        "posting_rewards": ("posting_rewards_min", "posting_rewards_max", 500, 1000000000000),  # Default 10-500
        "months": ("months", 6),  # Default 6
        "comments": ("comments", 10)
        # "Sort": ["ASC", "DECS"],
    },
}

# Function to cache the PyGWalker renderer
@st.cache_resource
def get_pyg_renderer(df):
    """Cache the PyGWalker renderer to avoid excessive memory usage."""
    return StreamlitRenderer(df, spec="./gw_config.json", spec_io_mode="rw")


def get_page():
    st.title("Hive Selection Parameters")

    col1, _ = st.columns([1, 2])

    with col1:
        params = {}
        for label, key in query_options['HIVE'].items():
            if isinstance(key, tuple) and len(key) == 4:  # Range parameters with defaults
                col_a, col_b = st.columns(2)
                with col_a:
                    params[key[0]] = st.number_input(f"{label} (Min)", value=key[2], step=1)
                with col_b:
                    params[key[1]] = st.number_input(f"{label} (Max)", value=key[3], step=1)
            elif isinstance(key, tuple) and len(key) == 2:  # Single-value parameters
                params[key[0]] = st.number_input(label, value=key[1], step=1)
            else:
                params[key] = st.number_input(label, value=10, step=1)  # Fallback default

    # Initialize session state for query results
    if "query_results" not in st.session_state:
        st.session_state.query_results = None
        st.session_state.params = None
    if "spl_query_results" not in st.session_state:
        st.session_state.spl_query_results = None

    col_hive, col_spl = st.columns([1,5])
    with col_hive:
        # Button to execute the query
        if st.button("Retrieve HIVE data"):
            st.session_state.spl_query_results = None # Clear SPL dataframe

            df = hive_sql.get_hive_balances_params(params)
            st.session_state.query_results = df  # Store hive data in session state
            st.session_state.params = params  # Store params as well
            st.rerun()
    with col_spl:
        # Display query results if available
        if st.session_state.query_results is not None:
            df = st.session_state.query_results
            if st.button("Attach SPL data") and not df.empty:
                df_spl = spl_balances.prepare_date(df)
                st.session_state.spl_query_results = df_spl  # Store attached spl data in session state
                st.dataframe(df_spl)
                st.rerun()

    if st.session_state.query_results is not None:
        df = st.session_state.query_results
        st.write(f"Accounts found: {df.index.size}, with params {params}")
        if st.session_state.spl_query_results is not None:
            df_spl = st.session_state.spl_query_results
            st.dataframe(df_spl)
        else:
            st.dataframe(df)

    if st.session_state.spl_query_results is not None:
        df = st.session_state.spl_query_results
        if not df.empty:
            st.subheader("📊 Explore Data with PyGWalker")
            renderer = get_pyg_renderer(df)
            renderer.explorer()
