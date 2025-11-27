#!/usr/bin/env python3
"""
Analyze die 98 gefundenen on-chain Identities.

Prüft:
1. Haben sie Seeds/Private Keys? (identity.lower()[:55])
2. Können wir weitere Layer ableiten?
3. Welche Patterns haben sie?
"""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

OUTPUT_DIR = Path("outputs/derived")
INPUT_FILE = OUTPUT_DIR / "checksum_identities_onchain_validation.json"
OUTPUT_FILE = OUTPUT_DIR / "found_identities_analysis.json"
VENV_PYTHON = Path(__file__).parent.parent.parent / "venv-tx" / "bin" / "python"

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

def main():
 """Analyze gefundene Identities."""
 
 print("=" * 80)
 print("ANALYSE DER 98 GEFUNDENEN IDENTITIES")
 print("=" * 80)
 print()
 
 # Load Identities
 if not INPUT_FILE.exists():
 print(f"❌ Input-Datei nicht gefunden: {INPUT_FILE}")
 return
 
 with INPUT_FILE.open() as f:
 data = json.load(f)
 
 onchain_identities = data.get("onchain_identities", [])
 print(f"Geloadn: {len(onchain_identities)} Identities")
 print()
 
 if not VENV_PYTHON.exists():
 print(f"❌ venv-tx Python nicht gefunden: {VENV_PYTHON}")
 return
 
 # Analyze Identities
 results = []
 seeds_found = 0
 layer2_derivable = 0
 layer2_onchain = 0
 
 for i, identity in enumerate(onchain_identities, 1):
 if i % 20 == 0:
 print(f" Progress: {i}/{len(onchain_identities)}...")
 
 # Extrahiere Seed
 seed = identity_to_seed(identity)
 
 # Versuche Layer-2 Identity abzuleiten
 layer2_identity = derive_identity_from_seed(seed)
 
 layer2_exists = False
 if layer2_identity:
 layer2_exists = check_identity_onchain(layer2_identity)
 if layer2_exists:
 layer2_onchain += 1
 
 result = {
 "identity": identity,
 "seed": seed,
 "has_seed": True,
 "layer2_derivable": layer2_identity is not None,
 "layer2_identity": layer2_identity,
 "layer2_onchain": layer2_exists,
 }
 
 results.append(result)
 
 if seed:
 seeds_found += 1
 if layer2_identity:
 layer2_derivable += 1
 
 print()
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 print(f"Analysiert: {len(results)} Identities")
 print(f"Seeds gefunden: {seeds_found}/{len(results)} ({seeds_found/len(results)*100:.1f}%)")
 print(f"Layer-2 ableitbar: {layer2_derivable}/{len(results)} ({layer2_derivable/len(results)*100:.1f}%)")
 print(f"Layer-2 on-chain: {layer2_onchain}/{layer2_derivable} ({layer2_onchain/layer2_derivable*100:.1f}% von ableitbaren)" if layer2_derivable > 0 else "Layer-2 on-chain: 0")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "summary": {
 "total_analyzed": len(results),
 "seeds_found": seeds_found,
 "layer2_derivable": layer2_derivable,
 "layer2_onchain": layer2_onchain,
 },
 "results": results[:50], # Nur erste 50 for JSON
 "all_seeds": [r["seed"] for r in results if r["has_seed"]],
 "layer2_identities": [r["layer2_identity"] for r in results if r.get("layer2_identity")],
 }
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 print()
 
 if layer2_onchain > 0:
 print(f"🎉 {layer2_onchain} Layer-2 Identities on-chain gefunden!")
 print(" Diese könnten Teil der rekursiven Struktur sein!")

if __name__ == "__main__":
 main()

