#!/usr/bin/env python3
"""
KRITISCHE Validierung: Sind die perfekten Mappings wirklich perfekt?
- Check jeden einzelnen Fall
- Keine Annahmen - nur echte Daten
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
MAPPING_FILE = project_root / "outputs" / "derived" / "seed_identity_position_mapping_analysis.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def critically_validate_mapping(mapping: Dict) -> Dict:
 """KRITISCH: Validate ein Mapping."""
 
 seed_pos = mapping["seed_position"]
 seed_char = mapping["seed_char"]
 identity_pos = mapping["identity_position"]
 expected_char = mapping["identity_char"]
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 matching = []
 errors = []
 
 for entry in layer3_results:
 identity = entry.get("layer3_identity", "")
 if len(identity) != 60:
 continue
 
 seed = identity_to_seed(identity)
 if len(seed) > seed_pos and len(identity) > identity_pos:
 if seed[seed_pos].lower() == seed_char.lower():
 matching.append(identity)
 
 actual_char = identity[identity_pos].upper()
 if actual_char != expected_char.upper():
 errors.append({
 "identity": identity,
 "seed": seed,
 "expected": expected_char.upper(),
 "actual": actual_char
 })
 
 total = len(matching)
 error_count = len(errors)
 success_count = total - error_count
 actual_rate = success_count / total * 100 if total > 0 else 0
 
 return {
 "mapping": mapping,
 "total": total,
 "success_count": success_count,
 "error_count": error_count,
 "actual_rate": actual_rate,
 "is_perfect": error_count == 0,
 "errors": errors[:10] # Sample
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("KRITISCHE VALIDIERUNG: PERFEKTE MAPPINGS")
 print("=" * 80)
 print()
 print("⚠️ PRÜFE JEDEN EINZELNEN FALL - KEINE ANNAHMEN!")
 print()
 
 # Load Mappings
 with MAPPING_FILE.open() as f:
 data = json.load(f)
 
 perfect_mappings = data.get("perfect_mappings", [])
 
 print(f"🔍 Validate {len(perfect_mappings)} perfekte Mappings...")
 print()
 
 # Validate jeden einzelnen
 validation_results = []
 all_perfect = True
 total_errors = 0
 
 for i, mapping in enumerate(perfect_mappings, 1):
 if i % 10 == 0:
 print(f" Progress: {i}/{len(perfect_mappings)}...")
 
 result = critically_validate_mapping(mapping)
 validation_results.append(result)
 
 if not result["is_perfect"]:
 all_perfect = False
 total_errors += result["error_count"]
 
 print("✅ Alle Mappings validiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("VALIDIERUNGS-ERGEBNISSE")
 print("=" * 80)
 print()
 
 perfect_count = sum(1 for r in validation_results if r["is_perfect"])
 imperfect_count = len(validation_results) - perfect_count
 
 print(f"📊 Perfekt: {perfect_count}/{len(validation_results)}")
 print(f"📊 Nicht perfekt: {imperfect_count}/{len(validation_results)}")
 print(f"📊 Total Fehler: {total_errors}")
 print()
 
 if all_perfect:
 print("✅ ALLE MAPPINGS SIND WIRKLICH PERFEKT!")
 print(" ✅ Keine Fehler gefunden")
 print(" ✅ Behauptungen sind KORREKT")
 else:
 print("⚠️ WARNUNG: Nicht alle Mappings sind perfekt!")
 print(f" ⚠️ {total_errors} Fehler gefunden")
 print(" ⚠️ Behauptungen müssen korrigiert werden")
 
 # Zeige fehlerhafte Mappings
 print()
 print("⚠️ Fehlerhafte Mappings:")
 for result in validation_results:
 if not result["is_perfect"]:
 m = result["mapping"]
 print(f" Seed[{m['seed_position']}]='{m['seed_char']}' → Identity[{m['identity_position']}]='{m['identity_char']}': {result['error_count']} Fehler")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_mappings": len(validation_results),
 "perfect_count": perfect_count,
 "imperfect_count": imperfect_count,
 "total_errors": total_errors,
 "all_perfect": all_perfect,
 "validation_results": validation_results
 }
 
 output_file = OUTPUT_DIR / "perfect_mappings_critical_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Kritische Validierung: Perfekte Mappings",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Zusammenfassung",
 "",
 f"- **Total Mappings**: {len(validation_results)}",
 f"- **Perfekt**: {perfect_count}",
 f"- **Nicht perfekt**: {imperfect_count}",
 f"- **Total Fehler**: {total_errors}",
 f"- **Alle perfekt**: {'✅ JA' if all_perfect else '❌ NEIN'}",
 ""
 ]
 
 if not all_perfect:
 report_lines.append("## Fehlerhafte Mappings")
 report_lines.append("")
 for result in validation_results:
 if not result["is_perfect"]:
 m = result["mapping"]
 report_lines.append(f"### Seed[{m['seed_position']}]='{m['seed_char']}' → Identity[{m['identity_position']}]='{m['identity_char']}'")
 report_lines.append(f"- **Fehler**: {result['error_count']}/{result['total']}")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "perfect_mappings_critical_validation_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

