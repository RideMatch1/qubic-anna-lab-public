#!/usr/bin/env python3
"""
Check die ECHTEN Layer-2 Identities mit 50 GENESIS und QUBIC
"""

import sys
sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")

from qubipy.rpc import rpc_client
import time
import json
from pathlib import Path

# Die ECHTEN Layer-2 Identities (aus CORRECT_LAYER2_MASTER_DATA.json)
LAYER2_IDENTITIES = [
 {"label": "Diagonal #1", "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd", "identity": "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP"},
 {"label": "Diagonal #2", "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr", "identity": "FPEXLMCOGJNYAAELTBSEDHAZCCNAGXJRPRFNBEXUKPDHFTVAHETKPANQCMLM"},
 {"label": "Diagonal #3", "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn", "identity": "ABCXUAPWHTDRJDASQEZSNCDAMXNJAXDTNESWQLNWPZBBUXDGNJLGYXETNGHN"},
 {"label": "Diagonal #4", "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht", "identity": "AGTIRJYQVZXUEFAUCPEBEYHDAFXZFMFOARDSUKLHHBETDIVPWVZMOORUOXSD"},
 {"label": "Vortex #1", "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml", "identity": "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB"},
 {"label": "Vortex #2", "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb", "identity": "ADVDNZIGNSCXAODGDMEXMKICVHFOHBROQQMVZOGAMVASHQURDBPDNJRJJQRM"},
 {"label": "Vortex #3", "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw", "identity": "HFVFDNEHUVRRBIESYPSSRPNJSVVSDBIPNAXAHIKISLAKYZFKMWNJXVVUEUQJ"},
 {"label": "Vortex #4", "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc", "identity": "BIARJWYAYURJYJBXXEDMQOKGSJXBFNWCDSHXZILITIDHCMJYUMPPXQZQAXNR"},
]

MASTER_IDENTITY = "BZBQFLLBNCXEMGLOBHUVFTLUPLVCPQUASSILFABOFFBCADQSSUPNWLZBQEXK"

print("=" * 80)
print("ECHTE LAYER-2 IDENTITIES CHECK")
print("=" * 80)
print()

rpc = rpc_client.QubiPy_RPC()

results = []

for item in LAYER2_IDENTITIES:
 label = item["label"]
 seed = item["seed"]
 identity = item["identity"]
 
 print(f"{label}:")
 print(f" Seed: {seed[:30]}...")
 print(f" Identity: {identity}")
 
 try:
 time.sleep(2.0)
 balance_data = rpc.get_balance(identity)
 if balance_data:
 balance = int(balance_data.get("balance", 0))
 valid_for_tick = balance_data.get("validForTick", 0)
 incoming = balance_data.get("numberOfIncomingTransfers", 0)
 outgoing = balance_data.get("numberOfOutgoingTransfers", 0)
 
 print(f" Balance: {balance / 1_000_000:.2f} QUBIC ({balance} QU)")
 print(f" Valid for Tick: {valid_for_tick}")
 print(f" Incoming: {incoming}, Outgoing: {outgoing}")
 
 # Check Assets
 try:
 time.sleep(2.0)
 assets = rpc.get_owned_assets(identity)
 genesis_count = 0
 if assets:
 for asset in assets:
 asset_data = asset.get("data", {})
 issued_asset = asset_data.get("issuedAsset", {})
 asset_name = issued_asset.get("name", "Unknown")
 units = asset_data.get("numberOfUnits", "0")
 if asset_name == "GENESIS":
 genesis_count = int(units)
 print(f" - {asset_name}: {units} units")
 
 print(f" Assets: {len(assets)} total, {genesis_count} GENESIS")
 else:
 print(f" Assets: 0")
 
 results.append({
 "label": label,
 "seed": seed,
 "identity": identity,
 "balance": balance,
 "balance_qubic": balance / 1_000_000,
 "genesis_count": genesis_count,
 "total_assets": len(assets) if assets else 0,
 "valid_for_tick": valid_for_tick,
 })
 except Exception as e:
 print(f" Assets: Error - {e}")
 else:
 print(f" ❌ Could not retrieve balance")
 except Exception as e:
 print(f" ❌ Error: {e}")
 
 print()

print("=" * 80)
print("ZUSAMMENFASSUNG")
print("=" * 80)
print()

total_balance = sum(r.get("balance", 0) for r in results)
total_genesis = sum(r.get("genesis_count", 0) for r in results)

print(f"Total Balance: {total_balance / 1_000_000:.2f} QUBIC")
print(f"Total GENESIS: {total_genesis}")
print()

# Speichere Ergebnisse
output_path = Path("outputs/derived/real_layer2_check.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with output_path.open("w") as f:
 json.dump(results, f, indent=2)

print(f"💾 Results saved to: {output_path}")

