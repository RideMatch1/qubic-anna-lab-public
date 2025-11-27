#!/usr/bin/env python3
"""
Warum ist Position 27 so besonders? - Umfassende Analyse
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime
import statistics

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
MATRIX_FILE = project_root / "outputs" / "analysis" / "anna_matrix.npy"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

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

def analyze_position27_vs_30(pairs: List[Dict]) -> Dict:
 """Analyze Zusammenhang zwischen Position 27 und 30."""
 
 # Position 27 ist 3 Positionen vor Position 30 (Mitte)
 # Analyze ob es Zusammenhang gibt
 
 pos27_30_combinations = defaultdict(lambda: {"same_27": 0, "same_30": 0, "both_same": 0, "total": 0})
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 if len(l3_id) > 30 and len(l4_id) > 30:
 pos27_same = l3_id[27].upper() == l4_id[27].upper()
 pos30_same = l3_id[30].upper() == l4_id[30].upper()
 
 combo = f"{l3_id[27].upper()}{l3_id[30].upper()}"
 pos27_30_combinations[combo]["total"] += 1
 
 if pos27_same:
 pos27_30_combinations[combo]["same_27"] += 1
 if pos30_same:
 pos27_30_combinations[combo]["same_30"] += 1
 if pos27_same and pos30_same:
 pos27_30_combinations[combo]["both_same"] += 1
 
 return {
 "combinations": {
 k: {
 "total": v["total"],
 "same_27_rate": v["same_27"] / v["total"] if v["total"] > 0 else 0,
 "same_30_rate": v["same_30"] / v["total"] if v["total"] > 0 else 0,
 "both_same_rate": v["both_same"] / v["total"] if v["total"] > 0 else 0
 }
 for k, v in pos27_30_combinations.items()
 }
 }

def analyze_block1_special(pairs: List[Dict]) -> Dict:
 """Analyze ob Block 1 speziell ist."""
 
 # Block 1: Position 14-27
 # Vergleiche Block 1 mit anderen Blöcken
 
 block_stabilities = defaultdict(lambda: {"same": 0, "different": 0})
 
 block_ranges = [(0, 14), (14, 28), (28, 42), (42, 56)]
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 for block_idx, (start, end) in enumerate(block_ranges):
 for pos in range(start, end):
 if l3_id[pos].upper() == l4_id[pos].upper():
 block_stabilities[block_idx]["same"] += 1
 else:
 block_stabilities[block_idx]["different"] += 1
 
 # Berechne Stabilitätsraten
 block_rates = {}
 for block_idx in range(4):
 stats = block_stabilities[block_idx]
 total = stats["same"] + stats["different"]
 if total > 0:
 block_rates[block_idx] = {
 "stability_rate": stats["same"] / total,
 "same": stats["same"],
 "different": stats["different"],
 "total": total
 }
 
 return {
 "block_stabilities": {str(k): dict(v) for k, v in block_stabilities.items()},
 "block_rates": {str(k): v for k, v in block_rates.items()}
 }

def analyze_position27_matrix_relationship(pairs: List[Dict]) -> Dict:
 """Analyze Matrix-Beziehung for Position 27."""
 
 # Position 27 entspricht welcher Matrix-Koordinate?
 # Identity hat 60 Characters = 4 Blocks à 14 Characters
 # Position 27 ist in Block 1, Position 13 im Block
 
 # Vereinfachte Analyse: Character-Werte in Position 27
 pos27_values = []
 
 for pair in pairs:
 l3_id = pair["layer3"]
 if len(l3_id) > 27:
 char = l3_id[27].upper()
 char_val = ord(char) - ord('A')
 pos27_values.append(char_val)
 
 return {
 "char_value_distribution": dict(Counter(pos27_values)),
 "mean_char_value": statistics.mean(pos27_values) if pos27_values else 0,
 "median_char_value": statistics.median(pos27_values) if pos27_values else 0
 }

def analyze_symmetry_around_position27(pairs: List[Dict]) -> Dict:
 """Analyze Symmetrie um Position 27."""
 
 # Position 27 ist 3 Positionen vor Mitte (30)
 # Analyze Symmetrie: Position 27 vs. Position 33 (3 nach Mitte)
 # Oder: Position 27 vs. Position 23 (4 vor Position 27)
 
 symmetry_analysis = {
 "pos27_vs_pos33": {"both_same": 0, "both_different": 0, "one_same": 0, "total": 0},
 "pos27_vs_pos23": {"both_same": 0, "both_different": 0, "one_same": 0, "total": 0},
 "pos27_vs_pos30": {"both_same": 0, "both_different": 0, "one_same": 0, "total": 0}
 }
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 if len(l3_id) > 33 and len(l4_id) > 33:
 pos27_same = l3_id[27].upper() == l4_id[27].upper()
 pos33_same = l3_id[33].upper() == l4_id[33].upper()
 pos23_same = l3_id[23].upper() == l4_id[23].upper() if len(l3_id) > 23 else False
 pos30_same = l3_id[30].upper() == l4_id[30].upper()
 
 # Position 27 vs. 33 (symmetrisch um Mitte)
 symmetry_analysis["pos27_vs_pos33"]["total"] += 1
 if pos27_same and pos33_same:
 symmetry_analysis["pos27_vs_pos33"]["both_same"] += 1
 elif not pos27_same and not pos33_same:
 symmetry_analysis["pos27_vs_pos33"]["both_different"] += 1
 else:
 symmetry_analysis["pos27_vs_pos33"]["one_same"] += 1
 
 # Position 27 vs. 23 (4 Positionen Abstand)
 if pos23_same:
 symmetry_analysis["pos27_vs_pos23"]["total"] += 1
 if pos27_same and pos23_same:
 symmetry_analysis["pos27_vs_pos23"]["both_same"] += 1
 elif not pos27_same and not pos23_same:
 symmetry_analysis["pos27_vs_pos23"]["both_different"] += 1
 else:
 symmetry_analysis["pos27_vs_pos23"]["one_same"] += 1
 
 # Position 27 vs. 30 (Mitte)
 symmetry_analysis["pos27_vs_pos30"]["total"] += 1
 if pos27_same and pos30_same:
 symmetry_analysis["pos27_vs_pos30"]["both_same"] += 1
 elif not pos27_same and not pos30_same:
 symmetry_analysis["pos27_vs_pos30"]["both_different"] += 1
 else:
 symmetry_analysis["pos27_vs_pos30"]["one_same"] += 1
 
 return symmetry_analysis

def analyze_position27_context(pairs: List[Dict]) -> Dict:
 """Analyze Context um Position 27."""
 
 # Analyze Positionen 25-29 (Context um Position 27)
 context_analysis = defaultdict(lambda: {"same": 0, "different": 0})
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 for pos in range(25, 30):
 if len(l3_id) > pos and len(l4_id) > pos:
 if l3_id[pos].upper() == l4_id[pos].upper():
 context_analysis[pos]["same"] += 1
 else:
 context_analysis[pos]["different"] += 1
 
 context_rates = {}
 for pos in range(25, 30):
 if pos in context_analysis:
 stats = context_analysis[pos]
 total = stats["same"] + stats["different"]
 if total > 0:
 context_rates[pos] = {
 "stability_rate": stats["same"] / total,
 "same": stats["same"],
 "different": stats["different"]
 }
 
 return {
 "context_rates": {str(k): v for k, v in context_rates.items()}
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("WARUM IST POSITION 27 SO BESONDERS? - UMFASSENDE ANALYSE")
 print("=" * 80)
 print()
 
 # Load Paare
 print("📂 Load Layer-3 → Layer-4 Paare...")
 pairs = load_pairs()
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Verschiedene Analysen
 print("🔍 Analyze Position 27 vs. Position 30...")
 pos27_30_analysis = analyze_position27_vs_30(pairs)
 print("✅ Position 27 vs. 30 analysiert")
 print()
 
 print("🔍 Analyze Block 1 (ist Block 1 speziell?)...")
 block1_analysis = analyze_block1_special(pairs)
 print("✅ Block 1 analysiert")
 print()
 
 print("🔍 Analyze Position 27 Matrix-Beziehung...")
 matrix_analysis = analyze_position27_matrix_relationship(pairs)
 print("✅ Matrix-Beziehung analysiert")
 print()
 
 print("🔍 Analyze Symmetrie um Position 27...")
 symmetry_analysis = analyze_symmetry_around_position27(pairs)
 print("✅ Symmetrie analysiert")
 print()
 
 print("🔍 Analyze Context um Position 27...")
 context_analysis = analyze_position27_context(pairs)
 print("✅ Context analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Block 1 Analyse
 block_rates = block1_analysis.get("block_rates", {})
 if block_rates:
 print("📊 Block-Stabilität Vergleich:")
 for block_idx in range(4):
 block_str = str(block_idx)
 if block_str in block_rates:
 rate = block_rates[block_str].get("stability_rate", 0) * 100
 print(f" Block {block_idx}: {rate:.1f}% stabil")
 print()
 
 # Position 27 vs. 30
 combinations = pos27_30_analysis.get("combinations", {})
 if combinations:
 # Finde Kombinationen wo beide gleich bleiben
 both_same_combos = [(k, v) for k, v in combinations.items() if v.get("both_same_rate", 0) > 0.1]
 if both_same_combos:
 print("📊 Position 27+30 Kombinationen (beide gleich, Rate > 10%):")
 sorted_combos = sorted(both_same_combos, key=lambda x: x[1]["both_same_rate"], reverse=True)
 for combo, stats in sorted_combos[:10]:
 rate = stats.get("both_same_rate", 0) * 100
 print(f" {combo}: {rate:.1f}% beide gleich ({stats.get('total', 0)} Fälle)")
 print()
 
 # Symmetrie
 symmetry = symmetry_analysis
 if symmetry:
 print("📊 Symmetrie-Analyse:")
 for key, stats in symmetry.items():
 total = stats.get("total", 0)
 if total > 0:
 both_same_rate = stats.get("both_same", 0) / total * 100
 both_diff_rate = stats.get("both_different", 0) / total * 100
 one_same_rate = stats.get("one_same", 0) / total * 100
 print(f" {key}:")
 print(f" Beide gleich: {both_same_rate:.1f}%")
 print(f" Beide different: {both_diff_rate:.1f}%")
 print(f" Einer gleich: {one_same_rate:.1f}%")
 print()
 
 # Context
 context = context_analysis.get("context_rates", {})
 if context:
 print("📊 Context um Position 27 (Position 25-29):")
 for pos in range(25, 30):
 pos_str = str(pos)
 if pos_str in context:
 rate = context[pos_str].get("stability_rate", 0) * 100
 marker = "⭐" if pos == 27 else " "
 print(f" {marker} Position {pos}: {rate:.1f}% stabil")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "pos27_30_analysis": pos27_30_analysis,
 "block1_analysis": block1_analysis,
 "matrix_analysis": matrix_analysis,
 "symmetry_analysis": symmetry_analysis,
 "context_analysis": context_analysis
 }
 
 output_file = OUTPUT_DIR / "why_position27_special_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Warum ist Position 27 so besonders? - Umfassende Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Hypothesen getestet",
 "",
 "1. **Zusammenhang mit Position 30** (Mitte der Identity)",
 "2. **Block 1 ist speziell?**",
 "3. **Matrix-Beziehung**",
 "4. **Symmetrie um Position 27**",
 "5. **Context um Position 27**",
 ""
 ]
 
 report_file = REPORTS_DIR / "why_position27_special_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

