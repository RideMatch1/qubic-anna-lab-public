#!/usr/bin/env python3
"""
Check Status der On-Chain Validierung

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
"""

import json
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("outputs/derived")
CHECKPOINT_FILE = OUTPUT_DIR / "onchain_validation_checkpoint.json"
FINAL_FILE = OUTPUT_DIR / "onchain_validation_all_identities.json"
LOG_FILE = Path("/tmp/onchain_validation.log")

def main():
 print("=" * 80)
 print("ON-CHAIN VALIDATION STATUS")
 print("=" * 80)
 print()
 print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
 print()
 
 # Check Checkpoint
 if CHECKPOINT_FILE.exists():
 try:
 with CHECKPOINT_FILE.open() as f:
 checkpoint = json.load(f)
 total_checked = checkpoint.get("total_checked", 0)
 onchain_count = checkpoint.get("onchain_count", 0)
 
 print("📊 Checkpoint Status:")
 print(f" Checked: {total_checked}/2449 identities")
 print(f" On-chain: {onchain_count}")
 if total_checked > 0:
 onchain_rate = (onchain_count / total_checked) * 100
 print(f" On-chain rate: {onchain_rate:.1f}%")
 progress = (total_checked / 2449) * 100
 print(f" Progress: {progress:.1f}%")
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
 print(f" Total checked: {summary.get('total_checked', 0)}")
 print(f" On-chain: {summary.get('onchain_count', 0)}")
 print(f" Off-chain: {summary.get('offchain_count', 0)}")
 print(f" On-chain rate: {summary.get('onchain_rate', 0):.1f}%")
 print()
 
 layer_stats = data.get("layer_statistics", {})
 if layer_stats:
 print(" Layer statistics:")
 for layer in sorted(layer_stats.keys()):
 stats = layer_stats[layer]
 print(f" Layer {layer}: {stats['onchain']}/{stats['total']} on-chain ({stats['onchain_rate']:.1f}%)")
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
 
 print("=" * 80)

if __name__ == "__main__":
 main()

