#!/usr/bin/env python3
"""
Matrix Coordinate Analyzer: Map the original extraction coordinates
for the 8 Layer-1 identities and analyze the matrix values at these positions.

Hypothesis: The matrix values at the start coordinates encode the "Block-ID" (1-8)
that must be sent to the Smart Contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from analysis.utils.data_loader import load_anna_matrix
from analysis.utils.identity_tools import base26_char

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "matrix_coordinate_analysis.json"

def get_diagonal_coordinates() -> List[Dict]:
 """Get the exact coordinates used for diagonal extraction."""
 # From analysis/21_base26_identity_extraction.py
 # Pattern: 4 identities, each from a 32x32 window
 # Each identity: 4 blocks of 14 characters each
 
 coordinates = []
 
 for idx, base_row in enumerate(range(0, 128, 32), start=1):
 # Each identity uses 4 blocks
 for block in range(4):
 row_offset = base_row + (block // 2) * 16
 col_offset = (block % 2) * 16
 
 # Each block has 14 characters along the diagonal
 block_coords = []
 for j in range(14):
 row = row_offset + j
 col = col_offset + j
 if row < 128 and col < 128:
 block_coords.append((row, col))
 
 coordinates.append({
 "identity_index": idx,
 "block_index": block,
 "start_coordinate": block_coords[0] if block_coords else None,
 "end_coordinate": block_coords[-1] if block_coords else None,
 "all_coordinates": block_coords,
 })
 
 return coordinates

def get_vortex_coordinates() -> List[Dict]:
 """Get the exact coordinates used for vortex extraction."""
 # From analysis/71_9_vortex_extraction.py
 # Pattern: 4 identities from 9-Vortex rings
 
 # This is more complex - we need to find the ring positions
 # For now, we'll extract the coordinates from the actual extraction
 # The vortex extraction finds cells with digital root = 9 and orders them
 
 coordinates = []
 
 # We'll need to re-run the vortex extraction to get exact coordinates
 # For now, return placeholder structure
 for idx in range(1, 5):
 coordinates.append({
 "identity_index": idx + 4, # Vortex #1-4 are identities 5-8
 "block_index": 0,
 "start_coordinate": None, # Will be filled by actual extraction
 "end_coordinate": None,
 "all_coordinates": [],
 })
 
 return coordinates

def extract_vortex_coordinates_from_matrix(matrix: np.ndarray) -> List[Dict]:
 """Extract vortex ring coordinates by re-running the extraction logic."""
 
 def digital_root(value: float) -> np.ndarray:
 """Calculate digital root for matrix values."""
 val = np.abs(value).astype(int)
 while np.any(val >= 10):
 val = np.array([sum(int(d) for d in str(v)) for v in val])
 return val
 
 def _ring_positions(matrix: np.ndarray, radius: int, tolerance: float = 1.5) -> List[Tuple[int, int]]:
 """Find positions on a ring with digital root = 9."""
 size = matrix.shape[0]
 center_r, center_c = size // 2, size // 2
 
 positions = []
 for r in range(size):
 for c in range(size):
 dr = r - center_r
 dc = c - center_c
 distance = np.sqrt(dr**2 + dc**2)
 
 if abs(distance - radius) < tolerance:
 val = matrix[r, c]
 if digital_root(np.array([val]))[0] == 9:
 positions.append((r, c))
 
 # Order by angle
 if positions:
 angles = []
 for r, c in positions:
 dr = r - center_r
 dc = c - center_c
 angle = np.arctan2(dr, dc)
 angles.append((angle, r, c))
 angles.sort()
 positions = [(r, c) for _, r, c in angles]
 
 return positions
 
 coordinates = []
 
 # From the original extraction, we know the target radii
 TARGET_RADII = [10, 20, 30, 40] # Approximate radii from the original extraction
 
 for idx, radius in enumerate(TARGET_RADII, start=1):
 ring_positions = _ring_positions(matrix, radius)
 
 if len(ring_positions) >= 56:
 coordinates.append({
 "identity_index": idx + 4, # Vortex #1-4 are identities 5-8
 "block_index": 0,
 "start_coordinate": ring_positions[0],
 "end_coordinate": ring_positions[55],
 "all_coordinates": ring_positions[:56],
 })
 
 return coordinates

def analyze_matrix_values_at_coordinates(matrix: np.ndarray, coordinates: List[Dict]) -> Dict:
 """Analyze matrix values at the extraction coordinates."""
 results = []
 
 # Group coordinates by identity
 identity_groups = {}
 for coord_info in coordinates:
 identity_idx = coord_info["identity_index"]
 if identity_idx not in identity_groups:
 identity_groups[identity_idx] = []
 identity_groups[identity_idx].append(coord_info)
 
 # Analyze first coordinate of each identity (the true start)
 for identity_idx, coord_list in sorted(identity_groups.items()):
 # Get the FIRST block's start coordinate (the true extraction start)
 first_coord_info = sorted(coord_list, key=lambda x: x.get("block_index", 0))[0]
 start_coord = first_coord_info.get("start_coordinate")
 
 if not start_coord:
 continue
 
 # Get matrix value at start coordinate
 start_r, start_c = start_coord
 start_value = matrix[start_r, start_c]
 start_base26 = (int(start_value) % 26) if not np.isnan(start_value) else None
 
 # Get all values along ALL paths for this identity
 all_path_values = []
 for coord_info in coord_list:
 for r, c in coord_info.get("all_coordinates", [])[:56]:
 val = matrix[r, c]
 all_path_values.append({
 "coordinate": (r, c),
 "value": float(val),
 "base26": int(val) % 26 if not np.isnan(val) else None,
 "base26_char": base26_char(val),
 })
 
 # Check if start value encodes the identity index (1-8)
 # Multiple hypotheses to test
 encoding_hypotheses = {}
 if start_base26 is not None:
 # Test various encoding methods
 encoding_hypotheses["base26_mod8"] = start_base26 % 8
 encoding_hypotheses["base26_mod26"] = start_base26
 encoding_hypotheses["value_mod8"] = int(start_value) % 8
 encoding_hypotheses["value_mod26"] = int(start_value) % 26
 encoding_hypotheses["value_mod8_plus1"] = (int(start_value) % 8) + 1 # 1-8 instead of 0-7
 encoding_hypotheses["base26_mod8_plus1"] = (start_base26 % 8) + 1
 encoding_hypotheses["abs_value_mod8"] = int(abs(start_value)) % 8
 encoding_hypotheses["abs_value_mod8_plus1"] = (int(abs(start_value)) % 8) + 1
 
 results.append({
 "identity_index": identity_idx,
 "start_coordinate": start_coord,
 "start_value": float(start_value),
 "start_base26": start_base26,
 "start_base26_char": base26_char(start_value),
 "encoding_hypotheses": encoding_hypotheses,
 "total_blocks": len(coord_list),
 "path_length": len(all_path_values),
 "path_values_sample": all_path_values[:10], # First 10 for brevity
 })
 
 return {"coordinate_analyses": results}

def find_block_id_pattern(analyses: List[Dict]) -> Dict:
 """Find patterns that might encode Block-ID (1-8)."""
 patterns = {}
 
 for analysis in analyses:
 identity_idx = analysis["identity_index"]
 hypotheses = analysis.get("encoding_hypotheses", {})
 
 for hypothesis_name, value in hypotheses.items():
 if hypothesis_name not in patterns:
 patterns[hypothesis_name] = []
 
 # Test multiple matching criteria
 matches_exact = value == identity_idx
 matches_minus1 = value == (identity_idx - 1) # 0-based indexing
 matches_mod8 = (value % 8) == ((identity_idx - 1) % 8)
 
 patterns[hypothesis_name].append({
 "identity_index": identity_idx,
 "value": value,
 "matches_exact": matches_exact,
 "matches_minus1": matches_minus1,
 "matches_mod8": matches_mod8,
 })
 
 # Check which hypothesis best matches identity indices
 best_hypothesis = None
 best_match_count = 0
 best_match_type = None
 
 for hypothesis_name, matches in patterns.items():
 # Try different matching criteria
 exact_count = sum(1 for m in matches if m["matches_exact"])
 minus1_count = sum(1 for m in matches if m["matches_minus1"])
 mod8_count = sum(1 for m in matches if m["matches_mod8"])
 
 # Find best match type
 max_count = max(exact_count, minus1_count, mod8_count)
 if max_count > best_match_count:
 best_match_count = max_count
 best_hypothesis = hypothesis_name
 if max_count == exact_count:
 best_match_type = "exact"
 elif max_count == minus1_count:
 best_match_type = "minus1"
 else:
 best_match_type = "mod8"
 
 return {
 "patterns": patterns,
 "best_hypothesis": best_hypothesis,
 "best_match_type": best_match_type,
 "best_match_count": best_match_count,
 "total_identities": len(analyses),
 }

def main() -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=== Matrix Coordinate Analyzer ===\n")
 print("Mapping original extraction coordinates and analyzing matrix values...\n")
 
 payload = load_anna_matrix()
 matrix = payload.matrix
 
 print("1. Extracting diagonal coordinates...")
 diagonal_coords = get_diagonal_coordinates()
 print(f" Found {len(diagonal_coords)} coordinate blocks for 4 diagonal identities")
 
 print("\n2. Extracting vortex coordinates...")
 vortex_coords = extract_vortex_coordinates_from_matrix(matrix)
 print(f" Found {len(vortex_coords)} vortex rings for 4 vortex identities")
 
 print("\n3. Analyzing matrix values at coordinates...")
 all_coords = diagonal_coords + vortex_coords
 analysis = analyze_matrix_values_at_coordinates(matrix, all_coords)
 
 print("\n4. Searching for Block-ID patterns...")
 pattern_analysis = find_block_id_pattern(analysis["coordinate_analyses"])
 
 # Print results
 print("\n=== Results ===")
 
 print("\nStart Coordinates and Values:")
 for coord_analysis in analysis["coordinate_analyses"]:
 idx = coord_analysis["identity_index"]
 start = coord_analysis["start_coordinate"]
 val = coord_analysis["start_value"]
 base26 = coord_analysis["start_base26"]
 char = coord_analysis["start_base26_char"]
 
 print(f" Identity #{idx}: Start={start}, Value={val:.1f}, Base26={base26} ({char})")
 
 # Check encoding hypotheses
 hypotheses = coord_analysis.get("encoding_hypotheses", {})
 for hyp_name, hyp_value in hypotheses.items():
 matches = (hyp_value == idx) or (hyp_value == idx - 1)
 match_str = "✅ MATCH" if matches else ""
 print(f" {hyp_name}: {hyp_value} {match_str}")
 
 print(f"\n=== Pattern Analysis ===")
 print(f"Best hypothesis: {pattern_analysis['best_hypothesis']}")
 print(f"Match count: {pattern_analysis['best_match_count']}/{pattern_analysis['total_identities']}")
 
 if pattern_analysis['best_match_count'] > 0:
 print(f"\n🎉 FOUND PATTERN! {pattern_analysis['best_hypothesis']} encodes Block-ID!")
 print(f"\nBlock-ID mapping:")
 best_pattern = pattern_analysis["patterns"][pattern_analysis["best_hypothesis"]]
 for match in best_pattern:
 idx = match["identity_index"]
 val = match["value"]
 print(f" Identity #{idx} → Block-ID {val}")
 
 # Save results
 output = {
 "diagonal_coordinates": diagonal_coords,
 "vortex_coordinates": vortex_coords,
 "coordinate_analysis": analysis,
 "pattern_analysis": pattern_analysis,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print(f"\nReport saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
 main()

