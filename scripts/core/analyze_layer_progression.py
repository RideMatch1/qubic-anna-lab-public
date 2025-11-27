#!/usr/bin/env python3
"""
Analyze Layer-Progression: Layer 1 → 2 → 3 → ... → 8

Hypothese: Wir müssen die Layer-Struktur verstehen, um zu Layer 8 (Genesis) zu kommen.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

VENV_PATH = Path(__file__).parent.parent.parent / "venv-tx"
OUTPUT_DIR = Path("outputs/derived")
SCAN_FILE = OUTPUT_DIR / "comprehensive_identity_seed_scan.json"
OUTPUT_JSON = OUTPUT_DIR / "layer_progression_analysis.json"
OUTPUT_MD = OUTPUT_DIR / "LAYER_PROGRESSION_ANALYSIS.md"

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

def analyze_layer_progression():
 """Analyze wie Layer 1 zu Layer 2, Layer 2 zu Layer 3, etc. führt."""
 
 if not SCAN_FILE.exists():
 print(f"❌ Scan file not found: {SCAN_FILE}")
 return None
 
 print("Loading comprehensive scan data...")
 with SCAN_FILE.open() as f:
 scan_data = json.load(f)
 
 seed_results = scan_data.get("seed_results", [])
 print(f"✅ Loaded {len(seed_results)} seed results")
 print()
 
 # Analyze Layer-Progression
 print("=" * 80)
 print("LAYER PROGRESSION ANALYSIS")
 print("=" * 80)
 print()
 
 progression_map = {}
 layer_stats = defaultdict(lambda: {"total": 0, "has_next": 0})
 
 for seed_result in seed_results:
 seed = seed_result.get("seed")
 derived_identities = seed_result.get("derived_identities", {})
 
 # Finde Layer-Progression
 for layer_str in sorted(derived_identities.keys(), key=lambda x: int(x) if x.isdigit() else 0):
 layer = int(layer_str) if layer_str.isdigit() else 0
 layer_stats[layer_str]["total"] += 1
 
 identity = derived_identities[layer_str]
 
 # Check ob diese Identity zu nächster Layer führt
 next_layer_str = str(layer + 1)
 if next_layer_str in derived_identities:
 layer_stats[layer_str]["has_next"] += 1
 
 next_identity = derived_identities[next_layer_str]
 
 # Extrahiere Seed for nächste Layer
 next_seed = identity.lower()[:55]
 
 # Validate: Führt dieser Seed zur nächsten Identity?
 derived_next = derive_identity_from_seed(next_seed)
 
 progression_map[f"{seed}_{layer_str}"] = {
 "layer": layer,
 "layer_str": layer_str,
 "identity": identity,
 "seed": seed if layer == 1 else None,
 "next_layer": layer + 1,
 "next_layer_str": next_layer_str,
 "next_identity": next_identity,
 "next_seed": next_seed,
 "derived_next": derived_next,
 "matches": derived_next == next_identity,
 }
 
 # Zusammenfassung
 print("Layer Progression Statistics:")
 for layer_str in sorted(layer_stats.keys(), key=lambda x: int(x) if x.isdigit() else 0):
 stats = layer_stats[layer_str]
 has_next_pct = (stats["has_next"] / stats["total"] * 100) if stats["total"] > 0 else 0
 print(f" Layer {layer_str}: {stats['has_next']}/{stats['total']} have next layer ({has_next_pct:.1f}%)")
 print()
 
 # Validate Progression
 print("Validating Layer Progression...")
 valid_progressions = []
 invalid_progressions = []
 
 for key, prog in progression_map.items():
 if prog["matches"]:
 valid_progressions.append(prog)
 print(f" ✅ Layer {prog['layer']} → {prog['next_layer']}: Valid")
 else:
 invalid_progressions.append(prog)
 if len(invalid_progressions) <= 5: # Zeige nur erste 5
 print(f" ❌ Layer {prog['layer']} → {prog['next_layer']}: Invalid")
 if prog.get('next_identity'):
 print(f" Expected: {prog['next_identity']}")
 if prog.get('derived_next'):
 print(f" Derived: {prog['derived_next']}")
 
 print()
 print(f"Valid progressions: {len(valid_progressions)}")
 print(f"Invalid progressions: {len(invalid_progressions)}")
 print()
 
 # Finde Layer 1 → Layer 2 Mappings (die ursprünglichen 8)
 print("Original 8 Layer-1 → Layer-2 Mappings:")
 original_mappings = []
 
 # Load bekannte Layer-1 Seeds
 known_layer1_seeds = {
 "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn": "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG",
 "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 }
 
 for seed, expected_layer2 in known_layer1_seeds.items():
 # Finde Layer-1 Identity
 layer1_identity = derive_identity_from_seed(seed)
 
 if layer1_identity:
 # Extrahiere Seed for Layer 2
 layer2_seed = layer1_identity.lower()[:55]
 layer2_identity = derive_identity_from_seed(layer2_seed)
 
 original_mappings.append({
 "layer1_seed": seed,
 "layer1_identity": layer1_identity,
 "layer2_seed": layer2_seed,
 "layer2_identity": layer2_identity,
 "expected_layer2": expected_layer2,
 "matches": layer2_identity == expected_layer2,
 })
 
 if layer2_identity == expected_layer2:
 print(f" ✅ {seed[:30]}... → {layer2_identity[:30]}...")
 else:
 print(f" ❌ {seed[:30]}... → {layer2_identity[:30]}... (expected {expected_layer2[:30]}...)")
 
 print()
 
 # Speichere Ergebnisse
 results = {
 "layer_stats": dict(layer_stats),
 "valid_progressions": valid_progressions,
 "invalid_progressions": invalid_progressions[:10], # Nur erste 10
 "original_mappings": original_mappings,
 }
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_JSON.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# Layer Progression Analysis\n\n")
 f.write("## Summary\n\n")
 f.write(f"- **Valid progressions**: {len(valid_progressions)}\n")
 f.write(f"- **Invalid progressions**: {len(invalid_progressions)}\n")
 f.write(f"- **Original 8 mappings**: {sum(1 for m in original_mappings if m['matches'])}/8 valid\n\n")
 f.write("## Original 8 Layer-1 → Layer-2 Mappings\n\n")
 f.write("| Layer-1 Seed | Layer-1 Identity | Layer-2 Seed | Layer-2 Identity | Valid |\n")
 f.write("|--------------|------------------|--------------|------------------|-------|\n")
 
 for mapping in original_mappings:
 f.write(f"| {mapping['layer1_seed'][:30]}... | {mapping['layer1_identity']} | {mapping['layer2_seed']} | {mapping['layer2_identity']} | {'✅' if mapping['matches'] else '❌'} |\n")
 
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")
 
 return results

if __name__ == "__main__":
 analyze_layer_progression()

