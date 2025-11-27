#!/usr/bin/env python3
"""Analyze alle Positionen (0-59) auf 23k Dataset for statistische Signifikanz."""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
import numpy as np
from scipy.stats import chi2_contingency

project_root = Path(__file__).parent.parent.parent
COMPLETE_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
RPC_RESULTS_FILE = project_root / "outputs" / "derived" / "rpc_sample_results.json"
EXTENDED_FILE = project_root / "outputs" / "derived" / "layer3_derivation_extended.json"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_all_with_status() -> List[Dict]:
 """Load alle Identities mit bekanntem Status."""
 all_entries = []
 
 if COMPLETE_FILE.exists():
 with COMPLETE_FILE.open() as f:
 data = json.load(f)
 all_entries.extend(data.get("results", []))
 
 if EXTENDED_FILE.exists():
 with EXTENDED_FILE.open() as f:
 data = json.load(f)
 all_entries.extend(data.get("results", []))
 
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
 
 for entry in all_entries:
 identity = entry.get("layer3_identity", "")
 if identity in rpc_map:
 entry["layer3_onchain"] = rpc_map[identity]
 
 return all_entries

def test_position(position: int, entries: List[Dict]) -> Dict:
 """Teste eine Position."""
 char_status = defaultdict(lambda: {"onchain": 0, "offchain": 0})
 
 for entry in entries:
 identity = entry.get("layer3_identity", "")
 status = entry.get("layer3_onchain")
 
 if status is None or len(identity) <= position:
 continue
 
 char = identity[position].upper()
 if status:
 char_status[char]["onchain"] += 1
 else:
 char_status[char]["offchain"] += 1
 
 if not char_status:
 return None
 
 contingency = []
 for char in sorted(char_status.keys()):
 contingency.append([
 char_status[char]["onchain"],
 char_status[char]["offchain"]
 ])
 
 contingency = np.array(contingency)
 
 # Check ob es Off-Chain gibt
 has_offchain = any(row[1] > 0 for row in contingency)
 
 if not has_offchain:
 # Alle sind on-chain - kein Chi-square Test möglich
 correct = sum(row[0] for row in contingency)
 total = contingency.sum()
 accuracy = (correct / total * 100) if total > 0 else 0
 return {
 "position": position,
 "all_onchain": True,
 "accuracy": accuracy,
 "sample_size": int(total),
 "p_value": None,
 "significant": None
 }
 
 try:
 chi2, p_value, dof, expected = chi2_contingency(contingency)
 except ValueError:
 # Fallback
 correct = sum(max(row) for row in contingency)
 total = contingency.sum()
 accuracy = (correct / total * 100) if total > 0 else 0
 return {
 "position": position,
 "accuracy": accuracy,
 "sample_size": int(total),
 "p_value": None,
 "significant": None
 }
 
 n = contingency.sum()
 min_dim = min(len(contingency), len(contingency[0]))
 cramers_v = np.sqrt(chi2 / (n * (min_dim - 1))) if n > 0 and min_dim > 1 else 0
 
 correct = 0
 total = 0
 for char in sorted(char_status.keys()):
 onchain = char_status[char]["onchain"]
 offchain = char_status[char]["offchain"]
 total_chars = onchain + offchain
 if total_chars > 0:
 correct += max(onchain, offchain)
 total += total_chars
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 return {
 "position": position,
 "chi2": float(chi2),
 "p_value": float(p_value),
 "significant": p_value < 0.05,
 "cramers_v": float(cramers_v),
 "accuracy": accuracy,
 "sample_size": int(total)
 }

def analyze_all_positions():
 """Analyze alle Positionen."""
 print("=" * 80)
 print("ALL POSITIONS ANALYSIS (23K DATASET)")
 print("=" * 80)
 print()
 
 all_entries = load_all_with_status()
 known_entries = [e for e in all_entries if e.get("layer3_onchain") is not None]
 
 print(f"Total Identities: {len(all_entries)}")
 print(f"With known status: {len(known_entries)}")
 print()
 
 if not known_entries:
 print("❌ No identities with known status found!")
 return
 
 # Teste alle Positionen
 results = []
 for pos in range(60):
 result = test_position(pos, known_entries)
 if result:
 results.append(result)
 if pos % 10 == 0 or (result.get("significant") is not None and result["significant"]):
 p_val = result.get('p_value', 'N/A')
 p_str = f"{p_val:.6f}" if p_val is not None else "N/A"
 sig_str = '✅' if result.get('significant') else '❌' if result.get('significant') is False else '⚠️'
 print(f"Position {pos:2d}: Accuracy={result.get('accuracy', 0):5.1f}%, "
 f"p={p_str}, "
 f"Significant={sig_str}")
 
 print()
 
 # Top Positions (alle mit Accuracy, sortiert)
 all_results = [r for r in results if r.get("accuracy") is not None]
 all_results.sort(key=lambda x: x.get("accuracy", 0), reverse=True)
 
 # Signifikante (falls vorhanden)
 significant_results = [r for r in results if r.get("significant") is True]
 
 if significant_results:
 print("## Top 10 Significant Positions (by Accuracy)")
 for i, result in enumerate(significant_results[:10], 1):
 p_val = result.get('p_value', 'N/A')
 p_str = f"{p_val:.6f}" if p_val is not None else "N/A"
 cv = result.get('cramers_v', 'N/A')
 cv_str = f"{cv:.4f}" if cv is not None else "N/A"
 print(f" {i:2d}. Position {result['position']:2d}: "
 f"Accuracy={result.get('accuracy', 0):5.1f}%, "
 f"p={p_str}, "
 f"Cramér's V={cv_str}")
 else:
 print("## Top 10 Positions (by Accuracy)")
 print(" ⚠️ Alle Identities sind on-chain - keine signifikanten Unterschiede")
 for i, result in enumerate(all_results[:10], 1):
 print(f" {i:2d}. Position {result['position']:2d}: "
 f"Accuracy={result.get('accuracy', 0):5.1f}% (alle on-chain)")
 print()
 
 # Report
 report_lines = [
 "# All Positions Analysis (23K Dataset)",
 "",
 f"**Total Identities**: {len(all_entries)}",
 f"**With known status**: {len(known_entries)}",
 f"**Significant Positions**: {len(significant_results)}",
 "",
 "## Top 10 Significant Positions (by Accuracy)",
 ""
 ]
 
 for i, result in enumerate(significant_results[:10], 1):
 report_lines.append(
 f"{i}. Position {result['position']:2d}: "
 f"Accuracy={result['accuracy']:5.1f}%, "
 f"p={result['p_value']:.6f}, "
 f"Cramér's V={result['cramers_v']:.4f}"
 )
 
 report_lines.extend([
 "",
 "## All Significant Positions",
 ""
 ])
 
 for result in significant_results:
 report_lines.append(
 f"- Position {result['position']:2d}: "
 f"Accuracy={result['accuracy']:5.1f}%, "
 f"p={result['p_value']:.6f}, "
 f"Cramér's V={result['cramers_v']:.4f}, "
 f"n={result['sample_size']}"
 )
 
 report_file = REPORTS_DIR / "ALL_POSITIONS_ANALYSIS_23K.md"
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 analyze_all_positions()

