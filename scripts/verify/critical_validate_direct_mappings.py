#!/usr/bin/env python3
"""
KRITISCHE Validierung: Sind die direkten Mappings wirklich perfekt?
- Check Stichproben for alle 52 Positionen
- Keine Annahmen - nur echte Daten
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter
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

def validate_direct_mapping(seed_pos: int, sample_size: int = 10) -> Dict:
 """Validate direktes Mapping for eine Position (Stichprobe)."""
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 # Teste verschiedene Characters
 test_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
 results = {}
 
 for seed_char in test_chars:
 matching = []
 errors = []
 
 for entry in layer3_results:
 identity = entry.get("layer3_identity", "")
 if len(identity) != 60:
 continue
 
 seed = identity_to_seed(identity)
 if len(seed) > seed_pos and len(identity) > seed_pos:
 if seed[seed_pos].lower() == seed_char.lower():
 matching.append(identity)
 
 expected_char = seed_char.upper()
 actual_char = identity[seed_pos].upper()
 if actual_char != expected_char:
 errors.append({
 "identity": identity,
 "expected": expected_char,
 "actual": actual_char
 })
 
 # Sample for Validierung
 if len(matching) > sample_size:
 sampled = random.sample(matching, sample_size)
 sampled_errors = [e for e in errors if e["identity"] in sampled]
 else:
 sampled = matching
 sampled_errors = errors
 
 total = len(sampled)
 error_count = len(sampled_errors)
 success_count = total - error_count
 actual_rate = success_count / total * 100 if total > 0 else 0
 
 results[seed_char] = {
 "total_found": len(matching),
 "sampled": total,
 "success_count": success_count,
 "error_count": error_count,
 "actual_rate": actual_rate,
 "is_perfect": error_count == 0
 }
 
 # Zusammenfassung
 perfect_count = sum(1 for r in results.values() if r["is_perfect"])
 total_tested = len(results)
 
 return {
 "seed_position": seed_pos,
 "total_tested": total_tested,
 "perfect_count": perfect_count,
 "results": results,
 "all_perfect": perfect_count == total_tested
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("KRITISCHE VALIDIERUNG: DIREKTE MAPPINGS")
 print("=" * 80)
 print()
 print("⚠️ PRÜFE STICHPROBEN FÜR ALLE 52 POSITIONEN!")
 print()
 
 # Load Mappings
 with MAPPING_FILE.open() as f:
 data = json.load(f)
 
 # Finde Positionen mit direktem Mapping
 perfect_mappings = data.get("all_perfect_mappings", [])
 direct_positions = set()
 
 for mapping in perfect_mappings:
 seed_pos = mapping["seed_position"]
 identity_pos = mapping["identity_position"]
 if seed_pos == identity_pos:
 direct_positions.add(seed_pos)
 
 direct_positions = sorted(list(direct_positions))
 
 print(f"🔍 Validate {len(direct_positions)} Positionen mit direktem Mapping...")
 print()
 
 # Validate Stichproben
 validation_results = []
 
 for i, seed_pos in enumerate(direct_positions, 1):
 if i % 10 == 0:
 print(f" Progress: {i}/{len(direct_positions)}...")
 
 result = validate_direct_mapping(seed_pos, sample_size=10)
 validation_results.append(result)
 
 print("✅ Alle Positionen validiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("VALIDIERUNGS-ERGEBNISSE")
 print("=" * 80)
 print()
 
 all_perfect = all(r["all_perfect"] for r in validation_results)
 perfect_positions = sum(1 for r in validation_results if r["all_perfect"])
 
 print(f"📊 Perfekt: {perfect_positions}/{len(validation_results)} Positionen")
 print()
 
 if all_perfect:
 print("✅ ALLE DIREKTEN MAPPINGS SIND WIRKLICH PERFEKT!")
 print(" ✅ Keine Fehler in Stichproben gefunden")
 print(" ✅ Behauptungen sind KORREKT")
 else:
 print("⚠️ WARNUNG: Nicht alle direkten Mappings sind perfekt!")
 print(" ⚠️ Einige Fehler in Stichproben gefunden")
 
 # Zeige fehlerhafte Positionen
 print()
 print("⚠️ Positionen mit Fehlern:")
 for result in validation_results:
 if not result["all_perfect"]:
 print(f" Seed[{result['seed_position']}]: {result['perfect_count']}/{result['total_tested']} Characters perfekt")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_positions": len(validation_results),
 "perfect_positions": perfect_positions,
 "all_perfect": all_perfect,
 "validation_results": validation_results
 }
 
 output_file = OUTPUT_DIR / "direct_mappings_critical_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Kritische Validierung: Direkte Mappings",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Zusammenfassung",
 "",
 f"- **Total Positionen**: {len(validation_results)}",
 f"- **Perfekt**: {perfect_positions}",
 f"- **Alle perfekt**: {'✅ JA' if all_perfect else '❌ NEIN'}",
 ""
 ]
 
 report_file = REPORTS_DIR / "direct_mappings_critical_validation_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

