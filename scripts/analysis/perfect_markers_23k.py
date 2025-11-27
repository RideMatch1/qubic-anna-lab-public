#!/usr/bin/env python3
"""Finde Perfect Markers auf 23k Dataset mit bekannten RPC Status."""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
COMPLETE_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
RPC_RESULTS_FILE = project_root / "outputs" / "derived" / "rpc_sample_results.json"
EXTENDED_FILE = project_root / "outputs" / "derived" / "layer3_derivation_extended.json"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_all_with_status() -> List[Dict]:
 """Load alle Identities mit bekanntem Status."""
 all_entries = []
 
 # Load 23k Dataset
 if COMPLETE_FILE.exists():
 with COMPLETE_FILE.open() as f:
 data = json.load(f)
 results = data.get("results", [])
 all_entries.extend(results)
 
 # Load extended Dataset
 if EXTENDED_FILE.exists():
 with EXTENDED_FILE.open() as f:
 data = json.load(f)
 results = data.get("results", [])
 all_entries.extend(results)
 
 # Merge RPC Results
 if RPC_RESULTS_FILE.exists():
 with RPC_RESULTS_FILE.open() as f:
 rpc_data = json.load(f)
 
 rpc_map = {}
 for result in rpc_data.get("results", []):
 identity = result.get("identity", "")
 status = result.get("rpc_status", "")
 if status == "ONCHAIN":
 rpc_map[identity] = True
 elif status == "NOT_FOUND":
 rpc_map[identity] = False
 
 # Update entries with RPC status
 for entry in all_entries:
 identity = entry.get("layer3_identity", "")
 if identity in rpc_map:
 entry["layer3_onchain"] = rpc_map[identity]
 
 return all_entries

