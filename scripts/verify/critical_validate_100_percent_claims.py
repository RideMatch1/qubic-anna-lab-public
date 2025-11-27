#!/usr/bin/env python3
"""
KRITISCHE Validierung: Sind die 100% Mappings wirklich 100%?
- Check jeden einzelnen Fall
- Keine Annahmen - nur echte Daten
- Dokumentiere jeden Fehler
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
DICTIONARY_FILE = project_root / "outputs" / "derived" / "anna_language_dictionary.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def critically_validate_100_percent_claim(combo_key: str, expected_char: str) -> Dict:
 """KRITISCH: Validate ob 100% Mapping wirklich 100% ist."""
 
 print(f"🔍 KRITISCHE VALIDIERUNG: {combo_key} → Identity[27]='{expected_char}'")
 print()
 
 # Load alle Daten
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 seed_chars = combo_key.split("_")
 if len(seed_chars) < 2:
 return {"error": "Invalid combo_key"}
 
 seed_27_char = seed_chars[0].lower()
 seed_54_char = seed_chars[1].lower()
 
 # Finde ALLE Identities mit dieser Kombination
 matching_identities = []
 errors = []
 
 for entry in layer3_results:
 identity = entry.get("layer3_identity", "")
 if len(identity) != 60:
 continue
 
 seed = identity_to_seed(identity)
 if len(seed) >= 55:
 # Check ob Kombination passt
 if seed[27].lower() == seed_27_char and seed[54].lower() == seed_54_char:
 matching_identities.append(identity)
 
 # KRITISCH: Check ob Identity[27] wirklich expected_char ist
 actual_char = identity[27].upper() if len(identity) > 27 else None
 if actual_char != expected_char.upper():
 errors.append({
 "identity": identity,
 "seed": seed,
 "expected": expected_char.upper(),
 "actual": actual_char,
 "seed_27": seed[27],
 "seed_54": seed[54]
 })
 
 total = len(matching_identities)
 error_count = len(errors)
 success_count = total - error_count
 actual_rate = success_count / total * 100 if total > 0 else 0
 
 print(f" Total gefunden: {total}")
 print(f" Erfolgreich: {success_count} ({actual_rate:.2f}%)")
 print(f" Fehler: {error_count}")
 print()
 
 if errors:
 print(" ⚠️ FEHLER GEFUNDEN:")
 for i, error in enumerate(errors[:5], 1):
 print(f" {i}. Identity: {error['identity'][:30]}...")
 print(f" Seed[27]='{error['seed_27']}', Seed[54]='{error['seed_54']}'")
 print(f" Erwartet: '{error['expected']}', Tatsächlich: '{error['actual']}'")
 if len(errors) > 5:
 print(f" ... und {len(errors) - 5} weitere Fehler")
 print()
 
 return {
 "combo_key": combo_key,
 "expected_char": expected_char.upper(),
 "total": total,
 "success_count": success_count,
 "error_count": error_count,
 "actual_rate": actual_rate,
 "is_100_percent": error_count == 0,
 "errors": errors[:20] # Sample
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("KRITISCHE VALIDIERUNG: 100% MAPPINGS")
 print("=" * 80)
 print()
 print("⚠️ KEINE ANNAHMEN - NUR ECHTE DATEN!")
 print()
 
 # Load Dictionary
 with DICTIONARY_FILE.open() as f:
 data = json.load(f)
 
 best_mappings = data.get("best_mappings", {})
 combinations = best_mappings.get("combinations", [])
 
 # Finde 100% Mappings
 target_chars = ["A", "B", "C", "D"]
 mappings_to_test = {}
 
 for char in target_chars:
 char_combos = [c for c in combinations if c.get("target_char") == char and c.get("success_rate", 0) >= 0.99]
 if char_combos:
 best = max(char_combos, key=lambda x: x["total"])
 mappings_to_test[char] = best
 
 print(f"🔍 Validate {len(mappings_to_test)} 100% Mappings...")
 print()
 
 # Validate jeden einzelnen
 validation_results = {}
 
 for char, mapping in mappings_to_test.items():
 combo_key = mapping.get("combo_key", "")
 result = critically_validate_100_percent_claim(combo_key, char)
 validation_results[char] = result
 
 # Zeige Zusammenfassung
 print("=" * 80)
 print("VALIDIERUNGS-ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 all_100_percent = True
 total_errors = 0
 
 for char, result in validation_results.items():
 if "error" in result:
 print(f"❌ '{char}': {result['error']}")
 continue
 
 is_100 = result["is_100_percent"]
 actual_rate = result["actual_rate"]
 error_count = result["error_count"]
 total_errors += error_count
 
 marker = "✅" if is_100 else "❌"
 print(f"{marker} '{char}': {actual_rate:.2f}% ({result['success_count']}/{result['total']})")
 if error_count > 0:
 print(f" ⚠️ {error_count} FEHLER gefunden!")
 all_100_percent = False
 
 print()
 
 if all_100_percent and total_errors == 0:
 print("✅ ALLE 100% MAPPINGS SIND WIRKLICH 100%!")
 print(" ✅ Keine Fehler gefunden")
 print(" ✅ Behauptungen sind korrekt")
 else:
 print("⚠️ WARNUNG: Nicht alle Mappings sind wirklich 100%!")
 print(f" ⚠️ {total_errors} Fehler gefunden")
 print(" ⚠️ Behauptungen müssen korrigiert werden")
 
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "validation_results": validation_results,
 "all_100_percent": all_100_percent,
 "total_errors": total_errors
 }
 
 output_file = OUTPUT_DIR / "critical_100_percent_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle kritischen Report
 report_lines = [
 "# Kritische Validierung: 100% Mappings",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Zusammenfassung",
 "",
 f"- **Alle 100%**: {'✅ JA' if all_100_percent else '❌ NEIN'}",
 f"- **Total Fehler**: {total_errors}",
 "",
 "## Detaillierte Ergebnisse",
 ""
 ]
 
 for char, result in validation_results.items():
 if "error" in result:
 report_lines.append(f"### '{char}': {result['error']}")
 else:
 marker = "✅" if result["is_100_percent"] else "❌"
 report_lines.append(f"### {marker} '{char}': {result['actual_rate']:.2f}%")
 report_lines.append(f"- **Combo**: {result['combo_key']}")
 report_lines.append(f"- **Total**: {result['total']}")
 report_lines.append(f"- **Erfolgreich**: {result['success_count']}")
 report_lines.append(f"- **Fehler**: {result['error_count']}")
 if result['error_count'] > 0:
 report_lines.append("")
 report_lines.append("**Fehler-Details:**")
 for i, error in enumerate(result['errors'][:10], 1):
 report_lines.append(f"{i}. Identity: `{error['identity']}`")
 report_lines.append(f" - Erwartet: '{error['expected']}', Tatsächlich: '{error['actual']}'")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "critical_100_percent_validation_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

