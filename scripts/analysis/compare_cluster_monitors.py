#!/usr/bin/env python3
"""
Vergleicht die Zeitreihen der Spalte-6- und NOW/NO-RPC-Monitore.
- Lädt `rpc_column6_hotspots_timeseries.jsonl` & `rpc_nowno_hotspots_timeseries.jsonl`
- Aggregiert Validitätsraten, erkennt Fehler/Timeouts
- Speichert Ergebnis nach `outputs/derived/cluster_monitor_comparison.json`
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent

COLUMN6_FILE = project_root / "outputs" / "derived" / "rpc_column6_hotspots_timeseries.jsonl"
NOWNO_FILE = project_root / "outputs" / "derived" / "rpc_nowno_hotspots_timeseries.jsonl"
OUTPUT_FILE = project_root / "outputs" / "derived" / "cluster_monitor_comparison.json"

def load_timeseries(file_path: Path) -> List[Dict]:
 entries: List[Dict] = []
 if not file_path.exists():
 return entries
 with file_path.open() as f:
 for line in f:
 line = line.strip()
 if not line:
 continue
 try:
 entries.append(json.loads(line))
 except json.JSONDecodeError:
 continue
 return entries

def summarize(entries: List[Dict]) -> Dict:
 if not entries:
 return {}
 valid_rates = [entry.get("valid_rate", 0) for entry in entries]
 avg_rate = sum(valid_rates) / len(valid_rates)
 min_rate = min(valid_rates)
 max_rate = max(valid_rates)

 total_errors = sum(len(entry.get("errors", [])) for entry in entries)
 error_identities = list({
 err.get("identity")
 for entry in entries
 for err in entry.get("errors", [])
 if err.get("identity")
 })

 return {
 "iterations": len(entries),
 "avg_valid_rate": avg_rate,
 "min_valid_rate": min_rate,
 "max_valid_rate": max_rate,
 "total_errors": total_errors,
 "error_identities": error_identities,
 }

def main():
 column6_entries = load_timeseries(COLUMN6_FILE)
 nowno_entries = load_timeseries(NOWNO_FILE)

 comparison = {
 "column6": summarize(column6_entries),
 "nowno": summarize(nowno_entries),
 "difference": {
 "avg_valid_rate_delta": (
 summarize(column6_entries).get("avg_valid_rate", 0)
 - summarize(nowno_entries).get("avg_valid_rate", 0)
 ),
 "error_count_delta": (
 summarize(column6_entries).get("total_errors", 0)
 - summarize(nowno_entries).get("total_errors", 0)
 ),
 },
 }

 OUTPUT_FILE.write_text(json.dumps(comparison, indent=2))
 print(f"Summary saved to {OUTPUT_FILE}")

if __name__ == "__main__":
 main()

