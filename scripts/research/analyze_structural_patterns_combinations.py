#!/usr/bin/env python3
"""
Analyze strukturelle Patterns in den besten Kombinationen
- Warum funktionieren manche Kombinationen besser?
- Gibt es strukturelle Zusammenhänge?
- KEINE Spekulationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

COMBINATIONS_FILE = project_root / "outputs" / "derived" / "best_target_combinations_analysis.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def analyze_structural_patterns() -> Dict:
 """Analyze strukturelle Patterns in den besten Kombinationen."""
 
 print("=" * 80)
 print("ANALYSE: STRUKTURELLE PATTERNS IN KOMBINATIONEN")
 print("=" * 80)
 print()
 
 with COMBINATIONS_FILE.open() as f:
 data = json.load(f)
 
 two_combinations = data.get("two_combinations", [])
 three_combinations = data.get("three_combinations", [])
 
 print(f"📊 {len(two_combinations)} 2er Kombinationen analysiert")
 print(f"📊 {len(three_combinations)} 3er Kombinationen analysiert")
 print()
 
 # Analyze 2er Kombinationen
 print("🔍 Analyze 2er Kombinationen...")
 
 # Finde häufigste Positionen in besten Kombinationen
 position_frequency_2 = Counter()
 position_pairs_2 = Counter()
 
 for combo in two_combinations:
 if combo.get("success_rate", 0) >= 90: # Nur beste
 positions = combo.get("positions", [])
 if len(positions) == 2:
 position_frequency_2[positions[0]] += 1
 position_frequency_2[positions[1]] += 1
 position_pairs_2[tuple(sorted(positions))] += 1
 
 print("✅ 2er Kombinationen analysiert")
 print()
 
 # Analyze 3er Kombinationen
 print("🔍 Analyze 3er Kombinationen...")
 
 position_frequency_3 = Counter()
 
 for combo in three_combinations:
 if combo.get("success_rate", 0) >= 80: # Nur beste
 positions = combo.get("positions", [])
 for pos in positions:
 position_frequency_3[pos] += 1
 
 print("✅ 3er Kombinationen analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("STRUKTURELLE PATTERNS")
 print("=" * 80)
 print()
 
 print("📊 Häufigste Positionen in besten 2er Kombinationen:")
 for pos, count in position_frequency_2.most_common(10):
 marker = "⭐" if count >= 10 else " "
 print(f" {marker} Position {pos:2d}: {count}x")
 print()
 
 print("📊 Häufigste Position-Paare in besten 2er Kombinationen:")
 for pair, count in position_pairs_2.most_common(10):
 marker = "⭐" if count >= 3 else " "
 print(f" {marker} {pair}: {count}x")
 print()
 
 print("📊 Häufigste Positionen in besten 3er Kombinationen:")
 for pos, count in position_frequency_3.most_common(10):
 marker = "⭐" if count >= 3 else " "
 print(f" {marker} Position {pos:2d}: {count}x")
 print()
 
 # Analyze Distanzen
 print("🔍 Analyze Distanzen zwischen Positionen...")
 
 distances_2 = []
 for combo in two_combinations:
 if combo.get("success_rate", 0) >= 90:
 positions = combo.get("positions", [])
 if len(positions) == 2:
 distance = abs(positions[1] - positions[0])
 distances_2.append(distance)
 
 if distances_2:
 distance_counter = Counter(distances_2)
 print("📊 Häufigste Distanzen in besten 2er Kombinationen:")
 for dist, count in distance_counter.most_common(10):
 marker = "⭐" if count >= 5 else " "
 print(f" {marker} Distanz {dist:2d}: {count}x")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "position_frequency_2": dict(position_frequency_2.most_common(20)),
 "position_pairs_2": {str(k): v for k, v in position_pairs_2.most_common(20)},
 "position_frequency_3": dict(position_frequency_3.most_common(20)),
 "distance_analysis_2": dict(distance_counter.most_common(20)) if distances_2 else {}
 }
 
 output_file = OUTPUT_DIR / "structural_patterns_combinations_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Strukturelle Patterns in Kombinationen",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Häufigste Positionen (2er Kombinationen)",
 ""
 ]
 
 for pos, count in position_frequency_2.most_common(20):
 report_lines.append(f"- Position {pos}: {count}x")
 report_lines.append("")
 
 report_lines.extend([
 "## Häufigste Position-Paare (2er Kombinationen)",
 ""
 ])
 
 for pair, count in position_pairs_2.most_common(20):
 report_lines.append(f"- {pair}: {count}x")
 report_lines.append("")
 
 if distances_2:
 report_lines.extend([
 "## Distanz-Analyse (2er Kombinationen)",
 ""
 ])
 for dist, count in distance_counter.most_common(20):
 report_lines.append(f"- Distanz {dist}: {count}x")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "structural_patterns_combinations_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 return output_data

def main():
 """Hauptfunktion."""
 analyze_structural_patterns()
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("💡 ERKENNTNISSE:")
 print()
 print(" ✅ Strukturelle Patterns identifiziert")
 print(" ✅ Häufigste Positionen und Paare gefunden")
 print(" ✅ KEINE Spekulationen - nur echte Daten!")
 print()

if __name__ == "__main__":
 main()

