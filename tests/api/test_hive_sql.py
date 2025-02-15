import datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock

import pandas as pd
import pypyodbc
import pytest
import streamlit as st

from src.api.hive_sql import (
    find_valid_connection_string,
    get_cached_connection_string,
    convert_dataframe_types,
    execute_query_df,
    get_hive_per_mvest,
    get_hive_balances,
    reputation_to_score,
    score_to_reputation,
    get_hive_balances_params,
    get_commentators,
    get_top_posting_rewards,
    get_active_hiver_users, get_db_credentials,
)

TEST_SERVER = "mockserver.local"
TEST_DB = "TestDB"


@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame for testing."""
    data = {
        "name": ["Alice", "Bob"],
        "age": [25, 30],
        "balance": [Decimal("100.50"), Decimal("250.75")],
        "birthdate": [datetime.date(1998, 5, 21), datetime.date(1993, 8, 10)],
        "is_active": [True, False],
    }
    return pd.DataFrame(data)


@pytest.fixture(autouse=True)
def mock_pypyodbc():
    """Fixture to mock pypyodbc connection and cursor"""
    with patch("src.api.hive_sql.pypyodbc.connect") as mock_connect, \
         patch("src.api.hive_sql.SERVER", TEST_SERVER), \
         patch("src.api.hive_sql.DB", TEST_DB):

        # Mock the connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Define mock behavior
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Yield the mocks for use in tests
        yield mock_connect, mock_conn, mock_cursor


@pytest.fixture(autouse=True)
def mock_clear_cache():
    st.cache_data.clear()
    st.cache_resource.clear()


@pytest.fixture(autouse=True)
def mock_get_db_credentials():
    """Automatically mock get_db_credentials for every test."""
    with patch("src.api.hive_sql.get_db_credentials", return_value=("test_user", "test_pass")):
        yield


@pytest.fixture(autouse=True)
def mock_streamlit_secrets():
    """Mock Streamlit secrets to prevent FileNotFoundError during tests."""
    with patch("src.api.hive_sql.st.secrets",
               {"database": {"username": "test_user_secret", "password": "test_user_secret"}}):
        yield


def test_get_db_credentials():
    """Test retrieving database credentials from Streamlit secrets."""
    mock_secrets = {
        "database": {
            "username": "test_user",
            "password": "test_pass"
        }
    }

    with patch.object(st, "secrets", mock_secrets):
        username, password = get_db_credentials()

    assert username == "test_user"
    assert password == "test_pass"


def test_find_valid_connection_string(mock_pypyodbc):
    """Test if function correctly finds a valid connection string"""
    mock_connect, mock_conn, mock_cursor = mock_pypyodbc

    result = find_valid_connection_string()
    assert result is not None  # A valid connection string should be returned
    assert "Driver=ODBC Driver" in result  # Should contain driver information
    mock_connect.assert_called_once()  # Should have attempted a connection


def test_find_valid_connection_string_no_working_driver(mock_pypyodbc):
    """Test when no ODBC driver works, expecting None as return."""
    mock_connect, mock_conn, mock_cursor = mock_pypyodbc

    # Simulate all drivers failing by raising an exception
    mock_connect.side_effect = pypyodbc.Error(pypyodbc.SQL_ERROR, "Connection failed")

    # Execute function
    result = find_valid_connection_string()

    # Assertions
    assert result is None  # Function should return None when no driver works
    assert mock_connect.call_count == 2  # Should attempt both drivers


def test_find_valid_connection_string_odbc_driver_not_found(mock_pypyodbc):
    """Test when no ODBC driver is found, ensuring correct error handling."""
    mock_connect, mock_conn, mock_cursor = mock_pypyodbc

    # Simulate all drivers being unavailable by raising an exception
    mock_connect.side_effect = pypyodbc.Error(pypyodbc.SQL_ERROR, "No ODBC driver found")

    # Execute function
    result = find_valid_connection_string()

    # Assertions
    assert result is None  # Should return None when no drivers work
    assert mock_connect.call_count == 2  # Should try both drivers


@patch("src.api.hive_sql.find_valid_connection_string")
def test_get_cached_connection_string(mock_find_valid_connection_string):
    """Test if the connection string is cached"""
    mock_find_valid_connection_string.return_value = "mock_connection_string"
    result = get_cached_connection_string()
    assert result == "mock_connection_string"


def test_convert_dataframe_types(sample_dataframe):
    """Test DataFrame type conversion function"""
    cursor_description = [
        ("name", str),
        ("age", int),
        ("balance", Decimal),
        ("birthdate", datetime.date),
        ("is_active", bool),
    ]

    df = convert_dataframe_types(sample_dataframe, cursor_description)

    assert df["age"].dtype == "int64"
    assert df["balance"].dtype == "float64"
    assert df["birthdate"].dtype == "datetime64[ns]"
    assert df["is_active"].dtype == "bool"


@patch("src.api.hive_sql.execute_query_df")
def test_get_hive_per_mvest(mock_execute_query_df):
    """Test hive per mvest calculation"""
    mock_execute_query_df.return_value = pd.DataFrame(
        {"total_vesting_fund_hive": [10000], "total_vesting_shares": [2000000]}
    )
    result = get_hive_per_mvest()
    assert result == 5000.0


@patch("src.api.hive_sql.execute_query_df")
def test_get_hive_per_mvest_div_zero(mock_execute_query_df):
    """Test hive per mvest calculation devided """
    mock_execute_query_df.return_value = pd.DataFrame(
        {"total_vesting_fund_hive": [10000], "total_vesting_shares": [0]}
    )
    result = get_hive_per_mvest()
    assert result == 0


@patch("src.api.hive_sql.execute_query_df")
def test_get_hive_per_mvest_empty(mock_execute_query_df):
    """Test hive per mvest calculation devided """
    mock_execute_query_df.return_value = pd.DataFrame()
    result = get_hive_per_mvest()
    assert result == 0


@patch("src.api.hive_sql.execute_query_df")
def test_get_hive_balances(mock_execute_query_df):
    """Test get_hive_balances function"""
    mock_execute_query_df1 = pd.DataFrame(
        {"total_vesting_fund_hive": [10000], "total_vesting_shares": [2000000]}
    )

    mock_execute_query_df2 = pd.DataFrame(
        {
            "name": ["Alice"],
            "vesting_shares": [1000000],
            "reputation": [1000],
            "delegated_vesting_shares": [0],
            "received_vesting_shares": [0],
            "posting_rewards": [10],
            "curation_rewards": [20],
        }
    )

    mock_execute_query_df.side_effect = [mock_execute_query_df1, mock_execute_query_df2]

    result = get_hive_balances(["Alice"])
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "reputation_score" in result.columns
    assert "hp" in result.columns


@patch("src.api.hive_sql.execute_query_df")
def test_get_hive_balances_no_accounts(mock_execute_query_df):
    """Test get_hive_balances function"""
    result = get_hive_balances([])
    assert isinstance(result, pd.DataFrame)
    assert result.empty


@patch("src.api.hive_sql.execute_query_df")
def test_get_hive_balances_incorrect_instance(mock_execute_query_df):
    """Test get_hive_balances function"""
    with pytest.raises(ValueError, match="account_names must be a list"):
        get_hive_balances("not_a_list")  # Passing a string instead of a list

    with pytest.raises(ValueError, match="account_names must be a list"):
        get_hive_balances(123)  # Passing an integer


def test_reputation_to_score_scalar():
    """Test reputation_to_score with scalar (int and float) inputs."""
    assert reputation_to_score(1000000000) == 25.0
    assert reputation_to_score(181245992354454) == pytest.approx(72.32, rel=0.01)
    assert reputation_to_score(0) == 0


def test_reputation_to_score_series():
    """Test reputation_to_score with Pandas Series input."""
    input_series = pd.Series([1000000000, 181245992354454])
    result_series = reputation_to_score(input_series)

    assert result_series is not None
    assert result_series[0] == 25.0
    assert result_series[1] == pytest.approx(72.32, rel=0.01)


def test_score_to_reputation_scalar():
    """Test reputation_to_score with scalar (int and float) inputs."""
    assert score_to_reputation(25.0) == 1000000000
    assert score_to_reputation(72.32) == pytest.approx(181245992354454, rel=1)


def test_score_to_reputation_series():
    """Test reputation_to_score with Pandas Series input."""
    input_series = pd.Series([25.0, 72.32])
    result_series = score_to_reputation(input_series)
    assert result_series is not None
    assert result_series[0] == 1000000000
    assert result_series[1] == pytest.approx(181245992354454, rel=1)


@patch("src.api.hive_sql.execute_query_df")
def test_get_hive_balances_params(mock_execute_query_df):
    """Test fetching hive balances with filters"""

    mock_execute_query_df1 = pd.DataFrame(
        {"total_vesting_fund_hive": [10000], "total_vesting_shares": [2000000]}
    )

    mock_execute_query_df2 = pd.DataFrame(
        {
            "name": ["Alice"],
            "comment_count": [5],
            "vesting_shares": [1000000],
            "reputation": [1000],
            "delegated_vesting_shares": [0],
            "received_vesting_shares": [0],
            "posting_rewards": [10],
            "curation_rewards": [20],
        }
    )

    mock_execute_query_df.side_effect = [mock_execute_query_df1, mock_execute_query_df2]

    params = {
        "hp_min": 0,
        "hp_max": 100000,
        "reputation_min": 25,
        "reputation_max": 80,
        "posting_rewards_min": 10,
        "posting_rewards_max": 5000,
        "months": 3,
        "comments": 2,
    }

    result = get_hive_balances_params(params)
    assert not result.empty


@patch("src.api.hive_sql.execute_query_df")
def test_get_commentators(mock_execute_query_df):
    """Test fetching unique commentators"""
    mock_execute_query_df.return_value = pd.DataFrame({"author": ["Alice", "Bob"]})
    result = get_commentators(["post1", "post2"])
    assert result == ["Alice", "Bob"]


@patch("src.api.hive_sql.execute_query_df")
def test_get_top_posting_rewards(mock_execute_query_df):
    """Test fetching users with top posting rewards"""
    mock_execute_query_df.return_value = pd.DataFrame({"name": ["Alice"], "posting_rewards": [1000]})
    result = get_top_posting_rewards(10, 500)
    assert not result.empty
    assert result.iloc[0]["name"] == "Alice"


@patch("src.api.hive_sql.execute_query_df")
def test_get_active_hiver_users(mock_execute_query_df):
    """Test fetching active users"""
    mock_execute_query_df.return_value = pd.DataFrame(
        {"name": ["Alice"], "posting_rewards": [1000], "comment_count": [20]}
    )
    result = get_active_hiver_users(500, 10, 3)
    assert not result.empty
    assert result.iloc[0]["name"] == "Alice"


def test_execute_query_df(mock_pypyodbc):
    """Test execute_query_df with a valid query and parameters."""
    mock_connect, mock_conn, mock_cursor = mock_pypyodbc

    # Define expected column names
    mock_cursor.description = [("id", str), ("name", str), ("age", Decimal)]  # Simulating SQL column metadata

    # Define expected rows
    expected_data = [(1, "Alice", 25), (2, "Bob", 30)]
    mock_cursor.fetchall.return_value = expected_data

    # Execute function
    query = "SELECT id, name, age FROM users WHERE age > ?"
    params = (20,)  # Example query parameter
    result_df = execute_query_df(query, params)

    # Assertions
    assert isinstance(result_df, pd.DataFrame)
    assert list(result_df.columns) == ["id", "name", "age"]  # Check column names
    assert result_df.shape == (2, 3)  # Check DataFrame shape
    assert result_df.iloc[0]["name"] == "Alice"  # Check first row data
    assert result_df.iloc[1]["age"] == 30  # Check second row data

    # Ensure query execution happened
    mock_cursor.execute.assert_called_once_with(query, params)
    mock_cursor.fetchall.assert_called_once()


def test_execute_query_df_no_results(mock_pypyodbc):
    """Test execute_query_df when the query returns no results."""
    mock_connect, mock_conn, mock_cursor = mock_pypyodbc

    # Simulate empty result set
    mock_cursor.description = [("id",), ("name",), ("age",)]
    mock_cursor.fetchall.return_value = []

    # Execute function
    query = "SELECT id, name, age FROM users WHERE age > ?"
    params = (50,)  # Example query parameter
    result_df = execute_query_df(query, params)

    # Assertions
    assert isinstance(result_df, pd.DataFrame)
    assert list(result_df.columns) == ["id", "name", "age"]  # Should return correct columns
    assert result_df.empty  # DataFrame should be empty


def test_execute_query_db_error(mock_pypyodbc):
    """Test execute_query_df when the query returns no results."""
    mock_connect, mock_conn, mock_cursor = mock_pypyodbc

    mock_connect.side_effect = pypyodbc.Error(pypyodbc.SQL_ERROR, "DB Error")

    # Execute function
    with patch("src.api.hive_sql.get_cached_connection_string", return_value="test_conn"):
        result_df = execute_query_df("SELECT * FROM users")

    # Assertions
    assert result_df.empty is True


def test_execute_query_df_no_connection_string():
    """Test execute_query_df when no valid connection string is available."""
    with patch("src.api.hive_sql.get_cached_connection_string", return_value=None):
        result_df = execute_query_df("SELECT * FROM users")

    # Assertions
    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty  # Should return an empty Da
