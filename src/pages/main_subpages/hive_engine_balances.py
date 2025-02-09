import pandas as pd
import streamlit as st

from src.api import hive_engine

filter_symbols = [
    'DEC',
    'LEO',
    'SPS',
    'SPT',
]


def add_token_balances(row):
    """
    Fetch Hive Engine token balances for a given account.

    :param row: A row from a DataFrame.
    :return: A DataFrame containing the updated token balances.
    """
    hive_engine_balances = hive_engine.get_account_balances(row["name"], filter_symbols)

    if hive_engine_balances.empty:
        return pd.DataFrame([row])  # Ensure function always returns a DataFrame

    # Pivot balances and stakes
    pivot_df = hive_engine_balances.pivot(index="account", columns="symbol", values=["balance", "stake"])

    # Rename columns to "HE_{symbol}" for balance and "HE_stake_{symbol}" for stake
    pivot_df.columns = [f"HE_{col[1]}" if col[0] == "balance" else f"HE_stake_{col[1]}" for col in pivot_df.columns]
    pivot_df = pivot_df.reset_index()

    # Convert row to a DataFrame
    row_df = pd.DataFrame([row])

    # Merge Hive Engine balances with original row
    merged_row = row_df.merge(pivot_df, left_on="name", right_on="account", how="left").drop(columns=["account"])

    # Ensure all expected token columns exist
    for col in pivot_df.columns:
        if col not in merged_row.columns:
            merged_row[col] = 0  # Default missing tokens to 0

    return merged_row


def prepare_data(df):
    """
    Process all rows in df by fetching Hive Engine token balances.
    Uses a Streamlit status update for real-time user feedback.
    """

    empty_space = st.empty()
    with empty_space.container():
        with st.status('Loading Hive Engine Balances...', expanded=True) as status:
            processed_rows = []  # Store processed rows

            for index, row in df.iterrows():
                status.update(label=f"Fetching balances for: {row['name']}...", state="running")

                updated_row = add_token_balances(row)  # Process row
                processed_rows.append(updated_row)  # Append result

                status.update(label=f"Completed {row['name']}", state="complete")

            # Combine processed rows into a DataFrame
            result_df = pd.concat(processed_rows, ignore_index=True) if processed_rows else pd.DataFrame(
                columns=df.columns)

            # Get original columns
            orig = df.columns.tolist()

            # Identify new columns
            new_cols = [col for col in result_df.columns if col not in orig]

            # Ensure column order: original columns first, then new ones
            result = result_df[orig + new_cols]
    empty_space.empty()
    return result


def get_page(df):
    st.title("Hive Engine Token Overview")
    df_he = df.filter(regex="HE_|name")
    df_he = df_he.rename(
        columns=lambda x: x.replace("HE_stake_", "").replace("HE_", "") + (" (staked)" if "stake" in x else ""))

    st.dataframe(df_he, hide_index=True)
