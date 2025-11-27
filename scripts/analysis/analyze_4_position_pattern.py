#!/usr/bin/env python3
"""
Analyze 4-Positionen-Pattern (Position 23, 27, 31, 35, etc.)
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
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

def analyze_4_position_pattern(pairs: List[Dict]) -> Dict:
 """Analyze 4-Positionen-Pattern."""
 
 # Teste verschiedene 4-Positionen-Abstände
 # Position 23, 27, 31, 35, 39, 43, 47, 51, 55 (jeweils +4)
 
 pattern_positions = list(range(23, 56, 4)) # 23, 27, 31, 35, 39, 43, 47, 51, 55
 
 # Analyze jede Position
 position_analyses = {}
 for pos in pattern_positions:
 same_count = 0
 different_count = 0
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 if len(l3_id) > pos and len(l4_id) > pos:
 if l3_id[pos].upper() == l4_id[pos].upper():
 same_count += 1
 else:
 different_count += 1
 
 total = same_count + different_count
 stability_rate = same_count / total if total > 0 else 0
 
 position_analyses[pos] = {
 "stability_rate": stability_rate,
 "same_count": same_count,
 "different_count": different_count,
 "total": total
 }
 
 # Analyze Paare von Positionen im Pattern
 pair_analyses = {}
 for i, pos1 in enumerate(pattern_positions):
 for pos2 in pattern_positions[i+1:]:
 both_same = 0
 both_different = 0
 one_same = 0
 total = 0
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 if len(l3_id) > max(pos1, pos2) and len(l4_id) > max(pos1, pos2):
 pos1_same = l3_id[pos1].upper() == l4_id[pos1].upper()
 pos2_same = l3_id[pos2].upper() == l4_id[pos2].upper()
 
 total += 1
 if pos1_same and pos2_same:
 both_same += 1
 elif not pos1_same and not pos2_same:
 both_different += 1
 else:
 one_same += 1
 
 if total > 0:
 pair_analyses[f"{pos1}+{pos2}"] = {
 "both_same_rate": both_same / total,
 "both_different_rate": both_different / total,
 "one_same_rate": one_same / total,
 "total": total
 }
 
 return {
 "pattern_positions": pattern_positions,
 "position_analyses": {str(k): v for k, v in position_analyses.items()},
 "pair_analyses": pair_analyses
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("4-POSITIONEN-PATTERN ANALYSE (Position 23, 27, 31, 35, ...)")
 print("=" * 80)
 print()
 
 # Load Paare
 print("📂 Load Layer-3 → Layer-4 Paare...")
 pairs = load_pairs()
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Analyze Pattern
 print("🔍 Analyze 4-Positionen-Pattern...")
 pattern_analysis = analyze_4_position_pattern(pairs)
 print("✅ Pattern analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Position-Analysen
 pos_analyses = pattern_analysis.get("position_analyses", {})
 if pos_analyses:
 print("📊 Stabilität im 4-Positionen-Pattern:")
 pattern_pos = pattern_analysis.get("pattern_positions", [])
 for pos in pattern_pos:
 pos_str = str(pos)
 if pos_str in pos_analyses:
 rate = pos_analyses[pos_str].get("stability_rate", 0) * 100
 marker = "⭐" if pos == 27 else " "
 print(f" {marker} Position {pos:2d}: {rate:5.1f}% stabil")
 print()
 
 # Paar-Analysen (Top 10)
 pair_analyses = pattern_analysis.get("pair_analyses", {})
 if pair_analyses:
 sorted_pairs = sorted(
 pair_analyses.items(),
 key=lambda x: x[1].get("both_same_rate", 0),
 reverse=True
 )
 print("📊 Top 10 Position-Paare (beide gleich):")
 for i, (pair, stats) in enumerate(sorted_pairs[:10], 1):
 rate = stats.get("both_same_rate", 0) * 100
 total = stats.get("total", 0)
 print(f" {i:2d}. Position {pair}: {rate:5.1f}% beide gleich ({total} Fälle)")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "pattern_analysis": pattern_analysis
 }
 
 output_file = OUTPUT_DIR / "4_position_pattern_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# 4-Positionen-Pattern Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Pattern-Positionen (jeweils +4)",
 ""
 ]
 
 if pos_analyses:
 pattern_pos = pattern_analysis.get("pattern_positions", [])
 for pos in pattern_pos:
 pos_str = str(pos)
 if pos_str in pos_analyses:
 rate = pos_analyses[pos_str].get("stability_rate", 0) * 100
 report_lines.append(f"- **Position {pos}**: {rate:.1f}% stabil")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "4_position_pattern_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

