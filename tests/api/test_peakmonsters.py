import pytest
import pandas as pd
import requests
from unittest.mock import patch, MagicMock

from src.api.peakmonsters import get_market_prices_df


@pytest.fixture
def mock_http_get():
    """Fixture to mock HTTP GET requests."""
    with patch("src.api.peakmonsters.http.get") as mock_get:
        yield mock_get


def test_get_market_prices_df_success(mock_http_get):
    """Test successful retrieval of market prices as a DataFrame."""
    mock_http_get.return_value.json.return_value = {
        "prices": [
            {"card_id": 1, "price": 10.5},
            {"card_id": 2, "price": 15.0}
        ]
    }

    df = get_market_prices_df()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert list(df.columns) == ["card_id", "price"]
    assert df.shape == (2, 2)
    assert df.iloc[0]["card_id"] == 1
    assert df.iloc[0]["price"] == 10.5


def test_get_market_prices_df_empty_response(mock_http_get):
    """Test handling when the API returns an empty list."""
    mock_http_get.return_value.json.return_value = {"prices": []}

    df = get_market_prices_df()

    assert isinstance(df, pd.DataFrame)
    assert df.empty  # Should return an empty DataFrame


def test_get_market_prices_df_no_prices_key(mock_http_get):
    """Test handling when the API response does not contain the 'prices' key."""
    mock_http_get.return_value.json.return_value = {}

    df = get_market_prices_df()

    assert isinstance(df, pd.DataFrame)
    assert df.empty  # Should return an empty DataFrame


def test_get_market_prices_df_invalid_json(mock_http_get):
    """Test handling when the API response is not valid JSON."""
    mock_http_get.return_value.json.side_effect = ValueError("Invalid JSON")

    df = get_market_prices_df()

    assert isinstance(df, pd.DataFrame)
    assert df.empty  # Should return an empty DataFrame


def test_get_market_prices_df_non_json_response(mock_http_get):
    """Test handling when the API response is an invalid non-JSON format (like HTML error page)."""
    mock_http_get.return_value.text = "<html><body>Error 500</body></html>"
    mock_http_get.return_value.json.side_effect = ValueError("No JSON")

    df = get_market_prices_df()

    assert isinstance(df, pd.DataFrame)
    assert df.empty  # Should return an empty DataFrame


def test_get_market_prices_df_connection_error(mock_http_get):
    """Test handling of connection errors."""
    mock_http_get.side_effect = requests.exceptions.ConnectionError("Failed to connect")

    df = get_market_prices_df()

    assert isinstance(df, pd.DataFrame)
    assert df.empty  # Should return an empty DataFrame

