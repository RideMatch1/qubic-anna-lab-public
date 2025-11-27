#!/usr/bin/env python3
"""Vergleiche layer3_derivation_complete vs. extended dataset."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

project_root = Path(__file__).parent.parent.parent
OUTPUT_DIR = project_root / "outputs"
DERIVED_DIR = OUTPUT_DIR / "derived"
REPORTS_DIR = OUTPUT_DIR / "reports"

COMPLETE_FILE = DERIVED_DIR / "layer3_derivation_complete.json"
extended_file = DERIVED_DIR / "layer3_derivation_extended.json"

@dataclass
class DatasetInfo:
 name: str
 total: int
 onchain: int
 offchain: int
 unknown: int
 ranges: Dict[str, Dict[str, float]]

def load_dataset(path: Path) -> List[Dict]:
 if not path.exists():
 raise FileNotFoundError(path)
 with path.open() as f:
 data = json.load(f)
 return data.get("results", [])

def summarize_dataset(name: str, entries: List[Dict], bucket_size: int = 100) -> DatasetInfo:
 total = len(entries)
 onchain = sum(1 for e in entries if e.get("layer3_onchain") is True)
 offchain = sum(1 for e in entries if e.get("layer3_onchain") is False)
 unknown = total - onchain - offchain

 ranges = {}
 if bucket_size > 0:
 for start in range(0, total, bucket_size):
 end = min(start + bucket_size, total)
 bucket_entries = entries[start:end]
 bucket_on = sum(1 for e in bucket_entries if e.get("layer3_onchain") is True)
 bucket_off = sum(1 for e in bucket_entries if e.get("layer3_onchain") is False)
 label = f"{start+1}-{end}"
 ranges[label] = {
 "total": len(bucket_entries),
 "onchain": bucket_on,
 "offchain": bucket_off,
 "unknown": len(bucket_entries) - bucket_on - bucket_off,
 }
 return DatasetInfo(name, total, onchain, offchain, unknown, ranges)

def compare_status(complete: List[Dict], extended: List[Dict]) -> Tuple[List[Dict], List[str]]:
 complete_map = {e.get("layer3_identity"): e for e in complete}
 extended_map = {e.get("layer3_identity"): e for e in extended}

 overlap = []
 mismatches = []

 for identity, comp_entry in complete_map.items():
 if identity in extended_map:
 ext_entry = extended_map[identity]
 overlap.append(identity)
 comp_status = comp_entry.get("layer3_onchain")
 ext_status = ext_entry.get("layer3_onchain")
 if comp_status != ext_status:
 mismatches.append({
 "identity": identity,
 "complete_status": comp_status,
 "extended_status": ext_status,
 })

 return [{"identity": i} for i in overlap], mismatches

def main():
 try:
 complete_entries = load_dataset(COMPLETE_FILE)
 extended_entries = load_dataset(extended_file)
 except FileNotFoundError as exc:
 print(f"❌ Datei nicht gefunden: {exc}")
 return

 complete_summary = summarize_dataset("complete", complete_entries)
 extended_summary = summarize_dataset("extended", extended_entries)

 overlap, mismatches = compare_status(complete_entries, extended_entries)

 summary = {
 "complete": complete_summary.__dict__,
 "extended": extended_summary.__dict__,
 "overlap_count": len(overlap),
 "status_mismatches": mismatches,
 }

 out_json = DERIVED_DIR / "dataset_alignment_summary.json"
 with out_json.open("w") as f:
 json.dump(summary, f, indent=2)
 print(f"💾 JSON gespeichert: {out_json}")

 report_lines = [
 "# Dataset Alignment Report",
 "",
 "## Zusammenfassung",
 f"- Complete Dataset: {complete_summary.total} Einträge",
 f"- Extended Dataset: {extended_summary.total} Einträge",
 f"- Überlappende Identities: {len(overlap)}",
 f"- Status-Mismatches: {len(mismatches)}",
 "",
 "## Complete Dataset",
 f"- On-chain: {complete_summary.onchain}",
 f"- Off-chain: {complete_summary.offchain}",
 f"- Unbekannt: {complete_summary.unknown}",
 "",
 "## Extended Dataset",
 f"- On-chain: {extended_summary.onchain}",
 f"- Off-chain: {extended_summary.offchain}",
 f"- Unbekannt: {extended_summary.unknown}",
 "",
 "## Bucket-Analyse (Extended)",
 ]

 for label, stats in extended_summary.ranges.items():
 report_lines.append(
 f"- {label}: on-chain {stats['onchain']}/{stats['total']} (off {stats['offchain']}, unk {stats['unknown']})"
 )

 if mismatches:
 report_lines.append("\n## Status-Mismatches")
 for mm in mismatches:
 report_lines.append(
 f"- {mm['identity']}: complete={mm['complete_status']} vs extended={mm['extended_status']}"
 )

 out_md = REPORTS_DIR / "DATASET_ALIGNMENT_REPORT.md"
 with out_md.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {out_md}")

if __name__ == "__main__":
 main()
