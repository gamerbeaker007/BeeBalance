import numpy as np
import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer

from src.api import hive_sql


def get_page():
    st.title("Custom Query Page")

    # You should cache your pygwalker renderer, if you don't want your memory to explode
    @st.cache_resource
    def get_pyg_renderer() -> "StreamlitRenderer":
        posting_reward = 10000
        number = 3000
        active_authors = hive_sql.get_top_posting_rewards(number, posting_reward)

        if active_authors.empty:
            st.warning("No active authors found.")
            return

        st.write(
            f"Accounts found: {active_authors.index.size}, with params "
            f"total posting_reward >{posting_reward}"
        )

        df = hive_sql.get_hive_balances(active_authors.name.tolist())

        st.write(
            f"Fetched data done"
        )

        df = df.sort_values(by="posting_rewards", ascending=False)
        m = df.loc[df['ke_ratio'] != np.inf, 'ke_ratio'].max()
        df['ke_ratio'] = df['ke_ratio'].replace(np.inf, m)

        return StreamlitRenderer(df, spec="./gw_config.json", spec_io_mode="rw")

    renderer = get_pyg_renderer()

    renderer.explorer()

