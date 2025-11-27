#!/usr/bin/env python3
"""
Analyze Checksum-Position (55) - kann sie beeinflusst werden?
- Check ob Seed-Positionen die Checksum beeinflussen
- Finde Patterns in Checksum-Berechnung
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
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def analyze_checksum_patterns() -> Dict:
 """Analyze Patterns in Checksum-Position (55)."""
 
 print("=" * 80)
 print("ANALYSE: CHECKSUM-POSITION (55)")
 print("=" * 80)
 print()
 print("⚠️ PRÜFE OB CHECKSUM BEEINFLUSSBAR IST!")
 print()
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 # Analyze Checksum-Character Distribution
 checksum_chars = Counter()
 checksum_by_seed_pos = defaultdict(Counter)
 checksum_by_identity_pos = defaultdict(Counter)
 
 for entry in layer3_results:
 identity = entry.get("layer3_identity", "")
 if len(identity) != 60:
 continue
 
 seed = identity_to_seed(identity)
 if len(seed) < 55:
 continue
 
 checksum_char = identity[55].upper() if len(identity) > 55 else None
 
 if checksum_char:
 checksum_chars[checksum_char] += 1
 
 # Check Korrelation mit Seed-Positionen
 for seed_pos in range(min(55, len(seed))):
 seed_char = seed[seed_pos].lower()
 checksum_by_seed_pos[seed_pos][(seed_char, checksum_char)] += 1
 
 # Check Korrelation mit Identity-Positionen
 for identity_pos in range(min(55, len(identity))):
 identity_char = identity[identity_pos].upper()
 checksum_by_identity_pos[identity_pos][(identity_char, checksum_char)] += 1
 
 print(f"📊 {len(checksum_chars)} verschiedene Checksum-Characters gefunden")
 print()
 
 # Finde stärkste Korrelationen
 print("🔍 Finde stärkste Korrelationen...")
 
 # Seed-Position → Checksum
 seed_checksum_correlations = []
 for seed_pos, counter in checksum_by_seed_pos.items():
 for (seed_char, checksum_char), count in counter.items():
 total_for_seed_char = sum(c for (s, _), c in counter.items() if s == seed_char)
 if total_for_seed_char >= 50: # Mindestens 50 Fälle
 rate = count / total_for_seed_char
 if rate >= 0.30: # Mindestens 30%
 seed_checksum_correlations.append({
 "seed_position": seed_pos,
 "seed_char": seed_char,
 "checksum_char": checksum_char,
 "rate": rate,
 "count": count,
 "total": total_for_seed_char
 })
 
 seed_checksum_correlations.sort(key=lambda x: x["rate"], reverse=True)
 
 # Identity-Position → Checksum
 identity_checksum_correlations = []
 for identity_pos, counter in checksum_by_identity_pos.items():
 for (identity_char, checksum_char), count in counter.items():
 total_for_identity_char = sum(c for (i, _), c in counter.items() if i == identity_char)
 if total_for_identity_char >= 50: # Mindestens 50 Fälle
 rate = count / total_for_identity_char
 if rate >= 0.30: # Mindestens 30%
 identity_checksum_correlations.append({
 "identity_position": identity_pos,
 "identity_char": identity_char,
 "checksum_char": checksum_char,
 "rate": rate,
 "count": count,
 "total": total_for_identity_char
 })
 
 identity_checksum_correlations.sort(key=lambda x: x["rate"], reverse=True)
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 print(f"📊 Checksum-Character Distribution:")
 for char, count in checksum_chars.most_common(10):
 percentage = count / sum(checksum_chars.values()) * 100
 print(f" '{char}': {count} ({percentage:.1f}%)")
 print()
 
 if seed_checksum_correlations:
 print(f"📊 Top 10 Seed-Position → Checksum Korrelationen:")
 for i, corr in enumerate(seed_checksum_correlations[:10], 1):
 marker = "⭐" if corr["rate"] >= 0.50 else " "
 print(f" {marker} {i:2d}. Seed[{corr['seed_position']:2d}]='{corr['seed_char']}' → Checksum='{corr['checksum_char']}' ({corr['rate']*100:.1f}%, {corr['count']}/{corr['total']})")
 print()
 else:
 print("❌ Keine starken Seed → Checksum Korrelationen gefunden")
 print()
 
 if identity_checksum_correlations:
 print(f"📊 Top 10 Identity-Position → Checksum Korrelationen:")
 for i, corr in enumerate(identity_checksum_correlations[:10], 1):
 marker = "⭐" if corr["rate"] >= 0.50 else " "
 print(f" {marker} {i:2d}. Identity[{corr['identity_position']:2d}]='{corr['identity_char']}' → Checksum='{corr['checksum_char']}' ({corr['rate']*100:.1f}%, {corr['count']}/{corr['total']})")
 print()
 else:
 print("❌ Keine starken Identity → Checksum Korrelationen gefunden")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "checksum_distribution": dict(checksum_chars.most_common(26)),
 "seed_checksum_correlations": seed_checksum_correlations[:20],
 "identity_checksum_correlations": identity_checksum_correlations[:20],
 "has_strong_correlations": len(seed_checksum_correlations) > 0 or len(identity_checksum_correlations) > 0
 }
 
 output_file = OUTPUT_DIR / "checksum_position_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Analyse: Checksum-Position (55)",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Checksum-Character Distribution",
 ""
 ]
 
 for char, count in checksum_chars.most_common(26):
 percentage = count / sum(checksum_chars.values()) * 100
 report_lines.append(f"- '{char}': {count} ({percentage:.1f}%)")
 report_lines.append("")
 
 if seed_checksum_correlations:
 report_lines.extend([
 "## Seed-Position → Checksum Korrelationen",
 ""
 ])
 for corr in seed_checksum_correlations[:20]:
 report_lines.append(f"- Seed[{corr['seed_position']}]='{corr['seed_char']}' → Checksum='{corr['checksum_char']}' ({corr['rate']*100:.1f}%, {corr['count']}/{corr['total']})")
 report_lines.append("")
 
 if identity_checksum_correlations:
 report_lines.extend([
 "## Identity-Position → Checksum Korrelationen",
 ""
 ])
 for corr in identity_checksum_correlations[:20]:
 report_lines.append(f"- Identity[{corr['identity_position']}]='{corr['identity_char']}' → Checksum='{corr['checksum_char']}' ({corr['rate']*100:.1f}%, {corr['count']}/{corr['total']})")
 report_lines.append("")
 
 if not seed_checksum_correlations and not identity_checksum_correlations:
 report_lines.append("**Keine starken Korrelationen gefunden** - Checksum scheint nicht direkt beeinflussbar zu sein.")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "checksum_position_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 return output_data

def main():
 """Hauptfunktion."""
 analyze_checksum_patterns()
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("💡 ERKENNTNISSE:")
 print()
 print(" ✅ Checksum-Position analysiert")
 print(" ✅ Korrelationen geprüft")
 print(" ✅ KEINE Spekulationen - nur echte Daten!")
 print()

if __name__ == "__main__":
 main()

