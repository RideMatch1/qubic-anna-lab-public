#!/usr/bin/env python3
"""
Identity-Pattern-Vergleich: Check ob Identities Muster zeigen.

Analysiert:
1. Vergleich systematische vs. comprehensive Identities
2. Seed-Patterns in beiden Gruppen
3. Gemeinsamkeiten und Unterschiede
4. Mathematische Eigenschaften
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter

OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs" / "derived"
SYSTEMATIC_DATA = OUTPUT_DIR / "systematic_matrix_extraction_complete.json"
COMPREHENSIVE_LAYER2 = OUTPUT_DIR / "comprehensive_scan_layer2_derivation.json"
OUTPUT_FILE = OUTPUT_DIR / "identity_pattern_comparison.json"
REPORT_FILE = OUTPUT_DIR / "identity_pattern_comparison_report.md"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def analyze_seed_patterns(seeds: List[str]) -> Dict:
 """Analyze Patterns in Seeds."""
 
 analysis = {
 "total": len(seeds),
 "unique_seeds": len(set(seeds)),
 "first_chars": Counter(s[0] for s in seeds),
 "last_chars": Counter(s[-1] for s in seeds),
 "common_substrings": {},
 "repeating_patterns": [],
 }
 
 # Finde häufige Substrings (3-5 Zeichen)
 all_substrings = []
 for seed in seeds:
 for length in [3, 4, 5]:
 for i in range(len(seed) - length + 1):
 all_substrings.append(seed[i:i+length])
 
 substring_counts = Counter(all_substrings)
 analysis["common_substrings"] = {
 k: v for k, v in substring_counts.most_common(20) if v > 1
 }
 
 # Finde wiederholende Patterns in einzelnen Seeds
 for seed in seeds[:50]: # Nur erste 50 for Performance
 for pattern_len in [2, 3]:
 for i in range(len(seed) - pattern_len * 2 + 1):
 pattern = seed[i:i+pattern_len]
 if pattern in seed[i+pattern_len:]:
 analysis["repeating_patterns"].append({
 "seed": seed[:20] + "...",
 "pattern": pattern,
 "position": i,
 })
 break # Nur einmal pro Seed
 
 return analysis

def compare_groups(systematic_seeds: List[str], comprehensive_seeds: List[str]) -> Dict:
 """Vergleiche systematische und comprehensive Seeds."""
 
 comparison = {
 "systematic_count": len(systematic_seeds),
 "comprehensive_count": len(comprehensive_seeds),
 "overlap": len(set(systematic_seeds) & set(comprehensive_seeds)),
 "systematic_unique": len(set(systematic_seeds) - set(comprehensive_seeds)),
 "comprehensive_unique": len(set(comprehensive_seeds) - set(systematic_seeds)),
 }
 
 # Charakter-Verteilung Vergleich
 systematic_first = Counter(s[0] for s in systematic_seeds)
 comprehensive_first = Counter(s[0] for s in comprehensive_seeds)
 
 comparison["first_char_comparison"] = {}
 all_first_chars = set(systematic_first.keys()) | set(comprehensive_first.keys())
 for char in all_first_chars:
 sys_count = systematic_first.get(char, 0)
 comp_count = comprehensive_first.get(char, 0)
 if sys_count != comp_count:
 comparison["first_char_comparison"][char] = {
 "systematic": sys_count,
 "comprehensive": comp_count,
 "diff": sys_count - comp_count,
 }
 
 return comparison

def main():
 """Identity-Pattern-Vergleich."""
 
 print("=" * 80)
 print("IDENTITY-PATTERN-VERGLEICH")
 print("=" * 80)
 print()
 print("⚠️ WICHTIG: Nur Fakten, keine Interpretationen!")
 print()
 
 # Load Comprehensive Scan Daten
 if not COMPREHENSIVE_LAYER2.exists():
 print(f"❌ Datei nicht gefunden: {COMPREHENSIVE_LAYER2}")
 return
 
 print("Load Comprehensive Scan Daten...")
 with COMPREHENSIVE_LAYER2.open() as f:
 comprehensive_data = json.load(f)
 
 comprehensive_results = comprehensive_data.get("results", [])
 comprehensive_identities = [r["layer1_identity"] for r in comprehensive_results]
 comprehensive_seeds = [identity_to_seed(id) for id in comprehensive_identities]
 
 print(f"✅ {len(comprehensive_seeds)} Comprehensive Seeds geloadn")
 
 # Load Systematic Daten (falls vorhanden)
 systematic_seeds = []
 if SYSTEMATIC_DATA.exists():
 print("Load Systematic Daten...")
 with SYSTEMATIC_DATA.open() as f:
 systematic_data = json.load(f)
 
 # Extrahiere Seeds aus Systematic (abhängig von Datenstruktur)
 # Für jetzt: nur Comprehensive analyzen
 print("⚠️ Systematic Daten-Struktur muss noch analysiert werden")
 
 print()
 
 # Analyze Comprehensive Seeds
 print("Analyze Comprehensive Seed-Patterns...")
 comprehensive_patterns = analyze_seed_patterns(comprehensive_seeds)
 print(f" ✅ Unique Seeds: {comprehensive_patterns['unique_seeds']}")
 print(f" ✅ Häufige Substrings: {len(comprehensive_patterns['common_substrings'])}")
 print(f" ✅ Wiederholende Patterns: {len(comprehensive_patterns['repeating_patterns'])}")
 
 # Vergleich (falls Systematic vorhanden)
 if systematic_seeds:
 print("Vergleiche Gruppen...")
 comparison = compare_groups(systematic_seeds, comprehensive_seeds)
 print(f" ✅ Overlap: {comparison['overlap']}")
 print(f" ✅ Comprehensive Unique: {comparison['comprehensive_unique']}")
 else:
 comparison = {}
 
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "comprehensive_patterns": comprehensive_patterns,
 "comparison": comparison,
 }
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 
 # Erstelle Report
 report_content = f"""# Identity-Pattern-Vergleich: Fakten

