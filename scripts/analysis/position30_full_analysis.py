#!/usr/bin/env python3
"""Analysiert Position 30/4 above kompletten Datensatz und erzeugt Prediction-File."""

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
OUTPUT_DIR = project_root / "outputs"
DERIVED_DIR = OUTPUT_DIR / "derived"
REPORTS_DIR = OUTPUT_DIR / "reports"

EXTENDED_FILE = DERIVED_DIR / "layer3_derivation_extended.json"

POS4_PERFECT_ON = set("QZF")
POS4_PERFECT_OFF = set("UJGHI MOSW".replace(" ", ""))
POS4_STRONG_ON = set("TYN P".replace(" ", ""))
POS4_STRONG_OFF = set("RBXEC")

def classify_position4(char: str) -> str:
 if not char:
 return "ON-CHAIN"
 if char in POS4_PERFECT_ON or char in POS4_STRONG_ON:
 return "ON-CHAIN"
 if char in POS4_PERFECT_OFF or char in POS4_STRONG_OFF:
 return "OFF-CHAIN"
 return "ON-CHAIN"

def build_prediction_dataset() -> Dict:
 with EXTENDED_FILE.open() as f:
 raw = json.load(f)

 rows = raw.get("results", [])

 entries: List[Dict] = []
 pos30_counts = Counter()
 pos4_counts = Counter()
 status_by_char = defaultdict(lambda: Counter())

 for idx, entry in enumerate(rows, start=1):
 identity = entry.get("layer3_identity", "")
 seed = entry.get("seed")
 pos30_char = identity[30].upper() if len(identity) > 30 else None
 pos4_char = identity[4].upper() if len(identity) > 4 else None
 actual = entry.get("layer3_onchain")

 if pos30_char:
 pos30_counts[pos30_char] += 1
 if actual is not None:
 status_by_char[("pos30", pos30_char)]["onchain" if actual else "offchain"] += 1
 if pos4_char:
 pos4_counts[pos4_char] += 1
 if actual is not None:
 status_by_char[("pos4", pos4_char)]["onchain" if actual else "offchain"] += 1

 predicted = classify_position4(pos4_char)

 entries.append({
 "index": idx,
 "seed": seed,
 "layer3_identity": identity,
 "position30_char": pos30_char,
 "position4_char": pos4_char,
 "prediction": predicted,
 "actual_onchain": actual
 })

 summary = {
 "total": len(entries),
 "position30_distribution": pos30_counts,
 "position4_distribution": pos4_counts,
 }

 return {
 "entries": entries,
 "summary": summary,
 "status_by_char": {
 f"{pos}_{char}": dict(counts)
 for (pos, char), counts in status_by_char.items()
 }
 }

def save_outputs(dataset: Dict):
 DERIVED_DIR.mkdir(parents=True, exist_ok=True)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)

 entries = dataset["entries"]
 summary = dataset["summary"]
 status_by_char = dataset["status_by_char"]

 out_json = DERIVED_DIR / "layer3_predictions_full.json"
 with out_json.open("w") as f:
 json.dump({
 "generated": Path(__file__).name,
 "total": summary["total"],
 "entries": entries
 }, f, indent=2)
 print(f"💾 Prediction dataset gespeichert: {out_json}")

 report_lines = [
 "# Position 30/4 Full Dataset Analysis",
 "",
 f"Total Identities: {summary['total']}",
 "",
 "## Position 30 Distribution",
 ]
 for char, count in summary["position30_distribution"].most_common():
 report_lines.append(f"- {char}: {count}")

 report_lines.extend(["", "## Position 4 Distribution"])
 for char, count in summary["position4_distribution"].most_common():
 report_lines.append(f"- {char}: {count}")

 if status_by_char:
 report_lines.extend(["", "## Known Status by Character (from validated subset)"])
 for key, counts in status_by_char.items():
 report_lines.append(f"- {key}: {counts}")

 out_md = REPORTS_DIR / "POSITION30_FULL_ANALYSIS.md"
 with out_md.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {out_md}")

def main():
 if not EXTENDED_FILE.exists():
 print(f"❌ Extended dataset not found: {EXTENDED_FILE}")
 return
 dataset = build_prediction_dataset()
 save_outputs(dataset)

if __name__ == "__main__":
 main()
