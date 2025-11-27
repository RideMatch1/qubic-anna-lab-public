#!/usr/bin/env python3
"""Simplified Pattern Analysis - Direct execution"""

import json
from pathlib import Path
from collections import Counter, defaultdict

project_root = Path(__file__).parent.parent.parent
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

CRITICAL_POSITIONS = [4, 6, 34, 36, 52]

# Load Daten
json_file = OUTPUT_DIR / "seed_identity_comparison.json"
with json_file.open() as f:
 data = json.load(f)
comparisons = data.get("comparisons", [])

# Analyze Positionen
position_analysis = {}
for pos in CRITICAL_POSITIONS:
 doc_chars = []
 derived_chars = []
 char_pairs = []
 
 for comp in comparisons:
 doc = comp.get("documented_identity", "")
 derived = comp.get("derived_identity", "")
 if len(doc) > pos and len(derived) > pos:
 if doc[pos] != derived[pos]:
 doc_chars.append(doc[pos])
 derived_chars.append(derived[pos])
 char_pairs.append((doc[pos], derived[pos]))
 
 position_analysis[f"position_{pos}"] = {
 "position": pos,
 "differences": len(char_pairs),
 "most_common_pairs": Counter(char_pairs).most_common(10),
 "most_common_documented": Counter(doc_chars).most_common(10),
 "most_common_derived": Counter(derived_chars).most_common(10)
 }

# Checksum-Analyse
checksum_diffs = []
for comp in comparisons:
 doc = comp.get("documented_identity", "")
 derived = comp.get("derived_identity", "")
 if len(doc) >= 4 and len(derived) >= 4:
 if doc[-4:] != derived[-4:]:
 checksum_diffs.append({
 "documented": doc[-4:],
 "derived": derived[-4:]
 })

# Speichere JSON
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
analysis = {
 "position_analysis": position_analysis,
 "checksum_analysis": {
 "total_differences": len(checksum_diffs),
 "most_common_documented": Counter([c["documented"] for c in checksum_diffs]).most_common(10),
 "most_common_derived": Counter([c["derived"] for c in checksum_diffs]).most_common(10)
 },
 "statistics": {
 "total_comparisons": len(comparisons),
 "critical_positions": CRITICAL_POSITIONS
 }
}

with (OUTPUT_DIR / "discrepancy_pattern_analysis.json").open("w") as f:
 json.dump(analysis, f, indent=2)

# Generiere Report
report = ["# Discrepancy Pattern Analysis Report\n\n"]
report.append("## Position Analysis\n\n")

for pos in CRITICAL_POSITIONS:
 pos_key = f"position_{pos}"
 if pos_key in position_analysis:
 pos_data = position_analysis[pos_key]
 report.append(f"### Position {pos}\n")
 report.append(f"- **Differences**: {pos_data['differences']}\n\n")
 
 if pos_data.get("most_common_pairs"):
 report.append("**Most Common Char Pairs:**\n")
 for pair, count in pos_data["most_common_pairs"][:5]:
 report.append(f"- `{pair[0]}` → `{pair[1]}`: {count}x\n")
 report.append("\n")

report.append("## Checksum Analysis\n")
report.append(f"- **Total differences**: {len(checksum_diffs)}\n\n")

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
with (REPORTS_DIR / "discrepancy_pattern_analysis_report.md").open("w") as f:
 f.write("".join(report))

print("✅ Analysis complete!")

