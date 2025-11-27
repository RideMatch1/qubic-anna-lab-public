#!/usr/bin/env python3
"""
Teste Kombination Seed-Position 27 + 54
- Könnte noch stärkere Korrelation geben als einzeln
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def test_seed_combination_27_54(pairs: List[Dict]) -> Dict:
 """Teste Kombination Seed-Position 27 + 54."""
 
 print("🔍 Teste Kombination Seed-Position 27 + 54...")
 
 # Gruppiere nach Seed-Position 27 + 54 Kombination
 combination_groups = defaultdict(lambda: {"stable": 0, "changing": 0})
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 seed = identity_to_seed(l3_id)
 
 if len(seed) >= 55 and len(l3_id) > 27 and len(l4_id) > 27:
 seed_pos27 = seed[27].lower()
 seed_pos54 = seed[54].lower()
 combination = f"{seed_pos27}_{seed_pos54}"
 
 stable = l3_id[27].upper() == l4_id[27].upper()
 
 if stable:
 combination_groups[combination]["stable"] += 1
 else:
 combination_groups[combination]["changing"] += 1
 
 # Berechne Raten
 combination_rates = {}
 for combo, stats in combination_groups.items():
 total = stats["stable"] + stats["changing"]
 if total >= 10: # Mindestens 10 Fälle
 rate = stats["stable"] / total
 combination_rates[combo] = {
 "rate": rate,
 "stable": stats["stable"],
 "changing": stats["changing"],
 "total": total
 }
 
 # Sortiere nach Rate
 sorted_combinations = sorted(
 combination_rates.items(),
 key=lambda x: x[1]["rate"],
 reverse=True
 )
 
 return {
 "combination_rates": dict(sorted_combinations[:50]), # Top 50
 "total_combinations": len(combination_rates),
 "top_10": dict(sorted_combinations[:10])
 }

def compare_single_vs_combination(pairs: List[Dict]) -> Dict:
 """Vergleiche einzelne Seed-Positionen vs. Kombination."""
 
 # Seed-Position 27 alleine
 seed27_alone = defaultdict(lambda: {"stable": 0, "changing": 0})
 # Seed-Position 54 alleine
 seed54_alone = defaultdict(lambda: {"stable": 0, "changing": 0})
 # Kombination 27 + 54
 combination = defaultdict(lambda: {"stable": 0, "changing": 0})
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 seed = identity_to_seed(l3_id)
 
 if len(seed) >= 55 and len(l3_id) > 27 and len(l4_id) > 27:
 seed_pos27 = seed[27].lower()
 seed_pos54 = seed[54].lower()
 stable = l3_id[27].upper() == l4_id[27].upper()
 
 # Seed-Position 27 alleine
 if stable:
 seed27_alone[seed_pos27]["stable"] += 1
 else:
 seed27_alone[seed_pos27]["changing"] += 1
 
 # Seed-Position 54 alleine
 if stable:
 seed54_alone[seed_pos54]["stable"] += 1
 else:
 seed54_alone[seed_pos54]["changing"] += 1
 
 # Kombination
 combo = f"{seed_pos27}_{seed_pos54}"
 if stable:
 combination[combo]["stable"] += 1
 else:
 combination[combo]["changing"] += 1
 
 # Berechne Raten
 def calc_rates(groups):
 rates = {}
 for char, stats in groups.items():
 total = stats["stable"] + stats["changing"]
 if total >= 10:
 rate = stats["stable"] / total
 rates[char] = {
 "rate": rate,
 "stable": stats["stable"],
 "changing": stats["changing"],
 "total": total
 }
 return rates
 
 seed27_rates = calc_rates(seed27_alone)
 seed54_rates = calc_rates(seed54_alone)
 combo_rates = calc_rates(combination)
 
 # Finde beste Kombinationen
 top_combinations = sorted(
 combo_rates.items(),
 key=lambda x: x[1]["rate"],
 reverse=True
 )[:20]
 
 return {
 "seed27_alone": seed27_rates,
 "seed54_alone": seed54_rates,
 "combination": dict(top_combinations),
 "improvement": {}
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("SEED KOMBINATION 27 + 54 TEST")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Layer-3 und Layer-4 Daten...")
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 
 # Erstelle Paare
 layer4_map = {}
 for entry in layer4_results:
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 if l3_id and l4_id:
 layer4_map[l3_id] = l4_id
 
 pairs = []
 for l3_entry in layer3_results:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 if l3_id and l4_id and len(l3_id) == 60 and len(l4_id) == 60:
 pairs.append({"layer3": l3_id, "layer4": l4_id})
 
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Teste Kombination
 print("🔍 Teste Kombination Seed-Position 27 + 54...")
 combination_results = test_seed_combination_27_54(pairs)
 print("✅ Kombination getestet")
 print()
 
 # Vergleiche
 print("🔍 Vergleiche einzelne vs. Kombination...")
 comparison = compare_single_vs_combination(pairs)
 print("✅ Vergleich abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Top Kombinationen
 top_combinations = combination_results.get("top_10", {})
 if top_combinations:
 print("📊 Top 10 Seed-Kombinationen (Position 27 + 54):")
 for i, (combo, stats) in enumerate(list(top_combinations.items())[:10], 1):
 rate = stats["rate"] * 100
 seed27, seed54 = combo.split("_")
 marker = "⭐" if rate > 30 else " "
 print(f" {marker} {i:2d}. Seed[{27}]='{seed27}' + Seed[{54}]='{seed54}': {rate:.1f}% ({stats['stable']}/{stats['total']})")
 print()
 
 # Vergleich einzelne vs. Kombination
 seed27_alone = comparison.get("seed27_alone", {})
 seed54_alone = comparison.get("seed54_alone", {})
 combo = comparison.get("combination", {})
 
 if seed27_alone and seed54_alone and combo:
 print("📊 Vergleich: Einzelne vs. Kombination")
 print()
 
 # Beste einzelne
 best_seed27 = max(seed27_alone.items(), key=lambda x: x[1]["rate"])
 best_seed54 = max(seed54_alone.items(), key=lambda x: x[1]["rate"])
 best_combo = max(combo.items(), key=lambda x: x[1]["rate"])
 
 print(f" Seed[{27}]='{best_seed27[0]}' alleine: {best_seed27[1]['rate']*100:.1f}%")
 print(f" Seed[{54}]='{best_seed54[0]}' alleine: {best_seed54[1]['rate']*100:.1f}%")
 print(f" Kombination {best_combo[0]}: {best_combo[1]['rate']*100:.1f}%")
 
 improvement = best_combo[1]['rate'] - max(best_seed27[1]['rate'], best_seed54[1]['rate'])
 if improvement > 0:
 print(f" ⭐ Verbesserung: +{improvement*100:.1f}% durch Kombination!")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "combination_results": combination_results,
 "comparison": comparison
 }
 
 output_file = OUTPUT_DIR / "seed_combination_27_54_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Seed Kombination 27 + 54 Test",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Top 10 Kombinationen",
 ""
 ]
 
 if top_combinations:
 for i, (combo, stats) in enumerate(list(top_combinations.items())[:10], 1):
 rate = stats["rate"] * 100
 seed27, seed54 = combo.split("_")
 report_lines.append(f"{i}. **Seed[{27}]='{seed27}' + Seed[{54}]='{seed54}'**: {rate:.1f}% ({stats['stable']}/{stats['total']})")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "seed_combination_27_54_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

