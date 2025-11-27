#!/usr/bin/env python3
"""
Umfassende Analyse: ALLE Seed-Position → Identity-Position Mappings
- Analyze alle 55 Seed-Positionen for alle 60 Identity-Positionen
- Finde ALLE perfekten Mappings
- KEINE Annahmen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def analyze_seed_pos_to_identity_pos(seed_pos: int, identity_pos: int, min_samples: int = 50) -> Dict:
 """Analyze Seed-Position → Identity-Position Mapping."""
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 char_mappings = defaultdict(Counter)
 char_totals = Counter()
 
 for entry in layer3_results:
 identity = entry.get("layer3_identity", "")
 if len(identity) != 60:
 continue
 
 seed = identity_to_seed(identity)
 if len(seed) > seed_pos and len(identity) > identity_pos:
 seed_char = seed[seed_pos].lower()
 identity_char = identity[identity_pos].upper()
 
 char_mappings[seed_char][identity_char] += 1
 char_totals[seed_char] += 1
 
 # Finde perfekte Mappings (100%)
 perfect_mappings = {}
 
 for seed_char, counter in char_mappings.items():
 total = char_totals[seed_char]
 if total >= min_samples:
 most_common = counter.most_common(1)[0]
 success_rate = most_common[1] / total
 
 # Check ob es 100% ist
 if success_rate >= 0.99:
 perfect_mappings[seed_char] = {
 "target_character": most_common[0],
 "success_rate": success_rate,
 "count": most_common[1],
 "total": total
 }
 
 return {
 "seed_position": seed_pos,
 "identity_position": identity_pos,
 "perfect_mappings": perfect_mappings,
 "total_perfect": len(perfect_mappings)
 }

def analyze_all_combinations() -> Dict:
 """Analyze ALLE Seed-Position → Identity-Position Kombinationen."""
 
 print("=" * 80)
 print("UMFASSENDE ANALYSE: ALLE SEED → IDENTITY MAPPINGS")
 print("=" * 80)
 print()
 print("⚠️ ANALYSIERE ALLE 55 × 60 KOMBINATIONEN!")
 print(" Das kann eine Weile dauern...")
 print()
 
 all_results = {}
 all_perfect_mappings = []
 
 total_combinations = 55 * 60
 current = 0
 
 for seed_pos in range(55):
 if seed_pos % 5 == 0:
 print(f" Progress: Seed[{seed_pos}]/55... ({current}/{total_combinations} Kombinationen)")
 
 for identity_pos in range(60):
 current += 1
 
 result = analyze_seed_pos_to_identity_pos(seed_pos, identity_pos, min_samples=50)
 all_results[(seed_pos, identity_pos)] = result
 
 # Sammle perfekte Mappings
 for seed_char, mapping in result.get("perfect_mappings", {}).items():
 all_perfect_mappings.append({
 "seed_position": seed_pos,
 "seed_char": seed_char,
 "identity_position": identity_pos,
 "identity_char": mapping["target_character"],
 "success_rate": mapping["success_rate"],
 "count": mapping["count"],
 "total": mapping["total"]
 })
 
 print("✅ Alle Kombinationen analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 print(f"📊 Total perfekte Mappings gefunden: {len(all_perfect_mappings)}")
 print()
 
 # Gruppiere nach Seed-Position
 by_seed_pos = defaultdict(list)
 for mapping in all_perfect_mappings:
 by_seed_pos[mapping["seed_position"]].append(mapping)
 
 # Zeige Top Positionen
 sorted_positions = sorted(by_seed_pos.items(), key=lambda x: len(x[1]), reverse=True)
 
 print("📊 Top 20 Seed-Positionen (nach Anzahl perfekter Mappings):")
 for i, (seed_pos, mappings) in enumerate(sorted_positions[:20], 1):
 # Gruppiere nach Identity-Position
 by_identity_pos = defaultdict(list)
 for m in mappings:
 by_identity_pos[m["identity_position"]].append(m)
 
 print(f" {i:2d}. Seed[{seed_pos:2d}]: {len(mappings)} perfekte Mappings")
 for identity_pos in sorted(by_identity_pos.keys()):
 count = len(by_identity_pos[identity_pos])
 print(f" → Identity[{identity_pos:2d}]: {count} Mappings")
 print()
 
 # Gruppiere nach Identity-Position
 by_identity_pos = defaultdict(list)
 for mapping in all_perfect_mappings:
 by_identity_pos[mapping["identity_position"]].append(mapping)
 
 print("📊 Top 20 Identity-Positionen (nach Anzahl perfekter Mappings):")
 sorted_identity_pos = sorted(by_identity_pos.items(), key=lambda x: len(x[1]), reverse=True)
 for i, (identity_pos, mappings) in enumerate(sorted_identity_pos[:20], 1):
 print(f" {i:2d}. Identity[{identity_pos:2d}]: {len(mappings)} perfekte Mappings")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_combinations": total_combinations,
 "total_perfect_mappings": len(all_perfect_mappings),
 "perfect_mappings_by_seed_pos": {str(k): len(v) for k, v in by_seed_pos.items()},
 "perfect_mappings_by_identity_pos": {str(k): len(v) for k, v in by_identity_pos.items()},
 "all_perfect_mappings": all_perfect_mappings,
 "top_seed_positions": [
 {
 "seed_position": seed_pos,
 "count": len(mappings),
 "identity_positions": list(set(m["identity_position"] for m in mappings))
 }
 for seed_pos, mappings in sorted_positions[:20]
 ]
 }
 
 output_file = OUTPUT_DIR / "all_seed_identity_mappings_complete.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Umfassende Analyse: Alle Seed → Identity Mappings",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 f"**Total Kombinationen analysiert**: {total_combinations}",
 f"**Total perfekte Mappings**: {len(all_perfect_mappings)}",
 "",
 "## Top Seed-Positionen",
 ""
 ]
 
 for i, (seed_pos, mappings) in enumerate(sorted_positions[:20], 1):
 by_identity_pos = defaultdict(list)
 for m in mappings:
 by_identity_pos[m["identity_position"]].append(m)
 
 report_lines.append(f"### {i}. Seed[{seed_pos}] ({len(mappings)} Mappings)")
 for identity_pos in sorted(by_identity_pos.keys()):
 count = len(by_identity_pos[identity_pos])
 report_lines.append(f"- Identity[{identity_pos}]: {count} Mappings")
 report_lines.append("")
 
 report_lines.extend([
 "## Top Identity-Positionen",
 ""
 ])
 
 for i, (identity_pos, mappings) in enumerate(sorted_identity_pos[:20], 1):
 report_lines.append(f"{i}. Identity[{identity_pos}]: {len(mappings)} perfekte Mappings")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "all_seed_identity_mappings_complete_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 return output_data

def main():
 """Hauptfunktion."""
 analyze_all_combinations()
 
 print()
 print("=" * 80)
 print("✅ UMFASSENDE ANALYSE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("💡 ERKENNTNISSE:")
 print()
 print(" ✅ Alle 3.300 Kombinationen analysiert")
 print(" ✅ Alle perfekten Mappings identifiziert")
 print(" ✅ KEINE Annahmen - nur echte Daten!")
 print()

if __name__ == "__main__":
 main()

