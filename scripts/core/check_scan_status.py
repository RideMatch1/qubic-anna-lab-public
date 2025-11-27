#!/usr/bin/env python3
"""
Check Scan-Status und zeige Fortschritt

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("outputs/derived")
CHECKPOINT_FILE = OUTPUT_DIR / "comprehensive_scan_checkpoint.json"
FINAL_FILE = OUTPUT_DIR / "comprehensive_identity_seed_scan.json"
LOG_FILE = Path("/tmp/comprehensive_scan.log")

def check_process():
 """Check ob Scan-Prozess läuft."""
 result = subprocess.run(
 ["ps", "aux"],
 capture_output=True,
 text=True
 )
 
 lines = result.stdout.split("\n")
 scan_processes = [l for l in lines if "comprehensive_identity_seed_scan" in l and "grep" not in l]
 
 return len(scan_processes) > 0, scan_processes

def main():
 print("=" * 80)
 print("SCAN STATUS CHECK")
 print("=" * 80)
 print()
 print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
 print()
 
 # Check Prozess
 is_running, processes = check_process()
 if is_running:
 print("✅ Scan is RUNNING")
 if processes:
 print(f" Process: {processes[0].split()[1]} (PID)")
 else:
 print("❌ Scan is NOT running")
 print()
 
 # Check Checkpoint
 if CHECKPOINT_FILE.exists():
 try:
 with CHECKPOINT_FILE.open() as f:
 checkpoint = json.load(f)
 processed = len(checkpoint.get("processed_seeds", []))
 total_found = checkpoint.get("total_found", 0)
 
 print("📊 Checkpoint Status:")
 print(f" Processed seeds: {processed}")
 print(f" Identities found: {total_found}")
 
 # Schätze Gesamtanzahl (525 Seeds bekannt)
 if processed > 0:
 progress_pct = (processed / 525) * 100
 print(f" Progress: {progress_pct:.1f}% (estimated)")
 remaining = 525 - processed
 print(f" Remaining: ~{remaining} seeds")
 except Exception as e:
 print(f"⚠️ Could not read checkpoint: {e}")
 else:
 print("⚠️ No checkpoint file found")
 print()
 
 # Check Finale Ergebnisse
 if FINAL_FILE.exists():
 try:
 with FINAL_FILE.open() as f:
 data = json.load(f)
 summary = data.get("summary", {})
 
 print("✅ Final Results Available:")
 print(f" Total seeds: {summary.get('total_seeds', 0)}")
 print(f" Seeds with identities: {summary.get('seeds_with_identities', 0)}")
 print(f" Total unique identities: {summary.get('total_unique_identities', 0)}")
 print(f" Max layer depth: {summary.get('max_layer_depth', 0)}")
 
 layer_dist = summary.get("layer_distribution", {})
 if layer_dist:
 print()
 print(" Layer distribution:")
 for layer in sorted(layer_dist.keys()):
 print(f" - Layer {layer}: {layer_dist[layer]} identities")
 except Exception as e:
 print(f"⚠️ Could not read final results: {e}")
 else:
 print("⚠️ No final results file yet")
 print()
 
 # Check Log
 if LOG_FILE.exists():
 try:
 with LOG_FILE.open() as f:
 lines = f.readlines()
 if lines:
 print("📝 Recent Log Output (last 5 lines):")
 for line in lines[-5:]:
 print(f" {line.rstrip()}")
 except Exception as e:
 print(f"⚠️ Could not read log: {e}")
 else:
 print("⚠️ No log file found")
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 if is_running:
 if CHECKPOINT_FILE.exists():
 with CHECKPOINT_FILE.open() as f:
 checkpoint = json.load(f)
 processed = len(checkpoint.get("processed_seeds", []))
 if processed > 0:
 progress = (processed / 525) * 100
 print(f"✅ Scan läuft: {processed}/525 seeds ({progress:.1f}%)")
 else:
 print("✅ Scan läuft: Startphase")
 else:
 print("✅ Scan läuft: Noch kein Checkpoint")
 elif FINAL_FILE.exists():
 print("✅ Scan ABGESCHLOSSEN - Finale Ergebnisse verfügbar")
 else:
 print("⚠️ Scan Status unklar - Check manuell")
 
 print()
 print("=" * 80)

if __name__ == "__main__":
 main()

