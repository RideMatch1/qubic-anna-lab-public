
import json
import time
from qubipy.rpc import rpc_client

identities = ["YSGDHHDFBDERGBSJQMJVGEELNPKBZXGQEWMAKKCXKEFEVOYZNPRFLIMEFKRK", "SXNDQUKVAWATVGFUDWDKEACUMPFBPULPZWEQNNCQXEIADAPKXIFDEHYCEQJO", "QZHNBTOWBLYUBAZTIAQOTCZNJTWAJFHUJVDBFVCDYEMQDFGZVILHXAZEREXK"]
methods = ["XOR Sum (Binary Fusion)", "Concatenation + K12 Hash", "Modular Sum (Character Addition)"]

rpc = rpc_client.QubiPy_RPC()
rpc_results = []

for i, (identity, method) in enumerate(zip(identities, methods), 1):
 print(f"[{i}/{len(identities)}] {method}: {identity[:40]}...")
 
 max_retries = 3
 retry_delay = 5.0
 
 for attempt in range(max_retries):
 try:
 time.sleep(retry_delay)
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
 time.sleep(2.0)
 assets = rpc.get_owned_assets(identity)
 result["assets"] = assets if assets else []
 except:
 result["assets"] = []
 
 try:
 time.sleep(2.0)
 history = rpc.get_transaction_history(identity, limit=10)
 result["history"] = history if history else []
 except:
 result["history"] = []
 
 balance_int = int(result["balance"])
 has_assets = result["assets"] and len(result["assets"]) > 0
 has_history = result["history"] and len(result["history"]) > 0
 
 if balance_int > 0 or has_assets or has_history:
 result["status"] = "HIT"
 print(f" 🎉🎉🎉 HIT! Balance: {result['balance']}, Assets: {len(result.get('assets', []))}, History: {len(result.get('history', []))}")
 else:
 result["status"] = "empty"
 print(f" Balance: {result['balance']} QU, Status: {result['status']}")
 else:
 result["status"] = "not_found"
 print(f" Status: {result['status']}")
 
 rpc_results.append(result)
 break # Success, exit retry loop
 
 except Exception as e:
 error_msg = str(e)
 if "429" in error_msg or "Too Many Requests" in error_msg:
 if attempt < max_retries - 1:
 wait_time = retry_delay * (attempt + 1)
 print(f" ⚠️ Rate limit ({error_msg[:50]}...), warte {wait_time}s...")
 time.sleep(wait_time)
 continue
 else:
 print(f" ❌ Rate limit nach {max_retries} Versuchen")
 rpc_results.append({
 "method": method,
 "identity": identity,
 "error": error_msg,
 "status": "rate_limited",
 })
 else:
 print(f" ❌ Error: {error_msg[:50]}...")
 rpc_results.append({
 "method": method,
 "identity": identity,
 "error": error_msg,
 "status": "rpc_error",
 })
 break
 
 print()

with open("outputs/derived/master_seed_fusion_layer1_rpc_check.json", "w") as f:
 json.dump(rpc_results, f, indent=2)

hits = [r for r in rpc_results if r.get("status") == "HIT"]
print()
print("=" * 80)
print("FINALER ERGEBNIS")
print("=" * 80)
print()
print(f"✅ RPC Check complete: {len(hits)} HIT(s) found")
print()

if hits:
 print("🎉🎉🎉 HIT(S) GEFUNDEN:")
 for hit in hits:
 print(f" Method: {hit['method']}")
 print(f" Identity: {hit['identity']}")
 print(f" Balance: {hit['balance']} QU")
 print(f" Assets: {len(hit.get('assets', []))}")
 print(f" History: {len(hit.get('history', []))} transactions")
 print()
else:
 print("❌ Keine HITs gefunden")
 print()
 print("Status aller Identitäten:")
 for r in rpc_results:
 print(f" {r['method']}: {r['status']}")
