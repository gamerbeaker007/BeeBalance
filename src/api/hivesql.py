from functools import lru_cache
import streamlit as st
import pandas as pd
import pypyodbc

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


def executeQuery(query, params=None):
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
        print(f"Database error: {e}")
        raise
    finally:
        if connection:
            connection.close()



@lru_cache(maxsize=1)
def get_hive_per_mvest():
    result = executeQuery("SELECT total_vesting_fund_hive, total_vesting_shares  FROM DynamicGlobalProperties")
    if result:  # Ensure result is not empty
        # Unpack the first row of the result
        total_vesting_fund_hive, total_vesting_shares = result[0]
        return float(total_vesting_fund_hive) / (float(total_vesting_shares) / 1e6)
    else:
        # Return an empty Series if the query returns no rows
        return 0


def vest_to_hp(hive_per_mvest, vesting_shares):
    return vesting_shares / 1e6 * hive_per_mvest


def batch_list(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


def get_hive_balances(account_names):
    if not isinstance(account_names, list):
        raise ValueError("account_names must be a list")

    hive_per_mvest = get_hive_per_mvest()  # Cacheable
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
            CAST(curation_rewards AS FLOAT) / 1000.0 AS curation,
            CAST(posting_rewards AS FLOAT) / 1000.0 AS posting
        FROM accounts
        WHERE name IN ({placeholders})
        """

        batch_result = executeQuery(query, batch)
        if batch_result:
            all_results.extend(batch_result)

    # Define DataFrame columns
    columns = [
        "name", "created", "hive", "hive_savings", "hbd", "hbd_savings",
        "reputation", "vesting_shares", "curation_rewards", "author_rewards"
    ]

    df = pd.DataFrame.from_records(all_results, columns=columns)

    df["hp"] = (hive_per_mvest / 1e6) * df["vesting_shares"]
    df["ke_ratio"] = (df["curation_rewards"] + df["author_rewards"]) / df["hp"]

    return df
