
import json
import time
from qubipy.rpc import rpc_client

derived_identities = ["ADCGHBXXIVLYCZBAMAEOJIMMGTCJDJDNMNCHLGGBTYGXHQWOEFQVNKSEJJXK", "FJWQDRNODSZWAIABHFMNHJVZZBNEFXNPGGEKDHXJGXFWBRRUDECSUZJSIVNR", "DBJNBVBHWFDCKWAUPZDCHLWJHUSCGDWYIDBWQSGLZXCFDBHDBSFSXRABEDPF", "EHXBKQGDMIUILXGWJSTAUMASJRHSERXHXCSBBBJQOXDQSJIYYPYOGVCVEXUR", "AJVUQFLZRUABTUCMYWFNXSGLABMZBKGDTWGHGHSKCEGDBHYHVEGLXUVQFQGD"]

rpc = rpc_client.QubiPy_RPC()
results = []

for identity in derived_identities:
 try:
 time.sleep(1.5)
 balance_data = rpc.get_balance(identity)
 
 if balance_data:
 results.append({
 "identity": identity,
 "exists": True,
 "balance": balance_data.get("balance", "0"),
 "valid_for_tick": balance_data.get("validForTick", 0),
 })
 else:
 results.append({
 "identity": identity,
 "exists": False,
 })
 except Exception as e:
 results.append({
 "identity": identity,
 "error": str(e),
 })

# Speichere Ergebnisse
with open("outputs/derived/step2f_derived_onchain_check.json", "w") as f:
 json.dump(results, f, indent=2)

# Zeige Zusammenfassung
verified = sum(1 for r in results if r.get("exists"))
print(f"Derived Identities on-chain: {verified}/{len(results)}")
