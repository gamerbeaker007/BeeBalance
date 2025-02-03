import pandas as pd
import streamlit as st

from src.api import hive_sql
from src.graphs import custom_graph
from src.pages.custom_queries_subpages import presets_section
from src.pages.main_subpages import spl_balances

unauthorized_limit = 100
query_options = {
    "hp": ("hp_min", "hp_max", 0, 1000000000000),
    "reputation": ("reputation_min", "reputation_max", 0, 100),
    "posting_rewards": ("posting_rewards_min", "posting_rewards_max", 500, 1000000000000),
    "months": ("months", 6),
    "comments": ("comments", 10),
}

def get_page():
    st.title("Hive Selection Parameters")

    col1, _ = st.columns([1, 2])

    with col1:
        params = {}
        for label, key in query_options.items():
            if isinstance(key, tuple) and len(key) == 4:
                col_a, col_b = st.columns(2)
                with col_a:
                    params[key[0]] = st.number_input(f"{label} (Min)", value=key[2], step=1)
                with col_b:
                    params[key[1]] = st.number_input(f"{label} (Max)", value=key[3], step=1)
            elif isinstance(key, tuple) and len(key) == 2:
                params[key[0]] = st.number_input(label, value=key[1], step=1)
            else:
                params[key] = st.number_input(label, value=10, step=1)

    if "query_results" not in st.session_state:
        st.session_state.query_results = None
        st.session_state.params = None
    if "spl_query_results" not in st.session_state:
        st.session_state.spl_query_results = None
    if "selected_preset" not in st.session_state:
        st.session_state.selected_preset = None

    if st.button("Retrieve HIVE data"):
        st.session_state.spl_query_results = None
        df = hive_sql.get_hive_balances_params(params)
        st.session_state.query_results = df
        st.session_state.params = params
        st.rerun()

    if st.session_state.query_results is not None:
        df = st.session_state.query_results
        if st.button("Attach SPL data") and not df.empty:
            if not st.session_state.get("authenticated") and df.index.size > unauthorized_limit:
                st.warning(
                    f"You are not authorized to perform such large query, continuing with top {unauthorized_limit} rows")
                df = df.head(unauthorized_limit)
            df_spl = spl_balances.prepare_date(df)
            st.session_state.spl_query_results = df_spl
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

    df = pd.DataFrame()
    if st.session_state.query_results is not None:
        df = st.session_state.query_results
    if st.session_state.spl_query_results is not None:
        df = st.session_state.spl_query_results

    if not df.empty:
        st.subheader("📊 View Presets")

        preset_params =  presets_section.get_preset_section(df)
        selected_preset = st.session_state.selected_preset

        if selected_preset:
            st.write(f"Applying Preset: **{selected_preset}**")

        st.subheader("📊 Explore Data with Custom Plotly")
        custom_graph.get_page(df, **preset_params)
