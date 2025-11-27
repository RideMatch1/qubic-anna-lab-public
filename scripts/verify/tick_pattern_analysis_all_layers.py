#!/usr/bin/env python3
"""
Tick Pattern Analysis: Analyze tick gaps across all 10 layers to find:
1. Inter-layer gaps (average tick distance between Layer N and Layer N+1)
2. Anomalies (layers with unusually large gaps)
3. Layer endpoints (especially Layer 9 → Layer 10 gap)
4. The "temporal signature" of the architect
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from qubipy.rpc import rpc_client

OUTPUT_DIR = Path("outputs/derived")
RECURSIVE_MAP_FILE = OUTPUT_DIR / "recursive_layer_map.json"
OUTPUT_JSON = OUTPUT_DIR / "tick_pattern_analysis_all_layers.json"

# Layer 1 identities (for reference)
LAYER1_IDENTITIES = [
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
]

def get_identity_tick(rpc: rpc_client.QubiPy_RPC, identity: str) -> int | None:
 """Get validForTick for an identity."""
 try:
 time.sleep(0.3)
 balance = rpc.get_balance(identity)
 if balance:
 return balance.get("validForTick")
 except:
 pass
 return None

def load_layer_structure() -> Dict:
 """Load the recursive layer structure."""
 if not RECURSIVE_MAP_FILE.exists():
 raise FileNotFoundError(f"Recursive layer map not found: {RECURSIVE_MAP_FILE}")
 
 with RECURSIVE_MAP_FILE.open("r", encoding="utf-8") as f:
 data = json.load(f)
 
 return data.get("known_8_exploration", {})

def collect_all_ticks(rpc: rpc_client.QubiPy_RPC, layer_map: Dict) -> Dict[int, List[Tuple[str, int]]]:
 """Collect ticks for all identities in all layers."""
 all_ticks: Dict[int, List[Tuple[str, int]]] = {}
 
 layer_map_data = layer_map.get("layer_map", {})
 
 for layer_str, identities in layer_map_data.items():
 layer = int(layer_str)
 all_ticks[layer] = []
 
 # Handle both list of strings and list of dicts
 identity_list = []
 if identities and isinstance(identities[0], dict):
 identity_list = [id_data.get("identity", id_data) if isinstance(id_data, dict) else id_data for id_data in identities]
 else:
 identity_list = identities
 
 print(f"Layer {layer}: Collecting ticks for {len(identity_list)} identities...")
 
 for identity in identity_list:
 # Ensure identity is a string
 identity_str = identity if isinstance(identity, str) else str(identity)
 tick = get_identity_tick(rpc, identity_str)
 if tick:
 all_ticks[layer].append((identity_str, tick))
 
 print(f" → Got ticks for {len(all_ticks[layer])}/{len(identity_list)} identities")
 
 return all_ticks

def analyze_inter_layer_gaps(all_ticks: Dict[int, List[Tuple[str, int]]]) -> Dict:
 """Analyze tick gaps between consecutive layers."""
 gaps = {}
 
 for layer in sorted(all_ticks.keys()):
 if layer == 1:
 continue
 
 prev_layer = layer - 1
 if prev_layer not in all_ticks:
 continue
 
 # Calculate gaps for each identity chain
 layer_gaps = []
 
 # Match identities by index (assuming same order)
 for idx, (identity, tick) in enumerate(all_ticks[layer]):
 if idx < len(all_ticks[prev_layer]):
 prev_identity, prev_tick = all_ticks[prev_layer][idx]
 gap = tick - prev_tick
 layer_gaps.append({
 "layer": layer,
 "identity": identity,
 "tick": tick,
 "prev_layer": prev_layer,
 "prev_identity": prev_identity,
 "prev_tick": prev_tick,
 "gap": gap,
 })
 
 if layer_gaps:
 gaps[f"L{prev_layer}_to_L{layer}"] = {
 "gaps": layer_gaps,
 "average_gap": sum(g["gap"] for g in layer_gaps) / len(layer_gaps),
 "min_gap": min(g["gap"] for g in layer_gaps),
 "max_gap": max(g["gap"] for g in layer_gaps),
 "std_dev": _calculate_std_dev([g["gap"] for g in layer_gaps]),
 }
 
 return gaps

def _calculate_std_dev(values: List[int]) -> float:
 """Calculate standard deviation."""
 if not values:
 return 0.0
 mean = sum(values) / len(values)
 variance = sum((x - mean) ** 2 for x in values) / len(values)
 return variance ** 0.5

def find_anomalies(gaps: Dict) -> List[Dict]:
 """Find layers with unusually large gaps."""
 if not gaps:
 return []
 
 # Calculate overall average gap
 all_averages = [gap_data["average_gap"] for gap_data in gaps.values()]
 overall_avg = sum(all_averages) / len(all_averages) if all_averages else 0
 
 # Find anomalies (gaps > 2x overall average)
 threshold = overall_avg * 2
 anomalies = []
 
 for gap_name, gap_data in gaps.items():
 if gap_data["average_gap"] > threshold:
 anomalies.append({
 "gap_name": gap_name,
 "average_gap": gap_data["average_gap"],
 "overall_average": overall_avg,
 "ratio": gap_data["average_gap"] / overall_avg if overall_avg > 0 else 0,
 "interpretation": "Unusually large gap - possible manual/triggered batch or exit point",
 })
 
 return anomalies

def analyze_layer_endpoints(all_ticks: Dict[int, List[Tuple[str, int]]]) -> Dict:
 """Analyze endpoints, especially Layer 9 → Layer 10."""
 max_layer = max(all_ticks.keys()) if all_ticks else 0
 
 endpoints = {
 "max_layer": max_layer,
 "layer_9_to_10": None,
 "final_layer_analysis": {},
 }
 
 if max_layer >= 10 and 9 in all_ticks and 10 in all_ticks:
 # Analyze Layer 9 → Layer 10 gap
 gaps_9_10 = []
 for idx, (identity, tick) in enumerate(all_ticks[10]):
 if idx < len(all_ticks[9]):
 prev_identity, prev_tick = all_ticks[9][idx]
 gap = tick - prev_tick
 gaps_9_10.append(gap)
 
 if gaps_9_10:
 endpoints["layer_9_to_10"] = {
 "average_gap": sum(gaps_9_10) / len(gaps_9_10),
 "min_gap": min(gaps_9_10),
 "max_gap": max(gaps_9_10),
 "gaps": gaps_9_10,
 }
 
 # Analyze final layer
 if max_layer in all_ticks:
 final_ticks = [tick for _, tick in all_ticks[max_layer]]
 endpoints["final_layer_analysis"] = {
 "layer": max_layer,
 "tick_range": max(final_ticks) - min(final_ticks) if final_ticks else 0,
 "min_tick": min(final_ticks) if final_ticks else None,
 "max_tick": max(final_ticks) if final_ticks else None,
 "average_tick": sum(final_ticks) / len(final_ticks) if final_ticks else None,
 }
 
 return endpoints

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("TICK PATTERN ANALYSIS - ALL 10 LAYERS")
 print("=" * 80)
 print()
 print("Goal: Find the temporal signature of the architect")
 print("Focus: Inter-layer gaps, anomalies, and endpoints")
 print()
 
 # Load structure
 print("Loading layer structure...")
 structure = load_layer_structure()
 layer_map = structure.get("layer_map", {})
 
 print(f"Found {len(layer_map)} layers")
 for layer in sorted(layer_map.keys(), key=int):
 print(f" Layer {layer}: {len(layer_map[layer])} identities")
 print()
 
 # Collect all ticks
 print("Collecting ticks for all identities...")
 print("(This will take a while due to rate limiting)")
 print()
 
 all_ticks = collect_all_ticks(rpc, layer_map)
 
 print()
 print("=" * 80)
 print("ANALYZING INTER-LAYER GAPS")
 print("=" * 80)
 print()
 
 # Analyze gaps
 gaps = analyze_inter_layer_gaps(all_ticks)
 
 print("Inter-Layer Gaps:")
 for gap_name in sorted(gaps.keys()):
 gap_data = gaps[gap_name]
 print(f" {gap_name}:")
 print(f" Average: {gap_data['average_gap']:.1f} ticks")
 print(f" Range: {gap_data['min_gap']} - {gap_data['max_gap']} ticks")
 print(f" Std Dev: {gap_data['std_dev']:.1f} ticks")
 
 print()
 print("=" * 80)
 print("FINDING ANOMALIES")
 print("=" * 80)
 print()
 
 anomalies = find_anomalies(gaps)
 
 if anomalies:
 print("⚠️ ANOMALIES FOUND:")
 for anomaly in anomalies:
 print(f" {anomaly['gap_name']}:")
 print(f" Average gap: {anomaly['average_gap']:.1f} ticks")
 print(f" Overall average: {anomaly['overall_average']:.1f} ticks")
 print(f" Ratio: {anomaly['ratio']:.2f}x")
 print(f" → {anomaly['interpretation']}")
 else:
 print("No significant anomalies found (all gaps are relatively consistent)")
 
 print()
 print("=" * 80)
 print("ANALYZING ENDPOINTS")
 print("=" * 80)
 print()
 
 endpoints = analyze_layer_endpoints(all_ticks)
 
 print(f"Max layer reached: {endpoints['max_layer']}")
 
 if endpoints["layer_9_to_10"]:
 l9_10 = endpoints["layer_9_to_10"]
 print()
 print("Layer 9 → Layer 10 Gap:")
 print(f" Average: {l9_10['average_gap']:.1f} ticks")
 print(f" Range: {l9_10['min_gap']} - {l9_10['max_gap']} ticks")
 
 # Compare to other gaps
 if gaps:
 other_avg = sum(g["average_gap"] for g in gaps.values()) / len(gaps)
 ratio = l9_10['average_gap'] / other_avg if other_avg > 0 else 0
 print(f" vs. Other gaps average: {other_avg:.1f} ticks")
 print(f" Ratio: {ratio:.2f}x")
 if ratio > 2:
 print(f" ⚠️ UNUSUALLY LARGE GAP - Possible exit point!")
 
 if endpoints["final_layer_analysis"]:
 final = endpoints["final_layer_analysis"]
 print()
 print("Final Layer Analysis:")
 print(f" Layer: {final['layer']}")
 print(f" Tick range: {final['tick_range']} ticks")
 print(f" Min tick: {final['min_tick']}")
 print(f" Max tick: {final['max_tick']}")
 
 # Save results
 output = {
 "all_ticks": {str(k): v for k, v in all_ticks.items()},
 "inter_layer_gaps": gaps,
 "anomalies": anomalies,
 "endpoints": endpoints,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print()
 print("=" * 80)
 print(f"Report saved to: {OUTPUT_JSON}")
 print("=" * 80)

if __name__ == "__main__":
 main()

