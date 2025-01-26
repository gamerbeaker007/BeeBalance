from src.util import collection_util, token_util, land_util


def get_portfolio_value(account_name, list_prices_df, market_prices_df, placeholder):

    placeholder.text(f"Determining card values for {account_name}")
    df1 = collection_util.get_card_edition_value(account_name, list_prices_df, market_prices_df)

    placeholder.text(f"Determining token values for {account_name}")
    df2 = token_util.get_token_value(account_name)
    total_df = df1.merge(df2)

    placeholder.text(f"Determining deeds value for {account_name}")
    df3 = land_util.get_deeds_value(account_name)
    total_df = total_df.merge(df3)

    placeholder.text(f"Determining DEC values for {account_name}")
    df4 = land_util.get_staked_dec_value(account_name)
    total_df = total_df.merge(df4)

    placeholder.text(f"Determining Land resource values for {account_name}")
    df5 = land_util.get_resources_value(account_name)
    total_df = total_df.merge(df5)

    return total_df
