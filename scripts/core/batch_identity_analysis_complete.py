#!/usr/bin/env python3
"""
Batch-Analyse aller gefundenen on-chain Identities.

Analysiert:
- Seeds (identity.lower()[:55])
- Layer-2 Ableitung
- Layer-3 Ableitung (Test)
- On-Chain Status
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

OUTPUT_DIR = Path("outputs/derived")
INPUT_FILE = OUTPUT_DIR / "checksum_identities_onchain_validation_complete.json"
OUTPUT_FILE = OUTPUT_DIR / "all_identities_complete_analysis.json"
CHECKPOINT_FILE = OUTPUT_DIR / "identity_analysis_checkpoint.json"
VENV_PYTHON = Path(__file__).parent.parent.parent / "venv-tx" / "bin" / "python"
BATCH_SIZE = 100
CHECKPOINT_INTERVAL = 50

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

def load_identities() -> List[str]:
 """Load alle on-chain Identities."""
 identities = []
 
 # Check Batch-Speicherung
 complete_file = OUTPUT_DIR / "checksum_identities_onchain_validation_complete.json"
 if complete_file.exists():
 with complete_file.open() as f:
 data = json.load(f)
 
 if "total_batches" in data:
 num_batches = data["total_batches"]
 for i in range(num_batches):
 batch_file = OUTPUT_DIR / f"onchain_identities_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch = json.load(f)
 identities.extend(batch)
 else:
 identities = data.get("onchain_identities", [])
 
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
 "last_processed_index": -1,
 }

def save_checkpoint(checkpoint: Dict):
 """Speichere Checkpoint."""
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with CHECKPOINT_FILE.open("w") as f:
 json.dump(checkpoint, f, indent=2)

def main():
 """Batch-Analyse aller Identities."""
 
 print("=" * 80)
 print("BATCH-ANALYSE ALLER ON-CHAIN IDENTITIES")
 print("=" * 80)
 print()
 
 # Load Identities
 print("Load on-chain Identities...")
 all_identities = load_identities()
 print(f"✅ {len(all_identities):,} Identities geloadn")
 print()
 
 if not all_identities:
 print("❌ Keine Identities gefunden!")
 return
 
 # Load Checkpoint
 checkpoint = load_checkpoint()
 if checkpoint.get("processed", 0) > 0:
 print(f"✅ Checkpoint geloadn: {checkpoint['processed']:,} bereits analysiert")
 print()
 
 # Initialisiere
 if not checkpoint.get("results"):
 checkpoint["results"] = []
 
 results = checkpoint["results"]
 start_index = checkpoint.get("last_processed_index", -1) + 1
 
 if not VENV_PYTHON.exists():
 print(f"❌ venv-tx Python nicht gefunden: {VENV_PYTHON}")
 return
 
 # Analyze Identities
 print(f"Analyze {len(all_identities):,} Identities...")
 print(f"Starte ab Index: {start_index}")
 print()
 
 total = len(all_identities)
 
 for i, identity in enumerate(all_identities[start_index:], start_index):
 if i % CHECKPOINT_INTERVAL == 0 and i > start_index:
 print(f" Progress: {i:,}/{total:,} ({i/total*100:.1f}%)")
 
 # Speichere Checkpoint
 checkpoint["processed"] = i + 1
 checkpoint["last_processed_index"] = i
 checkpoint["results"] = results
 save_checkpoint(checkpoint)
 
 # Extrahiere Seed
 seed = identity_to_seed(identity)
 
 # Layer-2 Ableitung
 layer2_identity = derive_identity_from_seed(seed)
 layer2_onchain = False
 if layer2_identity:
 layer2_onchain = check_identity_onchain(layer2_identity)
 
 # Layer-3 Ableitung (Test)
 layer3_identity = None
 layer3_onchain = False
 if layer2_identity:
 layer2_seed = layer2_identity.lower()[:55]
 layer3_identity = derive_identity_from_seed(layer2_seed)
 if layer3_identity:
 layer3_onchain = check_identity_onchain(layer3_identity)
 
 result = {
 "identity": identity,
 "seed": seed,
 "layer2_identity": layer2_identity,
 "layer2_onchain": layer2_onchain,
 "layer3_identity": layer3_identity,
 "layer3_onchain": layer3_onchain,
 }
 
 results.append(result)
 
 print()
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 total_analyzed = len(results)
 seeds_found = sum(1 for r in results if r.get("seed"))
 layer2_derivable = sum(1 for r in results if r.get("layer2_identity"))
 layer2_onchain = sum(1 for r in results if r.get("layer2_onchain"))
 layer3_derivable = sum(1 for r in results if r.get("layer3_identity"))
 layer3_onchain = sum(1 for r in results if r.get("layer3_onchain"))
 
 print(f"Analysiert: {total_analyzed:,}")
 print(f"Seeds gefunden: {seeds_found:,} ({seeds_found/total_analyzed*100:.1f}%)")
 print(f"Layer-2 ableitbar: {layer2_derivable:,} ({layer2_derivable/total_analyzed*100:.1f}%)")
 print(f"Layer-2 on-chain: {layer2_onchain:,} ({layer2_onchain/layer2_derivable*100:.1f}% von ableitbaren)" if layer2_derivable > 0 else "Layer-2 on-chain: 0")
 print(f"Layer-3 ableitbar: {layer3_derivable:,} ({layer3_derivable/total_analyzed*100:.1f}%)")
 print(f"Layer-3 on-chain: {layer3_onchain:,} ({layer3_onchain/layer3_derivable*100:.1f}% von ableitbaren)" if layer3_derivable > 0 else "Layer-3 on-chain: 0")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "summary": {
 "total_analyzed": total_analyzed,
 "seeds_found": seeds_found,
 "layer2_derivable": layer2_derivable,
 "layer2_onchain": layer2_onchain,
 "layer3_derivable": layer3_derivable,
 "layer3_onchain": layer3_onchain,
 },
 "results": results[:1000], # Nur Stichprobe for JSON
 }
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 
 # Lösche Checkpoint
 if CHECKPOINT_FILE.exists():
 CHECKPOINT_FILE.unlink()
 print("✅ Checkpoint gelöscht (Analyse komplett)")

if __name__ == "__main__":
 main()
