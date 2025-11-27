#!/usr/bin/env python3
"""
Coordinate Relationship Analysis: Find the "Vertical Code" by analyzing
coordinate relationships across all layers.

Hypothesis A: Does the seed derivation follow a pattern that relates back
to the original matrix coordinates of Layer-1 identities?

Hypothesis B: Is there a special identity whose seed (or derived seed) maps
back to a known encoded matrix position (e.g., coordinate 0,0)?

Goal: Find the third number (Layer-Index/Special-Path) for the Smart Contract payload.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from analysis.utils.data_loader import load_anna_matrix
from analysis.utils.identity_tools import base26_char
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

OUTPUT_DIR = Path("outputs/derived")
RECURSIVE_MAP_FILE = OUTPUT_DIR / "recursive_layer_map.json"
MATRIX_COORD_FILE = OUTPUT_DIR / "matrix_coordinate_analysis.json"
OUTPUT_JSON = OUTPUT_DIR / "coordinate_relationship_analysis.json"

# Original Layer-1 extraction coordinates (from matrix_coordinate_analysis)
LAYER1_START_COORDS = [
 (0, 0), # Diagonal #1
 (32, 0), # Diagonal #2
 (64, 0), # Diagonal #3
 (96, 0), # Diagonal #4
 (62, 44), # Vortex #1 (approximate)
 (62, 34), # Vortex #2 (approximate)
 (63, 23), # Vortex #3 (approximate)
 (64, 64), # Vortex #4 (center, approximate)
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

def find_seed_in_matrix(matrix: np.ndarray, seed: str) -> List[Tuple[int, int]]:
 """Find all positions in matrix where this seed string appears."""
 size = matrix.shape[0]
 matches = []
 
 # Convert matrix to Base-26 string
 base26_str = ""
 base26_coords = []
 for r in range(size):
 for c in range(size):
 char = base26_char(matrix[r, c])
 base26_str += char
 base26_coords.append((r, c))
 
 # Find all occurrences of seed in the Base-26 string
 seed_lower = seed.lower()
 for i in range(len(base26_str) - len(seed) + 1):
 window = base26_str[i:i+len(seed)].lower()
 if window == seed_lower:
 coords = base26_coords[i:i+len(seed)]
 matches.append(coords[0]) # Start coordinate
 
 return matches

def analyze_seed_to_coordinate_mapping(
 matrix: np.ndarray,
 layer_seeds: Dict[int, List[str]],
) -> Dict:
 """Analyze if seeds from different layers map back to matrix coordinates."""
 results = {}
 
 for layer, seeds in layer_seeds.items():
 layer_results = []
 
 for idx, seed in enumerate(seeds):
 matches = find_seed_in_matrix(matrix, seed)
 
 # Check if matches relate to original Layer-1 coordinates
 relates_to_layer1 = False
 if layer > 1 and idx < len(LAYER1_START_COORDS):
 original_coord = LAYER1_START_COORDS[idx]
 for match_coord in matches:
 # Check if match is near original (within 32 pixels)
 distance = abs(match_coord[0] - original_coord[0]) + abs(match_coord[1] - original_coord[1])
 if distance < 32:
 relates_to_layer1 = True
 break
 
 layer_results.append({
 "seed_index": idx,
 "seed": seed,
 "matches_in_matrix": len(matches),
 "match_coordinates": matches[:5], # First 5 matches
 "relates_to_layer1_coord": relates_to_layer1,
 })
 
 results[layer] = layer_results
 
 return results

def analyze_seed_transformation_pattern(layer_seeds: Dict[int, List[str]]) -> Dict:
 """Analyze patterns in seed transformations between layers."""
 transformations = {}
 
 for layer in sorted(layer_seeds.keys()):
 if layer == 1:
 continue
 
 prev_layer = layer - 1
 if prev_layer not in layer_seeds:
 continue
 
 layer_transforms = []
 
 for idx, seed in enumerate(layer_seeds[layer]):
 if idx < len(layer_seeds[prev_layer]):
 prev_seed = layer_seeds[prev_layer][idx]
 
 # Analyze transformation
 # Check character-level changes
 char_changes = sum(1 for a, b in zip(prev_seed, seed) if a != b)
 similarity = sum(1 for a, b in zip(prev_seed, seed) if a == b) / len(prev_seed) if prev_seed else 0
 
 # Check if transformation is consistent across identities
 layer_transforms.append({
 "seed_index": idx,
 "prev_seed": prev_seed,
 "new_seed": seed,
 "char_changes": char_changes,
 "similarity": similarity,
 })
 
 if layer_transforms:
 avg_similarity = sum(t["similarity"] for t in layer_transforms) / len(layer_transforms)
 transformations[f"L{prev_layer}_to_L{layer}"] = {
 "transforms": layer_transforms,
 "average_similarity": avg_similarity,
 "consistent": all(abs(t["similarity"] - avg_similarity) < 0.1 for t in layer_transforms),
 }
 
 return transformations

def find_special_positions(layer_seeds: Dict[int, List[str]], matrix: np.ndarray) -> Dict:
 """Find special positions (e.g., seeds that map to 0,0 or other significant coordinates)."""
 special = {
 "zero_zero_matches": [],
 "original_coord_matches": [],
 }
 
 for layer, seeds in layer_seeds.items():
 for idx, seed in enumerate(seeds):
 matches = find_seed_in_matrix(matrix, seed)
 
 # Check for (0, 0) matches
 if (0, 0) in matches:
 special["zero_zero_matches"].append({
 "layer": layer,
 "seed_index": idx,
 "seed": seed,
 })
 
 # Check if matches original Layer-1 coordinate
 if layer > 1 and idx < len(LAYER1_START_COORDS):
 original = LAYER1_START_COORDS[idx]
 if original in matches:
 special["original_coord_matches"].append({
 "layer": layer,
 "seed_index": idx,
 "seed": seed,
 "original_coord": original,
 })
 
 return special

def analyze_layer_index_pattern(layer_seeds: Dict[int, List[str]]) -> Dict:
 """Analyze if layer index itself encodes information."""
 patterns = {}
 
 for layer, seeds in layer_seeds.items():
 # Check if layer number appears in seed patterns
 # For example, does Layer N have N occurrences of a pattern?
 
 # Count specific patterns that might relate to layer number
 pattern_counts = {}
 for seed in seeds:
 # Count occurrences of layer number mod 26 as character
 layer_char = chr(ord('a') + (layer % 26))
 count = seed.count(layer_char)
 if count not in pattern_counts:
 pattern_counts[count] = 0
 pattern_counts[count] += 1
 
 patterns[layer] = {
 "layer": layer,
 "pattern_counts": pattern_counts,
 }
 
 return patterns

def main() -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("COORDINATE RELATIONSHIP ANALYSIS - VERTICAL CODE")
 print("=" * 80)
 print()
 print("Goal: Find the third number (Layer-Index/Special-Path)")
 print("Hypothesis A: Seed derivation relates back to original matrix coordinates")
 print("Hypothesis B: Special identity maps back to known matrix position")
 print()
 
 # Load layer structure
 print("Loading layer structure...")
 with RECURSIVE_MAP_FILE.open("r", encoding="utf-8") as f:
 data = json.load(f)
 
 structure = data.get("known_8_exploration", {})
 layer_map = structure.get("layer_map", {})
 
 # Extract seeds for all layers
 print("Extracting seeds from all layers...")
 layer_seeds: Dict[int, List[str]] = {}
 
 for layer_str, identities in layer_map.items():
 layer = int(layer_str)
 seeds = []
 for identity in identities:
 seed = identity_to_seed(identity)
 if seed:
 seeds.append(seed)
 layer_seeds[layer] = seeds
 print(f" Layer {layer}: {len(seeds)} seeds extracted")
 
 print()
 
 # Load matrix
 print("Loading Anna Matrix...")
 payload = load_anna_matrix()
 matrix = payload.matrix
 
 print()
 print("=" * 80)
 print("ANALYZING SEED-TO-COORDINATE MAPPING")
 print("=" * 80)
 print()
 
 # Analyze if seeds map back to matrix coordinates
 seed_mapping = analyze_seed_to_coordinate_mapping(matrix, layer_seeds)
 
 print("Seed-to-Coordinate Mapping Results:")
 for layer, results in seed_mapping.items():
 matches_count = sum(1 for r in results if r["matches_in_matrix"] > 0)
 relates_count = sum(1 for r in results if r["relates_to_layer1_coord"])
 print(f" Layer {layer}: {matches_count}/{len(results)} seeds found in matrix, {relates_count} relate to Layer-1 coords")
 
 print()
 print("=" * 80)
 print("ANALYZING SEED TRANSFORMATION PATTERNS")
 print("=" * 80)
 print()
 
 # Analyze seed transformation patterns
 transformations = analyze_seed_transformation_pattern(layer_seeds)
 
 print("Seed Transformation Patterns:")
 for transform_name, transform_data in transformations.items():
 print(f" {transform_name}:")
 print(f" Average similarity: {transform_data['average_similarity']:.2%}")
 print(f" Consistent across identities: {transform_data['consistent']}")
 
 print()
 print("=" * 80)
 print("FINDING SPECIAL POSITIONS")
 print("=" * 80)
 print()
 
 # Find special positions
 special = find_special_positions(layer_seeds, matrix)
 
 if special["zero_zero_matches"]:
 print(f"🎯 Found {len(special['zero_zero_matches'])} seeds that map to (0,0):")
 for match in special["zero_zero_matches"][:5]:
 print(f" Layer {match['layer']}, Index {match['seed_index']}: {match['seed'][:30]}...")
 else:
 print(" No seeds map to (0,0)")
 
 if special["original_coord_matches"]:
 print(f"\n🎯 Found {len(special['original_coord_matches'])} seeds that map to original Layer-1 coordinates:")
 for match in special["original_coord_matches"][:5]:
 print(f" Layer {match['layer']}, Index {match['seed_index']}, Coord {match['original_coord']}")
 else:
 print("\n No seeds map back to original Layer-1 coordinates")
 
 print()
 print("=" * 80)
 print("ANALYZING LAYER INDEX PATTERNS")
 print("=" * 80)
 print()
 
 # Analyze layer index patterns
 layer_patterns = analyze_layer_index_pattern(layer_seeds)
 
 print("Layer Index Patterns:")
 for layer, pattern_data in layer_patterns.items():
 print(f" Layer {layer}: Pattern counts = {pattern_data['pattern_counts']}")
 
 # Save results
 output = {
 "seed_to_coordinate_mapping": seed_mapping,
 "seed_transformations": transformations,
 "special_positions": special,
 "layer_index_patterns": layer_patterns,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print()
 print("=" * 80)
 print(f"Report saved to: {OUTPUT_JSON}")
 print("=" * 80)
 
 # Key insights
 print()
 print("KEY INSIGHTS:")
 if special["zero_zero_matches"] or special["original_coord_matches"]:
 print(" 🎯 SPECIAL POSITIONS FOUND - Possible vertical code!")
 else:
 print(" → Seeds don't directly map back to matrix coordinates")
 print(" → Vertical code might be in layer index or transformation pattern")
 
 if transformations:
 consistent = all(t["consistent"] for t in transformations.values())
 if consistent:
 print(" → Seed transformations are consistent across identities")
 print(" → Transformation pattern might encode layer information")

if __name__ == "__main__":
 main()

