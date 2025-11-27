#!/usr/bin/env python3
"""Position 30/4 Large-Scale Analysis auf ALLEN verfügbaren Identities."""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
EXTENDED_FILE = project_root / "outputs" / "derived" / "layer3_derivation_extended.json"
COMPLETE_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_all_identities() -> List[Dict]:
 """Load alle verfügbaren Identities."""
 all_results = []
 
 # Load extended file
 if EXTENDED_FILE.exists():
 with EXTENDED_FILE.open() as f:
 data = json.load(f)
 results = data.get("results", [])
 all_results.extend(results)
 print(f"✅ Loaded {len(results)} from extended file")
 
 # Load complete file
 if COMPLETE_FILE.exists():
 with COMPLETE_FILE.open() as f:
 data = json.load(f)
 results = data.get("results", [])
 all_results.extend(results)
 print(f"✅ Loaded {len(results)} from complete file")
 
 # Entferne Duplikate
 seen = set()
 unique_results = []
 for entry in all_results:
 identity = entry.get("layer3_identity", "")
 if identity and identity not in seen:
 seen.add(identity)
 unique_results.append(entry)
 
 print(f"✅ Total unique identities: {len(unique_results)}")
 return unique_results

def analyze_position30_full_scale():
 """Analyze Position 30/4 auf allen Identities."""
 print("=" * 80)
 print("POSITION 30/4 FULL-SCALE ANALYSIS")
 print("=" * 80)
 print()
 
 # Load alle Identities
 all_identities = load_all_identities()
 
 if not all_identities:
 print("❌ No identities found!")
 return
 
 # Analyze Position 30/4
 pos30_distribution = Counter()
 pos4_distribution = Counter()
 pos30_by_status = defaultdict(lambda: Counter())
 pos4_by_status = defaultdict(lambda: Counter())
 
 known_status_count = 0
 
 for entry in all_identities:
 identity = entry.get("layer3_identity", "")
 status = entry.get("layer3_onchain")
 
 if len(identity) > 30:
 pos30_char = identity[30].upper()
 pos30_distribution[pos30_char] += 1
 if status is not None:
 pos30_by_status["onchain" if status else "offchain"][pos30_char] += 1
 known_status_count += 1
 
 if len(identity) > 4:
 pos4_char = identity[4].upper()
 pos4_distribution[pos4_char] += 1
 if status is not None:
 pos4_by_status["onchain" if status else "offchain"][pos4_char] += 1
 
 print(f"Total Identities: {len(all_identities)}")
 print(f"With known status: {known_status_count}")
 print()
 
 # Position 30 Analysis
 print("## Position 30 Distribution (All 26 Characters)")
 for char in sorted(pos30_distribution.keys()):
 count = pos30_distribution[char]
 onchain = pos30_by_status["onchain"][char]
 offchain = pos30_by_status["offchain"][char]
 total_known = onchain + offchain
 onchain_rate = (onchain / total_known * 100) if total_known > 0 else 0
 print(f" {char}: {count:5d} total, {onchain}/{total_known} on-chain ({onchain_rate:.1f}%)" if total_known > 0 else f" {char}: {count:5d} total")
 print()
 
 # Position 4 Analysis
 print("## Position 4 Distribution (All 26 Characters)")
 for char in sorted(pos4_distribution.keys()):
 count = pos4_distribution[char]
 onchain = pos4_by_status["onchain"][char]
 offchain = pos4_by_status["offchain"][char]
 total_known = onchain + offchain
 onchain_rate = (onchain / total_known * 100) if total_known > 0 else 0
 print(f" {char}: {count:5d} total, {onchain}/{total_known} on-chain ({onchain_rate:.1f}%)" if total_known > 0 else f" {char}: {count:5d} total")
 print()
 
 # Perfect Markers (Position 4, n >= 10)
 print("## Perfect Markers (Position 4, n >= 10)")
 perfect_on = []
 perfect_off = []
 
 for char in sorted(pos4_distribution.keys()):
 count = pos4_distribution[char]
 if count >= 10:
 onchain = pos4_by_status["onchain"][char]
 offchain = pos4_by_status["offchain"][char]
 total_known = onchain + offchain
 if total_known > 0:
 if offchain == 0:
 perfect_on.append((char, count, onchain))
 elif onchain == 0:
 perfect_off.append((char, count, offchain))
 
 if perfect_on:
 print("On-Chain:")
 for char, count, onchain in sorted(perfect_on, key=lambda x: x[1], reverse=True):
 print(f" {char}: {onchain}/{count} (100% on-chain)")
 
 if perfect_off:
 print("Off-Chain:")
 for char, count, offchain in sorted(perfect_off, key=lambda x: x[1], reverse=True):
 print(f" {char}: {offchain}/{count} (100% off-chain)")
 
 if not perfect_on and not perfect_off:
 print(" No perfect markers found (n >= 10)")
 print()
 
 # Report
 report_lines = [
 "# Position 30/4 Full-Scale Analysis",
 "",
 f"**Total Identities**: {len(all_identities)}",
 f"**With known status**: {known_status_count}",
 "",
 "## Position 30 Distribution",
 ""
 ]
 
 for char in sorted(pos30_distribution.keys()):
 count = pos30_distribution[char]
 onchain = pos30_by_status["onchain"][char]
 offchain = pos30_by_status["offchain"][char]
 total_known = onchain + offchain
 if total_known > 0:
 onchain_rate = (onchain / total_known * 100)
 report_lines.append(f"- {char}: {count} total, {onchain}/{total_known} on-chain ({onchain_rate:.1f}%)")
 else:
 report_lines.append(f"- {char}: {count} total")
 
 report_lines.extend([
 "",
 "## Position 4 Distribution",
 ""
 ])
 
 for char in sorted(pos4_distribution.keys()):
 count = pos4_distribution[char]
 onchain = pos4_by_status["onchain"][char]
 offchain = pos4_by_status["offchain"][char]
 total_known = onchain + offchain
 if total_known > 0:
 onchain_rate = (onchain / total_known * 100)
 report_lines.append(f"- {char}: {count} total, {onchain}/{total_known} on-chain ({onchain_rate:.1f}%)")
 else:
 report_lines.append(f"- {char}: {count} total")
 
 if perfect_on:
 report_lines.extend([
 "",
 "## Perfect On-Chain Markers (Position 4, n >= 10)",
 ""
 ])
 for char, count, onchain in sorted(perfect_on, key=lambda x: x[1], reverse=True):
 report_lines.append(f"- {char}: {onchain}/{count} (100% on-chain)")
 
 if perfect_off:
 report_lines.extend([
 "",
 "## Perfect Off-Chain Markers (Position 4, n >= 10)",
 ""
 ])
 for char, count, offchain in sorted(perfect_off, key=lambda x: x[1], reverse=True):
 report_lines.append(f"- {char}: {offchain}/{count} (100% off-chain)")
 
 report_file = REPORTS_DIR / "POSITION30_FULL_SCALE_ANALYSIS.md"
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 analyze_position30_full_scale()

