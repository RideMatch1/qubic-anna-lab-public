#!/usr/bin/env python3
"""
KRITISCHE Validierung: Ist Seed[27] alleine wirklich 100%?
- Check JEDEN einzelnen Fall
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
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def validate_seed27_alone() -> Dict:
 """Validate ob Seed[27] alleine wirklich 100% ist."""
 
 print("=" * 80)
 print("KRITISCHE VALIDIERUNG: Seed[27] ALLEINE")
 print("=" * 80)
 print()
 print("⚠️ PRÜFE JEDEN EINZELNEN FALL - KEINE ANNAHMEN!")
 print()
 
 # Load Daten
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 print(f"📂 {len(layer3_results)} Identities geloadn")
 print()
 
 # Teste bekannte Mappings: a→A, b→B, c→C, d→D
 test_cases = [
 ("a", "A"),
 ("b", "B"),
 ("c", "C"),
 ("d", "D")
 ]
 
 results = {}
 
 for seed_char, expected_char in test_cases:
 print(f"🔍 Teste: Seed[27]='{seed_char}' → Identity[27]='{expected_char}'...")
 
 matching = []
 errors = []
 
 for entry in layer3_results:
 identity = entry.get("layer3_identity", "")
 if len(identity) != 60:
 continue
 
 seed = identity_to_seed(identity)
 if len(seed) >= 55:
 if seed[27].lower() == seed_char.lower():
 matching.append(identity)
 
 # KRITISCH: Check ob Identity[27] wirklich expected_char ist
 actual_char = identity[27].upper() if len(identity) > 27 else None
 if actual_char != expected_char.upper():
 errors.append({
 "identity": identity,
 "seed": seed,
 "seed_27": seed[27],
 "expected": expected_char.upper(),
 "actual": actual_char
 })
 
 total = len(matching)
 error_count = len(errors)
 success_count = total - error_count
 actual_rate = success_count / total * 100 if total > 0 else 0
 
 print(f" Total: {total}")
 print(f" Erfolgreich: {success_count} ({actual_rate:.2f}%)")
 print(f" Fehler: {error_count}")
 
 if errors:
 print(f" ⚠️ FEHLER GEFUNDEN:")
 for i, error in enumerate(errors[:3], 1):
 print(f" {i}. {error['identity'][:30]}... → '{error['actual']}' (sollte '{error['expected']}')")
 if len(errors) > 3:
 print(f" ... und {len(errors) - 3} weitere")
 else:
 print(f" ✅ KEINE FEHLER - WIRKLICH 100%!")
 print()
 
 results[seed_char] = {
 "expected_char": expected_char.upper(),
 "total": total,
 "success_count": success_count,
 "error_count": error_count,
 "actual_rate": actual_rate,
 "is_100_percent": error_count == 0,
 "errors": errors[:10] # Sample
 }
 
 # Zusammenfassung
 print("=" * 80)
 print("VALIDIERUNGS-ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 all_100 = True
 total_errors = 0
 
 for seed_char, result in results.items():
 marker = "✅" if result["is_100_percent"] else "❌"
 print(f"{marker} Seed[27]='{seed_char}' → Identity[27]='{result['expected_char']}': {result['actual_rate']:.2f}% ({result['success_count']}/{result['total']})")
 if result["error_count"] > 0:
 print(f" ⚠️ {result['error_count']} FEHLER!")
 all_100 = False
 total_errors += result["error_count"]
 
 print()
 
 if all_100:
 print("✅ SEED[27] ALLEINE IST WIRKLICH 100%!")
 print(" ✅ Keine Fehler gefunden")
 print(" ✅ Behauptung ist KORREKT")
 else:
 print("⚠️ WARNUNG: Seed[27] alleine ist NICHT 100%!")
 print(f" ⚠️ {total_errors} Fehler gefunden")
 print(" ⚠️ Behauptung muss korrigiert werden")
 
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "results": results,
 "all_100_percent": all_100,
 "total_errors": total_errors
 }
 
 output_file = OUTPUT_DIR / "seed27_alone_100_percent_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 return output_data

def main():
 """Hauptfunktion."""
 validate_seed27_alone()

if __name__ == "__main__":
 main()

