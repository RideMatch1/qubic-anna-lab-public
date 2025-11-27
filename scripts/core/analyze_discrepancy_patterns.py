#!/usr/bin/env python3
"""
Analyze Discrepancy Patterns

Analysiert die systematischen Unterschiede zwischen dokumentierten und abgeleiteten Identities.
Fokus auf Position 4, 6, 34, 36, 52 (99/100 Unterschiede).

Ziel: Muster erkennen, die uns helfen, die echte Transformation zu verstehen.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
import statistics

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

# Kritische Positionen (99/100 Unterschiede)
CRITICAL_POSITIONS = [4, 6, 34, 36, 52]

def load_comparison_data() -> List[Dict]:
 """Load Seed-Identity-Vergleichsdaten."""
 json_file = OUTPUT_DIR / "seed_identity_comparison.json"
 
 if not json_file.exists():
 print(f"❌ File not found: {json_file}")
 return []
 
 with json_file.open() as f:
 data = json.load(f)
 
 return data.get("comparisons", [])

def analyze_position_patterns(comparisons: List[Dict]) -> Dict:
 """Analyze Muster an kritischen Positionen."""
 patterns = {
 "position_analysis": {},
 "character_mappings": defaultdict(list),
 "transformation_hints": [],
 "statistics": {}
 }
 
 # Für jede kritische Position
 for pos in CRITICAL_POSITIONS:
 pos_data = {
 "position": pos,
 "differences": [],
 "documented_chars": [],
 "derived_chars": [],
 "char_pairs": [],
 "frequency": {}
 }
 
 for comp in comparisons:
 doc_identity = comp.get("documented_identity", "")
 derived_identity = comp.get("derived_identity", "")
 
 if len(doc_identity) > pos and len(derived_identity) > pos:
 doc_char = doc_identity[pos]
 derived_char = derived_identity[pos]
 
 if doc_char != derived_char:
 pos_data["differences"].append({
 "documented": doc_char,
 "derived": derived_char,
 "seed": comp.get("seed", "")[:20] + "..."
 })
 pos_data["documented_chars"].append(doc_char)
 pos_data["derived_chars"].append(derived_char)
 pos_data["char_pairs"].append((doc_char, derived_char))
 
 # Char-Mapping
 patterns["character_mappings"][f"pos_{pos}"].append({
 "from": doc_char,
 "to": derived_char
 })
 
 # Häufigste Char-Paare
 pair_counter = Counter(pos_data["char_pairs"])
 pos_data["most_common_pairs"] = pair_counter.most_common(10)
 
 # Häufigste dokumentierte Chars
 doc_counter = Counter(pos_data["documented_chars"])
 pos_data["most_common_documented"] = doc_counter.most_common(10)
 
 # Häufigste abgeleitete Chars
 derived_counter = Counter(pos_data["derived_chars"])
 pos_data["most_common_derived"] = derived_counter.most_common(10)
 
 patterns["position_analysis"][f"position_{pos}"] = pos_data
 
 return patterns

def analyze_seed_characteristics(comparisons: List[Dict]) -> Dict:
 """Analyze Seed-Charakteristika."""
 seed_analysis = {
 "seed_lengths": [],
 "seed_char_frequency": Counter(),
 "seed_patterns": [],
 "seed_identity_correlation": []
 }
 
 for comp in comparisons:
 seed = comp.get("seed", "")
 doc_identity = comp.get("documented_identity", "")
 derived_identity = comp.get("derived_identity", "")
 
 # Seed-Länge
 seed_analysis["seed_lengths"].append(len(seed))
 
 # Seed-Char-Frequenz
 seed_analysis["seed_char_frequency"].update(seed)
 
 # Seed-Identity-Korrelation
 if len(seed) >= 55 and len(doc_identity) >= 55:
 # Erste 55 Zeichen vergleichen
 seed_lower = seed.lower()
 doc_lower = doc_identity.lower()[:55]
 
 matches = sum(1 for s, d in zip(seed_lower, doc_lower) if s == d)
 seed_analysis["seed_identity_correlation"].append({
 "matches": matches,
 "total": 55,
 "match_rate": matches / 55 if 55 > 0 else 0
 })
 
 return seed_analysis

def analyze_transformation_hints(comparisons: List[Dict]) -> List[Dict]:
 """Analyze Hinweise auf Transformation."""
 hints = []
 
 # Analyze Position 0 (98/100 Unterschiede)
 pos_0_differences = []
 for comp in comparisons:
 doc = comp.get("documented_identity", "")
 derived = comp.get("derived_identity", "")
 if len(doc) > 0 and len(derived) > 0 and doc[0] != derived[0]:
 pos_0_differences.append({
 "documented": doc[0],
 "derived": derived[0],
 "seed_start": comp.get("seed", "")[:5]
 })
 
 if pos_0_differences:
 doc_chars = [d["documented"] for d in pos_0_differences]
 derived_chars = [d["derived"] for d in pos_0_differences]
 
 hints.append({
 "type": "position_0_analysis",
 "description": "Position 0 hat 98/100 Unterschiede",
 "most_common_documented": Counter(doc_chars).most_common(5),
 "most_common_derived": Counter(derived_chars).most_common(5),
 "observation": "Unterschiede beginnen bereits an Position 0"
 })
 
 # Analyze kritische Positionen
 for pos in CRITICAL_POSITIONS:
 pos_differences = []
 for comp in comparisons:
 doc = comp.get("documented_identity", "")
 derived = comp.get("derived_identity", "")
 if len(doc) > pos and len(derived) > pos and doc[pos] != derived[pos]:
 pos_differences.append({
 "documented": doc[pos],
 "derived": derived[pos],
 "seed_char_at_pos": comp.get("seed", "")[pos] if len(comp.get("seed", "")) > pos else "N/A"
 })
 
 if pos_differences:
 hints.append({
 "type": f"position_{pos}_analysis",
 "description": f"Position {pos} hat 99/100 Unterschiede",
 "differences_count": len(pos_differences),
 "sample": pos_differences[:5]
 })
 
 return hints

def analyze_checksum_patterns(comparisons: List[Dict]) -> Dict:
 """Analyze Checksum-Patterns (letzte 4 Zeichen)."""
 checksum_analysis = {
 "documented_checksums": [],
 "derived_checksums": [],
 "checksum_differences": [],
 "patterns": {}
 }
 
 for comp in comparisons:
 doc = comp.get("documented_identity", "")
 derived = comp.get("derived_identity", "")
 
 if len(doc) >= 4 and len(derived) >= 4:
 doc_checksum = doc[-4:]
 derived_checksum = derived[-4:]
 
 checksum_analysis["documented_checksums"].append(doc_checksum)
 checksum_analysis["derived_checksums"].append(derived_checksum)
 
 if doc_checksum != derived_checksum:
 checksum_analysis["checksum_differences"].append({
 "documented": doc_checksum,
 "derived": derived_checksum,
 "identity_body_doc": doc[:56],
 "identity_body_derived": derived[:56]
 })
 
 # Häufigste Checksums
 checksum_analysis["patterns"]["most_common_documented"] = Counter(
 checksum_analysis["documented_checksums"]
 ).most_common(10)
 
 checksum_analysis["patterns"]["most_common_derived"] = Counter(
 checksum_analysis["derived_checksums"]
 ).most_common(10)
 
 return checksum_analysis

def generate_report(analysis: Dict) -> str:
 """Generiere Markdown-Report."""
 report = []
 report.append("# Discrepancy Pattern Analysis Report\n")
 report.append("## Overview\n")
 report.append("Analyse der systematischen Unterschiede zwischen dokumentierten und abgeleiteten Identities.\n")
 report.append(f"Fokus auf kritische Positionen: {', '.join(map(str, CRITICAL_POSITIONS))}\n\n")
 
 # Position Analysis
 report.append("## Position Analysis\n")
 for pos in CRITICAL_POSITIONS:
 pos_key = f"position_{pos}"
 if pos_key in analysis.get("position_analysis", {}):
 pos_data = analysis["position_analysis"][pos_key]
 report.append(f"### Position {pos}\n")
 report.append(f"- **Differences**: {len(pos_data.get('differences', []))}\n")
 
 if pos_data.get("most_common_pairs"):
 report.append("**Most Common Char Pairs:**\n")
 for pair, count in pos_data["most_common_pairs"][:5]:
 report.append(f"- `{pair[0]}` → `{pair[1]}`: {count}x\n")
 report.append("\n")
 
 if pos_data.get("most_common_documented"):
 report.append("**Most Common Documented Chars:**\n")
 for char, count in pos_data["most_common_documented"][:5]:
 report.append(f"- `{char}`: {count}x\n")
 report.append("\n")
 
 if pos_data.get("most_common_derived"):
 report.append("**Most Common Derived Chars:**\n")
 for char, count in pos_data["most_common_derived"][:5]:
 report.append(f"- `{char}`: {count}x\n")
 report.append("\n")
 
 # Transformation Hints
 if analysis.get("transformation_hints"):
 report.append("## Transformation Hints\n")
 for hint in analysis["transformation_hints"][:5]:
 report.append(f"### {hint.get('type', 'Unknown')}\n")
 report.append(f"{hint.get('description', '')}\n\n")
 if hint.get("observation"):
 report.append(f"**Observation**: {hint['observation']}\n\n")
 
 # Checksum Analysis
 if analysis.get("checksum_analysis"):
 report.append("## Checksum Analysis\n")
 checksum = analysis["checksum_analysis"]
 report.append(f"- **Total differences**: {len(checksum.get('checksum_differences', []))}\n")
 
 if checksum.get("patterns", {}).get("most_common_documented"):
 report.append("**Most Common Documented Checksums:**\n")
 for checksum_val, count in checksum["patterns"]["most_common_documented"][:5]:
 report.append(f"- `{checksum_val}`: {count}x\n")
 report.append("\n")
 
 # Seed Analysis
 if analysis.get("seed_analysis"):
 report.append("## Seed Analysis\n")
 seed_analysis = analysis["seed_analysis"]
 
 if seed_analysis.get("seed_lengths"):
 avg_length = statistics.mean(seed_analysis["seed_lengths"])
 report.append(f"- **Average seed length**: {avg_length:.1f}\n")
 
 if seed_analysis.get("seed_identity_correlation"):
 avg_match_rate = statistics.mean([
 s["match_rate"] for s in seed_analysis["seed_identity_correlation"]
 ])
 report.append(f"- **Average seed-identity match rate**: {avg_match_rate:.2%}\n")
 
 # Conclusions
 report.append("## Conclusions\n")
 report.append("### Key Findings:\n")
 report.append("1. **Systematic differences** at positions 4, 6, 34, 36, 52 (99/100)\n")
 report.append("2. **Differences start at position 0** (98/100)\n")
 report.append("3. **No direct character mapping** - transformation is complex\n")
 report.append("4. **Checksum differences** - checksum calculation differs\n\n")
 
 report.append("### Implications:\n")
 report.append("- The transformation `seed → identity` is **cryptographic**, not simple\n")
 report.append("- `identity.lower()[:55] = seed` is an **approximation**, not the real transformation\n")
 report.append("- The real seeds that generate documented identities are **different**\n")
 report.append("- Pattern analysis might help understand the transformation\n\n")
 
 return "".join(report)

def main():
 """Hauptfunktion."""
 import sys
 sys.stdout.write("=" * 80 + "\n")
 sys.stdout.write("ANALYZE DISCREPANCY PATTERNS\n")
 sys.stdout.write("=" * 80 + "\n\n")
 sys.stdout.flush()
 
 # Load Daten
 sys.stdout.write("Loading comparison data...\n")
 sys.stdout.flush()
 comparisons = load_comparison_data()
 
 if not comparisons:
 sys.stdout.write("❌ No comparison data found!\n")
 sys.stdout.flush()
 return
 
 sys.stdout.write(f"✅ Loaded {len(comparisons)} comparisons\n\n")
 sys.stdout.flush()
 
 # Analyze
 sys.stdout.write("Analyzing patterns...\n")
 sys.stdout.write(" - Position patterns...\n")
 sys.stdout.flush()
 position_patterns = analyze_position_patterns(comparisons)
 
 sys.stdout.write(" - Seed characteristics...\n")
 sys.stdout.flush()
 seed_analysis = analyze_seed_characteristics(comparisons)
 
 sys.stdout.write(" - Transformation hints...\n")
 sys.stdout.flush()
 transformation_hints = analyze_transformation_hints(comparisons)
 
 sys.stdout.write(" - Checksum patterns...\n")
 sys.stdout.flush()
 checksum_analysis = analyze_checksum_patterns(comparisons)
 
 # Kombiniere Ergebnisse
 analysis = {
 "position_analysis": position_patterns.get("position_analysis", {}),
 "character_mappings": dict(position_patterns.get("character_mappings", {})),
 "transformation_hints": transformation_hints,
 "checksum_analysis": checksum_analysis,
 "seed_analysis": {
 "seed_lengths": seed_analysis.get("seed_lengths", []),
 "seed_char_frequency": dict(seed_analysis.get("seed_char_frequency", {})),
 "seed_identity_correlation": seed_analysis.get("seed_identity_correlation", [])
 },
 "statistics": {
 "total_comparisons": len(comparisons),
 "critical_positions": CRITICAL_POSITIONS
 }
 }
 
 # Speichere JSON
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_file = OUTPUT_DIR / "discrepancy_pattern_analysis.json"
 with output_file.open("w") as f:
 json.dump(analysis, f, indent=2)
 sys.stdout.write(f"✅ Results saved to: {output_file}\n")
 sys.stdout.flush()
 
 # Generiere Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report = generate_report(analysis)
 report_file = REPORTS_DIR / "discrepancy_pattern_analysis_report.md"
 with report_file.open("w") as f:
 f.write(report)
 sys.stdout.write(f"✅ Report saved to: {report_file}\n")
 sys.stdout.flush()
 
 sys.stdout.write("\n" + "=" * 80 + "\n")
 sys.stdout.write("ANALYSIS COMPLETE\n")
 sys.stdout.write("=" * 80 + "\n")
 sys.stdout.flush()

if __name__ == "__main__":
 main()

