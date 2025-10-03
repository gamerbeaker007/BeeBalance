import logging

from psycopg2 import pool
import pandas as pd

# Database configuration
DB_CONFIG = {
    'host': 'hafsql-sql.mahdiyari.info',
    'port': 5432,
    'database': 'haf_block_log',
    'user': 'hafsql_public',
    'password': 'hafsql_public',
}

_db_pool = None

log = logging.getLogger('hafsql')


def get_pool():
    global _db_pool
    if _db_pool is None:
        _db_pool = pool.SimpleConnectionPool(
            1, 6,
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
    return _db_pool


def fetch_balance_history(account_names):
    if not account_names:
        log.warning("⚠️ No account names provided.")
        return pd.DataFrame()
    log.info(f"Fetching balance history for accounts: {account_names}")

    db_pool = get_pool()
    conn = db_pool.getconn()
    try:
        placeholders = ', '.join(['%s'] * len(account_names))
        query = f"""
WITH bh AS (
  SELECT
    bh.*,
    hb.timestamp AS block_timestamp,
    date_trunc('month', hb.timestamp) AS month_start,
    ROW_NUMBER() OVER (
      PARTITION BY bh.account_name
      ORDER BY bh.block_num ASC
    ) AS rn_first,
    ROW_NUMBER() OVER (
      PARTITION BY bh.account_name
      ORDER BY bh.block_num DESC
    ) AS rn_last,
    ROW_NUMBER() OVER (
      PARTITION BY bh.account_name, date_trunc('month', hb.timestamp)
      ORDER BY hb.timestamp ASC, bh.block_num ASC
    ) AS rn_month
  FROM hafsql.balances_history bh
  JOIN hafsql.haf_blocks hb
    ON hb.block_num = bh.block_num
  WHERE bh.account_name IN ({placeholders})   -- or = ANY(:account_names)
)
SELECT
  *
FROM bh
WHERE rn_first = 1
   OR rn_last  = 1
   OR rn_month = 1
ORDER BY account_name, block_num DESC;
        """

        with conn.cursor() as cur:
            cur.execute(query, account_names)
            rows = cur.fetchall()
            if not rows:
                print("⚠️ No results found.")
                return pd.DataFrame()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(rows, columns=columns)
            return df
    except Exception as e:
        log.error(f"❌ Database query error: {e}")
        return pd.DataFrame()
    finally:
        db_pool.putconn(conn)


def close_database_connection():
    global _db_pool
    if _db_pool:
        print('🔌 Closing database connection...')
        _db_pool.closeall()
        _db_pool = None
        print('✅ Database connection closed.')
