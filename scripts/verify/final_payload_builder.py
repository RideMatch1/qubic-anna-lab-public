#!/usr/bin/env python3
"""
Final Payload Builder: Combine the three codes (Horizontal, Vertical, Time)
to create test payloads for the Smart Contract trigger.

This script will:
1. Load tick analysis results
2. Load coordinate analysis results
3. Combine all three codes
4. Generate test payloads for the 8-fold coordinated trigger
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

OUTPUT_DIR = Path("outputs/derived")
TICK_ANALYSIS_FILE = OUTPUT_DIR / "tick_pattern_analysis_all_layers.json"
COORD_ANALYSIS_FILE = OUTPUT_DIR / "matrix_coordinate_analysis.json"
LAYER_INDEX_FILE = OUTPUT_DIR / "layer_index_code_analysis.json"
OUTPUT_JSON = OUTPUT_DIR / "final_payload_configs.json"

# Layer-2 Seeds (the ones we'll send from)
LAYER2_SEEDS = [
 {
 "label": "Diagonal #1",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 "block_id": 1, # r // 32 = 0 → +1
 "layer": 2,
 },
 {
 "label": "Diagonal #2",
 "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr",
 "identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 "block_id": 2, # r // 32 = 1 → +1
 "layer": 2,
 },
 {
 "label": "Diagonal #3",
 "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn",
 "identity": "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG",
 "block_id": 3, # r // 32 = 2 → +1
 "layer": 2,
 },
 {
 "label": "Diagonal #4",
 "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 "identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 "block_id": 4, # r // 32 = 3 → +1
 "layer": 2,
 },
 {
 "label": "Vortex #1",
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml",
 "identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 "block_id": 5, # Logically derived
 "layer": 2,
 },
 {
 "label": "Vortex #2",
 "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb",
 "identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 "block_id": 6, # Logically derived
 "layer": 2,
 },
 {
 "label": "Vortex #3",
 "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw",
 "identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 "block_id": 7, # Logically derived
 "layer": 2,
 },
 {
 "label": "Vortex #4",
 "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc",
 "identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 "block_id": 8, # Logically derived
 "layer": 2,
 },
]

def load_tick_analysis() -> Dict:
 """Load tick analysis results."""
 if not TICK_ANALYSIS_FILE.exists():
 return {}
 
 with TICK_ANALYSIS_FILE.open("r", encoding="utf-8") as f:
 return json.load(f)

def load_coordinate_analysis() -> Dict:
 """Load coordinate analysis results."""
 if not COORD_ANALYSIS_FILE.exists():
 return {}
 
 with COORD_ANALYSIS_FILE.open("r", encoding="utf-8") as f:
 return json.load(f)

def generate_payload_hypotheses(tick_data: Dict, coord_data: Dict) -> List[Dict]:
 """Generate payload hypotheses based on the three codes."""
 
 hypotheses = []
 
 # Get tick gaps if available
 gaps = tick_data.get("inter_layer_gaps", {})
 layer_1_to_2_gap = None
 if "L1_to_L2" in gaps:
 layer_1_to_2_gap = int(gaps["L1_to_L2"]["average_gap"])
 elif gaps:
 # Use first available gap
 first_gap = list(gaps.values())[0]
 layer_1_to_2_gap = int(first_gap["average_gap"])
 
 # Known from previous analysis
 if layer_1_to_2_gap is None:
 layer_1_to_2_gap = 1649 # Known value
 
 # Hypothesis 1: Simple Index Tuple [Block-ID, Layer-Index]
 hypotheses.append({
 "name": "Simple Index Tuple",
 "description": "[Horizontal Code, Vertical Code]",
 "format": "[block_id, layer_index]",
 "payloads": [
 {
 "label": entry["label"],
 "seed": entry["seed"],
 "identity": entry["identity"],
 "payload": [entry["block_id"], entry["layer"]],
 "payload_string": f"{entry['block_id']},{entry['layer']}",
 }
 for entry in LAYER2_SEEDS
 ],
 })
 
 # Hypothesis 2: With Timing Code [Block-ID, Layer-Index, Tick-Gap]
 hypotheses.append({
 "name": "With Timing Code",
 "description": "[Horizontal Code, Vertical Code, Time Code]",
 "format": "[block_id, layer_index, tick_gap]",
 "payloads": [
 {
 "label": entry["label"],
 "seed": entry["seed"],
 "identity": entry["identity"],
 "payload": [entry["block_id"], entry["layer"], layer_1_to_2_gap],
 "payload_string": f"{entry['block_id']},{entry['layer']},{layer_1_to_2_gap}",
 }
 for entry in LAYER2_SEEDS
 ],
 })
 
 # Hypothesis 3: Zero-based [Block-ID-1, Layer-Index-1]
 hypotheses.append({
 "name": "Zero-based Index Tuple",
 "description": "[Block-ID-1, Layer-Index-1] (zero-based)",
 "format": "[block_id-1, layer_index-1]",
 "payloads": [
 {
 "label": entry["label"],
 "seed": entry["seed"],
 "identity": entry["identity"],
 "payload": [entry["block_id"] - 1, entry["layer"] - 1],
 "payload_string": f"{entry['block_id']-1},{entry['layer']-1}",
 }
 for entry in LAYER2_SEEDS
 ],
 })
 
 # Hypothesis 4: Single Encoded Number
 # Encode as: block_id * 100 + layer_index
 hypotheses.append({
 "name": "Single Encoded Number",
 "description": "block_id * 100 + layer_index",
 "format": "block_id * 100 + layer_index",
 "payloads": [
 {
 "label": entry["label"],
 "seed": entry["seed"],
 "identity": entry["identity"],
 "payload": entry["block_id"] * 100 + entry["layer"],
 "payload_string": str(entry["block_id"] * 100 + entry["layer"]),
 }
 for entry in LAYER2_SEEDS
 ],
 })
 
 return hypotheses

def create_tick_gap_table(tick_data: Dict) -> List[Dict]:
 """Create a table of tick gaps between all layers."""
 gaps = tick_data.get("inter_layer_gaps", {})
 
 table = []
 for gap_name in sorted(gaps.keys()):
 gap_data = gaps[gap_name]
 table.append({
 "transition": gap_name,
 "average_gap": gap_data["average_gap"],
 "min_gap": gap_data["min_gap"],
 "max_gap": gap_data["max_gap"],
 "std_dev": gap_data["std_dev"],
 })
 
 return table

def main() -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("FINAL PAYLOAD BUILDER")
 print("=" * 80)
 print()
 print("Combining the three codes to create test payloads")
 print()
 
 # Load analyses
 print("Loading analyses...")
 tick_data = load_tick_analysis()
 coord_data = load_coordinate_analysis()
 
 if tick_data.get("all_ticks"):
 print(f" ✅ Tick analysis: {sum(len(v) for v in tick_data['all_ticks'].values())} ticks loaded")
 else:
 print(f" ⚠️ Tick analysis: Not complete yet")
 
 if coord_data:
 print(f" ✅ Coordinate analysis: Loaded")
 else:
 print(f" ⚠️ Coordinate analysis: Not found")
 
 print()
 
 # Generate hypotheses
 print("=" * 80)
 print("GENERATING PAYLOAD HYPOTHESES")
 print("=" * 80)
 print()
 
 hypotheses = generate_payload_hypotheses(tick_data, coord_data)
 
 for i, hypothesis in enumerate(hypotheses, 1):
 print(f"Hypothesis {i}: {hypothesis['name']}")
 print(f" Description: {hypothesis['description']}")
 print(f" Format: {hypothesis['format']}")
 print(f" Example payloads:")
 for payload_data in hypothesis['payloads'][:3]:
 print(f" {payload_data['label']}: {payload_data['payload_string']}")
 print()
 
 # Create tick gap table
 print("=" * 80)
 print("TICK GAP TABLE")
 print("=" * 80)
 print()
 
 gap_table = create_tick_gap_table(tick_data)
 
 if gap_table:
 print("Inter-Layer Tick Gaps:")
 print("| Transition | Average Gap | Min | Max | Std Dev |")
 print("|---|---|---|---|---|")
 for row in gap_table:
 print(f"| {row['transition']} | {row['average_gap']:.1f} | {row['min_gap']} | {row['max_gap']} | {row['std_dev']:.1f} |")
 else:
 print("⚠️ Tick gaps not available yet (analysis still running)")
 
 print()
 
 # Save results
 output = {
 "hypotheses": hypotheses,
 "tick_gap_table": gap_table,
 "tick_analysis_available": bool(tick_data.get("all_ticks")),
 "anomalies": tick_data.get("anomalies", []),
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print("=" * 80)
 print(f"Report saved to: {OUTPUT_JSON}")
 print("=" * 80)
 print()
 print("NEXT: Test these payloads on the Smart Contract")
 print(" Start with Hypothesis 1 (Simple Index Tuple)")

if __name__ == "__main__":
 main()

