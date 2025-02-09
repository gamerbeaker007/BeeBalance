import logging
from time import sleep

import pandas as pd
import streamlit as st
from hiveengine.api import Api

from src.api import hive_node

# hive-engine nodes see https://beacon.peakd.com/
hive_engine_nodes = [
    'https://api2.hive-engine.com/rpc/',
    # 'https://api.hive-engine.com/rpc/', # is preferred as firs attempt
    'https://engine.rishipanthee.com/',  # is preferred
    'https://herpc.dtools.dev/',
    'https://engine.deathwing.me/',
    'https://ha.herpc.dtools.dev/',
    'https://api.primersion.com/',
    'https://herpc.kanibot.com/',
    'https://he.sourov.dev/',
    'https://herpc.actifit.io/',
    'https://ctpmain.com/',
    'https://he.ausbit.dev/']


@st.cache_data(ttl="1h")
def get_liquidity_positions(account, token_pair):
    query = {"account": account, "tokenPair": token_pair}
    result = find_one_with_retry('marketpools', 'liquidityPositions', query)

    if len(result) > 0 and result[0]:
        return float(result[0]['shares'])
    else:
        # no liquidity pool found
        return None


@st.cache_data(ttl="1h")
def get_quantity(token_pair):
    query = {"tokenPair": token_pair}
    result = find_one_with_retry('marketpools', 'pools', query)

    return float(result[0]['baseQuantity']), \
        float(result[0]['quoteQuantity']), \
        float(result[0]['totalShares'])


def find_one_with_retry(contract_name, table_name, query):
    result = None
    success = False
    iterations = 3

    #  Might consider special handling when a RPCErrorDoRetry is raised

    # First try with preferred node.
    try:
        api = Api(url=hive_node.PREFERRED_NODE)
        result = api.find_one(contract_name=contract_name, table_name=table_name, query=query)
        success = True
    except Exception as e:
        logging.warning('find_one_with_retry (' + type(e).__name__ + ') preferred  node: ' + hive_node.PREFERRED_NODE
                        + '. Continue try on other nodes')
        for iter_ in range(iterations):
            for node in hive_engine_nodes:
                # noinspection PyBroadException
                try:
                    api = Api(url=node)
                    result = api.find_one(contract_name=contract_name, table_name=table_name, query=query)
                    success = True
                    hive_node.PREFERRED_NODE = node
                    break
                except Exception as e:
                    logging.warning('find_one_with_retry (' + type(e).__name__ + ') on node: ' + str(
                        node) + '. Continue retry on next node')
                    sleep(1)

            if success:
                break

    if not success:
        raise Exception(
            'find_one_with_retry failed 5 times over all nodes'
            + ' contract:' + str(contract_name)
            + ' table_name:' + str(table_name)
            + ' query:' + str(query)
            + ' stop update .....'
        )
    return result


def find_with_retry(contract_name, table_name, query):
    result = None
    success = False
    iterations = 3

    #  Might consider special handling when a RPCErrorDoRetry is raised

    # First try with preferred node.
    try:
        api = Api(url=hive_node.PREFERRED_NODE)
        result = api.find(contract_name=contract_name, table_name=table_name, query=query)
        success = True
    except Exception as e:
        logging.warning('find_one_with_retry (' + type(e).__name__ + ') preferred  node: ' + hive_node.PREFERRED_NODE
                        + '. Continue try on other nodes')
        for iter_ in range(iterations):
            for node in hive_engine_nodes:
                # noinspection PyBroadException
                try:
                    api = Api(url=node)
                    result = api.find_one(contract_name=contract_name, table_name=table_name, query=query)
                    success = True
                    hive_node.PREFERRED_NODE = node
                    break
                except Exception as e:
                    logging.warning('find_one_with_retry (' + type(e).__name__ + ') on node: ' + str(
                        node) + '. Continue retry on next node')
                    sleep(1)

            if success:
                break

    if not success:
        raise Exception(
            'find_one_with_retry failed 5 times over all nodes'
            + ' contract:' + str(contract_name)
            + ' table_name:' + str(table_name)
            + ' query:' + str(query)
            + ' stop update .....'
        )
    return result


@st.cache_data(ttl="1h")
def get_market_with_retry(token):
    market = find_one_with_retry('market', 'metrics', {'symbol': token})
    if market:
        return market[0]
    else:
        return None


@st.cache_data(ttl="1h")
def get_account_balances(account_name, filter_symbols=None):
    balances = find_with_retry('tokens', 'balances', {"account": account_name})
    df = pd.DataFrame(balances)
    if not df.empty and filter_symbols:
        return df[df.symbol.isin(filter_symbols)]
    else:
        return df
