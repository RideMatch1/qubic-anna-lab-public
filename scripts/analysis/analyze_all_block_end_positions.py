#!/usr/bin/env python3
"""
Analyze alle Block-Ende-Positionen (13, 27, 41, 55) auf gemeinsame Patterns
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime
import statistics

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

# Block-Ende-Positionen: 13, 27, 41, 55
BLOCK_END_POSITIONS = [13, 27, 41, 55]

def load_pairs() -> List[Dict]:
 """Load Layer-3 → Layer-4 Paare."""
 layer3_data = []
 if LAYER3_FILE.exists():
 with LAYER3_FILE.open() as f:
 data = json.load(f)
 layer3_data = data.get("results", [])
 
 layer4_map = {}
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 data = json.load(f)
 for entry in data.get("results", []):
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 if l3_id and l4_id:
 layer4_map[l3_id] = l4_id
 
 pairs = []
 for l3_entry in layer3_data:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 if l3_id and l4_id and len(l3_id) == 60 and len(l4_id) == 60:
 pairs.append({"layer3": l3_id, "layer4": l4_id})
 
 return pairs

def analyze_block_end_positions(pairs: List[Dict]) -> Dict:
 """Analyze alle Block-Ende-Positionen."""
 
 position_analyses = {}
 
 for pos in BLOCK_END_POSITIONS:
 # Character-Distribution
 l3_chars = Counter()
 l4_chars = Counter()
 
 # Transitions
 transitions = Counter()
 
 # Stabile Characters
 stable_chars = Counter()
 
 # Character-Distanzen
 distances = []
 
 # Stabilität
 same_count = 0
 different_count = 0
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 if len(l3_id) > pos and len(l4_id) > pos:
 l3_char = l3_id[pos].upper()
 l4_char = l4_id[pos].upper()
 
 l3_chars[l3_char] += 1
 l4_chars[l4_char] += 1
 
 if l3_char == l4_char:
 same_count += 1
 stable_chars[l3_char] += 1
 else:
 different_count += 1
 transition = f"{l3_char}->{l4_char}"
 transitions[transition] += 1
 
 # Character-Distanz
 l3_val = ord(l3_char) - ord('A')
 l4_val = ord(l4_char) - ord('A')
 distance = min((l4_val - l3_val) % 26, (l3_val - l4_val) % 26)
 distances.append(distance)
 
 total = same_count + different_count
 stability_rate = same_count / total if total > 0 else 0
 
 position_analyses[pos] = {
 "block": pos // 14, # Block-Nummer (0, 1, 2, 3)
 "position_in_block": pos % 14, # Position im Block
 "stability_rate": stability_rate,
 "same_count": same_count,
 "different_count": different_count,
 "total": total,
 "l3_distribution": dict(l3_chars.most_common(10)),
 "l4_distribution": dict(l4_chars.most_common(10)),
 "transitions": dict(transitions.most_common(15)),
 "stable_chars": dict(stable_chars.most_common(10)),
 "distance_stats": {
 "mean": statistics.mean(distances) if distances else 0,
 "median": statistics.median(distances) if distances else 0,
 "stdev": statistics.stdev(distances) if len(distances) > 1 else 0,
 "distribution": dict(Counter(distances).most_common(10))
 }
 }
 
 # Vergleiche alle Block-Ende-Positionen
 comparison = {
 "stability_comparison": {
 str(pos): position_analyses[pos]["stability_rate"]
 for pos in BLOCK_END_POSITIONS
 },
 "distance_comparison": {
 str(pos): position_analyses[pos]["distance_stats"]["mean"]
 for pos in BLOCK_END_POSITIONS
 },
 "common_patterns": {}
 }
 
 # Finde gemeinsame Patterns
 # 1. Gemeinsame stabile Characters
 all_stable_chars = [set(position_analyses[pos]["stable_chars"].keys()) for pos in BLOCK_END_POSITIONS]
 common_stable = set.intersection(*all_stable_chars) if all_stable_chars else set()
 
 # 2. Gemeinsame Top Transitions
 all_transitions = [set(position_analyses[pos]["transitions"].keys()) for pos in BLOCK_END_POSITIONS]
 common_transitions = set.intersection(*all_transitions) if all_transitions else set()
 
 comparison["common_patterns"] = {
 "common_stable_chars": list(common_stable),
 "common_transitions": list(common_transitions),
 "all_stable_chars": {str(pos): list(position_analyses[pos]["stable_chars"].keys())[:5] for pos in BLOCK_END_POSITIONS},
 "all_top_transitions": {str(pos): list(position_analyses[pos]["transitions"].keys())[:5] for pos in BLOCK_END_POSITIONS}
 }
 
 return {
 "position_analyses": {str(k): v for k, v in position_analyses.items()},
 "comparison": comparison
 }

def analyze_block_structure(pairs: List[Dict]) -> Dict:
 """Analyze Block-Struktur im Detail."""
 
 # Analyze alle Positionen in jedem Block
 block_analyses = defaultdict(lambda: defaultdict(lambda: {"same": 0, "different": 0}))
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 # 4 Blocks: 0-13, 14-27, 28-41, 42-55
 block_ranges = [(0, 14), (14, 28), (28, 42), (42, 56)]
 
 for block_idx, (start, end) in enumerate(block_ranges):
 for pos in range(start, end):
 if l3_id[pos].upper() == l4_id[pos].upper():
 block_analyses[block_idx][pos - start]["same"] += 1
 else:
 block_analyses[block_idx][pos - start]["different"] += 1
 
 # Berechne Stabilitätsraten pro Position im Block
 block_stability_rates = {}
 for block_idx in range(4):
 block_stability_rates[block_idx] = {}
 for pos_in_block in range(14):
 if pos_in_block in block_analyses[block_idx]:
 stats = block_analyses[block_idx][pos_in_block]
 total = stats["same"] + stats["different"]
 if total > 0:
 block_stability_rates[block_idx][pos_in_block] = {
 "stability_rate": stats["same"] / total,
 "same": stats["same"],
 "different": stats["different"]
 }
 
 # Finde Positionen mit höchster Stabilität in jedem Block
 block_most_stable = {}
 for block_idx in range(4):
 if block_idx in block_stability_rates:
 sorted_positions = sorted(
 block_stability_rates[block_idx].items(),
 key=lambda x: x[1]["stability_rate"],
 reverse=True
 )
 block_most_stable[block_idx] = {
 "most_stable": sorted_positions[0] if sorted_positions else None,
 "top_5": sorted_positions[:5]
 }
 
 return {
 "block_stability_rates": {
 str(k): {str(p): v for p, v in positions.items()}
 for k, positions in block_stability_rates.items()
 },
 "block_most_stable": {
 str(k): {
 "most_stable": (str(v["most_stable"][0]), v["most_stable"][1]) if v["most_stable"] else None,
 "top_5": [(str(p), rates) for p, rates in v["top_5"]]
 }
 for k, v in block_most_stable.items()
 }
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("ALLE BLOCK-ENDE-POSITIONEN ANALYSE (13, 27, 41, 55)")
 print("=" * 80)
 print()
 
 # Load Paare
 print("📂 Load Layer-3 → Layer-4 Paare...")
 pairs = load_pairs()
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Analyze Block-Ende-Positionen
 print("🔍 Analyze Block-Ende-Positionen...")
 block_end_analysis = analyze_block_end_positions(pairs)
 print("✅ Block-Ende-Positionen analysiert")
 print()
 
 # Analyze Block-Struktur
 print("🔍 Analyze Block-Struktur...")
 block_structure = analyze_block_structure(pairs)
 print("✅ Block-Struktur analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Vergleich aller Block-Ende-Positionen
 pos_analyses = block_end_analysis.get("position_analyses", {})
 comparison = block_end_analysis.get("comparison", {})
 
 print("📊 BLOCK-ENDE-POSITIONEN VERGLEICH:")
 print()
 for pos in BLOCK_END_POSITIONS:
 pos_str = str(pos)
 if pos_str in pos_analyses:
 analysis = pos_analyses[pos_str]
 block = analysis.get("block", 0)
 pos_in_block = analysis.get("position_in_block", 0)
 stability = analysis.get("stability_rate", 0) * 100
 distance_mean = analysis.get("distance_stats", {}).get("mean", 0)
 
 print(f" Position {pos:2d} (Block {block}, Pos {pos_in_block:2d} im Block):")
 print(f" Stabilität: {stability:5.1f}%")
 print(f" Mean Distanz: {distance_mean:.2f}")
 print()
 
 # Stabilitäts-Vergleich
 stab_comp = comparison.get("stability_comparison", {})
 if stab_comp:
 print("📊 Stabilitäts-Vergleich:")
 sorted_stab = sorted(stab_comp.items(), key=lambda x: x[1], reverse=True)
 for pos_str, rate in sorted_stab:
 print(f" Position {pos_str:2s}: {rate*100:5.1f}%")
 print()
 
 # Distanz-Vergleich
 dist_comp = comparison.get("distance_comparison", {})
 if dist_comp:
 print("📊 Distanz-Vergleich (Mean):")
 sorted_dist = sorted(dist_comp.items(), key=lambda x: x[1])
 for pos_str, mean_dist in sorted_dist:
 print(f" Position {pos_str:2s}: {mean_dist:.2f}")
 print()
 
 # Gemeinsame Patterns
 common = comparison.get("common_patterns", {})
 if common:
 print("📊 Gemeinsame Patterns:")
 if common.get("common_stable_chars"):
 print(f" Gemeinsame stabile Characters: {', '.join(common['common_stable_chars'])}")
 else:
 print(" Keine gemeinsamen stabilen Characters")
 if common.get("common_transitions"):
 print(f" Gemeinsame Transitions: {', '.join(common['common_transitions'][:5])}")
 else:
 print(" Keine gemeinsamen Transitions")
 print()
 
 # Block-Struktur: Top Positionen pro Block
 block_most_stable = block_structure.get("block_most_stable", {})
 if block_most_stable:
 print("📊 Top Stabile Positionen pro Block:")
 for block_idx in range(4):
 block_str = str(block_idx)
 if block_str in block_most_stable:
 most_stable = block_most_stable[block_str].get("most_stable")
 if most_stable:
 pos_in_block, rates = most_stable
 global_pos = block_idx * 14 + int(pos_in_block)
 stab_rate = rates.get("stability_rate", 0) * 100
 print(f" Block {block_idx}: Position {pos_in_block} (Global {global_pos}) - {stab_rate:.1f}%")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "block_end_analysis": block_end_analysis,
 "block_structure": block_structure
 }
 
 output_file = OUTPUT_DIR / "all_block_end_positions_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Alle Block-Ende-Positionen Analyse (13, 27, 41, 55)",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Block-Ende-Positionen Vergleich",
 ""
 ]
 
 for pos in BLOCK_END_POSITIONS:
 pos_str = str(pos)
 if pos_str in pos_analyses:
 analysis = pos_analyses[pos_str]
 block = analysis.get("block", 0)
 pos_in_block = analysis.get("position_in_block", 0)
 stability = analysis.get("stability_rate", 0) * 100
 distance_mean = analysis.get("distance_stats", {}).get("mean", 0)
 
 report_lines.extend([
 f"### Position {pos} (Block {block}, Position {pos_in_block} im Block):",
 f"- **Stabilität**: {stability:.1f}%",
 f"- **Mean Character-Distanz**: {distance_mean:.2f}",
 ""
 ])
 
 report_file = REPORTS_DIR / "all_block_end_positions_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

