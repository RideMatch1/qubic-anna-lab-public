#!/usr/bin/env python3
"""
Leite Layer-3 Identities for alle Layer-2 Identities ab.

Testet ob die evolutionäre Progression weitergeht und ob Layer-3 Identities
for Oracle Machine Operations existieren.
"""

import json
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.core.identity_constants import SEED_LENGTH

OUTPUT_DIR = Path("outputs/derived")
REPORTS_DIR = Path("outputs/reports")
CHECKPOINT_FILE = OUTPUT_DIR / "layer3_derivation_checkpoint.json"
COMPLETE_FILE = OUTPUT_DIR / "layer3_derivation_complete.json"
REPORT_FILE = REPORTS_DIR / "layer3_derivation_report.md"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:SEED_LENGTH]

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Leite Identity aus Seed ab."""
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{seed}"
seed_bytes = seed.encode('utf-8')
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
"""
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 
 if result.returncode != 0:
 return None
 
 identity = result.stdout.strip()
 if len(identity) == 60 and identity.isupper():
 return identity
 return None
 except Exception:
 return None

def check_identity_onchain(identity: str) -> bool:
 """Check ob Identity on-chain existiert."""
 script = f"""
from qubipy.rpc import rpc_client
identity = "{identity}"
try:
 rpc = rpc_client.QubiPy_RPC()
 balance = rpc.get_balance(identity)
 if balance is not None:
 print("EXISTS")
 else:
 print("NOT_FOUND")
except Exception:
 print("ERROR")
"""
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 return "EXISTS" in result.stdout
 except Exception:
 return False

def load_layer2_identities() -> List[Dict]:
 """Load alle Layer-2 Identities aus Layer-2 Derivation."""
 
 # Check ob Layer-2 Complete File existiert
 layer2_complete = OUTPUT_DIR / "layer2_derivation_complete.json"
 if layer2_complete.exists():
 with layer2_complete.open() as f:
 data = json.load(f)
 results = data.get("results", [])
 # Filtere nur on-chain Layer-2 Identities
 layer2_identities = []
 for r in results:
 if r.get("layer2_onchain", False) and r.get("layer2_identity"):
 layer2_identities.append({
 "layer1_identity": r.get("identity", ""),
 "layer1_seed": r.get("seed", ""),
 "layer2_identity": r.get("layer2_identity", ""),
 "layer2_seed": identity_to_seed(r.get("layer2_identity", "")),
 })
 return layer2_identities
 
 # Fallback: Load aus Checkpoint
 layer2_checkpoint = OUTPUT_DIR / "layer2_derivation_checkpoint.json"
 if layer2_checkpoint.exists():
 with layer2_checkpoint.open() as f:
 data = json.load(f)
 results = data.get("results", [])
 layer2_identities = []
 for r in results:
 if r.get("layer2_onchain", False) and r.get("layer2_identity"):
 layer2_identities.append({
 "layer1_identity": r.get("identity", ""),
 "layer1_seed": r.get("seed", ""),
 "layer2_identity": r.get("layer2_identity", ""),
 "layer2_seed": identity_to_seed(r.get("layer2_identity", "")),
 })
 return layer2_identities
 
 return []

def load_checkpoint() -> Dict:
 """Load Checkpoint for Layer-3 Ableitung."""
 if CHECKPOINT_FILE.exists():
 try:
 with CHECKPOINT_FILE.open() as f:
 return json.load(f)
 except Exception:
 pass
 
 return {
 "processed": 0,
 "results": [],
 "last_processed_index": -1,
 "layer3_derivable_count": 0,
 "layer3_onchain_count": 0,
 "start_time": datetime.now().isoformat(),
 }

def save_checkpoint(checkpoint: Dict):
 """Speichere Checkpoint for Layer-3 Ableitung."""
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 checkpoint["last_update"] = datetime.now().isoformat()
 with CHECKPOINT_FILE.open("w") as f:
 json.dump(checkpoint, f, indent=2)

