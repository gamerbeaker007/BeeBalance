import pytest
import streamlit as st
from unittest.mock import MagicMock

from src.pages.custom_queries_subpages.query_remark import add_section

# Sample test parameters
params = {
    "hp_min": 100,
    "hp_max": 5000,
    "reputation_min": 50,
    "reputation_max": 75,
    "posting_rewards_min": 10,
    "posting_rewards_max": 100,
    "months": 6,
    "posts": 1,
    "comments": 5
}


@pytest.fixture
def mock_streamlit(monkeypatch):
    """Mocks Streamlit functions used in add_section."""
    monkeypatch.setattr(st, "write", MagicMock())
    monkeypatch.setattr(st, "expander", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(st, "markdown", MagicMock())


def test_add_section(mock_streamlit):
    """Tests if add_section correctly calls Streamlit functions."""
    num_accounts = 25

    add_section(num_accounts, params)

    # Check if st.write was called with expected text
    st.write.assert_called_once_with(f"We found {num_accounts} accounts matching the specified criteria.")

    # Check if st.expander was used correctly
    st.expander.assert_called_once_with("Query explanation", expanded=False)

    # Check if st.markdown was called with the expected query explanation
    expected_markdown = f"""
            #### This query helps identify active accounts ({num_accounts}) that have
            - Hive Power (HP) - Between {params["hp_min"]} and {params["hp_max"]}
            - Reputation Score - Between {params["reputation_min"]} and {params["reputation_max"]}
            - Posting Rewards - Between  {params["posting_rewards_min"]} and {params["posting_rewards_max"]}
            - Have made more than {params["posts"]} posts in the last {params["months"]}
            - Have been active in the last {params["months"]} months with minimal {params["comments"]} comments
        """
    st.markdown.assert_called_once_with(expected_markdown)
