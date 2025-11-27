
import json
import time
from qubipy.rpc import rpc_client

layer2_identities = ["CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP", "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP", "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP", "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP", "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB", "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB", "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB", "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB"]

rpc = rpc_client.QubiPy_RPC()
results = []

for identity in layer2_identities:
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

with open("outputs/derived/original_layer2_onchain_check.json", "w") as f:
 json.dump(results, f, indent=2)

verified = sum(1 for r in results if r.get("exists"))
print(f"On-chain verifiziert: {verified}/{len(results)}")
