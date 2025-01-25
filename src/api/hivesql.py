import streamlit as st
import pandas as pd
import pypyodbc

# Access secrets
db_username = st.secrets["database"]["username"]
db_password = st.secrets["database"]["password"]

# Connection string using secrets
connection_string = (
    f"Driver={{ODBC Driver 18 for SQL Server}};"
    f"Server=vip.hivesql.io;"
    f"Database=DBHive;"
    f"UID={db_username};"
    f"PWD={db_password};"
    f"TrustServerCertificate=yes;"
    f"Encrypt=yes"
)

def executeQuery(query, params=None):
    connection = pypyodbc.connect(connection_string)
    cursor = connection.cursor()
    cursor.execute(query, params or ())
    result = cursor.fetchall()
    connection.close()
    return result


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


def get_hive_balances(account_names):
    # Ensure account_names is a list
    if not isinstance(account_names, list):
        raise ValueError("account_names must be a list")

    # Prepare the query with placeholders for multiple names
    placeholders = ', '.join(['?'] * len(account_names))
    query = f"""
        SELECT
            name,
            created,
            CAST(balance AS FLOAT) AS hive,
            CAST(savings_balance AS FLOAT) AS hive_savings,
            CAST(hbd_balance AS FLOAT) AS hbd,
            CAST(savings_hbd_balance AS FLOAT) AS hbd_savings,
            CAST(reputation AS FLOAT),
            CAST(vesting_shares AS FLOAT),  
            CAST(curation_rewards AS FLOAT) / 1000.0 AS curation, 
            CAST(posting_rewards AS FLOAT) / 1000.0 AS posting
        FROM accounts
        WHERE name IN ({placeholders})
    """
    # Execute the query with the list of names
    result = executeQuery(query, account_names)
    # Define column names to match the query
    columns = [
        "name", "created", "hive", "hive_savings", "hbd", "hbd_savings",
        "reputation", "vesting_shares", "curation_rewards", "author_rewards"
    ]

    # Create DataFrame
    df = pd.DataFrame(result, columns=columns)

    hive_per_mvest = get_hive_per_mvest()
    df["hp"] = df["vesting_shares"].apply(lambda vesting_shares: vest_to_hp(hive_per_mvest, vesting_shares))

    # Calculate KE ratio
    df["ke_ratio"] = (df["curation_rewards"] + df["author_rewards"]) / df["hp"]

    return df
