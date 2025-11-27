
import json
import time
from qubipy.rpc import rpc_client

seeds_data = [{"method": "All 8 - XOR", "seed": "ndymtdwwrybuxaeyvegabftikrefvfwaqbekdoreanmansaaofwsays", "identity": "YSGDHHDFBDERGBSJQMJVGEELNPKBZXGQEWMAKKCXKEFEVOYZNPRFLIMEFKRK"}, {"method": "All 8 - Sum", "seed": "thsmntckvkxoxgyatoaqxxtukfqpxnosctyspcfmofemzmqaklmmqqk", "identity": "QZHNBTOWBLYUBAZTIAQOTCZNJTWAJFHUJVDBFVCDYEMQDFGZVILHXAZEREXK"}, {"method": "4 Seeds XOR - Combo 1", "seed": "amoffkmognuycpwjcqhgeeqkeyirahuqsuoxfstagfgqccmxavkqiym", "identity": "YBVNGMZMELXLXDODGDOYRVOVKSVCIKYPWBTJJCKCWBWNAVGPKHCLJJTFXKOH"}, {"method": "4 Seeds XOR - Combo 2", "seed": "sqfueaymfenkbsaczmmhxhqledrgwcspjrkwudtzadcitbhxrsbfitu", "identity": "GCNFBDJHHMWSGEYSSQJKYNUZSXACPOQTDKBQCPOHDECAVATKSVUQMWBHAIGB"}, {"method": "4 Seeds XOR - Combo 3", "seed": "bnbbfnllfvcwmucfdwfhyewdidluresrncybudfuebecydswdrbwfde", "identity": "ISJDFZZPEJKFRGFJDAPLHHQSNDSCLGWPHHZGXQTESAZQUCRGKRQHJYPFZBMJ"}, {"method": "4 Seeds XOR - Combo 4", "seed": "porcxcexhcbmpxlkddywexchlybeuoqfvpgwxfczhsbtdllahebtbdj", "identity": "LGINJSHVKNIDGDXVJDYBTYCEANPDVIFGUXDFCTXCDCUCBHYNAMFGSMXEIHPN"}, {"method": "4 Seeds XOR - Combo 5", "seed": "rcdaayniqyfcjebyonkkophtjrnygosrttegrdskfgnxhhswbnhyetd", "identity": "BLHDHZCECZJITFHDWNIVWPRHVQNCWOFUEUXHNFRTKELDDQGPKKWAMMGDARKA"}, {"method": "Diagonal XOR", "seed": "amoffkmognuycpwjcqhgeeqkeyirahuqsuoxfstagfgqccmxavkqiym", "identity": "YBVNGMZMELXLXDODGDOYRVOVKSVCIKYPWBTJJCKCWBWNAVGPKHCLJJTFXKOH"}, {"method": "Vortex XOR", "seed": "npwjmxayxvpmlvsrxubcfbdcojwovcckcpkdgccecskqromnuqccsae", "identity": "ORTZBLLYMAYESCNJEZVCZTREOPCABBYKRVRNCVKZXFCJHZFSDHMXMIWDIUFG"}]

rpc = rpc_client.QubiPy_RPC()
results = []

print("=" * 80)
print("RPC-CHECK: ALLE IDENTITIES")
print("=" * 80)
print()

for i, seed_info in enumerate(seeds_data, 1):
 method = seed_info.get("method", "Unknown")
 identity = seed_info.get("identity")
 seed = seed_info.get("seed", "")[:30]
 
 print(f"[{i}/{len(seeds_data)}] {method}:")
 print(f" Seed: {seed}...")
 print(f" Identity: {identity[:40]}...")
 
 try:
 time.sleep(2.0)
 balance_data = rpc.get_balance(identity)
 
 result = {
 "method": method,
 "seed": seed_info.get("seed", ""),
 "identity": identity,
 "balance": None,
 "assets": None,
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
 
 balance_int = int(result["balance"])
 has_assets = result["assets"] and len(result["assets"]) > 0
 
 if balance_int > 0 or has_assets:
 result["status"] = "HIT"
 print(f" 🎉 HIT! Balance: {result['balance']}, Assets: {len(result.get('assets', []))}")
 else:
 result["status"] = "empty"
 print(f" Balance: {result['balance']} QU, Assets: {len(result.get('assets', []))}")
 else:
 result["status"] = "not_found"
 print(f" Status: {result['status']}")
 
 results.append(result)
 except Exception as e:
 error_msg = str(e)
 if "429" in error_msg or "Too Many Requests" in error_msg:
 print(f" ⚠️ Rate limit")
 results.append({
 "method": method,
 "seed": seed_info.get("seed", ""),
 "identity": identity,
 "error": error_msg,
 "status": "rate_limited",
 })
 else:
 print(f" ❌ Error: {error_msg[:50]}...")
 results.append({
 "method": method,
 "seed": seed_info.get("seed", ""),
 "identity": identity,
 "error": error_msg,
 "status": "rpc_error",
 })
 
 print()

with open("outputs/derived/all_seeds_rpc_check.json", "w") as f:
 json.dump(results, f, indent=2)

hits = [r for r in results if r.get("status") == "HIT"]
print()
print("=" * 80)
print("ERGEBNISSE")
print("=" * 80)
print()
print(f"✅ RPC Check complete: {len(hits)} HIT(s) found")
print()

if hits:
 print("🎉 HIT(S) GEFUNDEN:")
 for hit in hits:
 print(f" {hit['method']}: {hit['identity']}")
 print(f" Balance: {hit['balance']} QU, Assets: {len(hit.get('assets', []))}")
 print()
else:
 print("❌ Keine HITs gefunden")
 print()
 print("Status:")
 for r in results:
 status_icon = "✅" if r.get("status") == "empty" else "⚠️" if r.get("status") == "rate_limited" else "❌"
 print(f" {status_icon} {r['method']}: {r['status']}")
