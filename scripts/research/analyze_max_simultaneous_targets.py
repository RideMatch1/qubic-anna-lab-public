#!/usr/bin/env python3
"""
Analyze: Wie viele Positionen können gleichzeitig gesetzt werden?
- Teste verschiedene Kombinationen
- Finde maximale Anzahl gleichzeitiger Targets
- KEINE Spekulationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
from datetime import datetime
import random

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
MAPPING_FILE = project_root / "outputs" / "derived" / "all_seed_identity_mappings_complete.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def find_seeds_with_targets(targets: Dict[int, str]) -> List[str]:
 """Finde Seeds die alle Targets erfüllen."""
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 matching = []
 
 for entry in layer3_results:
 identity = entry.get("layer3_identity", "")
 if len(identity) != 60:
 continue
 
 seed = identity_to_seed(identity)
 if len(seed) < 55:
 continue
 
 # Check ob Seed alle Targets erfüllt
 seed_matches = True
 for pos, target_char in targets.items():
 if pos < 55:
 if len(seed) > pos and seed[pos].lower() != target_char.lower():
 seed_matches = False
 break
 
 if seed_matches:
 # Check ob Identity auch alle Targets erfüllt
 identity_matches = True
 for pos, target_char in targets.items():
 if len(identity) > pos and identity[pos].upper() != target_char.upper():
 identity_matches = False
 break
 
 if identity_matches:
 matching.append(identity)
 
 return matching

def test_simultaneous_targets(num_positions: int, num_tests: int = 10) -> Dict:
 """Teste ob num_positions gleichzeitig gesetzt werden können."""
 
 with MAPPING_FILE.open() as f:
 data = json.load(f)
 
 perfect_mappings = data.get("all_perfect_mappings", [])
 
 # Finde Positionen mit direktem Mapping
 direct_positions = set()
 for mapping in perfect_mappings:
 seed_pos = mapping["seed_position"]
 identity_pos = mapping["identity_position"]
 if seed_pos == identity_pos:
 direct_positions.add(seed_pos)
 
 direct_positions = sorted(list(direct_positions))
 
 if len(direct_positions) < num_positions:
 return {
 "num_positions": num_positions,
 "possible": False,
 "reason": f"Nur {len(direct_positions)} Positionen verfügbar"
 }
 
 # Teste verschiedene Kombinationen
 results = []
 
 for test_num in range(num_tests):
 # Wähle zufällige Positionen
 selected_positions = random.sample(direct_positions, num_positions)
 
 # Wähle zufällige Characters for jede Position
 targets = {}
 for pos in selected_positions:
 # Finde verfügbare Characters for diese Position
 available_chars = set()
 for mapping in perfect_mappings:
 if mapping["seed_position"] == pos and mapping["identity_position"] == pos:
 available_chars.add(mapping["seed_char"].upper())
 
 if available_chars:
 targets[pos] = random.choice(list(available_chars))
 
 # Finde Seeds
 matching = find_seeds_with_targets(targets)
 
 results.append({
 "targets": targets,
 "count": len(matching),
 "success": len(matching) > 0
 })
 
 success_count = sum(1 for r in results if r["success"])
 success_rate = success_count / num_tests * 100 if num_tests > 0 else 0
 avg_count = sum(r["count"] for r in results) / len(results) if results else 0
 
 return {
 "num_positions": num_positions,
 "possible": success_rate > 0,
 "success_rate": success_rate,
 "success_count": success_count,
 "total_tests": num_tests,
 "avg_matching_seeds": avg_count,
 "results": results[:5] # Sample
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("ANALYSE: MAXIMALE GLEICHZEITIGE TARGETS")
 print("=" * 80)
 print()
 print("⚠️ TESTE WIE VIELE POSITIONEN GLEICHZEITIG GESETZT WERDEN KÖNNEN!")
 print()
 
 # Teste verschiedene Anzahlen
 test_counts = [1, 2, 3, 5, 10, 15, 20, 25, 30]
 all_results = {}
 
 for num_pos in test_counts:
 print(f"🔍 Teste {num_pos} Positionen gleichzeitig...")
 result = test_simultaneous_targets(num_pos, num_tests=20)
 all_results[num_pos] = result
 
 if result["possible"]:
 print(f" ✅ Erfolgsrate: {result['success_rate']:.1f}% ({result['success_count']}/{result['total_tests']})")
 print(f" ✅ Durchschnitt: {result['avg_matching_seeds']:.1f} Seeds pro Test")
 else:
 print(f" ❌ {result.get('reason', 'Nicht möglich')}")
 print()
 
 # Zeige Zusammenfassung
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 max_positions = max([num for num, r in all_results.items() if r.get("possible", False)], default=0)
 
 print(f"📊 Maximale gleichzeitige Positionen: {max_positions}")
 print()
 
 print("📊 Ergebnisse nach Anzahl Positionen:")
 for num_pos in test_counts:
 result = all_results[num_pos]
 if result.get("possible", False):
 marker = "✅" if result["success_rate"] >= 80 else "⚠️"
 print(f" {marker} {num_pos:2d} Positionen: {result['success_rate']:.1f}% ({result['success_count']}/{result['total_tests']})")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "max_positions": max_positions,
 "all_results": all_results
 }
 
 output_file = OUTPUT_DIR / "max_simultaneous_targets_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Analyse: Maximale gleichzeitige Targets",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 f"**Maximale gleichzeitige Positionen**: {max_positions}",
 "",
 "## Ergebnisse",
 ""
 ]
 
 for num_pos in test_counts:
 result = all_results[num_pos]
 if result.get("possible", False):
 marker = "✅" if result["success_rate"] >= 80 else "⚠️"
 report_lines.append(f"{marker} **{num_pos} Positionen**: {result['success_rate']:.1f}% ({result['success_count']}/{result['total_tests']}), Durchschnitt: {result['avg_matching_seeds']:.1f} Seeds")
 else:
 report_lines.append(f"❌ **{num_pos} Positionen**: {result.get('reason', 'Nicht möglich')}")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "max_simultaneous_targets_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