def write_report(results: Dict, total_layer2: int):
 """Schreibe finalen Report."""
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 total_processed = results["processed"]
 layer3_derivable = results["layer3_derivable_count"]
 layer3_onchain = results["layer3_onchain_count"]
 
 derivable_rate = (layer3_derivable / total_processed * 100) if total_processed > 0 else 0
 onchain_rate = (layer3_onchain / layer3_derivable * 100) if layer3_derivable > 0 else 0
 
 lines = [
 "# Layer-3 Derivation Report",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Overview",
 "This report summarizes the results of deriving Layer-3 identities from Layer-2 identities.",
 "",
 "## Summary of Results",
 f"- **Total Layer-2 identities processed**: {total_processed:,} / {total_layer2:,}",
 f"- **Layer-3 identities derivable**: {layer3_derivable:,} ({derivable_rate:.2f}%)",
 f"- **Layer-3 identities found on-chain**: {layer3_onchain:,} ({onchain_rate:.2f}% of derivable)",
 "",
 "## Interpretation",
 "If Layer-3 derivation works consistently, this confirms:",
 "- Evolutionary progression continues beyond Layer-2",
 "- Layer-3 identities may serve Oracle Machine operations",
 "- The hierarchical structure extends to Layer-3",
 "",
 "## Sample Layer-3 Identities (First 10)",
 "",
 "| Layer-2 Identity (Excerpt) | Layer-3 Identity (Excerpt) | On-Chain |",
 "| --- | --- | --- |",
 ]
 
 for i, res in enumerate(results["results"]):
 if i >= 10:
 break
 lines.append(
 f"| `{res['layer2_identity'][:20]}...` | `{res.get('layer3_identity', 'N/A')[:20]}...` | {'✅' if res.get('layer3_onchain') else '❌'} |"
 )
 lines.append("")
 
 REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
 print(f"[layer3-derivation] ✓ Report -> {REPORT_FILE}")

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("LAYER-3 DERIVATION FOR LAYER-2 IDENTITIES")
 print("=" * 80)
 print()
 
 print("Loading Layer-2 identities...")
 layer2_identities = load_layer2_identities()
 if not layer2_identities:
 print("❌ No Layer-2 identities found. Run Layer-2 derivation first.")
 return
 
 print(f"✅ Loaded {len(layer2_identities):,} Layer-2 identities.")
 print()
 
 checkpoint = load_checkpoint()
 processed = checkpoint.get("processed", 0)
 results = checkpoint.get("results", [])
 
 if processed > 0:
 print(f"✅ Resuming from checkpoint: {processed:,} / {len(layer2_identities):,} processed")
 else:
 print("Starting new Layer-3 derivation.")
 checkpoint = {
 "processed": 0,
 "results": [],
 "last_processed_index": -1,
 "layer3_derivable_count": 0,
 "layer3_onchain_count": 0,
 "start_time": datetime.now().isoformat(),
 }
 print()
 
 start_index = checkpoint["last_processed_index"] + 1
 total_layer2 = len(layer2_identities)
 
 print(f"Processing {total_layer2:,} Layer-2 identities, starting from index {start_index:,}...")
 print("(Saving checkpoint every 50 identities)")
 print()
 
 start_time = time.time()
 for i in range(start_index, total_layer2):
 layer2_data = layer2_identities[i]
 layer2_identity = layer2_data["layer2_identity"]
 layer2_seed = layer2_data["layer2_seed"]
 
 if (i + 1) % 50 == 0:
 save_checkpoint(checkpoint)
 elapsed_time = time.time() - start_time
 identities_per_sec = (i - start_index + 1) / elapsed_time if elapsed_time > 0 else 0
 remaining_identities = total_layer2 - i - 1
 remaining_time_sec = remaining_identities / identities_per_sec if identities_per_sec > 0 else 0
 progress = (i + 1) / total_layer2 * 100
 print(f" Progress: {i+1:,} / {total_layer2:,} ({progress:.1f}%) | Est. remaining: {remaining_time_sec/60:.1f} min")
 
 # Leite Layer-3 ab
 layer3_identity = derive_identity_from_seed(layer2_seed)
 
 is_derivable = layer3_identity is not None
 is_onchain = False
 if is_derivable:
 is_onchain = check_identity_onchain(layer3_identity)
 
 result = {
 "layer1_identity": layer2_data["layer1_identity"],
 "layer2_identity": layer2_identity,
 "layer2_seed": layer2_seed,
 "layer3_identity": layer3_identity,
 "layer3_derivable": is_derivable,
 "layer3_onchain": is_onchain,
 }
 
 checkpoint["results"].append(result)
 checkpoint["processed"] += 1
 checkpoint["last_processed_index"] = i
 
 if is_derivable:
 checkpoint["layer3_derivable_count"] += 1
 if is_onchain:
 checkpoint["layer3_onchain_count"] += 1
 
 save_checkpoint(checkpoint) # Final save
 COMPLETE_FILE.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
 CHECKPOINT_FILE.unlink(missing_ok=True) # Remove checkpoint after completion
 
 print()
 print("=" * 80)
 print("LAYER-3 DERIVATION COMPLETE")
 print("=" * 80)
 print()
 
 write_report(checkpoint, total_layer2)
 print(f"💾 Final results saved to: {COMPLETE_FILE}")
 print(f"📄 Report saved to: {REPORT_FILE}")
 print()

if __name__ == "__main__":
 main()

