from unittest.mock import patch

import pandas as pd
import pytest
from requests.exceptions import RequestException

from src.api.sps_validator import get_rich_list_spsp


@pytest.fixture
def mock_http_get():
    """Mock requests.Session.get"""
    with patch("src.api.sps_validator.http.get") as mock_get:
        yield mock_get


def test_get_rich_list_spsp_success(mock_http_get):
    """Test API returns valid SPSP balance data."""
    mock_http_get.return_value.status_code = 200
    mock_http_get.return_value.json.return_value = {
        "balances": [
            {"account": "user1", "balance": "1000.0"},
            {"account": "user2", "balance": "750.5"}
        ]
    }

    df = get_rich_list_spsp(2)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) == 2
    assert list(df.columns) == ["account", "balance"]
    assert df.iloc[0]["account"] == "user1"
    assert df.iloc[0]["balance"] == "1000.0"


def test_get_rich_list_spsp_empty_response(mock_http_get):
    """Test API returns an empty list."""
    mock_http_get.return_value.status_code = 200
    mock_http_get.return_value.json.return_value = {"balances": []}

    df = get_rich_list_spsp(2)

    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_get_rich_list_spsp_api_error(mock_http_get):
    """Test API returns an error message."""
    mock_http_get.return_value.status_code = 400
    mock_http_get.return_value.json.return_value = {"error": "Invalid request"}

    df = get_rich_list_spsp(2)

    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_get_rich_list_spsp_invalid_json(mock_http_get):
    """Test API returns invalid JSON structure."""
    mock_http_get.return_value.status_code = 200
    mock_http_get.return_value.json.return_value = {"invalid_key": "unexpected"}

    df = get_rich_list_spsp(2)

    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_get_rich_list_spsp_network_failure(mock_http_get):
    """Test handling of a network failure (timeout)."""
    mock_http_get.side_effect = RequestException("Network error")

    df = get_rich_list_spsp(2)

    assert isinstance(df, pd.DataFrame)
    assert df.empty
