#!/usr/bin/env python3
"""
Seed Delta Analyzer: Compare Layer-2 seeds vs Layer-3 seeds to find
the "rule" or "command code" that changes between layers.

This is the KEY to understanding the recursive structure.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "seed_delta_analysis.json"

# Known Layer-2 identities (from our previous analysis)
LAYER2_IDENTITIES = [
 "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD", # Diagonal #1
 "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE", # Diagonal #2
 "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG", # Diagonal #3
 "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI", # Diagonal #4
 "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL", # Vortex #1
 "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI", # Vortex #2
 "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN", # Vortex #3
 "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB", # Vortex #4
]

# Layer-1 identities (for reference)
LAYER1_IDENTITIES = [
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR", # Diagonal #1
 "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ", # Diagonal #2
 "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV", # Diagonal #3
 "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC", # Diagonal #4
 "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF", # Vortex #1
 "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD", # Vortex #2
 "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL", # Vortex #3
 "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK", # Vortex #4
]

def identity_to_seed(identity: str) -> str | None:
 """Convert identity to seed (55 chars, lowercase)."""
 body = identity[:56].lower()[:55]
 if len(body) == 55 and body.isalpha():
 return body
 return None

def derive_identity(seed: str) -> str | None:
 """Derive Qubic identity from seed."""
 try:
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 return get_identity_from_public_key(public_key)
 except:
 return None

def compare_seeds(seed1: str, seed2: str) -> Dict:
 """Compare two seeds character by character to find differences."""
 if len(seed1) != len(seed2):
 return {"error": "Different lengths"}
 
 differences = []
 for i, (c1, c2) in enumerate(zip(seed1, seed2)):
 if c1 != c2:
 differences.append({
 "position": i,
 "char1": c1,
 "char2": c2,
 "delta": ord(c2) - ord(c1),
 "delta_mod26": (ord(c2) - ord(c1)) % 26,
 })
 
 return {
 "total_differences": len(differences),
 "differences": differences,
 "similarity": (len(seed1) - len(differences)) / len(seed1),
 }

def analyze_layer_transition(layer1_identity: str, layer2_identity: str) -> Dict:
 """Analyze the transition from Layer-1 to Layer-2."""
 layer1_seed = identity_to_seed(layer1_identity)
 layer2_seed = identity_to_seed(layer2_identity)
 
 if not layer1_seed or not layer2_seed:
 return {"error": "Could not extract seeds"}
 
 comparison = compare_seeds(layer1_seed, layer2_seed)
 
 # Derive Layer-3 to see the pattern
 layer3_identity = derive_identity(layer2_seed)
 layer3_seed = identity_to_seed(layer3_identity) if layer3_identity else None
 
 layer2_to_layer3 = None
 if layer3_seed:
 layer2_to_layer3 = compare_seeds(layer2_seed, layer3_seed)
 
 return {
 "layer1_identity": layer1_identity,
 "layer1_seed": layer1_seed,
 "layer2_identity": layer2_identity,
 "layer2_seed": layer2_seed,
 "layer3_identity": layer3_identity,
 "layer3_seed": layer3_seed,
 "layer1_to_layer2": comparison,
 "layer2_to_layer3": layer2_to_layer3,
 }

def find_pattern_in_deltas(analyses: List[Dict]) -> Dict:
 """Find patterns in the delta changes across all layer transitions."""
 all_deltas = []
 all_positions = []
 
 for analysis in analyses:
 l1_to_l2 = analysis.get("layer1_to_layer2", {})
 if l1_to_l2.get("differences"):
 for diff in l1_to_l2["differences"]:
 all_deltas.append(diff["delta_mod26"])
 all_positions.append(diff["position"])
 
 # Find common patterns
 from collections import Counter
 delta_counter = Counter(all_deltas)
 position_counter = Counter(all_positions)
 
 return {
 "most_common_deltas": delta_counter.most_common(10),
 "most_common_positions": position_counter.most_common(10),
 "total_transitions_analyzed": len(analyses),
 }

def main() -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=== Seed Delta Analyzer ===\n")
 print("Analyzing Layer-1 → Layer-2 → Layer-3 transitions...")
 print("Looking for the 'rule' or 'command code' in seed changes.\n")
 
 analyses = []
 
 for i, (l1_id, l2_id) in enumerate(zip(LAYER1_IDENTITIES, LAYER2_IDENTITIES), 1):
 label = f"Diagonal #{i}" if i <= 4 else f"Vortex #{i-4}"
 print(f"Analyzing {label}...")
 
 analysis = analyze_layer_transition(l1_id, l2_id)
 analysis["label"] = label
 analyses.append(analysis)
 
 l1_to_l2 = analysis.get("layer1_to_layer2", {})
 if l1_to_l2.get("differences"):
 print(f" Layer-1 → Layer-2: {l1_to_l2['total_differences']} differences")
 print(f" Similarity: {l1_to_l2['similarity']:.2%}")
 
 # Show first few differences
 for diff in l1_to_l2["differences"][:5]:
 print(f" Pos {diff['position']}: '{diff['char1']}' → '{diff['char2']}' (Δ{diff['delta_mod26']})")
 
 l2_to_l3 = analysis.get("layer2_to_layer3")
 if l2_to_l3 and l2_to_l3.get("differences"):
 print(f" Layer-2 → Layer-3: {l2_to_l3['total_differences']} differences")
 print(f" Similarity: {l2_to_l3['similarity']:.2%}")
 print()
 
 # Pattern analysis
 print("=== Pattern Analysis ===")
 patterns = find_pattern_in_deltas(analyses)
 
 print(f"Most common delta values (mod 26):")
 for delta, count in patterns["most_common_deltas"]:
 print(f" Δ{delta}: {count} occurrences")
 
 print(f"\nMost common positions for changes:")
 for pos, count in patterns["most_common_positions"]:
 print(f" Position {pos}: {count} occurrences")
 
 # Save results
 output = {
 "analyses": analyses,
 "pattern_analysis": patterns,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print(f"\nReport saved to: {OUTPUT_JSON}")
 
 # Key insights
 print("\n=== Key Insights ===")
 print("1. If deltas are consistent → there's a mathematical rule")
 print("2. If positions are consistent → specific seed positions encode commands")
 print("3. If patterns emerge → these could be Smart Contract payloads")

if __name__ == "__main__":
 main()

