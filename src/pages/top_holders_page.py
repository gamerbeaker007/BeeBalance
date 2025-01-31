import logging
from datetime import datetime

import pandas as pd
import streamlit as st

from src.api import hive_sql, spl
from src.graphs import graphs
from src.pages.main_subpages import hivesql_balances, spl_balances

log = logging.getLogger("Top Holders")


def analyse_accounts(accounts, sps_balances=None):
    df = hivesql_balances.prepare_data(accounts)

    # Add date column
    df.insert(0, "date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if isinstance(sps_balances, pd.DataFrame):
        sps_balances = sps_balances.rename(columns={"balance": "SPSP"})
        df = df.merge(sps_balances, left_on="name", right_on="player", how="left")
        df = df.drop(['player'], axis=1)
    else:
        df = spl_balances.prepare_date(df)
    return df


def create_page(account_list, sps_balances=None):
    """Generate the results page with graphs and a table."""
    result = analyse_accounts(account_list, sps_balances)

    if not result.empty:
        # Create tabs for each graph
        tab1, tab2, tab3, tab4 = st.tabs(["KE Ratio", "KE vs HP", "SPSP vs HP", "SPSP Distribution"])

        with tab1:
            st.write("### KE Ratio Analysis")
            st.write("This graph shows the relationship between KE Ratio and other variables. "
                     "Higher KE ratios indicate more staking efficiency in the ecosystem.")
            graphs.add_ke_ratio_graph(result)

        with tab2:
            st.write("### KE vs HP")
            st.write(
                "This graph plots KE Ratio against HP, allowing us to see how staking power influences KE efficiency.")
            graphs.add_ke_hp_graph(result)

        with tab3:
            st.write("### SPSP vs HP")
            st.write("This graph shows the distribution of Staked SPS (SPSP) relative to HP holdings.")
            graphs.add_spsp_vs_hp_graph(result)

        with tab4:
            st.write("### SPSP Distribution")
            st.write("This graph visualizes the overall distribution of Staked SPS (SPSP) among holders.")
            graphs.add_spsp_graph(result)
        st.dataframe(result, hide_index=True)


def handle_top_active_authors(posting_reward, comments, months):
    """Fetch and display the top active authors."""
    active_authors = hive_sql.get_active_hivers(posting_reward, comments, months)

    if active_authors.empty:
        st.warning("No active authors found.")
        return

    st.write(
        f"Accounts found: {active_authors.index.size}, with params "
        f"total posting_reward >{posting_reward}, comments >{comments}, months -{months}"
    )

    active_authors = active_authors.sort_values(by="posting_rewards", ascending=False)
    st.dataframe(active_authors, hide_index=True)

    st.warning("TODO: Scaled down to 1000 for now")
    create_page(active_authors.head(1000).name.to_list())


def get_page():
    """Main Streamlit page layout and interaction."""
    col1, col2, col3, col4, _ = st.columns([1, 1, 1, 1, 4])

    # Ensure session state key exists
    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = None

    account_limit = 100
    posting_reward = 500
    comments = 10
    months = 6

    with col1:
        if st.button(f"TOP {account_limit} HP holders with posting rewards >{posting_reward}"):
            st.session_state.button_clicked = "top authors"

    with col2:
        if st.button("Richlist Staked SPS Holders"):
            st.session_state.button_clicked = "rich list spsp"

    with col3:
        if st.session_state.get("authenticated"):
            if st.button("Top active authors"):
                st.session_state.button_clicked = "top active authors"

    button_clicked = st.session_state.get("button_clicked")
    if not button_clicked:
        return

    log.info(f"Analysing top holders: {button_clicked}")

    with st.spinner("Fetching data..."):
        if button_clicked == "top active authors":
            if st.session_state.get("authenticated"):
                handle_top_active_authors(posting_reward, comments, months)

        elif button_clicked == "top authors":
            top_authors = hive_sql.get_top_posting_rewards(account_limit, posting_reward)
            create_page(top_authors.name.to_list())

        elif button_clicked == "rich list spsp":
            rich_list = spl.get_spsp_richlist()
            create_page(rich_list.player.to_list(), rich_list)
