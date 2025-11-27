#!/usr/bin/env python3
"""
RPC-Validierung for Spalte-6-Hotspots
- nutzt die 200 identitäten aus `column6_hotspot_sample.json`
- prüft via Qubic RPC (`validForTick`) ob die Identities on-chain existieren
- speichert statistiken + fehler in `outputs/derived/rpc_column6_hotspots_results.json`
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

SAMPLE_FILE = project_root / "outputs" / "derived" / "column6_hotspot_sample.json"
OUTPUT_FILE = project_root / "outputs" / "derived" / "rpc_column6_hotspots_results.json"
STATUS_FILE = project_root / "outputs" / "derived" / "rpc_column6_hotspots_status.txt"

try:
 from qubipy.rpc import rpc_client
except ImportError as exc:
 raise SystemExit(f"❌ qubipy fehlt: {exc}. Bitte venv-tx aktivieren.") from exc

def load_sample(limit: int = 200) -> List[str]:
 if not SAMPLE_FILE.exists():
 raise FileNotFoundError(f"Sample-Datei fehlt: {SAMPLE_FILE}")

 with SAMPLE_FILE.open() as f:
 data = json.load(f)

 identities = [entry["identity"] for entry in data.get("identities", []) if entry.get("identity")]
 return identities[:limit]

def log_status(message: str) -> None:
 STATUS_FILE.write_text(message + "\n")
 print(message)

def main():
 identities = load_sample(limit=200)
 if not identities:
 raise SystemExit("❌ Keine Identities im Sample gefunden.")

 client = rpc_client.QubiPy_RPC()

 results: List[Dict] = []
 valid = 0
 errors: List[Dict] = []

 log_status(f"🚀 Starte RPC-Check for {len(identities)} Spalte-6-Hotspots")

 start = time.time()
 for idx, identity in enumerate(identities, 1):
 try:
 response = client.get_balance(identity)
 is_valid = bool(response and response.get("validForTick"))
 if is_valid:
 valid += 1
 results.append(
 {
 "identity": identity,
 "validForTick": response.get("validForTick") if isinstance(response, dict) else None,
 "balance": response.get("balance") if isinstance(response, dict) else None,
 }
 )
 except Exception as exc: # noqa: BLE001
 errors.append({"identity": identity, "error": str(exc)})
 results.append({"identity": identity, "error": str(exc)})

 if idx % 25 == 0 or idx == len(identities):
 log_status(f"⏱️ {idx}/{len(identities)} geprüft – On-Chain: {valid}")

 time.sleep(0.3)

 duration = time.time() - start
 summary = {
 "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
 "sample_size": len(identities),
 "valid_count": valid,
 "valid_rate": valid / len(identities) * 100,
 "duration_seconds": duration,
 "results": results,
 "errors": errors,
 }

 OUTPUT_FILE.write_text(json.dumps(summary, indent=2))
 log_status(f"✅ Fertig. On-Chain {valid}/{len(identities)} ({summary['valid_rate']:.2f}%). Ergebnisse: {OUTPUT_FILE}")

if __name__ == "__main__":
 main()

