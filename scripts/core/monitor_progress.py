#!/usr/bin/env python3
"""
Monitor for laufende Prozesse - Prüft regelmäßig den Fortschritt.
"""

import json
import time
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("outputs/derived")
CHECKPOINT_FILES = {
 "onchain_validation": OUTPUT_DIR / "onchain_validation_checkpoint.json",
 "checksum_calculation": OUTPUT_DIR / "checksum_calculation_checkpoint.json",
}

def check_progress():
 """Check Fortschritt aller laufenden Prozesse."""
 
 print("=" * 80)
 print(f"FORTSCRITTS-MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
 print("=" * 80)
 print()
 
 # On-Chain Validierung
 checkpoint_file = CHECKPOINT_FILES["onchain_validation"]
 if checkpoint_file.exists():
 with checkpoint_file.open() as f:
 data = json.load(f)
 
 processed = data.get("processed", 0)
 onchain = len(data.get("onchain_identities", []))
 last_index = data.get("last_processed_index", -1)
 
 total = 23765
 progress = processed / total * 100 if total > 0 else 0
 rate = onchain / processed * 100 if processed > 0 else 0
 
 print("🔄 ON-CHAIN VALIDIERUNG:")
 print(f" Progress: {processed:,} / {total:,} ({progress:.1f}%)")
 print(f" On-chain gefunden: {onchain:,} ({rate:.1f}%)")
 print(f" Letzter Index: {last_index:,}")
 print(f" Verbleibend: {total - processed:,}")
 print()
 else:
 # Check ob komplett
 complete_file = OUTPUT_DIR / "checksum_identities_onchain_validation_complete.json"
 if complete_file.exists():
 with complete_file.open() as f:
 data = json.load(f)
 summary = data.get("summary", {})
 print("✅ ON-CHAIN VALIDIERUNG: KOMPLETT")
 print(f" Total geprüft: {summary.get('total_checked', 0):,}")
 print(f" On-chain gefunden: {summary.get('onchain_found', 0):,}")
 print()
 else:
 print("⏳ ON-CHAIN VALIDIERUNG: Noch nicht gestartet")
 print()
 
 # Checksum-Berechnung
 checksum_file = CHECKPOINT_FILES["checksum_calculation"]
 if checksum_file.exists():
 with checksum_file.open() as f:
 data = json.load(f)
 processed = data.get("processed", 0)
 print("🔄 CHECKSUM-BERECHNUNG:")
 print(f" Progress: {processed:,} verarbeitet")
 print()
 else:
 complete_file = OUTPUT_DIR / "candidates_with_checksums_complete.json"
 if complete_file.exists():
 print("✅ CHECKSUM-BERECHNUNG: KOMPLETT")
 print()
 else:
 print("⏳ CHECKSUM-BERECHNUNG: Noch nicht gestartet")
 print()

if __name__ == "__main__":
 check_progress()

