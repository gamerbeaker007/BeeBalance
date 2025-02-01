import logging
from functools import lru_cache

import numpy as np
import pandas as pd
import pypyodbc
import streamlit as st

log = logging.getLogger("Hive SQL")
# Access secrets
db_username = st.secrets["database"]["username"]
db_password = st.secrets["database"]["password"]

# Connection string using secrets
connection_string = (
    f"Driver={{ODBC Driver 17 for SQL Server}};"
    f"Server=vip.hivesql.io;"
    f"Database=DBHive;"
    f"UID={db_username};"
    f"PWD={db_password};"
    f"TrustServerCertificate=yes;"
    f"Encrypt=yes"
)


def execute_query(query, params=None):
    """
    Executes a SQL query with optional parameters.

    Parameters:
    - query: str, the SQL query to execute.
    - params: list or tuple, optional, the parameters for the query.

    Returns:
    - list of tuples, the result set from the query.
    """
    connection = None
    try:
        connection = pypyodbc.connect(connection_string)
        cursor = connection.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        try:
            result = cursor.fetchall()  # Fetch all rows
        except pypyodbc.ProgrammingError:
            result = None

        connection.commit()

        return result
    except pypyodbc.Error as e:
        log.error(f"Database error: {e}")
        raise
    finally:
        if connection:
            connection.close()


@lru_cache(maxsize=1)
def get_hive_per_mvest():
    result = execute_query("SELECT total_vesting_fund_hive, total_vesting_shares  FROM DynamicGlobalProperties")
    if result:  # Ensure result is not empty
        # Unpack the first row of the result
        total_vesting_fund_hive, total_vesting_shares = result[0]
        return float(total_vesting_fund_hive) / (float(total_vesting_shares) / 1e6)
    else:
        # Return an empty Series if the query returns no rows
        return 0


def batch_list(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


def get_hive_balances(account_names):
    if not isinstance(account_names, list):
        raise ValueError("account_names must be a list")

    hive_per_mvest = get_hive_per_mvest()
    all_results = []

    # Process account names in batches
    for batch in batch_list(account_names, batch_size=50):
        # Create the placeholders for the IN clause
        placeholders = ', '.join(['?'] * len(batch))

        # SQL query using IN clause
        query = f"""
        SELECT
            name,
            created,
            CAST(balance AS FLOAT) AS hive,
            CAST(savings_balance AS FLOAT) AS hive_savings,
            CAST(hbd_balance AS FLOAT) AS hbd,
            CAST(savings_hbd_balance AS FLOAT) AS hbd_savings,
            CAST(reputation AS FLOAT) AS reputation,
            CAST(vesting_shares AS FLOAT) AS vesting_shares,
            CAST(delegated_vesting_shares AS FLOAT) AS delegated_vesting_shares,
            CAST(received_vesting_shares AS FLOAT) AS received_vesting_shares,
            CAST(curation_rewards AS FLOAT) / 1000.0 AS curation,
            CAST(posting_rewards AS FLOAT) / 1000.0 AS posting
        FROM accounts
        WHERE name IN ({placeholders})
        """

        batch_result = execute_query(query, batch)
        if batch_result:
            all_results.extend(batch_result)

    # Define DataFrame columns
    columns = [
        "name", "created", "hive", "hive_savings", "hbd", "hbd_savings",
        "reputation", "vesting_shares", "delegated_vesting_shares", "received_vesting_shares", "curation_rewards",
        "posting_rewards"
    ]

    df = pd.DataFrame.from_records(all_results, columns=columns)
    df["reputation"] = np.where(
        df["reputation"] > 0,  # Only apply log10() to positive values
        ((np.log10(df["reputation"].clip(lower=1e-9)) - 9) * 9) + 25,
        0.0  # Assign 0.0 when reputation is 0 or negative
    )

    conversion_factor = hive_per_mvest / 1e6
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
    authors = execute_query(query, permlinks)
    authors = [row[0] for row in authors]
    return authors


def get_top_posting_rewards(number, minimal_posting_rewards):
    query = f"""
        SELECT TOP {number} name, posting_rewards 
        FROM accounts 
        WHERE posting_rewards > {minimal_posting_rewards}
        ORDER BY posting_rewards DESC
    """
    result = execute_query(query)

    columns = [
        "name", "posting_rewards"
    ]
    return pd.DataFrame.from_records(result, columns=columns)


def get_active_hivers(posting_rewards, comments, months):
    query = f"""
            SELECT 
                a.name,
                a.posting_rewards,
                COUNT(c.permlink) AS comment_count
            FROM 
                Accounts a
            JOIN 
                Comments c
            ON 
                a.name = c.author
            WHERE 
                a.posting_rewards > {posting_rewards}
                AND c.created >= DATEADD(MONTH, -{months}, GETDATE())
            GROUP BY 
                a.name, a.posting_rewards
            HAVING 
                COUNT(c.permlink) > {comments};
    """
    result = execute_query(query)
    columns = [
        "name", "posting_rewards", f"comment past {months} months"
    ]

    return pd.DataFrame.from_records(result, columns=columns)
