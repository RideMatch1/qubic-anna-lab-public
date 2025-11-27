#!/usr/bin/env python3
"""
Validate 100% Mappings mit EXAKTEN Seeds aus den Daten
- Nutze die tatsächlichen Seeds, die 100% Korrelation zeigen
- Check ob die Korrelation auch for neue Seeds gilt
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

def validate_100_percent_mapping(target_char: str = "A") -> Dict:
 """Validate 100% Mapping mit exakten Seeds aus den Daten."""
 
 print(f"🔍 Validate 100% Mapping for '{target_char}'...")
 print()
 
 # Load Dictionary
 with DICTIONARY_FILE.open() as f:
 data = json.load(f)
 
 best_mappings = data.get("best_mappings", {})
 combinations = best_mappings.get("combinations", [])
 
 # Finde beste Kombination for target_char
 target_combos = [c for c in combinations if c.get("target_char") == target_char.upper() and c.get("success_rate", 0) >= 0.99]
 if not target_combos:
 return {"error": f"No 100% mapping found for '{target_char}'"}
 
 best_combo = max(target_combos, key=lambda x: x["total"])
 combo_key = best_combo.get("combo_key", "")
 seed_chars = combo_key.split("_")
 
 print(f" Beste Kombination: {combo_key} → Identity[27]='{target_char.upper()}'")
 print(f" Sample-Größe: {best_combo['total']} Fälle")
 print()
 
 # Load Layer-3 Daten
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 # Finde alle Identities mit dieser Kombination
 matching_identities = []
 for entry in layer3_results:
 identity = entry.get("layer3_identity", "")
 if len(identity) != 60:
 continue
 
 seed = identity_to_seed(identity)
 if len(seed) >= 55:
 if len(seed_chars) >= 2:
 if seed[27].lower() == seed_chars[0].lower() and seed[54].lower() == seed_chars[1].lower():
 matching_identities.append({
 "identity": identity,
 "seed": seed,
 "identity_27": identity[27] if len(identity) > 27 else None
 })
 
 print(f" Gefundene Identities: {len(matching_identities)}")
 print()
 
 # Analyze
 if matching_identities:
 identity_27_chars = Counter()
 for item in matching_identities:
 if item["identity_27"]:
 identity_27_chars[item["identity_27"]] += 1
 
 total = len(matching_identities)
 target_count = identity_27_chars.get(target_char.upper(), 0)
 actual_rate = target_count / total if total > 0 else 0
 
 print(f"📊 Analyse:")
 print(f" Total Identities: {total}")
 print(f" Identity[27]='{target_char.upper()}': {target_count} ({actual_rate*100:.1f}%)")
 print()
 
 print(f" Identity[27] Distribution:")
 for char, count in identity_27_chars.most_common(10):
 percentage = count / total * 100
 marker = "✅" if char == target_char.upper() else " "
 print(f" {marker} '{char}': {count} ({percentage:.1f}%)")
 print()
 
 return {
 "combo_key": combo_key,
 "target_char": target_char.upper(),
 "total_identities": total,
 "target_count": target_count,
 "actual_rate": actual_rate,
 "expected_rate": best_combo.get("success_rate", 0),
 "distribution": dict(identity_27_chars),
 "sample_identities": matching_identities[:10] # Sample
 }
 
 return {"error": "No matching identities found"}

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("VALIDIERUNG 100% MAPPINGS")
 print("=" * 80)
 print()
 
 # Validate for verschiedene Characters
 characters = ["A", "B", "C", "D"]
 results = {}
 
 for char in characters:
 print(f"🔍 Validate '{char}'...")
 result = validate_100_percent_mapping(char)
 if "error" not in result:
 results[char] = result
 print()
 
 # Zeige Zusammenfassung
 print("=" * 80)
 print("VALIDIERUNGS-ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 for char, result in results.items():
 actual_rate = result["actual_rate"] * 100
 expected_rate = result["expected_rate"] * 100
 diff = actual_rate - expected_rate
 
 marker = "✅" if abs(diff) < 1 else "⚠️"
 print(f"{marker} '{char}': {actual_rate:.1f}% tatsächlich (erwartet: {expected_rate:.1f}%, Diff: {diff:+.1f}%)")
 print(f" Kombination: {result['combo_key']}")
 print(f" Sample: {result['total_identities']} Identities")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "validation_results": results
 }
 
 output_file = OUTPUT_DIR / "100_percent_mappings_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# 100% Mappings Validierung",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Zusammenfassung",
 ""
 ]
 
 for char, result in results.items():
 actual_rate = result["actual_rate"] * 100
 expected_rate = result["expected_rate"] * 100
 diff = actual_rate - expected_rate
 
 marker = "✅" if abs(diff) < 1 else "⚠️"
 report_lines.append(f"{marker} **'{char}'**: {actual_rate:.1f}% tatsächlich (erwartet: {expected_rate:.1f}%, Diff: {diff:+.1f}%)")
 report_lines.append(f" - Kombination: {result['combo_key']}")
 report_lines.append(f" - Sample: {result['total_identities']} Identities")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "100_percent_mappings_validation_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

