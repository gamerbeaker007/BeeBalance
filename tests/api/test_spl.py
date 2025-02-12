import pytest
import requests
import requests_mock
import streamlit as st

from src.api.spl import (
    fetch_api_data,
    get_player_collection_df,
    get_card_details,
    get_balances,
    get_prices,
    get_all_cards_for_sale_df,
    get_staked_dec_df,
    player_exist,
    get_player_details,
    get_spsp_richlist,
    API_URLS, get_deeds_collection, get_deeds_market, spl_get_pools, get_owned_resource_sum
)


@pytest.fixture
def mock_session():
    """Fixture to mock HTTP requests."""
    with requests_mock.Mocker() as m:
        st.cache_data.clear()
        yield m


def test_fetch_api_data_success(mock_session):
    """Test API request success and DataFrame conversion."""
    url = f"{API_URLS['base']}players/balances"
    mock_response = [{"player": "testuser", "token": "DEC", "balance": 1000}]

    mock_session.get(url, json=mock_response, status_code=200)

    df = fetch_api_data(url)
    assert not df.empty
    assert df.iloc[0]["player"] == "testuser"
    assert df.iloc[0]["token"] == "DEC"
    assert df.iloc[0]["balance"] == 1000


def test_fetch_api_data_error(mock_session):
    """Test API error response handling."""
    url = f"{API_URLS['base']}players/balances"
    mock_session.get(url, json={"error": "API Failure"}, status_code=400)

    df = fetch_api_data(url)
    assert df.empty


def test_fetch_api_data_timeout(mock_session):
    """Test request timeout handling."""
    url = f"{API_URLS['base']}players/balances"
    mock_session.get(url, exc=requests.exceptions.Timeout)

    df = fetch_api_data(url)
    assert df.empty


def test_get_player_collection_df(mock_session):
    """Test fetching and processing player collection data."""
    url = f"{API_URLS['base']}cards/collection/testuser"
    mock_response = {
        "cards": [
            {"player": "testuser", "uid": "1", "card_detail_id": 10, "collection_power": 500, "xp": 100, "gold": False,
             "edition": 3, "level": 2, "bcx": 1, "bcx_unbound": 1}
        ]
    }
    mock_session.get(url, json=mock_response, status_code=200)

    df = get_player_collection_df("testuser")
    assert not df.empty
    assert df.iloc[0]["player"] == "testuser"
    assert df.iloc[0]["card_detail_id"] == 10


def test_get_card_details(mock_session):
    """Test fetching card details."""
    url = f"{API_URLS['base']}cards/get_details"
    mock_response = [{"id": 1, "name": "Goblin"}]

    mock_session.get(url, json=mock_response, status_code=200)

    df = get_card_details()
    assert not df.empty
    assert "name" in df.columns
    assert df.index[0] == 1
    assert df.loc[1, "name"] == "Goblin"


def test_get_balances(mock_session):
    """Test fetching and filtering player balances."""
    url = f"{API_URLS['base']}players/balances"
    mock_response = [{"player": "testuser", "token": "DEC", "balance": 500}]

    mock_session.get(url, json=mock_response, status_code=200)

    df = get_balances("testuser", filter_tokens=["DEC", "SPS"])
    assert not df.empty
    assert "DEC" in df["token"].values
    assert "SPS" in df["token"].values  # Should be added as missing


def test_get_prices(mock_session):
    """Test fetching prices."""
    url = f"{API_URLS['prices']}prices"
    mock_response = {"DEC": 0.001, "SPS": 0.02}

    mock_session.get(url, json=mock_response, status_code=200)

    prices = get_prices()
    assert "DEC" in prices
    assert prices["DEC"] == 0.001


def test_get_all_cards_for_sale_df(mock_session):
    """Test fetching cards for sale."""
    url = f"{API_URLS['base']}market/for_sale_grouped"
    mock_response = [{"card_detail_id": 5, "price": 10.5}]

    mock_session.get(url, json=mock_response, status_code=200)

    df = get_all_cards_for_sale_df()
    assert not df.empty
    assert df.iloc[0]["card_detail_id"] == 5


def test_get_staked_dec_df(mock_session):
    """Test fetching staked DEC for land."""
    url = f"{API_URLS['land']}land/stake/decstaked"
    mock_response = {"data": [{"player": "testuser", "amount": 1000}]}

    mock_session.get(url, json=mock_response, status_code=200)

    df = get_staked_dec_df("testuser")
    assert not df.empty
    assert df.iloc[0]["amount"] == 1000


def test_player_exist(mock_session):
    """Test checking if a player exists."""
    url = f"{API_URLS['base']}players/balances"
    mock_response = [{"player": "testuser", "token": "DEC", "balance": 500}]

    mock_session.get(url, json=mock_response, status_code=200)

    assert player_exist("testuser") is True

    mock_session.get(url, json=[], status_code=200)
    assert player_exist("unknown") is False


