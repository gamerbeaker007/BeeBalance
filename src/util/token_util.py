from datetime import datetime

import pandas as pd

from src.api import spl, hive_engine
from src.pages.main_subpages.spl_balances import token_columns


def calculate_prices(df, balance_df, hive_in_dollar):
    for index, row in balance_df.iterrows():

        token = row.token
        balance = row.balance
        if token == 'SPSP':
            token_market = hive_engine.get_market_with_retry('SPS')
        elif token == 'DICE':
            token_market = hive_engine.get_market_with_retry('SLDICE')
        elif token == 'VOUCHER-G':
            token_market = hive_engine.get_market_with_retry('VOUCHER')
        elif token == 'CREDITS':
            df[str(token.lower()) + '_qty'] = balance
            df[str(token.lower()) + '_value'] = round(balance * 0.001, 2)
            token_market = None
        else:
            token_market = hive_engine.get_market_with_retry(token)

        if token_market:
            quantity = balance
            hive_value = float(token_market["highestBid"])
            value = round(hive_value * hive_in_dollar * quantity, 2)
            if quantity:
                df[str(token.lower()) + '_qty'] = quantity
                df[str(token.lower()) + '_value'] = value

    return df


def get_token_value(account):
    hive_in_dollar = float(spl.get_prices()['hive'])
    spl_balances = spl.get_balances(account, filter_tokens=token_columns)[['token', 'balance']]
    df = pd.DataFrame({'date': datetime.today().strftime('%Y-%m-%d'),
                       'account_name': account},
                      index=[0])
    df = calculate_prices(df, spl_balances, hive_in_dollar)
    df = get_liquidity_pool(df, account, hive_in_dollar)
    return df


def get_dec_last_price():
    df = pd.DataFrame(hive_engine.get_market_with_retry('DEC'), index=[0])
    return float(df.lastPrice.iloc[0])


def get_liquidity_pool(df, account, hive_in_dollar):
    token_pair = "DEC:SPS"
    my_shares = hive_engine.get_liquidity_positions(account, token_pair)
    dec = 0
    sps = 0
    value_usd = 0
    if my_shares:
        dec_qty, sps_qty, total_shares = hive_engine.get_quantity(token_pair)
        share_pct = my_shares / total_shares
        dec = share_pct * dec_qty
        sps = share_pct * sps_qty

        dec_last_price = get_dec_last_price()
        value_hive = dec_last_price * dec
        value_hive = value_hive * 2  # liquidity pool contain equal amount of dec and sps therefor times 2
        value_usd = value_hive * hive_in_dollar
    df['liq_pool_dec_qty'] = dec
    df['liq_pool_sps_qty'] = sps
    df['liq_pool_value'] = value_usd

    return df
