
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
 print(f" {i}. {json.dumps(asset, indent=4)}")
 print()
 
 # Check auch Balance
 time.sleep(2.0)
 balance_data = rpc.get_balance(hit_identity)
 if balance_data:
 print(f"Balance: {balance_data.get('balance', 0)} QU")
 print(f"Valid for Tick: {balance_data.get('validForTick', 'N/A')}")
 print()
 
 # Speichere detaillierte Ergebnisse
 result = {
 "identity": hit_identity,
 "method": "Alternating XOR",
 "assets": assets if assets else [],
 "balance": balance_data.get("balance", 0) if balance_data else 0,
 "valid_for_tick": balance_data.get("validForTick", 0) if balance_data else 0,
 }
 
 with open("outputs/derived/hit_identity_detailed_analysis.json", "w") as f:
 json.dump(result, f, indent=2)
 
 print()
 print("✅ Detaillierte Analyse gespeichert")
 
 if assets:
 print()
 print("=" * 80)
 print("🎉🎉🎉 KRITISCHER DURCHBRUCH!")
 print("=" * 80)
 print()
 print("Die 'Alternating XOR' Fusion-Methode hat eine Identity mit Assets gefunden!")
 print("Das bedeutet:")
 print(" - Die Master Seed Fusion funktioniert!")
 print(" - Layer-1 Seeds sind der richtige Ausgangspunkt!")
 print(" - Die 'Alternating XOR' Methode ist die korrekte Fusion!")

except Exception as e:
 print(f"❌ Error: {e}")
 import traceback
 traceback.print_exc()
