from src.util import collection_util, token_util, land_util


def get_portfolio_value(account_name, list_prices_df, market_prices_df):
    """
    Fetch portfolio values for a given account without UI elements.
    """
    # Fetch individual components
    df1 = collection_util.get_card_edition_value(account_name, list_prices_df, market_prices_df)
    df2 = token_util.get_token_value(account_name)
    df3 = land_util.get_deeds_value(account_name)
    df4 = land_util.get_staked_dec_value(account_name)
    df5 = land_util.get_resources_value(account_name)

    # Merge dataframes
    total_df = df1.merge(df2, how="outer").merge(df3, how="outer").merge(df4, how="outer").merge(df5, how="outer")

    return total_df
