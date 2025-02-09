import logging
from datetime import datetime

import pandas as pd

from src.static.static_values_enum import Edition

from src.api import spl

log = logging.getLogger("Collection Util")


def group_bcx(df):
    """
    Retrieve dataframe with grouped bxc or unbounded this reduces the time to indentify values
    e.g.:
    10 Baakjira's of 1 bcx  become 1 row with a count of 10
    if you have another Baakjira that is 11 bcx that will be other row with count 1,
     because that will reflect in a different price

    :param df: dataframe with card collection of a player
    :return: dataframe with grouped bxc or bcx_unbound with a count
    """
    return (df.groupby(['player', 'card_detail_id', 'xp', 'gold', 'edition', 'level', 'bcx', 'bcx_unbound']).size()
            .reset_index(name='count'))


def get_card_edition_value(account, list_prices_df, market_prices_df):
    log.info(f'get card values for account: {account}')
    player_collection = spl.get_player_collection_df(account)

    # Remove not fully unbouned form the list, because you cannot sell then they have no value for now!
    sellable_cards_df = player_collection[player_collection.apply(is_card_sellable, axis=1)].reset_index(drop=True)

    return_df = pd.DataFrame({'date': datetime.today().strftime('%Y-%m-%d'),
                              'account_name': account}, index=[0])

    if not sellable_cards_df.empty:
        # Group all bxc and unbounded
        sellable_cards_df = group_bcx(sellable_cards_df)

        for edition in Edition.__iter__():
            log.debug(f'processing edition: {edition}')
            temp_df = sellable_cards_df.loc[(sellable_cards_df.edition == edition.value)]
            collection = get_collection_value(temp_df, list_prices_df, market_prices_df)
            return_df[str(edition.name) + '_market_value'] = collection['market_value']
            return_df[str(edition.name) + '_list_value'] = collection['list_value']
            return_df[str(edition.name) + '_bcx'] = (player_collection[player_collection.edition ==
                                                                       edition.value].bcx.sum())
            return_df[str(edition.name) + '_number_of_cards'] = player_collection[player_collection.edition ==
                                                                                  edition.value].index.size

    return return_df


def is_card_sellable(collection_card):
    if collection_card.edition == Edition.gladius.value:
        return False  # Gladius cards are never be sellable
    elif collection_card.edition in [Edition.soulbound.value, Edition.soulboundrb.value]:
        return collection_card.bcx == collection_card.bcx_unbound  # Sellable when its fully unbounded
    else:
        return True  # All other editions are always sellable


def get_collection_value(df, list_prices_df, market_prices_df, new=False):
    total_list_value = 0
    total_market_value = 0

    for index, collection_card in df.iterrows():
        bcx = collection_card.bcx * collection_card['count']

        if is_card_sellable(collection_card):
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

    return {
        'list_value': total_list_value,
        'market_value': total_market_value,
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
