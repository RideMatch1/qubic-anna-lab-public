#!/usr/bin/env python3
"""
On-Chain Validierung ALLER gefundenen Identities

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
Prüft jede Identity gegen die Qubic Blockchain.
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

VENV_PATH = Path(__file__).parent.parent.parent / "venv-tx"
OUTPUT_DIR = Path("outputs/derived")
SCAN_FILE = OUTPUT_DIR / "comprehensive_identity_seed_scan.json"
OUTPUT_JSON = OUTPUT_DIR / "onchain_validation_all_identities.json"
OUTPUT_MD = OUTPUT_DIR / "ONCHAIN_VALIDATION_ALL_IDENTITIES.md"
CHECKPOINT_FILE = OUTPUT_DIR / "onchain_validation_checkpoint.json"

# Qubic RPC Nodes
RPC_NODES = [
 "95.217.207.236:21841",
 "65.108.75.114:21841",
 "65.21.234.94:21841",
 "135.181.73.60:21841",
 "65.108.9.105:21841",
]

def check_identity_onchain(identity: str) -> Dict:
 """Check Identity gegen Qubic Blockchain (mit venv-tx und qubipy)."""
 python_exe = VENV_PATH / "bin" / "python"
 
 script = f"""
from qubipy.rpc import rpc_client
import json
import sys

identity = "{identity}"

try:
 rpc = rpc_client.QubiPy_RPC()
 balance_data = rpc.get_balance(identity)
 
 if balance_data:
 result = {{
 "exists": True,
 "balance": balance_data.get("balance", 0),
 "validForTick": balance_data.get("validForTick", None),
 "incomingAmount": balance_data.get("incomingAmount", 0),
 "outgoingAmount": balance_data.get("outgoingAmount", 0),
 }}
 else:
 result = {{
 "exists": False,
 "balance": None,
 "validForTick": None,
 }}
 
 print(json.dumps(result))
except Exception as e:
 print(json.dumps({{
 "exists": False,
 "balance": None,
 "validForTick": None,
 "error": str(e)
 }}))
