#!/usr/bin/env python3
"""
Matrix Seed Mapper: Map seed strings back to Anna Matrix coordinates
to find which matrix positions generate the seed patterns.

This could reveal the "command structure" or "AI decision tree" in the matrix.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np

from analysis.utils.data_loader import load_anna_matrix
from analysis.utils.identity_tools import base26_char

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "matrix_seed_mapping.json"

# Known seeds
LAYER1_SEEDS = [
 "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd", # Diagonal #1
 "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr", # Diagonal #2
 "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn", # Diagonal #3
 "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht", # Diagonal #4
 "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml", # Vortex #1
 "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb", # Vortex #2
 "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw", # Vortex #3
 "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc", # Vortex #4
]

LAYER2_SEEDS = [
 "obwiipwfpowiqchgjhkfznmssyobynndluexaelxkeroiukixeuxmlz", # Diagonal #1
 "oqoomlaqlgojffaygxalstdvdgqdwkwgdqjrmnzsodhmwwwslsqzzah", # Diagonal #2
 "wezpwomkyyqygdzjduepiottukccqvbyemyhqutwgamhfvjjvrcqlmv", # Diagonal #3
 "buicahkiblqwqaionarlyroqgmrayeaoecszcpmtehuifxlkgtmapjf", # Diagonal #4
 "faeeivwninmpfaawuuymcjxmsfcagdjnfdrcehbfpgfccekuwtmcbhx", # Vortex #1
 "pruatxfveffwaehuadbsbkofeqtcyoxpsjhwpusukchbxgmrqqewitae", # Vortex #2
 "riomizkjdphcffgvymwsfokvbnxayckuxolhlhhcpcqduliitmfgzqu", # Vortex #3
 "dzgtelpkneitgbrurpcwrnzgltmbcrplrperufbzhdfdtfytjxoudyl", # Vortex #4
]

def find_seed_in_matrix(matrix: np.ndarray, seed: str) -> List[Tuple[int, int]]:
 """Find all positions in matrix that could generate this seed string."""
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
 matches.append(coords)
 
 return matches

def analyze_seed_patterns(seeds: List[str], matrix: np.ndarray) -> Dict:
 """Analyze seed patterns and their matrix positions."""
 results = []
 
 for i, seed in enumerate(seeds, 1):
 matches = find_seed_in_matrix(matrix, seed)
 
 # Analyze match positions
 if matches:
 # Check if matches form a pattern (diagonal, row, column, etc.)
 patterns = []
 for match_coords in matches[:5]: # Check first 5 matches
 rows = [r for r, c in match_coords]
 cols = [c for r, c in match_coords]
 
 is_diagonal = all(rows[j+1] == rows[j] + 1 and cols[j+1] == cols[j] + 1 
 for j in range(len(rows)-1))
 is_row = len(set(rows)) == 1
 is_col = len(set(cols)) == 1
 
 patterns.append({
 "is_diagonal": is_diagonal,
 "is_row": is_row,
 "is_col": is_col,
 "start": match_coords[0],
 "end": match_coords[-1],
 })
 else:
 patterns = []
 
 results.append({
 "seed_index": i,
 "seed": seed,
 "seed_length": len(seed),
 "matches_found": len(matches),
 "patterns": patterns,
 })
 
 return {"seed_analyses": results}

def find_common_substrings_in_matrix(matrix: np.ndarray, min_length: int = 4) -> Dict:
 """Find common substrings in the matrix that appear in multiple seeds."""
 size = matrix.shape[0]
 
 # Convert to Base-26
 base26_str = ""
 for r in range(size):
 for c in range(size):
 base26_str += base26_char(matrix[r, c])
 
 # Find all substrings of min_length
 all_substrings = set()
 for length in range(min_length, 20): # Check up to 20 chars
 for i in range(len(base26_str) - length + 1):
 substr = base26_str[i:i+length].lower()
 all_substrings.add(substr)
 
 # Check which substrings appear in seeds
 all_seeds = LAYER1_SEEDS + LAYER2_SEEDS
 seed_substrings = {}
 
 for seed in all_seeds:
 for length in range(min_length, min(20, len(seed))):
 for i in range(len(seed) - length + 1):
 substr = seed[i:i+length]
 if substr in all_substrings:
 if substr not in seed_substrings:
 seed_substrings[substr] = []
 seed_substrings[substr].append(seed)
 
 # Find substrings that appear in multiple seeds
 common = {substr: seeds for substr, seeds in seed_substrings.items() if len(seeds) > 1}
 
 return {
 "common_substrings": common,
 "total_unique_substrings_in_matrix": len(all_substrings),
 }

def main() -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=== Matrix Seed Mapper ===\n")
 print("Mapping seed strings back to Anna Matrix coordinates...\n")
 
 payload = load_anna_matrix()
 matrix = payload.matrix
 
 print("Analyzing Layer-1 seeds...")
 layer1_analysis = analyze_seed_patterns(LAYER1_SEEDS, matrix)
 
 print("Analyzing Layer-2 seeds...")
 layer2_analysis = analyze_seed_patterns(LAYER2_SEEDS, matrix)
 
 print("Finding common substrings...")
 substring_analysis = find_common_substrings_in_matrix(matrix, min_length=4)
 
 # Print results
 print("\n=== Results ===")
 
 print("\nLayer-1 Seeds:")
 for analysis in layer1_analysis["seed_analyses"]:
 print(f" Seed {analysis['seed_index']}: {analysis['matches_found']} matches in matrix")
 if analysis['patterns']:
 for pattern in analysis['patterns'][:2]:
 if pattern['is_diagonal']:
 print(f" → Diagonal pattern from {pattern['start']} to {pattern['end']}")
 
 print("\nLayer-2 Seeds:")
 for analysis in layer2_analysis["seed_analyses"]:
 print(f" Seed {analysis['seed_index']}: {analysis['matches_found']} matches in matrix")
 if analysis['patterns']:
 for pattern in analysis['patterns'][:2]:
 if pattern['is_diagonal']:
 print(f" → Diagonal pattern from {pattern['start']} to {pattern['end']}")
 
 print(f"\nCommon substrings (appear in multiple seeds):")
 common = substring_analysis["common_substrings"]
 sorted_common = sorted(common.items(), key=lambda x: len(x[1]), reverse=True)
 for substr, seeds in sorted_common[:10]:
 print(f" '{substr}' ({len(substr)} chars): appears in {len(seeds)} seeds")
 
 # Save
 output = {
 "layer1_analysis": layer1_analysis,
 "layer2_analysis": layer2_analysis,
 "substring_analysis": substring_analysis,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print(f"\nReport saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
 main()

