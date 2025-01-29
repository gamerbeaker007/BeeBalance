import logging
from datetime import datetime

import pandas as pd

from src.static.static_values_enum import Edition

from src.api import spl

log = logging.getLogger("Collection Util")


def get_card_edition_value(account, list_prices_df, market_prices_df):
    log.info(f'get card values for account: {account}')
    player_collection = spl.get_player_collection_df(account)
    return_df = pd.DataFrame({'date': datetime.today().strftime('%Y-%m-%d'),
                              'account_name': account}, index=[0])
    if not player_collection.empty:
        for edition in Edition.__iter__():
            log.debug(f'processing edition: {edition}')
            temp_df = player_collection.loc[(player_collection.edition == edition.value)]
            collection = get_collection(temp_df, list_prices_df, market_prices_df)
            return_df[str(edition.name) + '_market_value'] = collection['market_value']
            return_df[str(edition.name) + '_list_value'] = collection['list_value']
            return_df[str(edition.name) + '_bcx'] = collection['bcx']
            return_df[str(edition.name) + '_number_of_cards'] = collection['number_of_cards']

    return return_df


def is_fully_unbound(collection_card):
    return collection_card.bcx == collection_card.bcx_unbound


def get_collection(df, list_prices_df, market_prices_df):
    total_list_value = 0
    total_market_value = 0
    total_bcx = 0
    number_of_cards = 0

    for index, collection_card in df.iterrows():
        number_of_cards += 1
        bcx = collection_card.bcx
        total_bcx += bcx

        if (collection_card['edition'] == Edition.soulbound.value or
                collection_card['edition'] == Edition.soulboundrb.value):
            # determine total unbound bcx to calculate value.
            # only fully unbound soulbound units will be used for value calculations
            if not is_fully_unbound(collection_card):
                bcx = 0

        if collection_card['edition'] == Edition.gladius.value:
            pass  # Has no value, not relevant for now
        else:
            list_price = get_list_price(collection_card, list_prices_df)
            if list_price:
                total_list_value += bcx * list_price

            market_price = get_market_price(collection_card, market_prices_df, list_price)
            if market_price:
                total_market_value += bcx * market_price

            if not list_price and not market_price:
                details = spl.get_card_details()
                log.warning("Card '" +
                            str(details.loc[collection_card['card_detail_id']]['name']) +
                            "' Not found on the markt (list/market) ignore for collection value")

    return {'list_value': total_list_value,
            'market_value': total_market_value,
            'bcx': total_bcx,
            'number_of_cards': number_of_cards
            }


def get_list_price(collection_card, list_prices_df):
    list_price_filtered = find_card(collection_card, list_prices_df)
    if not list_price_filtered.empty:
        return float(list_price_filtered.low_price_bcx.iloc[0])
    return None


def get_market_price(collection_card, market_prices_df, list_price):
    market_prices_filtered = find_card(collection_card, market_prices_df)
    if not market_prices_filtered.empty:
        market_price = float(market_prices_filtered.last_bcx_price.iloc[0])
        if list_price:
            return min(market_price, list_price)
        else:
            return market_price
    return None


def find_card(collection_card, market_df):
    mask = (market_df.card_detail_id == collection_card['card_detail_id']) \
           & (market_df.gold == collection_card['gold']) \
           & (market_df.edition == collection_card['edition'])
    filtered_df = market_df.loc[mask]
    return filtered_df
