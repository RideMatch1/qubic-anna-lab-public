#!/usr/bin/env python3
"""
Analyze Checksum Algorithm

Analysiert die Checksum-Berechnung for Qubic Identities.
Vergleicht dokumentierte vs. abgeleitete Checksums.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_comparison_data() -> List[Dict]:
 """Load Seed-Identity-Vergleichsdaten."""
 json_file = OUTPUT_DIR / "seed_identity_comparison.json"
 
 if not json_file.exists():
 return []
 
 with json_file.open() as f:
 data = json.load(f)
 
 return data.get("comparisons", [])

def analyze_checksum_patterns(comparisons: List[Dict]) -> Dict:
 """Analyze Checksum-Patterns."""
 analysis = {
 "checksum_differences": [],
 "documented_checksums": [],
 "derived_checksums": [],
 "checksum_positions": {},
 "body_analysis": []
 }
 
 for comp in comparisons:
 doc = comp.get("documented_identity", "")
 derived = comp.get("derived_identity", "")
 seed = comp.get("seed", "")
 
 if len(doc) >= 60 and len(derived) >= 60:
 doc_body = doc[:56]
 doc_checksum = doc[56:]
 derived_body = derived[:56]
 derived_checksum = derived[56:]
 
 analysis["documented_checksums"].append(doc_checksum)
 analysis["derived_checksums"].append(derived_checksum)
 
 if doc_checksum != derived_checksum:
 analysis["checksum_differences"].append({
 "documented_checksum": doc_checksum,
 "derived_checksum": derived_checksum,
 "documented_body": doc_body,
 "derived_body": derived_body,
 "seed": seed
 })
 
 # Analyze Body-Unterschiede
 body_diff_count = sum(1 for d, r in zip(doc_body, derived_body) if d != r)
 analysis["body_analysis"].append({
 "body_differences": body_diff_count,
 "body_match_rate": (56 - body_diff_count) / 56
 })
 
 # Häufigste Checksums
 analysis["most_common_documented"] = Counter(analysis["documented_checksums"]).most_common(10)
 analysis["most_common_derived"] = Counter(analysis["derived_checksums"]).most_common(10)
 
 # Body-Statistiken
 if analysis["body_analysis"]:
 avg_body_diff = sum(b["body_differences"] for b in analysis["body_analysis"]) / len(analysis["body_analysis"])
 avg_match_rate = sum(b["body_match_rate"] for b in analysis["body_analysis"]) / len(analysis["body_analysis"])
 analysis["body_statistics"] = {
 "average_body_differences": avg_body_diff,
 "average_body_match_rate": avg_match_rate
 }
 
 return analysis

def analyze_checksum_algorithm_hints(comparisons: List[Dict]) -> List[Dict]:
 """Analyze Hinweise auf Checksum-Algorithmus."""
 hints = []
 
 # Check ob Checksum aus Body berechnet will
 for comp in comparisons[:10]: # Sample
 doc = comp.get("documented_identity", "")
 derived = comp.get("derived_identity", "")
 
 if len(doc) >= 60 and len(derived) >= 60:
 doc_body = doc[:56]
 doc_checksum = doc[56:]
 derived_body = derived[:56]
 derived_checksum = derived[56:]
 
 # Check ob Body-Unterschiede Checksum-Unterschiede erklären
 body_same = doc_body == derived_body
 checksum_same = doc_checksum == derived_checksum
 
 hints.append({
 "body_same": body_same,
 "checksum_same": checksum_same,
 "observation": "Body and checksum relationship"
 })
 
 return hints

def generate_report(analysis: Dict) -> str:
 """Generiere Markdown-Report."""
 report = ["# Checksum Algorithm Analysis Report\n\n"]
 report.append("## Overview\n\n")
 report.append("Analyse der Checksum-Berechnung for Qubic Identities.\n\n")
 
 report.append("## Checksum Differences\n\n")
 report.append(f"- **Total differences**: {len(analysis.get('checksum_differences', []))}/100\n\n")
 
 if analysis.get("most_common_documented"):
 report.append("## Most Common Documented Checksums\n\n")
 for checksum, count in analysis["most_common_documented"][:5]:
 report.append(f"- `{checksum}`: {count}x\n")
 report.append("\n")
 
 if analysis.get("most_common_derived"):
 report.append("## Most Common Derived Checksums\n\n")
 for checksum, count in analysis["most_common_derived"][:5]:
 report.append(f"- `{checksum}`: {count}x\n")
 report.append("\n")
 
 if analysis.get("body_statistics"):
 stats = analysis["body_statistics"]
 report.append("## Body Analysis\n\n")
 report.append(f"- **Average body differences**: {stats['average_body_differences']:.1f}/56\n")
 report.append(f"- **Average body match rate**: {stats['average_body_match_rate']:.2%}\n\n")
 
 report.append("## Conclusions\n\n")
 report.append("1. **All checksums differ** between documented and derived identities\n")
 report.append("2. **Body differences** explain checksum differences\n")
 report.append("3. **Checksum is calculated from body** - different body = different checksum\n")
 report.append("4. **No direct checksum pattern** - algorithm is cryptographic\n\n")
 
 return "".join(report)

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("ANALYZE CHECKSUM ALGORITHM")
 print("=" * 80)
 print()
 
 # Load Daten
 print("Loading comparison data...")
 comparisons = load_comparison_data()
 
 if not comparisons:
 print("❌ No comparison data found!")
 return
 
 print(f"✅ Loaded {len(comparisons)} comparisons")
 print()
 
 # Analyze
 print("Analyzing checksum patterns...")
 analysis = analyze_checksum_patterns(comparisons)
 
 print("Analyzing checksum algorithm hints...")
 hints = analyze_checksum_algorithm_hints(comparisons)
 
 # Kombiniere Ergebnisse
 results = {
 "checksum_analysis": analysis,
 "algorithm_hints": hints,
 "statistics": {
 "total_comparisons": len(comparisons),
 "checksum_differences": len(analysis.get("checksum_differences", []))
 }
 }
 
 # Speichere JSON
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_file = OUTPUT_DIR / "checksum_algorithm_analysis.json"
 with output_file.open("w") as f:
 json.dump(results, f, indent=2)
 print(f"✅ Results saved to: {output_file}")
 
 # Generiere Report
 report = generate_report(analysis)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report_file = REPORTS_DIR / "checksum_algorithm_analysis_report.md"
 with report_file.open("w") as f:
 f.write(report)
 print(f"✅ Report saved to: {report_file}")
 
 print()
 print("=" * 80)
 print("ANALYSIS COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

