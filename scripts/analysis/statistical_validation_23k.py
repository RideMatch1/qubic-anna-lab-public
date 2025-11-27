#!/usr/bin/env python3
"""Statistische Validierung Position 30/4 auf 23k Dataset."""

import json
from pathlib import Path
from collections import Counter, defaultdict
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

def test_position_significance(position: int, entries: List[Dict]) -> Dict:
 """Teste statistische Signifikanz for eine Position."""
 # Baue Contingency Table
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
 return {"error": "No data"}
 
 # Erstelle Contingency Table
 chars = sorted(char_status.keys())
 contingency = []
 for char in chars:
 contingency.append([
 char_status[char]["onchain"],
 char_status[char]["offchain"]
 ])
 
 contingency = np.array(contingency)
 
 # Check ob es Off-Chain gibt
 has_offchain = any(row[1] > 0 for row in contingency)
 
 if not has_offchain:
 # Alle sind on-chain - kein Chi-square Test möglich
 return {
 "position": position,
 "error": "All identities are on-chain - no statistical test possible",
 "all_onchain": True,
 "sample_size": int(contingency.sum())
 }
 
 # Chi-square Test
 try:
 chi2, p_value, dof, expected = chi2_contingency(contingency)
 except ValueError:
 # Fallback wenn Test nicht möglich
 return {
 "position": position,
 "error": "Chi-square test not possible (zero expected frequencies)",
 "sample_size": int(contingency.sum())
 }
 
 # Cramér's V
 n = contingency.sum()
 min_dim = min(len(contingency), len(contingency[0]))
 cramers_v = np.sqrt(chi2 / (n * (min_dim - 1))) if n > 0 and min_dim > 1 else 0
 
 # Accuracy (vereinfacht: häufigeres Label)
 correct = 0
 total = 0
 for char in chars:
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
 "dof": int(dof),
 "cramers_v": float(cramers_v),
 "effect_size": "large" if cramers_v > 0.5 else "medium" if cramers_v > 0.3 else "small",
 "accuracy": accuracy,
 "sample_size": int(total),
 "unique_chars": len(chars)
 }

def statistical_validation_23k():
 """Statistische Validierung auf 23k Dataset."""
 print("=" * 80)
 print("STATISTISCHE VALIDIERUNG (23K DATASET)")
 print("=" * 80)
 print()
 
 # Load alle Identities mit Status
 all_entries = load_all_with_status()
 known_entries = [e for e in all_entries if e.get("layer3_onchain") is not None]
 
 print(f"Total Identities: {len(all_entries)}")
 print(f"With known status: {len(known_entries)}")
 print()
 
 if not known_entries:
 print("❌ No identities with known status found!")
 return
 
 # Teste Position 30
 print("## Position 30 Statistical Test")
 pos30_result = test_position_significance(30, known_entries)
 if "error" in pos30_result:
 if pos30_result.get("all_onchain"):
 print(f" ⚠️ Alle Identities sind on-chain (100%)")
 print(f" Sample Size: {pos30_result.get('sample_size', 0)}")
 print(f" Kein statistischer Test möglich (keine Off-Chain Kategorie)")
 else:
 print(f" ❌ Error: {pos30_result.get('error', 'Unknown')}")
 else:
 print(f" Chi-square: {pos30_result['chi2']:.4f}")
 print(f" p-value: {pos30_result['p_value']:.6f}")
 print(f" Significant: {'✅ YES' if pos30_result['significant'] else '❌ NO'}")
 print(f" Cramér's V: {pos30_result['cramers_v']:.4f} ({pos30_result['effect_size']})")
 print(f" Accuracy: {pos30_result['accuracy']:.1f}%")
 print(f" Sample Size: {pos30_result['sample_size']}")
 print(f" Unique Chars: {pos30_result['unique_chars']}")
 print()
 
 # Teste Position 4
 print("## Position 4 Statistical Test")
 pos4_result = test_position_significance(4, known_entries)
 if "error" in pos4_result:
 if pos4_result.get("all_onchain"):
 print(f" ⚠️ Alle Identities sind on-chain (100%)")
 print(f" Sample Size: {pos4_result.get('sample_size', 0)}")
 print(f" Kein statistischer Test möglich (keine Off-Chain Kategorie)")
 else:
 print(f" ❌ Error: {pos4_result.get('error', 'Unknown')}")
 else:
 print(f" Chi-square: {pos4_result['chi2']:.4f}")
 print(f" p-value: {pos4_result['p_value']:.6f}")
 print(f" Significant: {'✅ YES' if pos4_result['significant'] else '❌ NO'}")
 print(f" Cramér's V: {pos4_result['cramers_v']:.4f} ({pos4_result['effect_size']})")
 print(f" Accuracy: {pos4_result['accuracy']:.1f}%")
 print(f" Sample Size: {pos4_result['sample_size']}")
 print(f" Unique Chars: {pos4_result['unique_chars']}")
 print()
 
 # Baseline
 onchain_count = sum(1 for e in known_entries if e.get("layer3_onchain"))
 baseline = (onchain_count / len(known_entries) * 100) if known_entries else 0
 
 print(f"## Baseline")
 print(f" On-chain Rate: {baseline:.1f}%")
 if "error" not in pos30_result:
 print(f" Position 30 Improvement: {pos30_result.get('accuracy', 0) - baseline:.1f}%")
 if "error" not in pos4_result:
 print(f" Position 4 Improvement: {pos4_result.get('accuracy', 0) - baseline:.1f}%")
 print()
 
 # Report
 report_lines = [
 "# Statistical Validation (23K Dataset)",
 "",
 f"**Total Identities**: {len(all_entries)}",
 f"**With known status**: {len(known_entries)}",
 f"**Baseline (On-chain Rate)**: {baseline:.1f}%",
 "",
 "## Position 30",
 ""
 ]
 
 if "error" not in pos30_result:
 report_lines.extend([
 f"- **Chi-square**: {pos30_result['chi2']:.4f}",
 f"- **p-value**: {pos30_result['p_value']:.6f}",
 f"- **Significant**: {'✅ YES' if pos30_result['significant'] else '❌ NO'}",
 f"- **Cramér's V**: {pos30_result['cramers_v']:.4f} ({pos30_result['effect_size']})",
 f"- **Accuracy**: {pos30_result['accuracy']:.1f}%",
 f"- **Improvement over Baseline**: {pos30_result['accuracy'] - baseline:.1f}%",
 f"- **Sample Size**: {pos30_result['sample_size']}",
 f"- **Unique Chars**: {pos30_result['unique_chars']}",
 ])
 else:
 report_lines.append("- Error: No data")
 
 report_lines.extend([
 "",
 "## Position 4",
 ""
 ])
 
 if "error" not in pos4_result:
 report_lines.extend([
 f"- **Chi-square**: {pos4_result['chi2']:.4f}",
 f"- **p-value**: {pos4_result['p_value']:.6f}",
 f"- **Significant**: {'✅ YES' if pos4_result['significant'] else '❌ NO'}",
 f"- **Cramér's V**: {pos4_result['cramers_v']:.4f} ({pos4_result['effect_size']})",
 f"- **Accuracy**: {pos4_result['accuracy']:.1f}%",
 f"- **Improvement over Baseline**: {pos4_result['accuracy'] - baseline:.1f}%",
 f"- **Sample Size**: {pos4_result['sample_size']}",
 f"- **Unique Chars**: {pos4_result['unique_chars']}",
 ])
 else:
 report_lines.append("- Error: No data")
 
 report_file = REPORTS_DIR / "STATISTICAL_VALIDATION_23K.md"
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 statistical_validation_23k()

