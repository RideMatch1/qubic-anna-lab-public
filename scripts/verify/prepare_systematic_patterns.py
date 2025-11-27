#!/usr/bin/env python3
"""
Prepare Systematic Pattern Extraction: Define pattern families to test.

This script prepares the pattern extraction by:
1. Defining systematic pattern families
2. Calculating all possible variants
3. Preparing the extraction script structure
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "systematic_patterns_definition.json"
OUTPUT_MD = OUTPUT_DIR / "systematic_patterns_definition.md"

def define_pattern_families() -> Dict:
 """Define systematic pattern families to test."""
 
 patterns = {
 "26x26_blocks": {
 "description": "26×26 blocks (676 cells per block)",
 "variants": [],
 "count": 0,
 },
 "1649_step_patterns": {
 "description": "1649-step patterns (various directions)",
 "variants": [],
 "count": 0,
 },
 "spirals": {
 "description": "Spirals (various start points and directions)",
 "variants": [],
 "count": 0,
 },
 "grid_based": {
 "description": "Grid-based extractions (various grid sizes)",
 "variants": [],
 "count": 0,
 },
 "multi_diagonal": {
 "description": "Multi-diagonal patterns (parallel diagonals)",
 "variants": [],
 "count": 0,
 },
 }
 
 # Calculate variants for each pattern family
 matrix_size = 128
 
 # 26×26 blocks
 block_size = 26
 for start_row in range(0, matrix_size - block_size + 1, block_size):
 for start_col in range(0, matrix_size - block_size + 1, block_size):
 patterns["26x26_blocks"]["variants"].append({
 "start": (start_row, start_col),
 "size": (block_size, block_size),
 })
 patterns["26x26_blocks"]["count"] = len(patterns["26x26_blocks"]["variants"])
 
 # 1649-step patterns
 step = 1649 % (matrix_size * matrix_size) # Normalize to matrix size
 for direction in ["horizontal", "vertical", "diagonal", "reverse_diagonal"]:
 patterns["1649_step_patterns"]["variants"].append({
 "step": step,
 "direction": direction,
 })
 patterns["1649_step_patterns"]["count"] = len(patterns["1649_step_patterns"]["variants"])
 
 # Spirals
 for start in [(0, 0), (64, 64), (0, 64), (64, 0)]:
 for direction in ["clockwise", "counterclockwise"]:
 patterns["spirals"]["variants"].append({
 "start": start,
 "direction": direction,
 })
 patterns["spirals"]["count"] = len(patterns["spirals"]["variants"])
 
 # Grid-based
 for grid_size in [8, 16, 32, 64]:
 patterns["grid_based"]["variants"].append({
 "grid_size": grid_size,
 })
 patterns["grid_based"]["count"] = len(patterns["grid_based"]["variants"])
 
 # Multi-diagonal
 for num_diagonals in [2, 4, 8]:
 for spacing in [1, 2, 4]:
 patterns["multi_diagonal"]["variants"].append({
 "num_diagonals": num_diagonals,
 "spacing": spacing,
 })
 patterns["multi_diagonal"]["count"] = len(patterns["multi_diagonal"]["variants"])
 
 return patterns

def main() -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("PREPARE SYSTEMATIC PATTERN EXTRACTION")
 print("=" * 80)
 print()
 
 print("Defining pattern families...")
 patterns = define_pattern_families()
 
 total_variants = sum(p["count"] for p in patterns.values())
 
 print(f"✅ {len(patterns)} pattern families defined")
 print(f"✅ {total_variants} total variants to test")
 print()
 
 for name, pattern in patterns.items():
 print(f"{name}:")
 print(f" Description: {pattern['description']}")
 print(f" Variants: {pattern['count']}")
 print()
 
 # Save definition
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(patterns, f, indent=2)
 
 # Create markdown report
 with OUTPUT_MD.open("w", encoding="utf-8") as f:
 f.write("# Systematic Pattern Extraction - Pattern Definitions\n\n")
 f.write(f"**Total Pattern Families:** {len(patterns)}\n")
 f.write(f"**Total Variants:** {total_variants}\n\n")
 
 for name, pattern in patterns.items():
 f.write(f"## {name}\n\n")
 f.write(f"**Description:** {pattern['description']}\n")
 f.write(f"**Variants:** {pattern['count']}\n\n")
 if pattern['variants']:
 f.write("Example variants:\n\n")
 for i, variant in enumerate(pattern['variants'][:5], 1):
 f.write(f"{i}. {variant}\n")
 if len(pattern['variants']) > 5:
 f.write(f"... and {len(pattern['variants']) - 5} more\n")
 f.write("\n")
 
 print(f"Pattern definitions saved:")
 print(f" - {OUTPUT_JSON}")
 print(f" - {OUTPUT_MD}")
 print()
 print("Next step: Create extraction script that uses these patterns")

if __name__ == "__main__":
 main()

