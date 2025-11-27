#!/usr/bin/env python3
"""Ziehe Stichprobe von Layer-3 Identities und validate via Live RPC."""

import argparse
import json
import random
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
PREDICTION_FILE = project_root / "outputs" / "derived" / "layer3_predictions_full.json"
DERIVED_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

DEFAULT_RPC_DELAY = 2.0 # seconds

def load_predictions() -> List[Dict]:
 if not PREDICTION_FILE.exists():
 raise FileNotFoundError(PREDICTION_FILE)
 with PREDICTION_FILE.open() as f:
 data = json.load(f)
 return data.get("entries", [])

def save_predictions(entries: List[Dict]):
 data = {
 "generated": datetime.now().isoformat(),
 "total": len(entries),
 "entries": entries,
 }
 with PREDICTION_FILE.open("w") as f:
 json.dump(data, f, indent=2)

def select_sample(entries: List[Dict], sample_size: int, strategy: str) -> List[Dict]:
 unknown = [e for e in entries if e.get("actual_onchain") is None]
 known = [e for e in entries if e.get("actual_onchain") is not None]

 if strategy == "unknown" or not known:
 population = unknown or entries
 elif strategy == "mixed":
 half = sample_size // 2
 sample = random.sample(unknown, min(len(unknown), half)) if unknown else []
 remaining = sample_size - len(sample)
 if remaining > 0 and known:
 sample.extend(random.sample(known, min(len(known), remaining)))
 return sample
 else: # strategy == "random"
 population = entries

 if len(population) <= sample_size:
 return population
 return random.sample(population, sample_size)

def check_identity_onchain(identity: str, retries: int = 3) -> Dict:
 script = f"""
from qubipy.rpc import rpc_client
import json, time
identity = "{identity}"
try:
 rpc = rpc_client.QubiPy_RPC()
 balance = rpc.get_balance(identity)
 if balance is not None:
 print(json.dumps({{'status': 'ONCHAIN', 'balance': balance}}))
 else:
 print(json.dumps({{'status': 'NOT_FOUND'}}))
except Exception as e:
 print(json.dumps({{'status': 'ERROR', 'error': str(e)}}))
"""
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=30,
 cwd=project_root
 )
 except subprocess.TimeoutExpired:
 return {"status": "ERROR", "error": "timeout"}

 try:
 return json.loads(result.stdout.strip())
 except Exception:
 return {"status": "ERROR", "error": result.stdout.strip() or result.stderr.strip()}

def main():
 parser = argparse.ArgumentParser(description="RPC Sample Validation for Layer-3 Identities")
 parser.add_argument("--sample-size", type=int, default=200)
 parser.add_argument("--strategy", choices=["unknown", "random", "mixed"], default="unknown")
 parser.add_argument("--delay", type=float, default=DEFAULT_RPC_DELAY, help="Delay between RPC calls (seconds)")
 args = parser.parse_args()

 entries = load_predictions()
 sample = select_sample(entries, args.sample_size, args.strategy)
 if not sample:
 print("❌ Kein Sample verfügbar")
 return

 print(f"Validate {len(sample)} Identities via RPC (Strategie: {args.strategy})...")

 success = 0
 errors = 0
 updated_entries = { (e["layer3_identity"]): e for e in entries }
 sample_results = []

 for idx, entry in enumerate(sample, start=1):
 identity = entry["layer3_identity"]
 result = check_identity_onchain(identity)
 status = result.get("status")

 if status == "ONCHAIN":
 entry["actual_onchain"] = True
 success += 1
 elif status == "NOT_FOUND":
 entry["actual_onchain"] = False
 else:
 entry.setdefault("rpc_errors", 0)
 entry["rpc_errors"] = entry.get("rpc_errors", 0) + 1
 errors += 1

 updated_entries[identity] = entry
 sample_results.append({
 "identity": identity,
 "position30_char": entry.get("position30_char"),
 "position4_char": entry.get("position4_char"),
 "rpc_status": status,
 "prediction": entry.get("prediction"),
 "timestamp": datetime.now().isoformat(),
 })

 if idx % 10 == 0:
 print(f" {idx}/{len(sample)} geprüft - ONCHAIN: {success}, Errors: {errors}")
 time.sleep(args.delay)

 # Speichere aktualisierte Predictions
 save_predictions(list(updated_entries.values()))

 # Speichere Stichprobenergebnisse
 summary = {
 "sample_size": len(sample),
 "strategy": args.strategy,
 "onchain_confirmed": success,
 "errors": errors,
 "timestamp": datetime.now().isoformat(),
 "results": sample_results,
 }

 DERIVED_DIR.mkdir(parents=True, exist_ok=True)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)

 out_json = DERIVED_DIR / "rpc_sample_results.json"
 with out_json.open("w") as f:
 json.dump(summary, f, indent=2)
 print(f"💾 Stichprobenergebnisse gespeichert: {out_json}")

 onchain_rate = success / len(sample) * 100 if sample else 0
 report_lines = [
 "# RPC Sample Validation",
 "",
 f"Sample Size: {len(sample)}",
 f"Strategy: {args.strategy}",
 f"Confirmed On-chain: {success} ({onchain_rate:.1f}%)",
 f"Errors: {errors}",
 "",
 "## Beispiele",
 ]
 for item in sample_results[:10]:
 report_lines.append(
 f"- {item['identity'][:20]}... pos30={item['position30_char']} rpc={item['rpc_status']} pred={item['prediction']}"
 )

 out_md = REPORTS_DIR / "RPC_SAMPLE_VALIDATION_REPORT.md"
 with out_md.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {out_md}")

if __name__ == "__main__":
 main()
