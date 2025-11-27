#!/usr/bin/env python3
"""
Vollständige Struktur-Mapping for alle gefundenen Layer-1 Einstiegspunkte.

Mappt Layer 1 → 2 → 3 → ... → 8 for alle gefundenen Identities.
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict

OUTPUT_DIR = Path("outputs/derived")
INPUT_FILE = OUTPUT_DIR / "all_identities_complete_analysis.json"
OUTPUT_FILE = OUTPUT_DIR / "complete_structure_mapping_all.json"
CHECKPOINT_FILE = OUTPUT_DIR / "structure_mapping_checkpoint.json"
VENV_PYTHON = Path(__file__).parent.parent.parent / "venv-tx" / "bin" / "python"
MAX_LAYERS = 8

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

def map_structure_for_identity(layer1_identity: str, max_layers: int = 8) -> Dict:
 """Mappe vollständige Struktur for eine Identity."""
 
 structure = {
 "layer1_identity": layer1_identity,
 "layer1_seed": identity_to_seed(layer1_identity),
 "path": [],
 "max_layer": 0,
 }
 
 current_seed = structure["layer1_seed"]
 
 for layer in range(1, max_layers + 1):
 identity = derive_identity_from_seed(current_seed)
 
 if not identity:
 break
 
 structure["path"].append({
 "layer": layer,
 "seed": current_seed,
 "identity": identity,
 })
 
 structure["max_layer"] = layer
 
 # Für nächste Layer
 if layer < max_layers:
 current_seed = identity.lower()[:55]
 
 return structure

def main():
 """Vollständige Struktur-Mapping."""
 
 print("=" * 80)
 print("VOLLSTÄNDIGE STRUKTUR-MAPPING")
 print("=" * 80)
 print()
 
 # Load Identities
 if not INPUT_FILE.exists():
 print(f"❌ Input-Datei nicht gefunden: {INPUT_FILE}")
 print(" Führe zuerst batch_identity_analysis_complete.py aus")
 return
 
 with INPUT_FILE.open() as f:
 data = json.load(f)
 
 results = data.get("results", [])
 layer1_identities = [r["identity"] for r in results if r.get("identity")]
 
 print(f"Geloadn: {len(layer1_identities):,} Layer-1 Identities")
 print()
 
 if not VENV_PYTHON.exists():
 print(f"❌ venv-tx Python nicht gefunden: {VENV_PYTHON}")
 return
 
 # Load Checkpoint
 checkpoint = {}
 if CHECKPOINT_FILE.exists():
 with CHECKPOINT_FILE.open() as f:
 checkpoint = json.load(f)
 
 processed = checkpoint.get("processed", 0)
 structures = checkpoint.get("structures", [])
 
 if processed > 0:
 print(f"✅ Checkpoint geloadn: {processed:,} bereits gemappt")
 print()
 
 # Mappe Strukturen
 print(f"Mappe Strukturen for {len(layer1_identities):,} Identities...")
 print(f"Starte ab Index: {processed}")
 print()
 
 for i, identity in enumerate(layer1_identities[processed:], processed):
 if i % 100 == 0 and i > processed:
 print(f" Progress: {i:,}/{len(layer1_identities):,} ({i/len(layer1_identities)*100:.1f}%)")
 
 # Speichere Checkpoint
 checkpoint["processed"] = i + 1
 checkpoint["structures"] = structures
 with CHECKPOINT_FILE.open("w") as f:
 json.dump(checkpoint, f, indent=2)
 
 structure = map_structure_for_identity(identity, MAX_LAYERS)
 structures.append(structure)
 
 print()
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 layer_counts = defaultdict(int)
 for structure in structures:
 max_layer = structure.get("max_layer", 0)
 layer_counts[max_layer] += 1
 
 print("Layer-Verteilung:")
 for layer in sorted(layer_counts.keys()):
 print(f" Layer {layer}: {layer_counts[layer]:,} Identities erreichen diese Tiefe")
 
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "summary": {
 "total_identities": len(structures),
 "max_layer_reached": max(layer_counts.keys()) if layer_counts else 0,
 "layer_counts": dict(layer_counts),
 },
 "structures": structures[:100], # Nur Stichprobe
 }
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 
 # Lösche Checkpoint
 if CHECKPOINT_FILE.exists():
 CHECKPOINT_FILE.unlink()
 print("✅ Checkpoint gelöscht (Mapping komplett)")

if __name__ == "__main__":
 main()
