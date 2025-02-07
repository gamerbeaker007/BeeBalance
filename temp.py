import pandas as pd
from hiveengine.wallet import Wallet

from src.api import hive_engine
from src.api.hive_engine import hive_engine_nodes
from src.api.hive_node import PREFERRED_NODE

wallet = Wallet('azircon')
bal = wallet.get_balances()
df = pd.DataFrame(bal)

filter_symbols = ['LEO']
if not df.empty and filter_symbols:
     df = df[df.symbol.isin(filter_symbols)]

print(f'DEFAULT NODE OF HIVE ENGINE: {df[['symbol', 'balance', 'stake']].head()}')

account_name = 'azircon'
result = hive_engine.find_one_with_retry('tokens', 'balances', {"account": account_name, "symbol": 'LEO'})
print(f'default {result}')

for i in hive_engine_nodes:
    result = hive_engine.find_one_with_retry('tokens', 'balances', {"account": account_name, "symbol": 'LEO'}, pref_node=i)
    print(f'Result with NODE: {i}: {result}')

