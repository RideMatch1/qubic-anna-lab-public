#!/usr/bin/env python3
"""
Analyze warum Position 13 so besonders for Kombinationen ist
- Vergleiche Position 13 mit anderen Positionen
- Finde strukturelle Unterschiede
- KEINE Spekulationen - nur echte Daten!
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
MAPPING_FILE = project_root / "outputs" / "derived" / "all_seed_identity_mappings_complete.json"
COMBINATIONS_FILE = project_root / "outputs" / "derived" / "best_target_combinations_analysis.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def analyze_position_characteristics(pos: int) -> Dict:
 """Analyze Charakteristiken einer Position."""
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 # Analyze Seed-Character Distribution
 seed_chars = Counter()
 identity_chars = Counter()
 seed_identity_pairs = defaultdict(Counter)
 
 for entry in layer3_results:
 identity = entry.get("layer3_identity", "")
 if len(identity) != 60:
 continue
 
 seed = identity_to_seed(identity)
 if len(seed) > pos and len(identity) > pos:
 seed_char = seed[pos].lower()
 identity_char = identity[pos].upper()
 
 seed_chars[seed_char] += 1
 identity_chars[identity_char] += 1
 seed_identity_pairs[seed_char][identity_char] += 1
 
 # Berechne Perfekt-Rate
 perfect_count = 0
 total = 0
 
 for seed_char, counter in seed_identity_pairs.items():
 if counter:
 most_common = counter.most_common(1)[0]
 total_for_char = sum(counter.values())
 if most_common[1] / total_for_char >= 0.99:
 perfect_count += 1
 total += 1
 
 perfect_rate = perfect_count / total * 100 if total > 0 else 0
 
 return {
 "position": pos,
 "total_seeds": sum(seed_chars.values()),
 "unique_seed_chars": len(seed_chars),
 "unique_identity_chars": len(identity_chars),
 "perfect_mappings_count": perfect_count,
 "perfect_rate": perfect_rate,
 "seed_char_distribution": dict(seed_chars.most_common(10)),
 "identity_char_distribution": dict(identity_chars.most_common(10))
 }

def compare_positions() -> Dict:
 """Vergleiche Position 13 mit anderen Positionen."""
 
 print("=" * 80)
 print("ANALYSE: WARUM IST POSITION 13 BESONDERS?")
 print("=" * 80)
 print()
 
 # Analyze Position 13
 print("🔍 Analyze Position 13...")
 pos13_chars = analyze_position_characteristics(13)
 print("✅ Position 13 analysiert")
 print()
 
 # Analyze Vergleichspositionen
 comparison_positions = [0, 27, 30, 41] # Andere wichtige Positionen
 
 print("🔍 Analyze Vergleichspositionen...")
 comparison_chars = {}
 for pos in comparison_positions:
 print(f" Position {pos}...")
 comparison_chars[pos] = analyze_position_characteristics(pos)
 print("✅ Vergleichspositionen analysiert")
 print()
 
 # Zeige Vergleich
 print("=" * 80)
 print("VERGLEICH")
 print("=" * 80)
 print()
 
 print("📊 Position 13:")
 print(f" Total Seeds: {pos13_chars['total_seeds']}")
 print(f" Unique Seed Chars: {pos13_chars['unique_seed_chars']}")
 print(f" Unique Identity Chars: {pos13_chars['unique_identity_chars']}")
 print(f" Perfekte Mappings: {pos13_chars['perfect_mappings_count']} ({pos13_chars['perfect_rate']:.1f}%)")
 print()
 
 print("📊 Vergleichspositionen:")
 for pos, chars in comparison_chars.items():
 print(f" Position {pos:2d}: {chars['perfect_mappings_count']} perfekte Mappings ({chars['perfect_rate']:.1f}%)")
 print()
 
 # Analyze Kombinationen mit Position 13
 with COMBINATIONS_FILE.open() as f:
 data = json.load(f)
 
 two_combinations = data.get("two_combinations", [])
 
 pos13_combinations = [c for c in two_combinations if 13 in c.get("positions", [])]
 other_combinations = [c for c in two_combinations if 13 not in c.get("positions", [])]
 
 if pos13_combinations and other_combinations:
 avg_success_13 = sum(c.get("success_rate", 0) for c in pos13_combinations) / len(pos13_combinations)
 avg_success_other = sum(c.get("success_rate", 0) for c in other_combinations) / len(other_combinations)
 avg_seeds_13 = sum(c.get("avg_seeds", 0) for c in pos13_combinations) / len(pos13_combinations)
 avg_seeds_other = sum(c.get("avg_seeds", 0) for c in other_combinations) / len(other_combinations)
 
 print("📊 Kombinationen mit vs. ohne Position 13:")
 print(f" Mit Position 13: {len(pos13_combinations)} Kombinationen")
 print(f" Durchschnittliche Erfolgsrate: {avg_success_13:.1f}%")
 print(f" Durchschnittliche Seeds: {avg_seeds_13:.1f}")
 print(f" Ohne Position 13: {len(other_combinations)} Kombinationen")
 print(f" Durchschnittliche Erfolgsrate: {avg_success_other:.1f}%")
 print(f" Durchschnittliche Seeds: {avg_seeds_other:.1f}")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "position_13": pos13_chars,
 "comparison_positions": comparison_chars,
 "combination_analysis": {
 "with_pos13": {
 "count": len(pos13_combinations),
 "avg_success_rate": avg_success_13 if pos13_combinations else 0,
 "avg_seeds": avg_seeds_13 if pos13_combinations else 0
 },
 "without_pos13": {
 "count": len(other_combinations),
 "avg_success_rate": avg_success_other if other_combinations else 0,
 "avg_seeds": avg_seeds_other if other_combinations else 0
 }
 }
 }
 
 output_file = OUTPUT_DIR / "why_position13_special_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Analyse: Warum ist Position 13 besonders?",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Position 13 Charakteristiken",
 "",
 f"- **Total Seeds**: {pos13_chars['total_seeds']}",
 f"- **Unique Seed Chars**: {pos13_chars['unique_seed_chars']}",
 f"- **Unique Identity Chars**: {pos13_chars['unique_identity_chars']}",
 f"- **Perfekte Mappings**: {pos13_chars['perfect_mappings_count']} ({pos13_chars['perfect_rate']:.1f}%)",
 "",
 "## Vergleich mit anderen Positionen",
 ""
 ]
 
 for pos, chars in comparison_chars.items():
 report_lines.append(f"**Position {pos}**: {chars['perfect_mappings_count']} perfekte Mappings ({chars['perfect_rate']:.1f}%)")
 report_lines.append("")
 
 if pos13_combinations and other_combinations:
 report_lines.extend([
 "## Kombinationen-Analyse",
 "",
 f"**Mit Position 13**: {len(pos13_combinations)} Kombinationen, {avg_success_13:.1f}% Erfolgsrate, {avg_seeds_13:.1f} Seeds",
 f"**Ohne Position 13**: {len(other_combinations)} Kombinationen, {avg_success_other:.1f}% Erfolgsrate, {avg_seeds_other:.1f} Seeds",
 ""
 ])
 
 report_file = REPORTS_DIR / "why_position13_special_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 return output_data

def main():
 """Hauptfunktion."""
 compare_positions()
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("💡 ERKENNTNISSE:")
 print()
 print(" ✅ Position 13 Charakteristiken analysiert")
 print(" ✅ Vergleich mit anderen Positionen durchgeführt")
 print(" ✅ KEINE Spekulationen - nur echte Daten!")
 print()

if __name__ == "__main__":
 main()