def find_perfect_markers():
 """Finde Perfect Markers auf 23k Dataset."""
 print("=" * 80)
 print("PERFECT MARKERS ANALYSIS (23K DATASET)")
 print("=" * 80)
 print()
 
 # Load alle Identities mit Status
 all_entries = load_all_with_status()
 
 # Filtere nur bekannte Status
 known_entries = [e for e in all_entries if e.get("layer3_onchain") is not None]
 
 print(f"Total Identities: {len(all_entries)}")
 print(f"With known status: {len(known_entries)}")
 print()
 
 if not known_entries:
 print("❌ No identities with known status found!")
 return
 
 # Analyze Position 30/4
 pos30_stats = defaultdict(lambda: {"onchain": 0, "offchain": 0, "total": 0})
 pos4_stats = defaultdict(lambda: {"onchain": 0, "offchain": 0, "total": 0})
 
 for entry in known_entries:
 identity = entry.get("layer3_identity", "")
 status = entry.get("layer3_onchain")
 
 if len(identity) > 30:
 pos30_char = identity[30].upper()
 pos30_stats[pos30_char]["total"] += 1
 if status:
 pos30_stats[pos30_char]["onchain"] += 1
 else:
 pos30_stats[pos30_char]["offchain"] += 1
 
 if len(identity) > 4:
 pos4_char = identity[4].upper()
 pos4_stats[pos4_char]["total"] += 1
 if status:
 pos4_stats[pos4_char]["onchain"] += 1
 else:
 pos4_stats[pos4_char]["offchain"] += 1
 
 # Finde Perfect Markers (n >= 10)
 print("## Perfect On-Chain Markers (Position 30, n >= 10)")
 perfect_on_pos30 = []
 for char in sorted(pos30_stats.keys()):
 stats = pos30_stats[char]
 if stats["total"] >= 10 and stats["offchain"] == 0:
 perfect_on_pos30.append((char, stats["total"], stats["onchain"]))
 
 if perfect_on_pos30:
 for char, total, onchain in sorted(perfect_on_pos30, key=lambda x: x[1], reverse=True):
 print(f" {char}: {onchain}/{total} (100% on-chain)")
 else:
 print(" Keine gefunden")
 print()
 
 print("## Perfect Off-Chain Markers (Position 30, n >= 10)")
 perfect_off_pos30 = []
 for char in sorted(pos30_stats.keys()):
 stats = pos30_stats[char]
 if stats["total"] >= 10 and stats["onchain"] == 0:
 perfect_off_pos30.append((char, stats["total"], stats["offchain"]))
 
 if perfect_off_pos30:
 for char, total, offchain in sorted(perfect_off_pos30, key=lambda x: x[1], reverse=True):
 print(f" {char}: {offchain}/{total} (100% off-chain)")
 else:
 print(" Keine gefunden")
 print()
 
 print("## Perfect On-Chain Markers (Position 4, n >= 10)")
 perfect_on_pos4 = []
 for char in sorted(pos4_stats.keys()):
 stats = pos4_stats[char]
 if stats["total"] >= 10 and stats["offchain"] == 0:
 perfect_on_pos4.append((char, stats["total"], stats["onchain"]))
 
 if perfect_on_pos4:
 for char, total, onchain in sorted(perfect_on_pos4, key=lambda x: x[1], reverse=True):
 print(f" {char}: {onchain}/{total} (100% on-chain)")
 else:
 print(" Keine gefunden")
 print()
 
 print("## Perfect Off-Chain Markers (Position 4, n >= 10)")
 perfect_off_pos4 = []
 for char in sorted(pos4_stats.keys()):
 stats = pos4_stats[char]
 if stats["total"] >= 10 and stats["onchain"] == 0:
 perfect_off_pos4.append((char, stats["total"], stats["offchain"]))
 
 if perfect_off_pos4:
 for char, total, offchain in sorted(perfect_off_pos4, key=lambda x: x[1], reverse=True):
 print(f" {char}: {offchain}/{total} (100% off-chain)")
 else:
 print(" Keine gefunden")
 print()
 
 # Report
 report_lines = [
 "# Perfect Markers Analysis (23K Dataset)",
 "",
 f"**Total Identities**: {len(all_entries)}",
 f"**With known status**: {len(known_entries)}",
 "",
 "## Perfect On-Chain Markers (Position 30, n >= 10)",
 ""
 ]
 
 if perfect_on_pos30:
 for char, total, onchain in sorted(perfect_on_pos30, key=lambda x: x[1], reverse=True):
 report_lines.append(f"- {char}: {onchain}/{total} (100% on-chain)")
 else:
 report_lines.append("Keine gefunden")
 
 report_lines.extend([
 "",
 "## Perfect Off-Chain Markers (Position 30, n >= 10)",
 ""
 ])
 
 if perfect_off_pos30:
 for char, total, offchain in sorted(perfect_off_pos30, key=lambda x: x[1], reverse=True):
 report_lines.append(f"- {char}: {offchain}/{total} (100% off-chain)")
 else:
 report_lines.append("Keine gefunden")
 
 report_lines.extend([
 "",
 "## Perfect On-Chain Markers (Position 4, n >= 10)",
 ""
 ])
 
 if perfect_on_pos4:
 for char, total, onchain in sorted(perfect_on_pos4, key=lambda x: x[1], reverse=True):
 report_lines.append(f"- {char}: {onchain}/{total} (100% on-chain)")
 else:
 report_lines.append("Keine gefunden")
 
 report_lines.extend([
 "",
 "## Perfect Off-Chain Markers (Position 4, n >= 10)",
 ""
 ])
 
 if perfect_off_pos4:
 for char, total, offchain in sorted(perfect_off_pos4, key=lambda x: x[1], reverse=True):
 report_lines.append(f"- {char}: {offchain}/{total} (100% off-chain)")
 else:
 report_lines.append("Keine gefunden")
 
 report_file = REPORTS_DIR / "PERFECT_MARKERS_23K.md"
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 find_perfect_markers()

