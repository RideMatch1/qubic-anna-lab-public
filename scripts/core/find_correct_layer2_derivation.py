#!/usr/bin/env python3
"""
Finde die korrekte Ableitungsmethode for Layer-1 → Layer-2 Identities

Wir wissen:
- 8 Layer-1 Seeds (korrekt)
- 8 erwartete Layer-2 Identities (korrekt)
- Aktuelle Ableitung funktioniert nicht

Ziel: Finde die Methode, die von Layer-1 Seed zu erwarteter Layer-2 Identity führt.
"""

import json
import subprocess
from pathlib import Path
from typing import Optional

VENV_PATH = Path(__file__).parent.parent.parent / "venv-tx"
OUTPUT_DIR = Path("outputs/derived")

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Leite Identity aus Seed ab (Standard-Methode)."""
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

def test_derivation_methods():
 """Teste verschiedene Ableitungsmethoden."""
 
 # Load korrekte Mappings
 with (OUTPUT_DIR / "correct_layer1_to_layer2_mappings.json").open() as f:
 data = json.load(f)
 
 correct_mappings = data["correct_mappings"]
 
 print("=" * 80)
 print("FINDE KORREKTE LAYER-2 ABLEITUNGSMETHODE")
 print("=" * 80)
 print()
 
 results = []
 
 for mapping in correct_mappings:
 label = mapping["label"]
 layer1_seed = mapping["layer1_seed"]
 expected_layer2 = mapping["expected_layer2_identity"]
 
 print(f"Testing {label}...")
 print(f" Layer-1 Seed: {layer1_seed[:40]}...")
 print(f" Expected Layer-2: {expected_layer2}")
 
 # Methode 1: Direkte Ableitung vom Seed
 derived_layer2_method1 = derive_identity_from_seed(layer1_seed)
 
 result = {
 "label": label,
 "layer1_seed": layer1_seed,
 "expected_layer2": expected_layer2,
 "method1_direct": derived_layer2_method1,
 "method1_match": derived_layer2_method1 == expected_layer2,
 }
 
 if derived_layer2_method1:
 if derived_layer2_method1 == expected_layer2:
 print(f" ✅ Method 1 (Direct): MATCH!")
 else:
 print(f" ❌ Method 1 (Direct): {derived_layer2_method1[:40]}...")
 else:
 print(f" ❌ Method 1 (Direct): Failed")
 
 # Methode 2: Seed → Layer-1 Identity → Layer-2 Seed → Layer-2 Identity
 # (Das ist die Methode, die wir bisher verwendet haben)
 layer1_identity = derive_identity_from_seed(layer1_seed)
 if layer1_identity:
 layer2_seed = layer1_identity.lower()[:55]
 derived_layer2_method2 = derive_identity_from_seed(layer2_seed)
 
 result["layer1_identity"] = layer1_identity
 result["layer2_seed"] = layer2_seed
 result["method2_via_identity"] = derived_layer2_method2
 result["method2_match"] = derived_layer2_method2 == expected_layer2
 
 if derived_layer2_method2:
 if derived_layer2_method2 == expected_layer2:
 print(f" ✅ Method 2 (Via Identity): MATCH!")
 else:
 print(f" ❌ Method 2 (Via Identity): {derived_layer2_method2[:40]}...")
 else:
 print(f" ❌ Method 2 (Via Identity): Failed")
 else:
 result["method2_via_identity"] = None
 result["method2_match"] = False
 print(f" ❌ Method 2: Could not derive Layer-1 Identity")
 
 results.append(result)
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 method1_matches = sum(1 for r in results if r.get("method1_match"))
 method2_matches = sum(1 for r in results if r.get("method2_match"))
 
 print(f"Method 1 (Direct from Seed): {method1_matches}/8 matches")
 print(f"Method 2 (Via Identity): {method2_matches}/8 matches")
 print()
 
 if method1_matches == 8:
 print("🎯 METHOD 1 IST KORREKT: Layer-1 Seed → direkt Layer-2 Identity")
 elif method2_matches == 8:
 print("🎯 METHOD 2 IST KORREKT: Layer-1 Seed → Layer-1 Identity → Layer-2 Seed → Layer-2 Identity")
 else:
 print("⚠️ Keine Methode funktioniert for alle 8 Mappings!")
 print(" Möglicherweise gibt es eine andere Ableitungsmethode.")
 
 # Speichere Ergebnisse
 output = {
 "summary": {
 "method1_matches": method1_matches,
 "method2_matches": method2_matches,
 "total": len(results),
 },
 "results": results,
 }
 
 with (OUTPUT_DIR / "layer2_derivation_method_analysis.json").open("w") as f:
 json.dump(output, f, indent=2)
 
 print()
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_DIR / 'layer2_derivation_method_analysis.json'}")
 
 return output

if __name__ == "__main__":
 test_derivation_methods()

