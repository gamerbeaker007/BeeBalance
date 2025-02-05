import streamlit as st

def add_section(num_accounts, params):
    st.write(f"We found {num_accounts} accounts matching the specified criteria.")

    with st.expander("Query explanation", expanded=False):
        st.markdown(f"""
            #### This query helps identify active accounts ({num_accounts}) that have
            - Hive Power (HP) - Between {params["hp_min"]} and {params["hp_max"]}
            - Reputation Score - Between {params["reputation_min"]} and {params["reputation_max"]}
            - Posting Rewards - Between  {params["posting_rewards_min"]} and {params["posting_rewards_max"]}
            - Have been active in the last {params["months"]} months with minimal {params["comments"]} comments
        """)
