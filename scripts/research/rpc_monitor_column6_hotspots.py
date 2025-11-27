#!/usr/bin/env python3
"""
RPC-Monitor for Spalte-6-Hotspots

- Liest Identitäten aus `column6_hotspot_sample.json`
- Führt wiederholte RPC-Abfragen (`get_balance`) aus
- Speichert alle Messpunkte als Zeitreihe in `outputs/derived/rpc_column6_hotspots_timeseries.jsonl`
- Fortschritt landet in `outputs/derived/rpc_column6_hotspots_monitor_status.txt`

Nutzung:
 python scripts/research/rpc_monitor_column6_hotspots.py --iterations 3 --interval-seconds 600
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

SAMPLE_FILE = project_root / "outputs" / "derived" / "column6_hotspot_sample.json"
TIMESERIES_FILE = project_root / "outputs" / "derived" / "rpc_column6_hotspots_timeseries.jsonl"
STATUS_FILE = project_root / "outputs" / "derived" / "rpc_column6_hotspots_monitor_status.txt"

try:
 from qubipy.rpc import rpc_client
except ImportError as exc: # noqa: BLE001
 raise SystemExit(
 f"❌ qubipy fehlt: {exc}. Bitte `source venv-tx/bin/activate` ausführen."
 ) from exc

def load_identities(limit: int | None = None) -> List[str]:
 if not SAMPLE_FILE.exists():
 raise FileNotFoundError(f"Sample-Datei fehlt: {SAMPLE_FILE}")

 with SAMPLE_FILE.open() as f:
 data = json.load(f)

 identities = [
 entry["identity"]
 for entry in data.get("identities", [])
 if entry.get("identity")
 ]
 if limit:
 identities = identities[:limit]
 return identities

def append_timeseries_entry(entry: Dict) -> None:
 with TIMESERIES_FILE.open("a") as f:
 f.write(json.dumps(entry) + "\n")

def log_status(message: str) -> None:
 STATUS_FILE.write_text(message + "\n")
 print(message)

def main():
 parser = argparse.ArgumentParser(description="RPC Monitor for Spalte-6-Hotspots")
 parser.add_argument(
 "--interval-seconds",
 type=int,
 default=600,
 help="Wartezeit zwischen zwei Iterationen (Default 600s = 10 Minuten)",
 )
 parser.add_argument(
 "--iterations",
 type=int,
 default=3,
 help="Anzahl der Messzyklen (Default 3)",
 )
 parser.add_argument(
 "--limit",
 type=int,
 default=200,
 help="Max. Anzahl Identities aus dem Sample (Default 200)",
 )
 args = parser.parse_args()

 identities = load_identities(limit=args.limit)
 if not identities:
 raise SystemExit("❌ Keine Identities im Sample gefunden.")

 client = rpc_client.QubiPy_RPC()
 log_status(
 f"🚀 RPC-Monitor gestartet – {len(identities)} Identities, {args.iterations} Iterationen, "
 f"Intervall {args.interval_seconds}s"
 )

 for iteration in range(1, args.iterations + 1):
 iteration_start = time.time()
 timestamp = datetime.utcnow().isoformat()
 valid = 0
 measurements: List[Dict] = []
 errors: List[Dict] = []

 for identity in identities:
 response = None
 last_error = None
 for attempt in range(3):
 try:
 response = client.get_balance(identity)
 break
 except Exception as exc: # noqa: BLE001
 last_error = exc
 time.sleep(0.5 * (attempt + 1))

 if response is None:
 measure = {"identity": identity, "error": str(last_error)}
 errors.append(measure)
 measurements.append(measure)
 continue

 measure = {
 "identity": identity,
 "validForTick": response.get("validForTick") if isinstance(response, dict) else None,
 "balance": response.get("balance") if isinstance(response, dict) else None,
 }
 if measure["validForTick"]:
 valid += 1
 measurements.append(measure)
 time.sleep(0.3) # rate limit

 iteration_entry = {
 "timestamp": timestamp,
 "iteration": iteration,
 "identity_count": len(identities),
 "valid_count": valid,
 "valid_rate": valid / len(identities) * 100,
 "measurements": measurements,
 "errors": errors,
 }
 append_timeseries_entry(iteration_entry)
 log_status(
 f"⏱️ Iteration {iteration}/{args.iterations}: valid {valid}/{len(identities)} "
 f"({iteration_entry['valid_rate']:.2f}%) – Dauer {time.time() - iteration_start:.1f}s"
 )

 if iteration < args.iterations:
 time.sleep(args.interval_seconds)

 log_status(f"✅ RPC-Monitor abgeschlossen. Ergebnisse → {TIMESERIES_FILE}")

if __name__ == "__main__":
 main()

