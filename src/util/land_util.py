import logging
from datetime import datetime

import pandas as pd

from src.api import spl, hive_engine
from src.static.static_values_enum import LAND_SWAP_FEE


def filter_items(deed, df, param):
    if deed[param]:
        # return matching values
        return df.loc[(df[param] == deed[param])]
    else:
        # return value either None or ""
        return df[(df[param].isnull()) | (df[param] == "")]


def get_deeds_value(account_name):
    collection = spl.get_deeds_collection(account_name)
    market_df = pd.DataFrame(spl.get_deeds_market())
    deeds_price_found = 0
    deeds_owned = 0
    deeds_total = 0.0
    for index, deed in collection.iterrows():
        deeds_owned += 1
        filter_types = ["rarity", 'plot_status', 'magic_type', 'deed_type']
        df = market_df
        missing_types = []
        for filter_type in filter_types:
            temp = filter_items(deed, df, filter_type)
            if not temp.empty:
                df = temp
            else:
                missing_types.append(filter_type)
        if missing_types:
            logging.warning("Not a perfect match found missing filters: " + str(missing_types))
            logging.warning("Was looking for: \n"
                            + "\n".join([str(x) + ": " + str(deed[x]) for x in filter_types]))
            logging.warning("Current estimated best value now: "
                            + str(df.astype({'listing_price': 'float'}).listing_price.min()))
        listing_price = df.astype({'listing_price': 'float'}).listing_price.min()
        deeds_price_found += 1

        deeds_total += listing_price

    return pd.DataFrame({'date': datetime.today().strftime('%Y-%m-%d'),
                         'account_name': account_name,
                         'deeds_qty': deeds_owned,
                         'deeds_price_found_qty': deeds_price_found,
                         'deeds_value': deeds_total}, index=[0])


def get_staked_dec_value(account_name):
    dec_staked_value = 0
    dec_staked_qty = 0

    dec_staked_df = spl.get_staked_dec_df(account_name)
    if not dec_staked_df.empty:
        dec_staked_qty = dec_staked_df.amount.sum()
        token_market = hive_engine.get_market_with_retry('DEC')
        hive_in_dollar = float(spl.get_prices()['hive'])

        if token_market:
            hive_value = float(token_market["highestBid"])
            dec_staked_value = round(hive_value * hive_in_dollar * dec_staked_qty, 2)

    return pd.DataFrame({'date': datetime.today().strftime('%Y-%m-%d'),
                         'account_name': account_name,
                         'dec_staked_qty': dec_staked_qty,
                         'dec_staked_value': dec_staked_value}, index=[0])


def get_resources_value(account):
    dec_value = spl.get_prices()['dec']
    pools = spl.spl_get_pools()
    total_value = 0
    if not pools.empty:
        for resource in pools.token_symbol.tolist():
            pool = pools.loc[pools.token_symbol == resource].iloc[0]
            qty = spl.get_owned_resource_sum(account, resource)
            if qty:
                value_dec = qty * pool.resource_price * LAND_SWAP_FEE
                total_value += value_dec * dec_value

    return pd.DataFrame({'date': [datetime.today().strftime('%Y-%m-%d')],
                         'account_name': [account],
                         'land_resources_value': [total_value]})