**Datum**: 2025-11-22 
**Ziel**: Check Patterns in Identities

## ⚠️ WICHTIG

**Nur Fakten, keine Interpretationen!**

## 1. Comprehensive Scan Seeds (FAKTEN)

### Basis-Statistiken
- **Total Seeds**: {comprehensive_patterns['total']}
- **Unique Seeds**: {comprehensive_patterns['unique_seeds']}
- **Duplikate**: {comprehensive_patterns['total'] - comprehensive_patterns['unique_seeds']}

### Häufigste erste Zeichen
"""
 
 for char, count in comprehensive_patterns['first_chars'].most_common(10):
 report_content += f"- `{char}`: {count}x ({count/comprehensive_patterns['total']*100:.1f}%)\n"
 
 report_content += "\n### Häufigste letzte Zeichen\n"
 for char, count in comprehensive_patterns['last_chars'].most_common(10):
 report_content += f"- `{char}`: {count}x ({count/comprehensive_patterns['total']*100:.1f}%)\n"
 
 if comprehensive_patterns['common_substrings']:
 report_content += "\n### Häufige Substrings (3-5 Zeichen)\n"
 for substring, count in list(comprehensive_patterns['common_substrings'].items())[:20]:
 report_content += f"- `{substring}`: {count}x\n"
 
 if comparison:
 report_content += f"""
## 2. Vergleich Systematic vs. Comprehensive (FAKTEN)

- **Systematic Count**: {comparison.get('systematic_count', 'N/A')}
- **Comprehensive Count**: {comparison.get('comprehensive_count', 'N/A')}
- **Overlap**: {comparison.get('overlap', 'N/A')}
- **Comprehensive Unique**: {comparison.get('comprehensive_unique', 'N/A')}
"""
 
 report_content += """
## ❓ OFFENE FRAGEN (NICHT BEANTWORTET)

1. ❓ Warum gibt es diese Patterns?
2. ❓ Sind sie beabsichtigt oder zufällig?
3. ❓ Was bedeuten sie?

## ⚠️ WICHTIG

**Diese Analyse zeigt nur FAKTEN!** 
**Keine Interpretationen!**
"""
 
 with REPORT_FILE.open("w") as f:
 f.write(report_content)
 
 print(f"📄 Report erstellt: {REPORT_FILE}")
 print()
 print("✅ Identity-Pattern-Vergleich abgeschlossen!")

if __name__ == "__main__":
 main()

