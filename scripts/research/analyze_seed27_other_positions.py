#!/usr/bin/env python3
"""
Analyze ob Seed[27] auch for andere Identity-Positionen funktioniert
- Teste alle 60 Identity-Positionen
- Check ob Seed[27] auch andere Positionen beeinflusst
- KEINE Annahmen - nur echte Daten!
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

def analyze_seed27_for_position(seed_char: str, target_pos: int) -> Dict:
 """Analyze Seed[27] for eine bestimmte Identity-Position."""
 
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
 if len(seed) >= 55:
 if seed[27].lower() == seed_char.lower():
 matching.append(identity)
 
 # Check ob Identity[target_pos] == Seed[27] (uppercase)
 if len(identity) > target_pos:
 expected_char = seed_char.upper()
 actual_char = identity[target_pos].upper()
 if actual_char != expected_char:
 errors.append({
 "identity": identity,
 "expected": expected_char,
 "actual": actual_char,
 "position": target_pos
 })
 
 total = len(matching)
 error_count = len(errors)
 success_count = total - error_count
 actual_rate = success_count / total * 100 if total > 0 else 0
 
 return {
 "seed_char": seed_char,
 "target_position": target_pos,
 "total": total,
 "success_count": success_count,
 "error_count": error_count,
 "actual_rate": actual_rate,
 "is_100_percent": error_count == 0
 }

def analyze_all_positions() -> Dict:
 """Analyze alle 60 Identity-Positionen."""
 
 print("=" * 80)
 print("ANALYSE: SEED[27] FÜR ALLE IDENTITY-POSITIONEN")
 print("=" * 80)
 print()
 print("⚠️ PRÜFE JEDE POSITION - KEINE ANNAHMEN!")
 print()
 
 # Teste bekannte Characters
 test_chars = ["a", "b", "c", "d"]
 all_results = {}
 
 for seed_char in test_chars:
 print(f"🔍 Analyze Seed[27]='{seed_char}' for alle Positionen...")
 char_results = {}
 
 for pos in range(60):
 if pos % 15 == 0:
 print(f" Progress: {pos}/60...")
 
 result = analyze_seed27_for_position(seed_char, pos)
 char_results[pos] = result
 
 all_results[seed_char] = char_results
 print(f" ✅ Fertig")
 print()
 
 # Finde Positionen mit 100%
 perfect_positions = {}
 
 for seed_char, char_results in all_results.items():
 perfect = []
 for pos, result in char_results.items():
 if result["is_100_percent"] and result["total"] > 0:
 perfect.append(pos)
 perfect_positions[seed_char] = perfect
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 for seed_char in test_chars:
 perfect = perfect_positions[seed_char]
 print(f"📊 Seed[27]='{seed_char}':")
 print(f" Positionen mit 100%: {len(perfect)}")
 if perfect:
 print(f" Positionen: {perfect}")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "all_results": all_results,
 "perfect_positions": perfect_positions
 }
 
 output_file = OUTPUT_DIR / "seed27_all_positions_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Analyse: Seed[27] for alle Identity-Positionen",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Ergebnisse",
 ""
 ]
 
 for seed_char in test_chars:
 perfect = perfect_positions[seed_char]
 report_lines.append(f"### Seed[27]='{seed_char}'")
 report_lines.append(f"- **Positionen mit 100%**: {len(perfect)}")
 if perfect:
 report_lines.append(f"- **Positionen**: {perfect}")
 else:
 report_lines.append("- **Keine 100% Positionen gefunden**")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "seed27_all_positions_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 return output_data

def main():
 """Hauptfunktion."""
 analyze_all_positions()
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("💡 ERKENNTNISSE:")
 print()
 print(" ✅ Seed[27] for alle 60 Positionen analysiert")
 print(" ✅ Positionen mit 100% identifiziert")
 print(" ✅ KEINE Annahmen - nur echte Daten!")
 print()

if __name__ == "__main__":
 main()