def test_get_player_details(mock_session):
    """Test fetching player details."""
    url = f"{API_URLS['base']}players/details"
    mock_response = {"name": "testuser", "rating": 1500}

    mock_session.get(url, json=mock_response, status_code=200)

    df = get_player_details("testuser")
    assert not df.empty
    assert df.iloc[0]["name"] == "testuser"
    assert df.iloc[0]["rating"] == 1500


def test_get_spsp_richlist(mock_session):
    """Test fetching SPSP rich list."""
    url = f"{API_URLS['base']}players/richlist"
    mock_response = {"richlist": [{"player": "richguy", "balance": 1000000}]}

    mock_session.get(url, json=mock_response, status_code=200)

    df = get_spsp_richlist()
    assert not df.empty
    assert df.iloc[0]["player"] == "richguy"
    assert df.iloc[0]["balance"] == 1000000


def test_get_deeds_collection(mock_session):
    """Test fetching a player's land deeds collection."""
    username = "testuser"
    url = f"{API_URLS['land']}land/deeds"
    mock_response = {"data": {"deeds": [
        {"id": 1, "player": username, "rarity": "Legendary"},
        {"id": 2, "player": username, "rarity": "Epic"},
    ]}}

    mock_session.get(url, json=mock_response, status_code=200)

    df = get_deeds_collection(username)
    assert not df.empty
    assert len(df) == 2
    assert "id" in df.columns
    assert "rarity" in df.columns
    assert df.iloc[0]["rarity"] == "Legendary"


def test_get_deeds_market(mock_session):
    """Test fetching land deeds currently on the market."""
    url = f"{API_URLS['land']}land/deeds"
    mock_response = {"data": {"deeds": [
        {"id": 101, "price": 500, "rarity": "Common"},
        {"id": 102, "price": 1200, "rarity": "Rare"},
    ]}}

    mock_session.get(url, json=mock_response, status_code=200)

    df = get_deeds_market()
    assert not df.empty
    assert len(df) == 2
    assert "id" in df.columns
    assert "price" in df.columns
    assert df.iloc[0]["price"] == 500


def test_spl_get_pools(mock_session):
    """Test fetching liquidity pool data."""
    url = f"{API_URLS['land']}land/liquidity/pools"
    mock_response = {"data": [
        {"pool_id": "SPS-DEC", "liquidity": 10000},
        {"pool_id": "SPS-HIVE", "liquidity": 5000},
    ]}

    mock_session.get(url, json=mock_response, status_code=200)

    df = spl_get_pools()
    assert not df.empty
    assert len(df) == 2
    assert "pool_id" in df.columns
    assert "liquidity" in df.columns
    assert df.iloc[0]["pool_id"] == "SPS-DEC"


def test_get_owned_resource_sum(mock_session):
    """Test fetching and summing owned resources for a player."""
    account = "testuser"
    resource = "GRAIN"
    url = f"{API_URLS['land']}land/resources/owned"

    # Mocked response with different resource amounts
    mock_response = {"data": [
        {"player": account, "resource": resource, "amount": 50},
        {"player": account, "resource": resource, "amount": 30},
        {"player": account, "resource": resource, "amount": 20},
    ]}

    mock_session.get(url, json=mock_response, status_code=200)

    result = get_owned_resource_sum(account, resource)
    assert result == 100  # Sum of 50 + 30 + 20


def test_get_owned_resource_sum_empty(mock_session):
    """Test fetching owned resources when none exist."""
    account = "testuser"
    resource = "GRAIN"
    url = f"{API_URLS['land']}land/resources/owned"

    # Mocked response with an empty list
    mock_session.get(url, json={"data": []}, status_code=200)

    result = get_owned_resource_sum(account, resource)
    assert result == 0  # Should return 0 if no resources exist


def test_get_owned_resource_sum_missing_column(mock_session):
    """Test fetching owned resources when 'amount' column is missing."""
    account = "testuser"
    resource = "GRAIN"
    url = f"{API_URLS['land']}land/resources/owned"

    # Mocked response where 'amount' column is missing
    mock_response = {"data": [
        {"player": account, "resource": resource},  # No 'amount' field
    ]}

    mock_session.get(url, json=mock_response, status_code=200)

    result = get_owned_resource_sum(account, resource)
    assert result == 0  # Should return 0 when 'amount' column is missing


def test_get_owned_resource_sum_api_failure(mock_session):
    """Test API failure handling in owned resource fetching."""
    account = "testuser"
    resource = "GRAIN"
    url = f"{API_URLS['land']}land/resources/owned"

    # Simulating an API failure (500 error)
    mock_session.get(url, status_code=500)

    result = get_owned_resource_sum(account, resource)
    assert result == 0  # Should return 0 on API failure
