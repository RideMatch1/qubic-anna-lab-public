#!/usr/bin/env python3
"""
KRITISCHE Validierung: Erfüllen die gefundenen Seeds wirklich alle Targets?
- Check jeden einzelnen Fall
- Keine Annahmen - nur echte Daten
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def validate_multi_target_seeds(targets: Dict[int, str], sample_size: int = 100) -> Dict:
 """Validate ob Seeds mit mehreren Targets wirklich alle erfüllen."""
 
 print("=" * 80)
 print("KRITISCHE VALIDIERUNG: MULTI-TARGET SEEDS")
 print("=" * 80)
 print()
 print(f"⚠️ PRÜFE OB SEEDS WIRKLICH ALLE TARGETS ERFÜLLEN!")
 print(f" Targets: {targets}")
 print()
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 matching_seeds = []
 errors = []
 
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
 matching_seeds.append(identity)
 
 # KRITISCH: Check ob Identity auch alle Targets erfüllt
 identity_matches = True
 error_details = []
 
 for pos, target_char in targets.items():
 if len(identity) > pos:
 actual_char = identity[pos].upper()
 expected_char = target_char.upper()
 if actual_char != expected_char:
 identity_matches = False
 error_details.append({
 "position": pos,
 "expected": expected_char,
 "actual": actual_char
 })
 
 if not identity_matches:
 errors.append({
 "identity": identity,
 "seed": seed,
 "errors": error_details
 })
 
 total = len(matching_seeds)
 error_count = len(errors)
 success_count = total - error_count
 success_rate = success_count / total * 100 if total > 0 else 0
 
 print(f"📊 Total Seeds gefunden: {total}")
 print(f"📊 Erfolgreich: {success_count} ({success_rate:.2f}%)")
 print(f"📊 Fehler: {error_count}")
 print()
 
 if errors:
 print("⚠️ FEHLER GEFUNDEN:")
 for i, error in enumerate(errors[:5], 1):
 print(f" {i}. {error['identity'][:30]}...")
 for err_detail in error["errors"]:
 print(f" Position {err_detail['position']}: Erwartet '{err_detail['expected']}', Tatsächlich '{err_detail['actual']}'")
 if len(errors) > 5:
 print(f" ... und {len(errors) - 5} weitere Fehler")
 print()
 else:
 print("✅ KEINE FEHLER - ALLE SEEDS ERFÜLLEN DIE TARGETS!")
 print()
 
 return {
 "targets": targets,
 "total": total,
 "success_count": success_count,
 "error_count": error_count,
 "success_rate": success_rate,
 "all_perfect": error_count == 0,
 "errors": errors[:20] # Sample
 }

def main():
 """Hauptfunktion."""
 import argparse
 
 parser = argparse.ArgumentParser(description="Validate Multi-Target Seeds")
 parser.add_argument("--targets", type=str, required=True, help="Targets als JSON: '{\"0\":\"A\",\"27\":\"B\"}'")
 args = parser.parse_args()
 
 # Parse Targets
 try:
 targets = json.loads(args.targets)
 targets = {int(k): v.upper() for k, v in targets.items()}
 except Exception as e:
 print(f"❌ Fehler beim Parsen der Targets: {e}")
 return
 
 result = validate_multi_target_seeds(targets)
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "validation_result": result
 }
 
 output_file = OUTPUT_DIR / "multi_target_seeds_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 if result["all_perfect"]:
 print("✅ VALIDIERUNG ERFOLGREICH - ALLE SEEDS ERFÜLLEN DIE TARGETS!")
 else:
 print("⚠️ VALIDIERUNG: Einige Seeds erfüllen nicht alle Targets")

if __name__ == "__main__":
 main()

