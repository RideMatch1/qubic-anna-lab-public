#!/usr/bin/env python3
"""Komplette Analyse der 23k Derivation Ergebnisse."""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
COMPLETE_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
RPC_RESULTS_FILE = project_root / "outputs" / "derived" / "rpc_sample_results.json"
REPORTS_DIR = project_root / "outputs" / "reports"

def analyze_23k_complete():
 """Analyze 23k Derivation komplett."""
 print("=" * 80)
 print("23K DERIVATION COMPLETE ANALYSIS")
 print("=" * 80)
 print()
 
 # Load 23k Dataset
 if not COMPLETE_FILE.exists():
 print("❌ 23k Derivation file not found!")
 return
 
 with COMPLETE_FILE.open() as f:
 data = json.load(f)
 
 results = data.get("results", [])
 total = len(results)
 
 print(f"✅ Total Identities: {total}")
 print()
 
 # Position 30/4 Distribution
 pos30_dist = Counter()
 pos4_dist = Counter()
 
 for entry in results:
 identity = entry.get("layer3_identity", "")
 if len(identity) > 30:
 pos30_dist[identity[30].upper()] += 1
 if len(identity) > 4:
 pos4_dist[identity[4].upper()] += 1
 
 print("## Position 30 Distribution (All 26 Characters)")
 for char in sorted(pos30_dist.keys()):
 count = pos30_dist[char]
 percentage = (count / total * 100) if total > 0 else 0
 print(f" {char}: {count:6d} ({percentage:5.2f}%)")
 print()
 
 print("## Position 4 Distribution (All 26 Characters)")
 for char in sorted(pos4_dist.keys()):
 count = pos4_dist[char]
 percentage = (count / total * 100) if total > 0 else 0
 print(f" {char}: {count:6d} ({percentage:5.2f}%)")
 print()
 
 # RPC Sample Analysis
 if RPC_RESULTS_FILE.exists():
 with RPC_RESULTS_FILE.open() as f:
 rpc_data = json.load(f)
 
 sample_size = rpc_data.get("sample_size", 0)
 onchain = rpc_data.get("onchain_confirmed", 0)
 errors = rpc_data.get("errors", 0)
 
 print("## RPC Sample Validation")
 print(f" Sample Size: {sample_size}")
 print(f" On-chain: {onchain}")
 print(f" Errors: {errors}")
 if sample_size > 0:
 print(f" Rate: {onchain/sample_size*100:.1f}%")
 print()
 print(f" ⚠️ Nur {sample_size} statt 2000 geprüft:")
 print(f" - Strategy 'unknown' prüft nur ungeprüfte Identities")
 print(f" - Im Dataset waren nur {sample_size} ungeprüfte vorhanden")
 print()
 
 # Report
 report_lines = [
 "# 23K Derivation Complete Analysis",
 "",
 f"**Total Identities**: {total}",
 "",
 "## Position 30 Distribution",
 ""
 ]
 
 for char in sorted(pos30_dist.keys()):
 count = pos30_dist[char]
 percentage = (count / total * 100) if total > 0 else 0
 report_lines.append(f"- {char}: {count} ({percentage:.2f}%)")
 
 report_lines.extend([
 "",
 "## Position 4 Distribution",
 ""
 ])
 
 for char in sorted(pos4_dist.keys()):
 count = pos4_dist[char]
 percentage = (count / total * 100) if total > 0 else 0
 report_lines.append(f"- {char}: {count} ({percentage:.2f}%)")
 
 if RPC_RESULTS_FILE.exists():
 report_lines.extend([
 "",
 "## RPC Sample Validation",
 f"- Sample Size: {sample_size}",
 f"- On-chain: {onchain}",
 f"- Errors: {errors}",
 f"- Rate: {onchain/sample_size*100:.1f}%" if sample_size > 0 else "- Rate: N/A",
 "",
 f"**Hinweis**: Nur {sample_size} statt 2000 geprüft, da Strategy 'unknown' nur ungeprüfte Identities prüft.",
 ])
 
 report_file = REPORTS_DIR / "23K_COMPLETE_ANALYSIS.md"
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 analyze_23k_complete()

