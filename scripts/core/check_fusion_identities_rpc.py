
import json
import time
from qubipy.rpc import rpc_client

identities = ["YSGDHHDFBDERGBSJQMJVGEELNPKBZXGQEWMAKKCXKEFEVOYZNPRFLIMEFKRK", "SXNDQUKVAWATVGFUDWDKEACUMPFBPULPZWEQNNCQXEIADAPKXIFDEHYCEQJO", "QZHNBTOWBLYUBAZTIAQOTCZNJTWAJFHUJVDBFVCDYEMQDFGZVILHXAZEREXK"]
methods = ["XOR Sum (Binary Fusion)", "Concatenation + K12 Hash", "Modular Sum (Character Addition)"]

rpc = rpc_client.QubiPy_RPC()
rpc_results = []

for identity, method in zip(identities, methods):
 try:
 time.sleep(1.5)
 balance_data = rpc.get_balance(identity)
 
 result = {
 "method": method,
 "identity": identity,
 "balance": None,
 "assets": None,
 "history": None,
 "status": "unknown",
 }
 
 if balance_data:
 result["balance"] = str(balance_data.get("balance", 0))
 
 try:
 assets = rpc.get_owned_assets(identity)
 result["assets"] = assets if assets else []
 except:
 result["assets"] = []
 
 try:
 history = rpc.get_transaction_history(identity, limit=10)
 result["history"] = history if history else []
 except:
 result["history"] = []
 
 balance_int = int(result["balance"])
 has_assets = result["assets"] and len(result["assets"]) > 0
 has_history = result["history"] and len(result["history"]) > 0
 
 if balance_int > 0 or has_assets or has_history:
 result["status"] = "HIT"
 else:
 result["status"] = "empty"
 else:
 result["status"] = "not_found"
 
 rpc_results.append(result)
 
 status_icon = "🎉" if result["status"] == "HIT" else " "
 print(f"{status_icon} {method}: {identity[:40]}...")
 if result["status"] == "HIT":
 print(f" Balance: {result['balance']}, Assets: {len(result.get('assets', []))}, History: {len(result.get('history', []))}")
 except Exception as e:
 print(f" ❌ {method}: Error - {e}")
 rpc_results.append({
 "method": method,
 "identity": identity,
 "error": str(e),
 "status": "rpc_error",
 })

with open("outputs/derived/master_seed_fusion_layer1_rpc_check.json", "w") as f:
 json.dump(rpc_results, f, indent=2)

hits = [r for r in rpc_results if r.get("status") == "HIT"]
print()
print(f"✅ RPC Check complete: {len(hits)} HIT(s) found")
