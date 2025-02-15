import datetime
import logging
from contextlib import closing
from decimal import Decimal

import numpy as np
import pandas as pd
import pypyodbc
import streamlit as st

log = logging.getLogger("Hive SQL")

SERVER="vip.hivesql.io"
DB="DBHive"

def get_db_credentials():
    """Retrieve database credentials from Streamlit secrets."""
    return st.secrets["database"]["username"], st.secrets["database"]["password"]


def find_valid_connection_string():
    """Finds a valid SQL connection string by testing available ODBC drivers."""
    db_username, db_password = get_db_credentials()
    driver_names = [f"ODBC Driver {x} for SQL Server" for x in [17, 18]]
    for driver_name in driver_names:
        conn_str = (
            f"Driver={driver_name};"
            f"Server={SERVER};"
            f"Database={DB};"
            f"UID={db_username};"
            f"PWD={db_password};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=yes"
        )
        try:
            with closing(pypyodbc.connect(conn_str)) as connection, closing(connection.cursor()):
                log.info(f"Connected successfully using {driver_name}")
                return conn_str
        except pypyodbc.Error as e:
            log.warning(f"Failed with {driver_name}: {e}")
    log.error("No working ODBC driver found.")
    return None


@st.cache_resource
def get_cached_connection_string():
    """Caches the SQL connection string to avoid redundant computations."""
    return find_valid_connection_string()


def convert_dataframe_types(df, cursor_descriptions):
    """
    Converts DataFrame columns to appropriate types based on SQL column types.

    Parameters:
    - df (pd.DataFrame): The DataFrame to be converted.
    - cursor_description (list): The cursor.description containing column names and types.

    Returns:
    - pd.DataFrame: DataFrame with converted column types.
    """
    type_map = {
        str: "string",
        int: "Int64",  # Pandas nullable integer type
        float: "float64",
        bool: "boolean",  # Pandas nullable boolean type
        Decimal: "float64",  # Convert Decimal to float for Pandas compatibility
        datetime.date: "datetime64[ns]",  # Convert to Pandas datetime format
        datetime.datetime: "datetime64[ns]",
    }

    for column_name, slq_type, *rest in cursor_descriptions:
        sample_value = df[column_name].dropna().iloc[0] if not df[column_name].dropna().empty else None
        python_type = type(sample_value)

        if python_type in type_map:
            df[column_name] = df[column_name].astype(type_map[python_type])

    return df


def execute_query_df(query, params=None):
    """
    Executes a SQL query with optional parameters and returns a Pandas DataFrame.

    Parameters:
    - query: str, the SQL query to execute.
    - params: list or tuple, optional, the parameters for the query.

    Returns:
    - pd.DataFrame with query results or an empty DataFrame on failure/no results.
    """
    conn_string = get_cached_connection_string()
    if conn_string is None:
        log.error("No valid database connection string found.")
        return pd.DataFrame()

    try:
        with closing(pypyodbc.connect(conn_string)) as connection, closing(connection.cursor()) as cursor:
            cursor.execute(query, params or ())
            columns = [column[0] for column in cursor.description] if cursor.description else []
            rows = cursor.fetchall()

            if not rows:
                return pd.DataFrame(columns=columns)

            # Convert rows to dict with proper types
            # Create DataFrame first, before type conversion
            df = pd.DataFrame(rows, columns=columns)

            # Convert DataFrame columns to correct types
            df = convert_dataframe_types(df, cursor.description)

            return df
    except pypyodbc.Error as e:
        log.error(f"Database error: {e}")
        return pd.DataFrame()


@st.cache_data(ttl="24h")
def get_hive_per_mvest():
    result = execute_query_df("SELECT total_vesting_fund_hive, total_vesting_shares FROM DynamicGlobalProperties")
    if not result.empty:
        total_vesting_fund_hive, total_vesting_shares = result.iloc[0]
        if total_vesting_shares == 0:
            log.warning("Total vesting shares is zero, returning 0.")
            return 0
        return total_vesting_fund_hive / (total_vesting_shares / 1e6)
    return 0


def batch_list(lst, batch_size):
    yield from (lst[i:i + batch_size] for i in range(0, len(lst), batch_size))


def get_hive_balances(account_names):
    if not account_names:
        log.warning("No account names provided, returning empty DataFrame.")
        return pd.DataFrame()

    if not isinstance(account_names, list):
        raise ValueError("account_names must be a list")

    hive_per_mvest = get_hive_per_mvest()
    df = pd.DataFrame()

    for batch in batch_list(account_names, batch_size=500):
        placeholders = ', '.join(['?'] * len(batch))
        query = f"""
        SELECT
            name,
            created,
            balance AS hive,
            savings_balance AS hive_savings,
            hbd_balance AS hbd,
            savings_hbd_balance AS hbd_savings,
            reputation AS reputation,
            vesting_shares AS vesting_shares,
            delegated_vesting_shares AS delegated_vesting_shares,
            received_vesting_shares AS received_vesting_shares,
            curation_rewards / 1000.0 AS curation_rewards,
            posting_rewards / 1000.0 AS posting_rewards
        FROM accounts WHERE name IN ({placeholders})
        """

        batch_result = execute_query_df(query, batch)
        df = pd.concat([df, batch_result]) if not batch_result.empty else df

    if not df.empty:
        df["reputation_score"] = reputation_to_score(df["reputation"])
        conversion_factor = hive_per_mvest / 1e6
        df["hp"] = conversion_factor * df["vesting_shares"]
        df["hp delegated"] = conversion_factor * df["delegated_vesting_shares"]
        df["hp received"] = conversion_factor * df["received_vesting_shares"]
        df["ke_ratio"] = np.where(df["hp"] > 0, (df["curation_rewards"] + df["posting_rewards"]) / df["hp"], 0)

    return df