"""
 
 result = subprocess.run(
 [str(python_exe), "-c", script],
 capture_output=True,
 text=True,
 cwd=Path(__file__).parent.parent.parent,
 timeout=15
 )
 
 if result.returncode == 0 and result.stdout:
 try:
 return json.loads(result.stdout.strip())
 except:
 pass
 
 return {
 "exists": False,
 "balance": None,
 "validForTick": None,
 "error": "Could not check",
 }

def main():
 print("=" * 80)
 print("ON-CHAIN VALIDATION: ALL IDENTITIES")
 print("=" * 80)
 print()
 print("WICHTIG: Nur echte, nachgewiesene Erkenntnisse!")
 print()
 
 if not VENV_PATH.exists():
 print(f"❌ venv-tx not found at: {VENV_PATH}")
 return False
 
 if not SCAN_FILE.exists():
 print(f"❌ Scan file not found: {SCAN_FILE}")
 return False
 
 # Load alle Identities
 print("Loading identities from scan results...")
 with SCAN_FILE.open() as f:
 scan_data = json.load(f)
 
 all_identities = scan_data.get("all_identities", [])
 print(f"✅ Loaded {len(all_identities)} unique identities")
 print()
 
 # Load Checkpoint falls vorhanden
 results = []
 onchain_count = 0
 total_checked = 0
 start_idx = 0
 
 if CHECKPOINT_FILE.exists():
 try:
 print("Loading checkpoint...")
 with CHECKPOINT_FILE.open() as f:
 checkpoint = json.load(f)
 total_checked = checkpoint.get("total_checked", 0)
 onchain_count = checkpoint.get("onchain_count", 0)
 results = checkpoint.get("results", [])
 start_idx = total_checked
 
 print(f"✅ Checkpoint loaded: {total_checked}/{len(all_identities)} identities already checked")
 print(f" On-chain: {onchain_count} ({onchain_count/total_checked*100:.1f}%)")
 print()
 except Exception as e:
 print(f"⚠️ Could not load checkpoint: {e}")
 print("Starting from beginning...")
 print()
 
 # Check jede Identity
 print("=" * 80)
 print("CHECKING IDENTITIES ON-CHAIN")
 print("=" * 80)
 print()
 
 # Check in Batches (for Progress-Anzeige)
 batch_size = 50
 total_batches = (len(all_identities) + batch_size - 1) // batch_size
 start_batch = start_idx // batch_size
 
 for batch_idx in range(start_batch, total_batches):
 start_idx = batch_idx * batch_size
 end_idx = min(start_idx + batch_size, len(all_identities))
 batch = all_identities[start_idx:end_idx]
 
 print(f"Batch {batch_idx + 1}/{total_batches} ({start_idx + 1}-{end_idx}/{len(all_identities)})...")
 
 for identity in batch:
 total_checked += 1
 result = check_identity_onchain(identity)
 
 result["identity"] = identity
 results.append(result)
 
 if result.get("exists"):
 onchain_count += 1
 balance = result.get("balance", 0)
 tick = result.get("validForTick", "N/A")
 print(f" ✅ {identity[:40]}... | Balance: {balance} QU | Tick: {tick}")
 elif total_checked % 10 == 0:
 print(f" ... checked {total_checked}/{len(all_identities)}")
 
 if total_checked > 0:
 print(f" Progress: {onchain_count}/{total_checked} on-chain ({onchain_count/total_checked*100:.1f}%)")
 print()
 
 # Speichere Zwischenergebnisse
 checkpoint = {
 "total_checked": total_checked,
 "onchain_count": onchain_count,
 "results": results,
 }
 checkpoint_file = OUTPUT_DIR / "onchain_validation_checkpoint.json"
 with checkpoint_file.open("w") as f:
 json.dump(checkpoint, f, indent=2)
 
 # Zusammenfassung
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 print(f"Total identities checked: {len(all_identities)}")
 print(f"On-chain identities: {onchain_count}")
 print(f"Off-chain identities: {len(all_identities) - onchain_count}")
 print(f"On-chain rate: {(onchain_count / len(all_identities) * 100):.1f}%")
 print()
 
 # Layer-Analyse
 layer_stats = defaultdict(lambda: {"total": 0, "onchain": 0})
 
 # Finde Layer for jede Identity
 seed_results = scan_data.get("seed_results", [])
 identity_to_layer = {}
 
 for seed_result in seed_results:
 for layer, identity in seed_result.get("derived_identities", {}).items():
 identity_to_layer[identity] = layer
 
 for result in results:
 identity = result["identity"]
 layer = identity_to_layer.get(identity, "unknown")
 layer_stats[layer]["total"] += 1
 if result.get("exists"):
 layer_stats[layer]["onchain"] += 1
 
 print("Layer statistics:")
 for layer in sorted(layer_stats.keys()):
 stats = layer_stats[layer]
 onchain_pct = (stats["onchain"] / stats["total"] * 100) if stats["total"] > 0 else 0
 print(f" Layer {layer}: {stats['onchain']}/{stats['total']} on-chain ({onchain_pct:.1f}%)")
 print()
 
 # Balance-Analyse
 balances = [int(r.get("balance", 0)) if isinstance(r.get("balance"), str) else r.get("balance", 0) for r in results if r.get("exists")]
 if balances:
 total_balance = sum(balances)
 non_zero = sum(1 for b in balances if b > 0)
 print(f"Balance statistics:")
 print(f" Total balance: {total_balance} QU")
 print(f" Identities with balance > 0: {non_zero}/{len(balances)}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 final_results = {
 "summary": {
 "total_checked": len(all_identities),
 "onchain_count": onchain_count,
 "offchain_count": len(all_identities) - onchain_count,
 "onchain_rate": (onchain_count / len(all_identities) * 100) if all_identities else 0,
 },
 "layer_statistics": {
 str(layer): {
 "total": stats["total"],
 "onchain": stats["onchain"],
 "onchain_rate": (stats["onchain"] / stats["total"] * 100) if stats["total"] > 0 else 0,
 }
 for layer, stats in layer_stats.items()
 },
 "results": results,
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(final_results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# On-Chain Validation: All Identities\n\n")
 f.write("## Summary\n\n")
 f.write(f"- **Total identities checked**: {len(all_identities)}\n")
 f.write(f"- **On-chain identities**: {onchain_count}\n")
 f.write(f"- **Off-chain identities**: {len(all_identities) - onchain_count}\n")
 f.write(f"- **On-chain rate**: {(onchain_count / len(all_identities) * 100):.1f}%\n\n")
 
 f.write("## Layer Statistics\n\n")
 for layer in sorted(layer_stats.keys()):
 stats = layer_stats[layer]
 onchain_pct = (stats["onchain"] / stats["total"] * 100) if stats["total"] > 0 else 0
 f.write(f"### Layer {layer}\n\n")
 f.write(f"- Total: {stats['total']}\n")
 f.write(f"- On-chain: {stats['onchain']}\n")
 f.write(f"- On-chain rate: {onchain_pct:.1f}%\n\n")
 
 if balances:
 f.write("## Balance Statistics\n\n")
 f.write(f"- Total balance: {total_balance} QU\n")
 f.write(f"- Identities with balance > 0: {non_zero}/{len(balances)}\n\n")
 
 f.write("## On-Chain Identities\n\n")
 onchain_results = [r for r in results if r.get("exists")]
 f.write(f"Total: {len(onchain_results)}\n\n")
 for result in onchain_results[:100]: # Erste 100
 f.write(f"- `{result['identity']}` | Balance: {result.get('balance', 0)} QU | Tick: {result.get('validForTick', 'N/A')}\n")
 if len(onchain_results) > 100:
 f.write(f"\n... and {len(onchain_results) - 100} more\n")
 
 print("=" * 80)
 print("✅ VALIDATION COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")
 print()
 print(f"📊 {onchain_count}/{len(all_identities)} identities exist on-chain")
 
 return True

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)

