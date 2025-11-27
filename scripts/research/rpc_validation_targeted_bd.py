#!/usr/bin/env python3
"""
Targeted RPC-Validierung for Position-27-Klassen (z.B. B & D)
------------------------------------------------------------
Ziel:
 - Zusätzliche on-chain verifizierte Datensätze for unterrepräsentierte Klassen
 - Fortschrittsanzeige + JSON-Status for lange Läufe

Kurzanleitung:
 source venv-tx/bin/activate
 python3 scripts/research/rpc_validation_targeted_bd.py \
 --targets BD \
 --sample-size 10000 \
 --delay-ms 300

Fortschritt beobachten:
 tail -f outputs/derived/rpc_validation_targeted_status.txt
 cat outputs/derived/rpc_validation_targeted_progress.json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

# Paths & Konstanten
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "derived"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LAYER3_FILE = OUTPUT_DIR / "layer3_derivation_23k_complete.json"
VALIDATED_FILE = OUTPUT_DIR / "rpc_validation_20000_validated_data.json"
RESULTS_FILE = OUTPUT_DIR / "rpc_validation_targeted_bd_results.json"
STATUS_FILE = OUTPUT_DIR / "rpc_validation_targeted_status.txt"
PROGRESS_FILE = OUTPUT_DIR / "rpc_validation_targeted_progress.json"
STOP_FILE = OUTPUT_DIR / "rpc_validation_targeted_stop"

TARGET_POS = 27
LOG_FIRST_N = 10
LOG_INTERVAL = 100

# RPC vorbereiten (Pfad der venv)
try:
 venv_path = PROJECT_ROOT / "venv-tx" / "lib" / "python3.11" / "site-packages"
 if venv_path.exists():
 sys.path.insert(0, str(venv_path))
 from qubipy.rpc import rpc_client
 RPC_AVAILABLE = True
except ImportError:
 RPC_AVAILABLE = False

def log_progress(message: str) -> None:
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 line = f"[{timestamp}] {message}"
 with STATUS_FILE.open("a") as fh:
 fh.write(line + "\n")
 print(line)

def save_progress(data: Dict) -> None:
 with PROGRESS_FILE.open("w") as fh:
 json.dump(data, fh, indent=2)

def load_layer3_data() -> List[Dict]:
 if not LAYER3_FILE.exists():
 raise FileNotFoundError(f"Layer-3-Datei fehlt: {LAYER3_FILE}")
 with LAYER3_FILE.open() as fh:
 raw = json.load(fh)
 return raw.get("results", [])

def load_existing_validations() -> Set[str]:
 if not VALIDATED_FILE.exists():
 return set()
 with VALIDATED_FILE.open() as fh:
 data = json.load(fh).get("data", [])
 return {entry["identity"] for entry in data if "identity" in entry}

def load_existing_results() -> Dict:
 if not RESULTS_FILE.exists():
 return {"runs": [], "data": []}
 with RESULTS_FILE.open() as fh:
 return json.load(fh)

def identity_char(entry: Dict) -> Optional[str]:
 ident = entry.get("layer3_identity", "")
 if len(ident) <= TARGET_POS:
 return None
 return ident[TARGET_POS].upper()

def validate_identity_rpc(identity: str, rpc_inst) -> Dict:
 try:
 balance = rpc_inst.get_balance(identity)
 if balance is None or not isinstance(balance, dict):
 return {
 "exists": False,
 "valid_for_tick": None,
 "has_activity": False,
 "error": "RPC returned invalid payload"
 }

 valid_for_tick = balance.get("validForTick")
 exists = valid_for_tick is not None
 balance_val = int(balance.get("balance", "0"))
 incoming = int(balance.get("incomingAmount", "0"))
 outgoing = int(balance.get("outgoingAmount", "0"))
 num_in = int(balance.get("numberOfIncomingTransfers", 0))
 num_out = int(balance.get("numberOfOutgoingTransfers", 0))
 has_activity = any([balance_val, incoming, outgoing, num_in, num_out])

 return {
 "exists": exists,
 "valid_for_tick": valid_for_tick,
 "balance": balance_val,
 "incoming": incoming,
 "outgoing": outgoing,
 "num_incoming": num_in,
 "num_outgoing": num_out,
 "has_activity": has_activity,
 "error": None if exists else "Identity not found"
 }
 except Exception as exc:
 return {
 "exists": False,
 "valid_for_tick": None,
 "has_activity": False,
 "error": str(exc)
 }

def parse_args() -> argparse.Namespace:
 parser = argparse.ArgumentParser(
 description="Targeted RPC Validation for Position-27-Klassen"
 )
 parser.add_argument(
 "--targets",
 default="BD",
 help="Buchstaben an Position 27, z.B. 'BD' oder 'BCD'.",
 )
 parser.add_argument(
 "--sample-size",
 type=int,
 default=None,
 help="Max. Anzahl Identities (Standard: alle verfügbaren Ziele).",
 )
 parser.add_argument(
 "--delay-ms",
 type=int,
 default=300,
 help="Pause zwischen RPC Calls in Millisekunden (Rate-Limit).",
 )
 parser.add_argument(
 "--shuffle-seed",
 type=int,
 default=2711,
 help="Seed for Zufallssortierung.",
 )
 return parser.parse_args()

def main() -> None:
 args = parse_args()

 if not RPC_AVAILABLE:
 log_progress("❌ qubipy konnte nicht importiert werden – bitte venv-tx aktivieren.")
 sys.exit(1)

 layer3_data = load_layer3_data()
 existing_valid = load_existing_validations()
 previous_results = load_existing_results()
 processed_identities: Set[str] = {entry.get("identity") for entry in previous_results.get("data", [])}
 processed_identities = {iden for iden in processed_identities if iden}

 target_letters = {ch.upper() for ch in args.targets if ch.strip()}

 filtered: List[Dict] = []
 for entry in layer3_data:
 ident = entry.get("layer3_identity")
 seed = entry.get("seed")
 if not ident or not seed or len(ident) <= TARGET_POS or len(seed) < 55:
 continue
 char = ident[TARGET_POS].upper()
 if char not in target_letters:
 continue
 if ident in existing_valid:
 continue
 filtered.append(entry)

 total_available = len(filtered)
 if total_available == 0:
 log_progress("⚠️ Keine passenden Identities gefunden (evtl. alles schon validiert).")
 return

 random.seed(args.shuffle_seed)
 random.shuffle(filtered)

 if args.sample_size:
 filtered = filtered[: args.sample_size]

 log_progress("=============================================================")
 log_progress("TARGETED RPC-VALIDIERUNG")
 log_progress(f"Ziel-Buchstaben : {sorted(target_letters)}")
 log_progress(f"Verfügbare Identities : {total_available}")
 log_progress(f"Geplante Stichprobe : {len(filtered)}")
 log_progress(f"Bereits verarbeitet : {len(processed_identities)} (will abovesprungen)")
 log_progress("=============================================================")

 rpc = rpc_client.QubiPy_RPC()
 delay = max(args.delay_ms, 0) / 1000.0
 start_time = time.time()

 run_meta = {
 "start": datetime.now().isoformat(),
 "targets": sorted(target_letters),
 "planned": len(filtered),
 "delay_ms": args.delay_ms,
 }

 stats = Counter()
 on_chain_count = 0
 total_processed = 0
 new_records: List[Dict] = []

 for idx, entry in enumerate(filtered, start=1):
 ident = entry["layer3_identity"]
 if ident in processed_identities:
 continue

 if STOP_FILE.exists():
 log_progress("🛑 STOP-Signal gefunden – sicherer Abbruch.")
 break

 seed = entry["seed"].lower()
 char = ident[TARGET_POS].upper()
 rpc_result = validate_identity_rpc(ident, rpc)
 exists = rpc_result.get("exists", False)

 record = {
 "identity": ident,
 "seed": seed,
 "target_char": char,
 "on_chain": exists,
 "rpc": rpc_result,
 "timestamp": datetime.now().isoformat(),
 }
 previous_results.setdefault("data", []).append(record)
 new_records.append(record)
 processed_identities.add(ident)

 total_processed += 1
 stats[char] += 1
 if exists:
 on_chain_count += 1

 progress_payload = {
 "status": "running",
 "targets": sorted(target_letters),
 "processed": total_processed,
 "planned": len(filtered),
 "on_chain": on_chain_count,
 "distribution": {letter: stats[letter] for letter in sorted(stats)},
 "elapsed_minutes": round((time.time() - start_time) / 60, 2),
 }
 save_progress(progress_payload)

 if total_processed <= LOG_FIRST_N or total_processed % LOG_INTERVAL == 0:
 log_progress(
 f"[{total_processed}/{len(filtered)}] "
 f"{ident[:8]}… pos27={char} – on_chain={exists}"
 )

 # Ergebnisse-Datei fortlaufend aktualisieren
 run_meta["last_update"] = datetime.now().isoformat()
 run_meta["processed"] = total_processed
 run_meta["on_chain"] = on_chain_count
 previous_results.setdefault("runs", [])
 previous_results["runs"].append(run_meta)
 # Nur letzten Run-Eintrag behalten (verhindert Aufblähung)
 previous_results["runs"] = previous_results["runs"][-1:]
 with RESULTS_FILE.open("w") as fh:
 json.dump(previous_results, fh, indent=2)

 time.sleep(delay)

 duration_min = (time.time() - start_time) / 60
 final_status = "completed" if total_processed == len(filtered) else "paused"
 progress_payload = {
 "status": final_status,
 "targets": sorted(target_letters),
 "processed": total_processed,
 "planned": len(filtered),
 "on_chain": on_chain_count,
 "distribution": {letter: stats[letter] for letter in sorted(stats)},
 "elapsed_minutes": round(duration_min, 2),
 }
 save_progress(progress_payload)

 log_progress("=============================================================")
 log_progress(f"FERTIG: {total_processed}/{len(filtered)} verarbeitet")
 log_progress(f"On-Chain bestätigt: {on_chain_count}")
 log_progress(f"Gesamtdauer: {duration_min:.2f} Minuten")
 log_progress(f"Status: {final_status}")
 log_progress("=============================================================")

if __name__ == "__main__":
 main()