def reputation_to_score(reputation):
    """
    Converts raw reputation to reputation score.

    Parameters:
    - reputation (float, int, or Pandas Series): The reputation value(s) to be converted.

    Returns:
    - Reputation score (float if input is scalar, Pandas Series if input is a Series)
    """
    if isinstance(reputation, (int, float)):  # Scalar case
        return ((np.log10(max(reputation, 1e-9)) - 9) * 9) + 25 if reputation > 0 else 0.0
    else:  # Pandas Series or NumPy array case
        return np.where(
            reputation > 0,
            ((np.log10(np.clip(reputation, 1e-9, None)) - 9) * 9) + 25,
            0.0
        )


def score_to_reputation(reputation_score):
    """
    Converts reputation score back to raw reputation.

    Parameters:
    - reputation_score (float, int, or Pandas Series): The reputation score to be converted.

    Returns:
    - Raw reputation (float if input is scalar, Pandas Series if input is a Series)
    """
    if isinstance(reputation_score, (int, float)):  # Scalar case
        return 10 ** ((reputation_score - 25) / 9 + 9) if reputation_score > 0 else 0.0
    else:  # Pandas Series or NumPy array case
        return np.where(
            reputation_score > 0,
            10 ** ((reputation_score - 25) / 9 + 9),
            0.0
        )


def get_hive_balances_params(params):
    hive_per_mvest = get_hive_per_mvest()
    conversion_factor = hive_per_mvest / 1e6

    vesting_shares_min = params['hp_min'] / conversion_factor
    vesting_shares_max = params['hp_max'] / conversion_factor
    reputation_min = score_to_reputation(params['reputation_min'])
    reputation_max = score_to_reputation(params['reputation_max'])

    query = f"""
        SELECT
            a.name,
            a.balance AS hive,
            a.savings_balance AS hive_savings,
            a.hbd_balance AS hbd,
            a.savings_hbd_balance AS hbd_savings,
            a.reputation AS reputation,
            a.vesting_shares AS vesting_shares,
            a.delegated_vesting_shares AS delegated_vesting_shares,
            a.received_vesting_shares AS received_vesting_shares,
            a.curation_rewards / 1000.0 AS curation_rewards,
            a.posting_rewards / 1000.0 AS posting_rewards,
            COUNT(c.permlink) AS comment_count
        FROM
            Accounts a
        JOIN
            Comments c
        ON
            a.name = c.author
        WHERE
            a.posting_rewards > {params['posting_rewards_min']}
            AND a.posting_rewards < {params['posting_rewards_max']}
            AND a.vesting_shares > {vesting_shares_min}
            AND a.vesting_shares < {vesting_shares_max}
            AND a.reputation > {reputation_min}
            AND a.reputation < {reputation_max}

            AND c.created >= DATEADD(MONTH, -{params['months']}, GETDATE())
        GROUP BY
            a.name,
            a.balance,
            a.savings_balance,
            a.hbd_balance,
            a.savings_hbd_balance,
            a.reputation,
            a.vesting_shares,
            a.delegated_vesting_shares,
            a.received_vesting_shares,
            a.curation_rewards,
            a.posting_rewards
        HAVING
            COUNT(c.permlink) > {params['comments']};
    """

    df = execute_query_df(query)

    if not df.empty:
        df["reputation_score"] = reputation_to_score(df['reputation'])

        df["hp"] = conversion_factor * df["vesting_shares"]
        df["hp delegated"] = conversion_factor * df["delegated_vesting_shares"]
        df["hp received"] = conversion_factor * df["received_vesting_shares"]
        df["ke_ratio"] = (df["curation_rewards"] + df["posting_rewards"]) / df["hp"]

    return df


def get_commentators(permlinks):
    placeholders = ', '.join(['?'] * len(permlinks))

    query = f"""
        SELECT DISTINCT author
        FROM comments
        WHERE parent_permlink IN ({placeholders})
        AND depth = 1
    """
    df = execute_query_df(query, permlinks)
    return df.author.to_list()


def get_top_posting_rewards(number, minimal_posting_rewards):
    query = """
        SELECT TOP ? name, posting_rewards
        FROM accounts
        WHERE posting_rewards > ?
        ORDER BY posting_rewards DESC
    """
    return execute_query_df(query, (number, minimal_posting_rewards))


def get_active_hiver_users(posting_rewards, comments, months):
    query = """
        SELECT
            a.name,
            a.posting_rewards,
            COUNT(c.permlink) AS comment_count
        FROM Accounts a
        JOIN Comments c ON a.name = c.author
        WHERE a.posting_rewards > ? AND c.created >= DATEADD(MONTH, ?, GETDATE())
        GROUP BY a.name, a.posting_rewards
        HAVING COUNT(c.permlink) > ?
    """
    return execute_query_df(query, (posting_rewards, -months, comments))
