import logging
from datetime import datetime

import pandas as pd
import streamlit as st

from src.api import hive_sql, sps_validator
from src.graphs import ke_ratio_graph, ke_hp_graph, hp_spsp_graph, spsp_graph
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
        df = spl_balances.prepare_data(df)
    return df


def create_page(account_list, sps_balances=None):
    """Generate the results page with graphs and a table."""
    if ("last_input" not in st.session_state) or (set(st.session_state.last_input) != set(account_list)):
        result = analyse_accounts(account_list, sps_balances)
        st.session_state.last_input = account_list   # store the *list* itself
        st.session_state.last_result = result        # store the analysis output
    else:
        result = st.session_state.last_result

    if not result.empty:
        # Create tabs for each graph
        tab1, tab2, tab3, tab4 = st.tabs(["KE Ratio", "KE vs HP", "SPSP vs HP", "SPSP Distribution"])

        with tab1:
            with st.expander("KE Ratio Analysis Graph Explanation"):
                st.markdown("""
                    ### KE Ratio Analysis
                    This graph visualizes the relationship between KE Ratio and HP, helping """
                            """to analyze how efficiently users generate rewards relative to their staked HP.

                    #### Graph Components:
                    * X-axis → HP (Hive Power) (Staked influence in the ecosystem).
                    * Y-axis → KE Ratio (Indicator of reward efficiency).
                    * Bubble Size → Staked SPS (SPSP) (Users’ staked SPS holdings).

                    #### How to Read This Graph
                    * Larger bubbles indicate users who have staked more SPSP.
                    * Higher KE Ratio means the user receives more rewards relative to their HP.
                    * Users with low HP but high KE Ratio are generating higher returns on their staked HP.
                    * Users with high HP but lower KE Ratio may have lower reward efficiency despite their large stake.

                    #### Key Insights
                    * Are higher HP holders also have higher KE Ratios, or is it independent of HP?
                    * Does staking SPSP impact KE efficiency?
                    * Are there outliers with exceptionally high KE Ratios (extractors)?

                    """, unsafe_allow_html=True)
            ke_ratio_graph.add(result)

        with tab2:
            with st.expander("KE vs HP Graph Explanation"):
                st.markdown(
                    """
                    ### KE vs HP
                    This graph visualizes the relationship between KE Ratio, Total Rewards, """
                    """and HP, plotted against Ranked HP.

                    #### Graph Components:
                    * 🟠 Orange Markers → KE Ratio (Efficiency indicator).
                    * 🔵 Blue Markers → Total Rewards (Sum of Author & Curation Rewards).
                    * 🔴 Red Line → HP Values (Distribution of Staked HP).

                    #### What is Ranked HP?
                    * Ranked HP is a way of organizing HP values from highest to lowest.
                    * The highest HP holder is assigned rank 0, the second highest rank 1, and so on.
                    * This allows for better visualization of how KE Ratio and """
                    """rewards are distributed across HP holders.

                    #### How to Read This Graph
                    * The X-axis represents Ranked HP (lower ranks = more HP).
                    * The Y-axis (left) shows KE Ratio and Total Rewards.
                    * The Y-axis (right) shows the actual HP values.
                    * Comparing the markers helps identify whether higher HP leads to better KE efficiency and rewards.

                    This graph provides insights into how different HP levels impact staking efficiency and """
                    """rewards earned.

                    """, unsafe_allow_html=True)
            ke_hp_graph.add(result)

        with tab3:
            with st.expander("SPSP vs HP Graph Explanation"):
                st.markdown("""
                ### SPSP vs HP
                This graph visualizes how Staked SPS (SPSP) is distributed relative to HP holdings, """
                            """providing insights into the staking behavior of users.

                #### Graph Components:
                * X-axis → HP (Hive Power) (Users’ staked influence in the ecosystem).
                * Y-axis → SPSP (Staked SPS) (How much SPS is staked by each user).
                * Bubble Size → Posting Rewards (Total author rewards received).

                #### How to Read This Graph
                * Larger bubbles indicate users who have earned higher posting rewards.
                * The higher a point is on the graph, the more SPSP a user has staked.
                * The further right a point is, the more HP the user has.

                #### Key Insights
                * Does higher HP correlate with higher SPSP staking?
                * Are users with high posting rewards also staking SPSP?
                *Are there outliers—users with high SPSP but low HP?

                This graph helps understand whether strong HP holders are also staking SPSP and """
                            """how posting rewards relate to staking behavior.
                """, unsafe_allow_html=True)
            hp_spsp_graph.add(result)

        with tab4:
            with st.expander("SPSP Distribution Graph Explanation"):
                st.markdown("""
                ### SPSP Distribution
                This graph visualizes the distribution of Staked SPS (SPSP) among holders, """
                            """showing how SPSP is concentrated among the top accounts.

                #### Graph Components:
                * X-axis → Account Names (Ordered by SPSP holdings, from highest to lowest).
                * Y-axis → Amount of SPSP (Staked SPS balance for each account).

                #### How to Read This Graph
                * The left side of the graph represents the top SPSP holders.
                * The right side represents users with lower SPSP stakes.
                * Higher bars indicate accounts with larger SPSP stakes.
                * The gradual decline (or sharp drop-off) shows how SPSP is distributed among the ranked list.

                #### Key Insights
                * Is SPSP concentrated among a few large holders, or is it more evenly distributed?
                * How steep is the drop-off from the highest to the lowest SPSP holders?
                * Are there many mid-sized holders, or is there a large gap between top and bottom accounts?

                This graph helps in understanding the concentration of staking power and """
                            """whether SPSP is widely distributed or dominated by a few top holders.
                """)
            spsp_graph.add(result)
        st.dataframe(result, hide_index=True)


def handle_top_active_authors(posting_reward, comments, months):
    """Fetch and display the top active authors."""
    active_authors = hive_sql.get_active_hiver_users(posting_reward, comments, months)

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

    # Ensure session state key exists
    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = None

    account_limit = 100
    posting_reward = 500
    comments = 10
    months = 6
    sps_rich_list_limit = 2000

    get_buttons_sections(account_limit, posting_reward, sps_rich_list_limit)

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
            rich_list = sps_validator.get_rich_list_spsp(sps_rich_list_limit)
            create_page(rich_list.player.to_list(), rich_list)


def get_buttons_sections(account_limit, posting_reward, sps_rich_list_limit):
    col1, col2, col3, col4, _ = st.columns([1, 1, 1, 1, 4])
    with col1:
        if st.button(f"TOP {account_limit} HP holders with posting rewards >{posting_reward}"):
            st.session_state.button_clicked = "top authors"
    with col2:
        if st.button(f"Richlist Staked SPS Holders (top {sps_rich_list_limit})"):
            st.session_state.button_clicked = "rich list spsp"
    with col3:
        if st.session_state.get("authenticated"):
            if st.button("Top active authors"):
                st.session_state.button_clicked = "top active authors"
