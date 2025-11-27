#!/usr/bin/env python3
"""
Analyze die 180 Comprehensive Scan Identities.

Analysiert:
- Seed-Extraktion
- Layer-2 Ableitung
- Vergleich mit systematischen Identities
- Pattern-Analyse
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from collections import Counter

OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs" / "derived"
SCAN_FILE = OUTPUT_DIR / "additional_identities_from_comprehensive_scan.json"
OUTPUT_FILE = OUTPUT_DIR / "comprehensive_scan_identities_analysis.json"
REPORT_FILE = OUTPUT_DIR / "comprehensive_scan_identities_analysis_report.md"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def analyze_identities(identities: List[str]) -> Dict:
 """Analyze Identities."""
 
 results = {
 "total": len(identities),
 "seeds": [],
 "seed_patterns": {},
 "first_chars": Counter(),
 "last_chars": Counter(),
 "common_patterns": [],
 }
 
 for identity in identities:
 seed = identity_to_seed(identity)
 results["seeds"].append({
 "identity": identity,
 "seed": seed,
 })
 
 # Pattern-Analyse
 results["first_chars"][identity[0]] += 1
 results["last_chars"][identity[-1]] += 1
 
 # Seed-Pattern
 seed_start = seed[:5]
 if seed_start not in results["seed_patterns"]:
 results["seed_patterns"][seed_start] = 0
 results["seed_patterns"][seed_start] += 1
 
 # Finde häufige Patterns
 results["common_patterns"] = [
 {"pattern": pattern, "count": count}
 for pattern, count in results["seed_patterns"].items()
 if count > 1
 ]
 results["common_patterns"].sort(key=lambda x: x["count"], reverse=True)
 
 return results

def main():
 """Analyze Comprehensive Scan Identities."""
 
 print("=" * 80)
 print("COMPREHENSIVE SCAN IDENTITIES ANALYSE")
 print("=" * 80)
 print()
 
 if not SCAN_FILE.exists():
 print(f"❌ Datei nicht gefunden: {SCAN_FILE}")
 return
 
 # Load Identities
 print("Load Comprehensive Scan Identities...")
 with SCAN_FILE.open() as f:
 data = json.load(f)
 
 identities = data.get("identities", [])
 print(f"✅ {len(identities)} Identities geloadn")
 print()
 
 if not identities:
 print("❌ Keine Identities gefunden!")
 return
 
 # Analyze
 print("Analyze Identities...")
 results = analyze_identities(identities)
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 print(f"Total Identities: {results['total']}")
 print()
 
 print("Häufigste erste Zeichen:")
 for char, count in results["first_chars"].most_common(5):
 print(f" {char}: {count}x ({count/results['total']*100:.1f}%)")
 print()
 
 print("Häufigste letzte Zeichen:")
 for char, count in results["last_chars"].most_common(5):
 print(f" {char}: {count}x ({count/results['total']*100:.1f}%)")
 print()
 
 if results["common_patterns"]:
 print("Häufige Seed-Patterns (erste 5 Zeichen):")
 for pattern_info in results["common_patterns"][:10]:
 print(f" {pattern_info['pattern']}: {pattern_info['count']}x")
 else:
 print("Keine häufigen Seed-Patterns gefunden")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 json.dump(results, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 
 # Erstelle Report
 report_content = f"""# Comprehensive Scan Identities Analyse

**Datum**: 2025-11-22 
**Total Identities**: {results['total']}

## Zusammenfassung

- **Total analysiert**: {results['total']}
- **Unique Seeds**: {len(set(r['seed'] for r in results['seeds']))}

## Pattern-Analyse

### Häufigste erste Zeichen
"""
 
 for char, count in results["first_chars"].most_common(10):
 report_content += f"- `{char}`: {count}x ({count/results['total']*100:.1f}%)\n"
 
 report_content += "\n### Häufigste letzte Zeichen\n"
 for char, count in results["last_chars"].most_common(10):
 report_content += f"- `{char}`: {count}x ({count/results['total']*100:.1f}%)\n"
 
 if results["common_patterns"]:
 report_content += "\n### Häufige Seed-Patterns (erste 5 Zeichen)\n"
 for pattern_info in results["common_patterns"][:20]:
 report_content += f"- `{pattern_info['pattern']}`: {pattern_info['count']}x\n"
 
 report_content += "\n## Nächste Schritte\n\n"
 report_content += "- Layer-2 Ableitung for alle Identities\n"
 report_content += "- Vergleich mit systematischen Identities\n"
 report_content += "- Pattern-Vergleich mit Matrix-Koordinaten\n"
 
 with REPORT_FILE.open("w") as f:
 f.write(report_content)
 
 print(f"📄 Report erstellt: {REPORT_FILE}")
 print()
 print("✅ Analyse abgeschlossen!")

if __name__ == "__main__":
 main()

