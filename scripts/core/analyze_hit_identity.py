
import json
import time
from qubipy.rpc import rpc_client

hit_identity = "BZBQFLLBNCXEMGLOBHUVFTLUPLVCPQUASSILFABOFFBCADQSSUPNWLZBQEXK"

rpc = rpc_client.QubiPy_RPC()

print("=" * 80)
print("DETAILLIERTE ASSET-ANALYSE")
print("=" * 80)
print()

try:
 time.sleep(2.0)
 assets = rpc.get_owned_assets(hit_identity)
 
 print(f"Identity: {hit_identity}")
 print(f"Assets gefunden: {len(assets) if assets else 0}")
 print()
 
 if assets:
 print("Asset-Details:")
 for i, asset in enumerate(assets, 1):
 print(f" {i}. Asset ID: {asset.get('asset_id', 'N/A')}")
 print(f" Name: {asset.get('name', 'N/A')}")
 print(f" Amount: {asset.get('amount', 'N/A')}")
 print(f" Issuer: {asset.get('issuer', 'N/A')}")
 print()
 
 # Check auch Balance und History
 time.sleep(2.0)
 balance_data = rpc.get_balance(hit_identity)
 if balance_data:
 print(f"Balance: {balance_data.get('balance', 0)} QU")
 print(f"Valid for Tick: {balance_data.get('validForTick', 'N/A')}")
 print()
 
 try:
 time.sleep(2.0)
 history = rpc.get_transaction_history(hit_identity, limit=20)
 if history:
 print(f"Transaction History: {len(history)} transactions")
 print()
 print("Letzte 5 Transaktionen:")
 for i, tx in enumerate(history[:5], 1):
 print(f" {i}. Tick: {tx.get('tick', 'N/A')}, Amount: {tx.get('amount', 'N/A')}")
 else:
 print("Transaction History: Keine Transaktionen")
 except Exception as e:
 print(f"History Error: {e}")
 
 # Speichere detaillierte Ergebnisse
 result = {
 "identity": hit_identity,
 "method": "Alternating XOR",
 "assets": assets if assets else [],
 "balance": balance_data.get("balance", 0) if balance_data else 0,
 "valid_for_tick": balance_data.get("validForTick", 0) if balance_data else 0,
 "history": history if history else [],
 }
 
 with open("outputs/derived/hit_identity_detailed_analysis.json", "w") as f:
 json.dump(result, f, indent=2)
 
 print()
 print("✅ Detaillierte Analyse gespeichert")

except Exception as e:
 print(f"❌ Error: {e}")
 import traceback
 traceback.print_exc()
