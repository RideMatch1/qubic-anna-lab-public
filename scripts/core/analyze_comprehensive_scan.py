#!/usr/bin/env python3
"""
Analyze comprehensive_matrix_scan.json for weitere Identities.

Vergleicht mit systematic extraction und findet zusätzliche Identities.
"""

import json
from pathlib import Path
from typing import Set, List

OUTPUT_DIR = Path("outputs/derived")

def main():
 """Analyze Comprehensive Scan."""
 
 print("=" * 80)
 print("COMPREHENSIVE SCAN - ANALYSE")
 print("=" * 80)
 print()
 
 # Load Comprehensive Scan
 comprehensive_file = OUTPUT_DIR / "comprehensive_matrix_scan.json"
 if not comprehensive_file.exists():
 print("❌ comprehensive_matrix_scan.json nicht gefunden")
 return
 
 with comprehensive_file.open() as f:
 data = json.load(f)
 
 comprehensive_identities = set(data.get("all_on_chain_identities", []))
 print(f"Comprehensive Scan: {len(comprehensive_identities):,} on-chain Identities")
 print()
 
 # Load Systematic Extraction
 systematic_file = OUTPUT_DIR / "systematic_matrix_extraction_complete.json"
 systematic_candidates = set()
 
 if systematic_file.exists():
 with systematic_file.open() as f:
 sys_data = json.load(f)
 
 if "total_batches" in sys_data:
 num_batches = sys_data["total_batches"]
 for i in range(num_batches):
 batch_file = OUTPUT_DIR / f"matrix_candidates_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch = json.load(f)
 systematic_candidates.update(batch)
 
 print(f"Systematic Extraction: {len(systematic_candidates):,} Kandidaten")
 print()
 
 # Vergleiche
 matches = comprehensive_identities & systematic_candidates
 additional = comprehensive_identities - systematic_candidates
 
 print(f"Matches: {len(matches):,}")
 print(f"Zusätzliche Identities: {len(additional):,}")
 print()
 
 if additional:
 print("⚠️ WICHTIG: Zusätzliche Identities gefunden!")
 print(f" {len(additional)} Identities aus Comprehensive Scan")
 print(" sind nicht in Systematic Extraction!")
 print()
 print("Erste 10 zusätzliche Identities:")
 for i, identity in enumerate(list(additional)[:10], 1):
 print(f" {i}. {identity}")
 print()
 print("→ Diese könnten aus anderen Patterns stammen!")
 print("→ Sollten wir diese auch analyzen!")
 
 # Speichere zusätzliche Identities
 output_file = OUTPUT_DIR / "additional_identities_from_comprehensive_scan.json"
 with output_file.open("w") as f:
 json.dump({
 "summary": {
 "total_additional": len(additional),
 "source": "comprehensive_matrix_scan.json",
 },
 "identities": sorted(list(additional)),
 }, f, indent=2)
 
 print(f"💾 Gespeichert in: {output_file}")
 else:
 print("✅ Alle Comprehensive Scan Identities sind in Systematic Extraction")
 else:
 print("⚠️ Systematic Extraction nicht gefunden")
 print(" Kann Vergleich nicht durchführen")
 
 print()
 print("=" * 80)
 print("ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

