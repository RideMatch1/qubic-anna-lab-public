#!/usr/bin/env python3
"""
Monitor for alle laufenden Forschungs-Prozesse.

Zeigt Fortschritt aller Hintergrund-Prozesse mit Checkpoints.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict
import subprocess

OUTPUT_DIR = Path("outputs/derived")

def check_process_running(process_name: str) -> bool:
 """Check ob Prozess läuft."""
 try:
 result = subprocess.run(
 ["ps", "aux"],
 capture_output=True,
 text=True
 )
 return process_name in result.stdout
 except:
 return False

def check_monte_carlo() -> Dict:
 """Check Monte-Carlo Fortschritt."""
 checkpoint_file = OUTPUT_DIR / "monte_carlo_checkpoint.json"
 final_file = OUTPUT_DIR / "monte_carlo_simulation_complete.json"
 
 if final_file.exists():
 with final_file.open() as f:
 data = json.load(f)
 summary = data.get("summary", {})
 return {
 "status": "COMPLETE",
 "matrices_tested": summary.get("total_matrices", 0),
 "identities_found": summary.get("identities_found", 0),
 "onchain_hits": summary.get("onchain_hits", 0),
 "hit_rate": summary.get("hit_rate", 0),
 }
 
 if checkpoint_file.exists():
 with checkpoint_file.open() as f:
 data = json.load(f)
 return {
 "status": "RUNNING",
 "matrices_tested": data.get("matrices_tested", 0),
 "identities_found": data.get("identities_found", 0),
 "onchain_hits": data.get("onchain_hits", 0),
 "last_update": data.get("last_update", "N/A"),
 }
 
 return {"status": "NOT STARTED"}

def check_layer2_derivation() -> Dict:
 """Check Layer-2 Derivation Fortschritt."""
 checkpoint_file = OUTPUT_DIR / "layer2_derivation_checkpoint.json"
 final_file = OUTPUT_DIR / "all_layer2_derivation.json"
 
 if final_file.exists():
 with final_file.open() as f:
 data = json.load(f)
 summary = data.get("summary", {})
 return {
 "status": "COMPLETE",
 "processed": summary.get("total_layer1", 0),
 "layer2_derivable": summary.get("layer2_derivable", 0),
 "layer2_onchain": summary.get("layer2_onchain", 0),
 "derivation_rate": summary.get("layer2_derivation_rate", 0),
 }
 
 if checkpoint_file.exists():
 with checkpoint_file.open() as f:
 data = json.load(f)
 return {
 "status": "RUNNING",
 "processed": data.get("processed", 0),
 "layer2_derivable": data.get("layer2_derivable", 0),
 "layer2_onchain": data.get("layer2_onchain", 0),
 "last_update": data.get("last_update", "N/A"),
 }
 
 return {"status": "NOT STARTED"}

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print(f"RESEARCH PROGRESS MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
 print("=" * 80)
 print()
 
 # Monte-Carlo Simulation
 print("1. MONTE-CARLO SIMULATION")
 print("-" * 80)
 mc_status = check_monte_carlo()
 mc_running = check_process_running("monte_carlo_with_checkpoints")
 
 if mc_status["status"] == "COMPLETE":
 print("✅ Status: COMPLETE")
 print(f" Matrices tested: {mc_status['matrices_tested']:,}")
 print(f" Identities found: {mc_status['identities_found']:,}")
 print(f" On-chain hits: {mc_status['onchain_hits']:,}")
 print(f" Hit rate: {mc_status['hit_rate']:.4f}%")
 elif mc_status["status"] == "RUNNING" or mc_running:
 print("🔄 Status: RUNNING")
 print(f" Matrices tested: {mc_status['matrices_tested']:,} / 10,000")
 print(f" Progress: {mc_status['matrices_tested']/10000*100:.1f}%")
 print(f" Identities found: {mc_status['identities_found']:,}")
 print(f" On-chain hits: {mc_status['onchain_hits']:,}")
 print(f" Last update: {mc_status.get('last_update', 'N/A')}")
 else:
 print("⏸️ Status: NOT STARTED")
 print()
 
 # Layer-2 Derivation
 print("2. LAYER-2 DERIVATION")
 print("-" * 80)
 l2_status = check_layer2_derivation()
 l2_running = check_process_running("derive_all_layer2")
 
 if l2_status["status"] == "COMPLETE":
 print("✅ Status: COMPLETE")
 print(f" Processed: {l2_status['processed']:,}")
 print(f" Layer-2 derivable: {l2_status['layer2_derivable']:,}")
 print(f" Layer-2 on-chain: {l2_status['layer2_onchain']:,}")
 print(f" Derivation rate: {l2_status['derivation_rate']:.1f}%")
 elif l2_status["status"] == "RUNNING" or l2_running:
 print("🔄 Status: RUNNING")
 total = 23477 # Geschätzt
 processed = l2_status.get("processed", 0)
 print(f" Processed: {processed:,} / {total:,}")
 print(f" Progress: {processed/total*100:.1f}%" if total > 0 else " Progress: N/A")
 print(f" Layer-2 derivable: {l2_status.get('layer2_derivable', 0):,}")
 print(f" Layer-2 on-chain: {l2_status.get('layer2_onchain', 0):,}")
 print(f" Last update: {l2_status.get('last_update', 'N/A')}")
 else:
 print("⏸️ Status: NOT STARTED")
 print()
 
 print("=" * 80)
 print()
 print("To start processes:")
 print(" python3 scripts/core/monte_carlo_with_checkpoints.py")
 print(" python3 scripts/core/derive_all_layer2_identities.py")
 print()

if __name__ == "__main__":
 main()

