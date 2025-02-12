import logging
from time import sleep

import pandas as pd
import streamlit as st
from hiveengine.api import Api


# Hive Engine nodes (see https://beacon.peakd.com/)
hive_engine_nodes = [
    "https://api2.hive-engine.com/rpc/",
    "https://engine.rishipanthee.com/",
    "https://herpc.dtools.dev/",
    "https://engine.deathwing.me/",
    "https://enginerpc.com/",
    "https://api.primersion.com/",
    "https://herpc.kanibot.com/",
    "https://he.sourov.dev/",
    "https://herpc.actifit.io/",
    "https://ctpmain.com/",
    "https://he.ausbit.dev/",
]


@st.cache_resource
def get_cached_preferred_node():
    """Cache and return the preferred node for the application runtime."""
    return {"preferred_node": hive_engine_nodes[0]}  # Default to the first node


def set_preferred_node(node):
    """Update the preferred node in the cached resource."""
    cache = get_cached_preferred_node()
    cache["preferred_node"] = node  # Update the stored node
    return cache  # Ensure the cache gets updated in Streamlit


def retry_api_call(call_func, contract_name, table_name, query, attempts=3):
    """Handles API calls with retries across multiple Hive Engine nodes."""

    # Retrieve the preferred node
    cached_data = get_cached_preferred_node()
    preferred_node = cached_data["preferred_node"]

    # Ensure the preferred node is first in the list
    nodes_to_try = [preferred_node] + [
        node for node in hive_engine_nodes if node != preferred_node
    ]

    for node in nodes_to_try:
        for attempt in range(attempts):
            try:
                api = Api(url=node)
                result = call_func(api, contract_name, table_name, query)

                if node != preferred_node:
                    set_preferred_node(node)  # Store new successful node as preferred

                return result

            except Exception as e:
                logging.warning(
                    f"[Attempt {attempt + 1}] {type(e).__name__} on node {node}. Retrying..."
                )
                sleep(0.1)

    raise RuntimeError(
        f"Failed after {attempts} retries for contract: {contract_name}, table: {table_name}, query: {query}"
    )


def find_one_with_retry(contract_name, table_name, query):
    return retry_api_call(lambda api, c, t, q: api.find_one(c, t, q), contract_name, table_name, query)


def find_with_retry(contract_name, table_name, query):
    return retry_api_call(lambda api, c, t, q: api.find(c, t, q), contract_name, table_name, query)


@st.cache_data(ttl="1h")
def get_liquidity_positions(account, token_pair):
    query = {"account": account, "tokenPair": token_pair}
    result = find_one_with_retry("marketpools", "liquidityPositions", query)

    if result:
        return float(result.get("shares", 0))
    return None


@st.cache_data(ttl="1h")
def get_quantity(token_pair):
    query = {"tokenPair": token_pair}
    result = find_one_with_retry("marketpools", "pools", query)

    if result:
        return (
            float(result.get("baseQuantity", 0)),
            float(result.get("quoteQuantity", 0)),
            float(result.get("totalShares", 0)),
        )
    return 0, 0, 0


@st.cache_data(ttl="1h")
def get_market_with_retry(token):
    market = find_one_with_retry("market", "metrics", {"symbol": token})
    return market if market else None


@st.cache_data(ttl="1h")
def get_account_balances(account_name, filter_symbols=None):
    balances = find_with_retry("tokens", "balances", {"account": account_name})
    df = pd.DataFrame(balances)

    if df.empty:
        return df  # Return empty DataFrame if no balances

    if filter_symbols:
        return df[df["symbol"].isin(filter_symbols)] if "symbol" in df else df

    return df
