
import json
import time
from qubipy.rpc import rpc_client

issuers = [{"asset_name": "CFB", "issuer": "CFBMEMZOIDEXQAUXYYSZIURADQLAPWPMNJXQSNVQZAHYVOPYUKKJBJUCTVJL", "units": "5"}, {"asset_name": "CODED", "issuer": "CODEDBUUDDYHECBVSUONSSWTOJRCLZSWHFHZIUWVFGNWVCKIWJCSDSWGQAAI", "units": "2"}, {"asset_name": "QXMR", "issuer": "QXMRTKAIIGLUREPIQPCMHCKWSIPDTUYFCFNYXQLTECSUJVYEMMDELBMDOEYB", "units": "5"}]

rpc = rpc_client.QubiPy_RPC()

print("=" * 80)
print("ISSUER-ANALYSE")
print("=" * 80)
print()

results = []

for issuer_data in issuers:
 asset_name = issuer_data["asset_name"]
 issuer = issuer_data["issuer"]
 units = issuer_data["units"]
 
 print(f"{asset_name} ({units} Units):")
 print(f" Issuer: {issuer}")
 
 try:
 time.sleep(2.0)
 balance_data = rpc.get_balance(issuer)
 
 result = {
 "asset_name": asset_name,
 "issuer": issuer,
 "units": units,
 "issuer_balance": None,
 "issuer_exists": False,
 }
 
 if balance_data:
 result["issuer_balance"] = str(balance_data.get("balance", 0))
 result["issuer_exists"] = True
 print(f" ✅ Issuer existiert on-chain")
 print(f" Balance: {result['issuer_balance']} QU")
 else:
 print(f" ❌ Issuer existiert nicht on-chain")
 
 results.append(result)
 except Exception as e:
 print(f" ❌ Error: {e}")
 results.append({
 "asset_name": asset_name,
 "issuer": issuer,
 "units": units,
 "error": str(e),
 })
 
 print()

with open("outputs/derived/asset_issuer_analysis.json", "w") as f:
 json.dump(results, f, indent=2)

print("✅ Issuer-Analyse gespeichert")
