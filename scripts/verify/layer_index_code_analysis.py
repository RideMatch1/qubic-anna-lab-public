#!/usr/bin/env python3
"""
Layer Index Code Analysis: Test if the Layer Index (1-10) itself is the "Vertical Code".

Since seeds don't map back to coordinates, the vertical code might simply be:
- The layer number (1-10)
- A function of the layer number
- The depth reached (how many layers deep)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

OUTPUT_DIR = Path("outputs/derived")
RECURSIVE_MAP_FILE = OUTPUT_DIR / "recursive_layer_map.json"
OUTPUT_JSON = OUTPUT_DIR / "layer_index_code_analysis.json"

def analyze_layer_structure() -> Dict:
 """Analyze the layer structure to find patterns."""
 
 with RECURSIVE_MAP_FILE.open("r", encoding="utf-8") as f:
 data = json.load(f)
 
 structure = data.get("known_8_exploration", {})
 layer_map = structure.get("layer_map", {})
 
 analysis = {
 "total_layers": len(layer_map),
 "identities_per_layer": {},
 "layer_indices": sorted([int(k) for k in layer_map.keys()]),
 }
 
 for layer_str, identities in layer_map.items():
 layer = int(layer_str)
 analysis["identities_per_layer"][layer] = len(identities)
 
 return analysis

def test_layer_index_hypotheses() -> Dict:
 """Test various hypotheses about layer index as code."""
 
 structure = analyze_layer_structure()
 layers = structure["layer_indices"]
 
 hypotheses = {
 "layer_index_direct": {
 "description": "Layer index itself (1-10)",
 "values": layers,
 },
 "layer_index_minus_one": {
 "description": "Layer index - 1 (0-9)",
 "values": [l - 1 for l in layers],
 },
 "layer_index_mod_8": {
 "description": "Layer index mod 8 (for 8 identities)",
 "values": [l % 8 for l in layers],
 },
 "layer_index_mod_26": {
 "description": "Layer index mod 26 (Base-26 encoding)",
 "values": [l % 26 for l in layers],
 },
 "depth_from_start": {
 "description": "Depth from Layer 1 (0-9)",
 "values": [l - 1 for l in layers],
 },
 "special_layers": {
 "description": "Special layers (2, 5, 10)",
 "values": [l for l in layers if l in [2, 5, 10]],
 },
 }
 
 return {
 "structure": structure,
 "hypotheses": hypotheses,
 }

def find_layer_patterns() -> Dict:
 """Find patterns that might indicate which layer is special."""
 
 structure = analyze_layer_structure()
 layers = structure["layer_indices"]
 
 patterns = {
 "even_layers": [l for l in layers if l % 2 == 0],
 "odd_layers": [l for l in layers if l % 2 == 1],
 "prime_layers": [l for l in layers if l in [2, 3, 5, 7]],
 "power_of_2_layers": [l for l in layers if l in [1, 2, 4, 8]],
 "divisible_by_5": [l for l in layers if l % 5 == 0],
 }
 
 return patterns

def main() -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("LAYER INDEX CODE ANALYSIS - VERTICAL CODE")
 print("=" * 80)
 print()
 print("Testing if Layer Index (1-10) is the Vertical Code")
 print()
 
 # Analyze structure
 structure = analyze_layer_structure()
 
 print("Layer Structure:")
 print(f" Total layers: {structure['total_layers']}")
 print(f" Layer indices: {structure['layer_indices']}")
 print(f" Identities per layer: {structure['identities_per_layer']}")
 print()
 
 # Test hypotheses
 print("=" * 80)
 print("TESTING LAYER INDEX HYPOTHESES")
 print("=" * 80)
 print()
 
 hypotheses = test_layer_index_hypotheses()
 
 for hyp_name, hyp_data in hypotheses["hypotheses"].items():
 print(f"{hyp_name}:")
 print(f" Description: {hyp_data['description']}")
 print(f" Values: {hyp_data['values']}")
 print()
 
 # Find patterns
 print("=" * 80)
 print("FINDING LAYER PATTERNS")
 print("=" * 80)
 print()
 
 patterns = find_layer_patterns()
 
 for pattern_name, pattern_values in patterns.items():
 if pattern_values:
 print(f"{pattern_name}: {pattern_values}")
 
 print()
 print("=" * 80)
 print("KEY INSIGHTS")
 print("=" * 80)
 print()
 print("Possible Vertical Codes:")
 print(" 1. Layer Index (1-10) - Direct")
 print(" 2. Layer Index - 1 (0-9) - Zero-based")
 print(" 3. Layer Index mod 8 (0-7) - Matches 8 identities")
 print(" 4. Special Layer (2, 5, or 10)")
 print()
 print("Most Likely:")
 print(" → Layer Index itself (1-10) OR")
 print(" → Layer Index - 1 (0-9) for zero-based indexing")
 print()
 
 # Save results
 output = {
 "structure": structure,
 "hypotheses": hypotheses,
 "patterns": patterns,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print(f"Report saved to: {OUTPUT_JSON}")
 print()
 print("=" * 80)
 print("NEXT: Combine with Tick Analysis to find the complete 3-part code:")
 print(" 1. Horizontal Code: Block-ID (from coordinates)")
 print(" 2. Time Code: Tick-Pattern or Layer-Index (from tick analysis)")
 print(" 3. Vertical Code: Layer-Index (1-10 or 0-9)")
 print("=" * 80)

if __name__ == "__main__":
 main()

