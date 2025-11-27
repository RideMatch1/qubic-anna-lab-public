#!/usr/bin/env python3
"""
Mappe die vollständige Layer-Struktur: Layer 1 → 2 → 3 → ... → 8

Verwendet alle gefundenen Identities als Seeds und leitet rekursiv ab.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict

VENV_PATH = Path(__file__).parent.parent.parent / "venv-tx"
OUTPUT_DIR = Path("outputs/derived")
SCAN_FILE = OUTPUT_DIR / "comprehensive_identity_seed_scan.json"
OUTPUT_JSON = OUTPUT_DIR / "complete_layer_structure.json"
OUTPUT_MD = OUTPUT_DIR / "COMPLETE_LAYER_STRUCTURE.md"

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

def map_complete_structure():
 """Mappe die vollständige Layer-Struktur."""
 
 print("=" * 80)
 print("VOLLSTÄNDIGE LAYER-STRUKTUR MAPPING")
 print("=" * 80)
 print()
 
 # Load bekannte Layer-1 Seeds (die 8 Original)
 known_layer1_seeds = [
 "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr",
 "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn",
 "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml",
 "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb",
 "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw",
 "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc",
 ]
 
 print(f"Starte mit {len(known_layer1_seeds)} Layer-1 Seeds")
 print()
 
 # Mappe rekursiv
 layer_structure = {}
 all_identities = set()
 
 for i, seed in enumerate(known_layer1_seeds, 1):
 print(f"Processing Seed {i}/{len(known_layer1_seeds)}: {seed[:30]}...")
 
 current_seed = seed
 layer_path = []
 
 # Leite bis zu Layer 8 ab
 for layer in range(1, 9):
 identity = derive_identity_from_seed(current_seed)
 
 if not identity:
 print(f" ⚠️ Layer {layer}: Failed to derive")
 break
 
 layer_path.append({
 "layer": layer,
 "seed": current_seed,
 "identity": identity,
 })
 
 all_identities.add(identity)
 
 # Für nächste Layer: Verwende identity.lower()[:55] als Seed
 if layer < 8:
 next_seed = identity.lower()[:55]
 current_seed = next_seed
 
 layer_structure[seed] = {
 "layer1_seed": seed,
 "path": layer_path,
 "max_layer": len(layer_path),
 }
 
 print(f" ✅ Mapped to Layer {len(layer_path)}")
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 layer_counts = defaultdict(int)
 for seed, data in layer_structure.items():
 max_layer = data["max_layer"]
 layer_counts[max_layer] += 1
 
 print("Layer-Verteilung:")
 for layer in sorted(layer_counts.keys()):
 print(f" Layer {layer}: {layer_counts[layer]} Seeds erreichen diese Tiefe")
 
 print()
 print(f"Total unique Identities: {len(all_identities)}")
 print()
 
 # Speichere Ergebnisse
 results = {
 "summary": {
 "layer1_seeds": len(known_layer1_seeds),
 "total_identities": len(all_identities),
 "max_layer_reached": max(layer_counts.keys()) if layer_counts else 0,
 },
 "layer_structure": layer_structure,
 "layer_counts": dict(layer_counts),
 }
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_JSON.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# Vollständige Layer-Struktur\n\n")
 f.write("## Summary\n\n")
 f.write(f"- **Layer-1 Seeds**: {len(known_layer1_seeds)}\n")
 f.write(f"- **Total Identities**: {len(all_identities)}\n")
 f.write(f"- **Max Layer Reached**: {max(layer_counts.keys()) if layer_counts else 0}\n\n")
 f.write("## Layer Structure\n\n")
 
 for seed, data in layer_structure.items():
 f.write(f"### Seed: {seed[:30]}...\n\n")
 f.write(f"Max Layer: {data['max_layer']}\n\n")
 f.write("| Layer | Identity | Seed |\n")
 f.write("|-------|----------|------|\n")
 for entry in data["path"]:
 f.write(f"| {entry['layer']} | {entry['identity']} | {entry['seed'][:30]}... |\n")
 f.write("\n")
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_JSON}")
 print(f"📄 Report gespeichert in: {OUTPUT_MD}")
 
 return results

if __name__ == "__main__":
 map_complete_structure()

