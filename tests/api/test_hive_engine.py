from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
import streamlit as st

from src.api.hive_engine import (
    get_liquidity_positions,
    get_quantity,
    get_market_with_retry,
    get_account_balances,
    find_one_with_retry,
    find_with_retry,
    retry_api_call, get_cached_preferred_node,
)

# Sample mock data
MOCK_LIQUIDITY_POSITION = [{"shares": "100.5"}]
MOCK_POOL = [{"baseQuantity": "200.0", "quoteQuantity": "150.0", "totalShares": "500.0"}]
MOCK_MARKET = {"symbol": "TOKEN", "price": "1.23"}
MOCK_BALANCES = [{"account": "user", "symbol": "TOKEN", "balance": "50"}]


# Mock Api.find_one and Api.find functions
@pytest.fixture(autouse=True)
def mock_api():
    st.cache_data.clear()
    st.cache_resource.clear()

    """Reset global state before every test."""
    with patch("src.api.hive_engine.Api") as mock_api_class:
        mock_instance = MagicMock()
        mock_api_class.return_value = mock_instance
        mock_instance.find_one.return_value = None  # Default to no result
        mock_instance.find.return_value = []  # Default to empty list
        yield mock_instance


def test_get_liquidity_positions(mock_api):
    """Test get_liquidity_positions function."""
    mock_api.find_one.return_value = MOCK_LIQUIDITY_POSITION

    result = get_liquidity_positions("user", "TOKEN_PAIR")
    assert result == 100.5


def test_get_liquidity_positions_no_result(mock_api):
    """Test get_liquidity_positions when no data is returned."""
    mock_api.find_one.return_value = None

    result = get_liquidity_positions("user", "TOKEN_PAIR")
    assert result is None


def test_get_quantity(mock_api):
    """Test get_quantity function."""
    mock_api.find_one.return_value = MOCK_POOL

    base, quote, shares = get_quantity("TOKEN_PAIR")
    assert base == 200.0
    assert quote == 150.0
    assert shares == 500.0


def test_get_quantity_no_result(mock_api):
    """Test get_quantity when no data is returned."""
    mock_api.find_one.return_value = None

    base, quote, shares = get_quantity("TOKEN_PAIR")
    assert base == 0
    assert quote == 0
    assert shares == 0


def test_get_market_with_retry(mock_api):
    """Test get_market_with_retry function."""
    mock_api.find_one.return_value = [MOCK_MARKET]

    result = get_market_with_retry("TOKEN")
    assert result == MOCK_MARKET


def test_get_market_with_retry_no_result(mock_api):
    """Test get_market_with_retry when no data is returned."""
    mock_api.find_one.return_value = None

    result = get_market_with_retry("TOKEN")
    assert result is None


def test_get_account_balances(mock_api):
    """Test get_account_balances function."""
    mock_api.find.return_value = MOCK_BALANCES

    result = get_account_balances("user")
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert result.iloc[0]["symbol"] == "TOKEN"
    assert result.iloc[0]["balance"] == "50"


def test_get_account_balances_no_balances(mock_api):
    """Test get_account_balances when no balances exist."""
    mock_api.find.return_value = []

    result = get_account_balances("user")
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_get_account_balances_filter_symbols(mock_api):
    """Test get_account_balances with symbol filtering."""
    mock_api.find.return_value = MOCK_BALANCES

    result = get_account_balances("user", filter_symbols=["TOKEN"])
    assert not result.empty
    assert result.iloc[0]["symbol"] == "TOKEN"

    # Filtering non-existent symbol
    result = get_account_balances("user", filter_symbols=["NON_EXISTENT"])
    assert result.empty


def test_find_one_with_retry(mock_api):
    """Test find_one_with_retry function with successful request."""
    mock_api.find_one.return_value = [MOCK_MARKET]

    result = find_one_with_retry("market", "metrics", {"symbol": "TOKEN"})
    assert result == MOCK_MARKET


def test_find_with_retry(mock_api):
    """Test find_with_retry function with successful request."""
    mock_api.find.return_value = MOCK_BALANCES

    result = find_with_retry("tokens", "balances", {"account": "user"})
    assert result == MOCK_BALANCES


def test_retry_api_call_success(mock_api):
    """Test retry_api_call with a successful first attempt."""
    mock_api.find_one.return_value = MOCK_MARKET

    with patch("src.api.hive_engine.hive_engine_nodes", ["https://test.node"]):
        result = retry_api_call(lambda api, c, t, q: api.find_one(c, t, q), "market", "metrics", {"symbol": "TOKEN"})

    assert result == MOCK_MARKET


def test_retry_api_call_fail(mock_api):
    """Test retry_api_call function when all nodes fail."""
    mock_api.find_one.side_effect = Exception("Test failure")

    with patch("src.api.hive_engine.hive_engine_nodes", ["https://test.node"]):
        with pytest.raises(RuntimeError, match="Failed after 3 retries"):
            retry_api_call(lambda api, c, t, q: api.find_one(c, t, q), "market", "metrics", {"symbol": "TOKEN"})


def test_retry_api_call_switches_node():
    """Test retry_api_call when the first node fails and the second node succeeds."""

    # Mock the API behavior
    with patch("src.api.hive_engine.Api") as mock_api_class, patch("src.api.hive_engine.hive_engine_nodes",
                                                                   ["https://node1.com", "https://node2.com"]):
        mock_instance_1 = MagicMock()
        mock_instance_2 = MagicMock()

        # Simulate first node failing
        mock_instance_1.find_one.side_effect = Exception("Node 1 failure")

        # Simulate second node succeeding
        mock_instance_2.find_one.return_value = {"symbol": "TOKEN", "price": "1.23"}

        # Ensure Api() instance returns different mocks depending on URL
        def api_side_effect(url):
            if url == "https://node1.com":
                return mock_instance_1
            elif url == "https://node2.com":
                return mock_instance_2
            else:
                raise ValueError("Unexpected node URL")

        mock_api_class.side_effect = api_side_effect

        # Call retry_api_call
        result = retry_api_call(lambda api, c, t, q: api.find_one(c, t, q), "market", "metrics", {"symbol": "TOKEN"})

        # Verify that it switched nodes and returned the correct data
        assert result == {"symbol": "TOKEN", "price": "1.23"}

        assert mock_instance_1.find_one.call_count == 3

        # Ensure second node was used
        mock_instance_2.find_one.assert_called_once()

        # Ensure PREFERRED_NODE was updated
        assert get_cached_preferred_node() == {"preferred_node": "https://node2.com"}


if __name__ == "__main__":
    pytest.main()
