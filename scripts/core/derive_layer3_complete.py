#!/usr/bin/env python3
"""
Derive Layer-3 Identities Complete

Leitet Layer-3 Identities von Layer-2 ab und prüft on-chain Status.
Mit Checkpointing for lange Läufe.
"""

import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"
CHECKPOINT_FILE = OUTPUT_DIR / "layer3_derivation_checkpoint.json"
COMPLETE_FILE = OUTPUT_DIR / "layer3_derivation_complete.json"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Leite Identity aus Seed ab."""
 if not VENV_PYTHON.exists():
 return None
 
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
 
 if result.returncode == 0:
 identity = result.stdout.strip()
 if len(identity) == 60 and identity.isupper():
 return identity
 return None
 except Exception:
 return None

def check_identity_onchain(identity: str) -> bool:
 """Check ob Identity on-chain existiert."""
 if not VENV_PYTHON.exists():
 return False
 
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

def load_layer2_identities() -> List[str]:
 """Load Layer-2 Identities."""
 identities = []
 
 # Versuche aus Layer-2 Complete
 layer2_file = OUTPUT_DIR / "layer2_derivation_complete.json"
 if layer2_file.exists():
 with layer2_file.open() as f:
 data = json.load(f)
 for result in data.get("results", []):
 if result.get("layer2_onchain") and result.get("layer2_identity"):
 identities.append(result["layer2_identity"])
 
 # Fallback: Leite von Layer-1 ab
 if not identities:
 onchain_file = OUTPUT_DIR / "checksum_identities_onchain_validation_complete.json"
 if onchain_file.exists():
 with onchain_file.open() as f:
 data = json.load(f)
 # Load Layer-1 Identities und leite Layer-2 ab
 num_batches = data.get("total_batches", 0)
 layer1_identities = []
 for i in range(min(10, num_batches)): # Limit for Test
 batch_file = OUTPUT_DIR / f"onchain_identities_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch_data = json.load(f)
 if isinstance(batch_data, list):
 layer1_identities.extend(batch_data[:10]) # Limit
 
 # Leite Layer-2 ab
 for identity in layer1_identities:
 seed = identity_to_seed(identity)
 layer2 = derive_identity_from_seed(seed)
 if layer2:
 identities.append(layer2)
 
 return identities[:100] # Limit for Test

def load_checkpoint() -> Dict:
 """Load Checkpoint."""
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
 }

def save_checkpoint(checkpoint: Dict):
 """Speichere Checkpoint."""
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with CHECKPOINT_FILE.open("w") as f:
 json.dump(checkpoint, f, indent=2)

def main():
 print("=" * 80)
 print("DERIVE LAYER-3 IDENTITIES COMPLETE")
 print("=" * 80)
 print()
 
 print("Loading Layer-2 identities...")
 layer2_identities = load_layer2_identities()
 print(f"✅ Loaded {len(layer2_identities)} Layer-2 identities")
 print()
 
 checkpoint = load_checkpoint()
 if checkpoint["processed"] > 0:
 print(f"✅ Resuming from checkpoint: {checkpoint['processed']:,} identities already processed.")
 else:
 print("Starting new Layer-3 derivation.")
 checkpoint = {
 "processed": 0,
 "results": [],
 "last_processed_index": -1,
 "layer3_derivable_count": 0,
 "layer3_onchain_count": 0,
 }
 print()
 
 start_index = checkpoint["last_processed_index"] + 1
 total_identities = len(layer2_identities)
 
 print(f"Processing {total_identities:,} Layer-2 identities, starting from index {start_index:,}...")
 print("(Saving checkpoint every 10 identities)")
 print()
 
 start_time = time.time()
 for i in range(start_index, total_identities):
 layer2_identity = layer2_identities[i]
 
 if i > start_index and i % 10 == 0:
 save_checkpoint(checkpoint)
 elapsed_time = time.time() - start_time
 identities_per_sec = (i - start_index) / elapsed_time if elapsed_time > 0 else 0
 remaining_identities = total_identities - i
 remaining_time_sec = remaining_identities / identities_per_sec if identities_per_sec > 0 else 0
 print(f" Progress: {i:,}/{total_identities:,} ({i/total_identities*100:.1f}%) | Est. remaining: {remaining_time_sec/60:.1f} min")
 
 seed = identity_to_seed(layer2_identity)
 layer3_identity = derive_identity_from_seed(seed)
 
 is_derivable = layer3_identity is not None
 is_onchain = False
 if is_derivable:
 is_onchain = check_identity_onchain(layer3_identity)
 
 result = {
 "layer2_identity": layer2_identity,
 "seed": seed,
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
 
 save_checkpoint(checkpoint)
 COMPLETE_FILE.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
 CHECKPOINT_FILE.unlink(missing_ok=True)
 
 print()
 print("=" * 80)
 print("LAYER-3 DERIVATION COMPLETE")
 print("=" * 80)
 print()
 print(f"✅ Final results saved to: {COMPLETE_FILE}")
 print(f" Layer-3 derivable: {checkpoint['layer3_derivable_count']:,}")
 print(f" Layer-3 on-chain: {checkpoint['layer3_onchain_count']:,}")
 print()

if __name__ == "__main__":
 main()

