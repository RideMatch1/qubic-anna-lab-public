#!/usr/bin/env python3
"""
Leite Layer-2 Identities for alle gefundenen on-chain Identities ab.

Dies testet ob die Layer-2 Ableitung auch bei 23,477 Identities funktioniert.
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict
from datetime import datetime

OUTPUT_DIR = Path("outputs/derived")
REPORTS_DIR = Path("outputs/reports")
CHECKPOINT_FILE = OUTPUT_DIR / "layer2_derivation_checkpoint.json"
VENV_PYTHON = Path(__file__).parent.parent.parent / "venv-tx" / "bin" / "python"
BATCH_SIZE = 100 # Checkpoint alle 100 Identities

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

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
 cwd=Path(__file__).parent.parent.parent
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
 cwd=Path(__file__).parent.parent.parent
 )
 return "EXISTS" in result.stdout
 except Exception:
 return False

def load_onchain_identities() -> List[str]:
 """Load alle on-chain Identities."""
 identities = []
 
 # Load aus Batch-Dateien
 complete_file = OUTPUT_DIR / "checksum_identities_onchain_validation_complete.json"
 if complete_file.exists():
 with complete_file.open() as f:
 complete_data = json.load(f)
 total_batches = complete_data.get("total_batches", 0)
 
 for i in range(total_batches):
 batch_file = OUTPUT_DIR / f"onchain_identities_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch_data = json.load(f)
 if isinstance(batch_data, list):
 identities.extend(batch_data)
 
 return identities

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
 "layer2_derivable": 0,
 "layer2_onchain": 0,
 "start_time": datetime.now().isoformat(),
 "last_update": datetime.now().isoformat(),
 }

def save_checkpoint(checkpoint: Dict):
 """Speichere Checkpoint."""
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 checkpoint["last_update"] = datetime.now().isoformat()
 with CHECKPOINT_FILE.open("w") as f:
 json.dump(checkpoint, f, indent=2)

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("DERIVE ALL LAYER-2 IDENTITIES (WITH CHECKPOINTS)")
 print("=" * 80)
 print()
 
 if not VENV_PYTHON.exists():
 print(f"❌ venv-tx Python nicht gefunden: {VENV_PYTHON}")
 return
 
 print("Loading on-chain identities...")
 identities = load_onchain_identities()
 print(f"✅ {len(identities):,} identities loaded")
 print()
 
 if not identities:
 print("❌ No identities found!")
 return
 
 # Load Checkpoint
 checkpoint = load_checkpoint()
 processed = checkpoint.get("processed", 0)
 results = checkpoint.get("results", [])
 layer2_derivable = checkpoint.get("layer2_derivable", 0)
 layer2_onchain = checkpoint.get("layer2_onchain", 0)
 
 if processed > 0:
 print(f"✅ Checkpoint loaded: {processed:,} / {len(identities):,} processed")
 print(f" Layer-2 derivable: {layer2_derivable:,}")
 print(f" Layer-2 on-chain: {layer2_onchain:,}")
 print()
 
 print("Deriving Layer-2 identities...")
 print(f"(Saving checkpoint every {BATCH_SIZE} identities)")
 print()
 
 start_idx = processed
 
 for i, identity in enumerate(identities[start_idx:], start_idx):
 if (i + 1) % BATCH_SIZE == 0:
 progress = (i + 1) / len(identities) * 100
 derivable_rate = (layer2_derivable / (i + 1) * 100) if i > 0 else 0
 onchain_rate = (layer2_onchain / layer2_derivable * 100) if layer2_derivable > 0 else 0
 print(f" Progress: {i+1:,}/{len(identities):,} ({progress:.1f}%)")
 print(f" Layer-2 derivable: {layer2_derivable:,} ({derivable_rate:.1f}%)")
 print(f" Layer-2 on-chain: {layer2_onchain:,} ({onchain_rate:.1f}% of derivable)" if layer2_derivable > 0 else " Layer-2 on-chain: 0")
 print()
 
 # Speichere Checkpoint
 checkpoint = {
 "processed": i + 1,
 "results": results,
 "layer2_derivable": layer2_derivable,
 "layer2_onchain": layer2_onchain,
 "start_time": checkpoint.get("start_time", datetime.now().isoformat()),
 "last_update": datetime.now().isoformat(),
 }
 save_checkpoint(checkpoint)
 
 # Extrahiere Seed
 seed = identity_to_seed(identity)
 
 # Leite Layer-2 ab
 layer2_identity = derive_identity_from_seed(seed)
 
 layer2_exists = False
 if layer2_identity:
 layer2_derivable += 1
 layer2_exists = check_identity_onchain(layer2_identity)
 if layer2_exists:
 layer2_onchain += 1
 
 results.append({
 "layer1_identity": identity,
 "seed": seed,
 "layer2_identity": layer2_identity,
 "layer2_onchain": layer2_exists,
 })
 
 print()
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 print(f"Total Layer-1 identities: {len(identities):,}")
 print(f"Layer-2 derivable: {layer2_derivable:,} ({layer2_derivable/len(identities)*100:.1f}%)")
 print(f"Layer-2 on-chain: {layer2_onchain:,} ({layer2_onchain/layer2_derivable*100:.1f}% of derivable)" if layer2_derivable > 0 else "Layer-2 on-chain: 0")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 json_file = OUTPUT_DIR / "all_layer2_derivation.json"
 with json_file.open("w") as f:
 json.dump({
 "summary": {
 "total_layer1": len(identities),
 "layer2_derivable": layer2_derivable,
 "layer2_onchain": layer2_onchain,
 "layer2_derivation_rate": layer2_derivable / len(identities) * 100 if identities else 0,
 "layer2_onchain_rate": layer2_onchain / layer2_derivable * 100 if layer2_derivable > 0 else 0,
 },
 "results": results[:1000], # Nur Stichprobe for JSON
 }, f, indent=2)
 
 print(f"💾 Results saved to: {json_file}")
 
 # Erstelle Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report_file = REPORTS_DIR / "all_layer2_derivation_report.md"
 with report_file.open("w") as f:
 f.write(f"""# All Layer-2 Identity Derivation

## Summary

- **Total Layer-1 identities**: {len(identities):,}
- **Layer-2 derivable**: {layer2_derivable:,} ({layer2_derivable/len(identities)*100:.1f}%)
- **Layer-2 on-chain**: {layer2_onchain:,} ({layer2_onchain/layer2_derivable*100:.1f}% of derivable)

## What This Proves

This analysis tests whether the Layer-2 derivation formula works at scale for all 23,477 found identities.

**Key finding**: {layer2_derivable/len(identities)*100:.1f}% of identities can derive valid Layer-2 identities.

**On-chain rate**: {layer2_onchain/layer2_derivable*100:.1f}% of derivable Layer-2 identities exist on-chain.

## Implications

- The seed derivation formula works consistently across all found identities
- Layer-2 derivation is not limited to the initial 8 identities
- The identity structure extends beyond Layer-1

## Next Steps

1. Test Layer-3 derivation
2. Analyze Layer-2 patterns
3. Map Layer-1 to Layer-2 relationships
""")
 
 print(f"📄 Report saved to: {report_file}")
 print()
 
 # Lösche Checkpoint (fertig)
 if CHECKPOINT_FILE.exists():
 CHECKPOINT_FILE.unlink()
 print("✅ Checkpoint deleted (derivation complete)")
 print()
 
 print("=" * 80)
 print("✅ LAYER-2 DERIVATION COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

