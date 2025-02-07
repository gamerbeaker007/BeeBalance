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


def execute_query_df(query, params=None):
    """
    Executes a SQL query with optional parameters and returns a Pandas DataFrame.

    Parameters:
    - query: str, the SQL query to execute.
    - params: list or tuple, optional, the parameters for the query.

    Returns:
    - pd.DataFrame with query results or an empty DataFrame on failure/no results.
    """
    connection = None
    try:
        connection = pypyodbc.connect(connection_string)
        cursor = connection.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Fetch column names dynamically from the cursor description
        columns = [column[0] for column in cursor.description] if cursor.description else []

        # Fetch results
        result = cursor.fetchall()
        if result:
            return pd.DataFrame(result, columns=columns)
        else:
            return pd.DataFrame(columns=columns)

    except pypyodbc.Error as e:
        log.error(f"Database error: {e}")
        return pd.DataFrame()  # Return empty DataFrame on database error

    finally:
        if connection:
            connection.close()


@lru_cache(maxsize=1)
def get_hive_per_mvest():
    result = execute_query_df("SELECT total_vesting_fund_hive, total_vesting_shares FROM DynamicGlobalProperties")
    if not result.empty:  # Ensure result is not empty
        # Unpack the first row of the result
        total_vesting_fund_hive, total_vesting_shares = result.iloc[0]
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
    df = pd.DataFrame()

    # Process account names in batches
    for batch in batch_list(account_names, batch_size=500):
        # Create the placeholders for the IN clause
        placeholders = ', '.join(['?'] * len(batch))

        # SQL query using IN clause
        query = f"""
        SELECT
            name,
            created,
            CAST (balance AS float) AS hive,
            CAST (savings_balance AS float) AS hive_savings,
            CAST (hbd_balance AS float) AS hbd,
            CAST (savings_hbd_balance AS float) AS hbd_savings,
            CAST (reputation AS float) AS reputation,
            CAST (vesting_shares AS float) AS vesting_shares,
            CAST (delegated_vesting_shares AS float) AS delegated_vesting_shares,
            CAST (received_vesting_shares AS float) AS received_vesting_shares,
            CAST (curation_rewards AS float) / 1000.0 AS curation_rewards,
            CAST (posting_rewards AS float) / 1000.0 AS posting_rewards
        FROM accounts
        WHERE name IN ({placeholders})
        """

        batch_result = execute_query_df(query, batch)
        if not batch_result.empty:
            df = pd.concat([df, batch_result])

    if not df.empty:
        df["reputation_score"] = reputation_to_score(df["reputation"])

        conversion_factor = hive_per_mvest / 1e6
        df["hp"] = conversion_factor * df["vesting_shares"]
        df["hp delegated"] = conversion_factor * df["delegated_vesting_shares"]
        df["hp received"] = conversion_factor * df["received_vesting_shares"]
        df["ke_ratio"] = (df["curation_rewards"] + df["posting_rewards"]) / df["hp"]

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
            CAST (a.balance AS float) AS hive,
            CAST (a.savings_balance AS float) AS hive_savings,
            CAST (a.hbd_balance AS float) AS hbd,
            CAST (a.savings_hbd_balance AS float) AS hbd_savings,
            CAST (a.reputation AS float) AS reputation,
            CAST (a.vesting_shares AS float) AS vesting_shares,
            CAST (a.delegated_vesting_shares AS float) AS delegated_vesting_shares,
            CAST (a.received_vesting_shares AS float) AS received_vesting_shares,
            CAST (a.curation_rewards AS float) / 1000.0 AS curation_rewards,
            CAST (a.posting_rewards AS float) / 1000.0 AS posting_rewards,
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
    query = f"""
        SELECT TOP {number} name, posting_rewards 
        FROM accounts 
        WHERE posting_rewards > {minimal_posting_rewards}
        ORDER BY posting_rewards DESC
    """
    result = execute_query_df(query)

    return result


def get_active_hiver_users(posting_rewards, comments, months):
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
    return execute_query_df(query)
