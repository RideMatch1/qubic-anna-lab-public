#!/usr/bin/env python3
"""
Leite die korrekten Layer-2 Identities ab

Methode: Layer-1 Seed → direkt Layer-2 Identity (nicht above Layer-1 Identity)
"""

import json
import subprocess
from pathlib import Path
from typing import Optional

VENV_PATH = Path(__file__).parent.parent.parent / "venv-tx"
OUTPUT_DIR = Path("outputs/derived")

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Leite Identity aus Seed ab."""
 python_exe = VENV_PATH / "bin" / "python"
 
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
 [str(python_exe), "-c", script],
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

def main():
 """Leite alle korrekten Layer-2 Identities ab."""
 
 # Load korrekte Mappings
 with (OUTPUT_DIR / "correct_layer1_to_layer2_mappings.json").open() as f:
 data = json.load(f)
 
 correct_mappings = data["correct_mappings"]
 
 print("=" * 80)
 print("LEITE KORREKTE LAYER-2 IDENTITIES AB")
 print("=" * 80)
 print()
 
 results = []
 
 for mapping in correct_mappings:
 label = mapping["label"]
 layer1_seed = mapping["layer1_seed"]
 expected_layer2 = mapping["expected_layer2_identity"]
 
 print(f"Processing {label}...")
 
 # Korrekte Methode: Layer-1 Seed → direkt Layer-2 Identity
 derived_layer2 = derive_identity_from_seed(layer1_seed)
 
 if derived_layer2 == expected_layer2:
 print(f" ✅ {derived_layer2}")
 results.append({
 "label": label,
 "layer1_seed": layer1_seed,
 "layer2_identity": derived_layer2,
 "expected": expected_layer2,
 "match": True,
 })
 else:
 print(f" ❌ Mismatch!")
 print(f" Expected: {expected_layer2}")
 print(f" Derived: {derived_layer2}")
 results.append({
 "label": label,
 "layer1_seed": layer1_seed,
 "layer2_identity": derived_layer2,
 "expected": expected_layer2,
 "match": False,
 })
 
 print()
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 matches = sum(1 for r in results if r["match"])
 print(f"✅ Korrekt abgeleitet: {matches}/{len(results)}")
 print()
 
 if matches == len(results):
 print("🎯 ALLE LAYER-2 IDENTITIES KORREKT ABGELEITET!")
 else:
 print("⚠️ Einige Identities stimmen nicht aboveein!")
 
 # Speichere Ergebnisse
 output = {
 "summary": {
 "total": len(results),
 "matches": matches,
 "all_correct": matches == len(results),
 },
 "layer2_identities": results,
 }
 
 with (OUTPUT_DIR / "correct_layer2_identities.json").open("w") as f:
 json.dump(output, f, indent=2)
 
 print()
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_DIR / 'correct_layer2_identities.json'}")
 
 # Erstelle auch eine einfache Liste for Smart Contract Tests
 layer2_list = [
 {
 "label": r["label"],
 "seed": r["layer1_seed"],
 "identity": r["layer2_identity"],
 }
 for r in results if r["match"]
 ]
 
 with (OUTPUT_DIR / "correct_layer2_for_contract_tests.json").open("w") as f:
 json.dump(layer2_list, f, indent=2)
 
 print(f"💾 Contract Test Liste gespeichert in: {OUTPUT_DIR / 'correct_layer2_for_contract_tests.json'}")
 
 return output

if __name__ == "__main__":
 main()

