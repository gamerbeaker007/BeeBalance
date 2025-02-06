import streamlit as st

from src.api import hive_engine

filter_symbols =[
    'DEC',
    'LEO',
    'SPS',
    'SPT',
]

def add_token_balances(row, placeholder):
    placeholder.text(f"Loading Hive Engine Balances for account: {row['name']}")

    # Specify tokens to filter

    hive_engine_balances = hive_engine.get_account_balances(row["name"], filter_symbols)

    # Pivot the balances DataFrame
    if hive_engine_balances.empty:
        # Return the original row if no balances are found
        return row

    pivot_df = hive_engine_balances.pivot(index="account", columns="symbol", values=["balance", "stake"])


    # Rename columns to "HE_{symbol}" for balance and "HE_stake_{symbol}" for stake
    pivot_df.columns = [f"HE_{col[1]}" if col[0] == "balance" else f"HE_stake_{col[1]}" for col in pivot_df.columns]

    # Convert the row to a single-row DataFrame for merging
    row_df = row.to_frame().T
    merged_row = row_df.merge(pivot_df, left_on="name", right_on="account", how="left")

    # Reorder the columns to ensure original columns are followed by the new ones
    for col in pivot_df.columns:
        if col not in row_df.columns:
            row_df[col] = pivot_df[col].iloc[0] if col in pivot_df.columns else 0

    return row_df.iloc[0]  # Return as a Series


def prepare_date(df):
    # Create a dynamic placeholder for loading text
    loading_placeholder = st.empty()

    with st.spinner('Loading data... Please wait.'):
        # Use a custom merge to ensure column order is preserved
        hive_engine_balances = df.apply(lambda row: add_token_balances(row, loading_placeholder), axis=1)

    loading_placeholder.empty()

    # Get the original columns
    orig = df.columns

    # Determine new columns from hive_engine_balances that are not already in df
    new = [col for col in hive_engine_balances.columns if col not in orig]

    # Reorder columns by placing new ones at the end
    return hive_engine_balances[list(orig) + new]


def get_page(df):
    st.title("Hive Engine Token Overview")
    df_he = df.filter(regex="HE_|name")
    df_he = df_he.rename(
        columns=lambda x: x.replace("HE_stake_", "").replace("HE_", "") + (" (staked)" if "stake" in x else ""))

    st.dataframe(df_he, hide_index=True)



