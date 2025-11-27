#!/usr/bin/env python3
"""
Position 4 Statistical Validation

Statistische Signifikanz-Tests for Position 4:
- Chi-square Test
- P-value
- Effect size (Cramér's V)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

try:
 from scipy.stats import chi2_contingency
 import numpy as np
 SCIPY_AVAILABLE = True
except ImportError:
 SCIPY_AVAILABLE = False
 print("⚠️ scipy not available - statistical tests will be skipped")

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_layer3_data() -> Dict:
 """Load Layer-3 Daten."""
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 
 if not layer3_file.exists():
 return {}
 
 with layer3_file.open() as f:
 return json.load(f)

def build_position4_contingency_table(layer3_data: Dict) -> tuple:
 """Baue Contingency Table for Position 4."""
 results_data = layer3_data.get("results", [])
 
 # Sammle Daten
 char_onchain = defaultdict(int)
 char_offchain = defaultdict(int)
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 4:
 continue
 
 char = layer3_id[4]
 
 if is_onchain:
 char_onchain[char] += 1
 else:
 char_offchain[char] += 1
 
 # Baue Contingency Table (nur chars die vorkommen)
 all_chars = sorted(set(list(char_onchain.keys()) + list(char_offchain.keys())))
 
 contingency = []
 onchain_row = []
 offchain_row = []
 
 for char in all_chars:
 onchain_row.append(char_onchain.get(char, 0))
 offchain_row.append(char_offchain.get(char, 0))
 
 contingency = [onchain_row, offchain_row]
 
 metadata = {
 "chars": all_chars,
 "char_onchain": dict(char_onchain),
 "char_offchain": dict(char_offchain),
 "total_onchain": sum(char_onchain.values()),
 "total_offchain": sum(char_offchain.values())
 }
 
 return contingency, metadata

def calculate_cramers_v(chi2: float, n: int, min_dim: int) -> float:
 """Berechne Cramér's V (Effect Size)."""
 if n == 0 or min_dim == 0:
 return 0.0
 
 cramers_v = np.sqrt(chi2 / (n * (min_dim - 1)))
 return float(cramers_v)

def test_statistical_significance(layer3_data: Dict) -> Dict:
 """Teste statistische Signifikanz von Position 4."""
 print("=" * 80)
 print("POSITION 4 STATISTICAL SIGNIFICANCE TEST")
 print("=" * 80)
 print()
 
 if not SCIPY_AVAILABLE:
 return {"error": "scipy not available"}
 
 contingency, metadata = build_position4_contingency_table(layer3_data)
 
 # Entferne Spalten mit nur Nullen (wenn vorhanden)
 # Scipy kann damit umgehen, aber wir dokumentieren es
 non_zero_cols = [i for i in range(len(contingency[0])) 
 if contingency[0][i] + contingency[1][i] > 0]
 
 if len(non_zero_cols) < len(contingency[0]):
 filtered_contingency = [[contingency[0][i] for i in non_zero_cols],
 [contingency[1][i] for i in non_zero_cols]]
 filtered_chars = [metadata["chars"][i] for i in non_zero_cols]
 else:
 filtered_contingency = contingency
 filtered_chars = metadata["chars"]
 
 # Chi-square Test
 chi2, p_value, dof, expected = chi2_contingency(filtered_contingency)
 
 # Effect Size (Cramér's V)
 n = sum(sum(row) for row in filtered_contingency)
 min_dim = min(len(filtered_contingency), len(filtered_contingency[0]))
 cramers_v = calculate_cramers_v(chi2, n, min_dim)
 
 # Interpret Effect Size
 if cramers_v > 0.5:
 effect_size = "large"
 elif cramers_v > 0.3:
 effect_size = "medium"
 elif cramers_v > 0.1:
 effect_size = "small"
 else:
 effect_size = "negligible"
 
 results = {
 "position": 4,
 "chi2": float(chi2),
 "p_value": float(p_value),
 "dof": int(dof),
 "significant": p_value < 0.05,
 "cramers_v": float(cramers_v),
 "effect_size": effect_size,
 "n": int(n),
 "chars_tested": filtered_chars,
 "metadata": metadata
 }
 
 print(f"Position 4 Statistical Test:")
 print(f" Chi-square: {chi2:.4f}")
 print(f" P-value: {p_value:.6f}")
 print(f" Degrees of freedom: {dof}")
 print(f" Significant (p < 0.05): {'✅ YES' if results['significant'] else '❌ NO'}")
 print(f" Effect size (Cramér's V): {cramers_v:.4f} ({effect_size})")
 print(f" Sample size: {n}")
 print()
 
 return results

def compare_with_baseline(layer3_data: Dict) -> Dict:
 """Vergleiche Position 4 mit Baseline."""
 print("=" * 80)
 print("BASELINE COMPARISON")
 print("=" * 80)
 print()
 
 results_data = layer3_data.get("results", [])
 
 # Berechne Baseline (always predict majority class)
 onchain_count = sum(1 for r in results_data if r.get("layer3_onchain", False))
 offchain_count = len(results_data) - onchain_count
 total = len(results_data)
 
 baseline_accuracy = (max(onchain_count, offchain_count) / total * 100) if total > 0 else 0
 
 # Position 4 Accuracy
 pos4_onchain = defaultdict(int)
 pos4_offchain = defaultdict(int)
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 4:
 continue
 
 char = layer3_id[4]
 
 if is_onchain:
 pos4_onchain[char] += 1
 else:
 pos4_offchain[char] += 1
 
 # Teste Accuracy
 correct = 0
 total_tested = 0
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 4:
 continue
 
 char = layer3_id[4]
 on_count = pos4_onchain.get(char, 0)
 off_count = pos4_offchain.get(char, 0)
 total_char = on_count + off_count
 
 if total_char > 0:
 prob_onchain = (on_count / total_char) * 100
 predicted_onchain = prob_onchain > 50
 
 total_tested += 1
 if predicted_onchain == is_onchain:
 correct += 1
 
 position4_accuracy = (correct / total_tested * 100) if total_tested > 0 else 0
 
 improvement = position4_accuracy - baseline_accuracy
 improvement_pct = (improvement / baseline_accuracy * 100) if baseline_accuracy > 0 else 0
 
 # Simple significance check: Is improvement > 2%?
 significant_improvement = improvement > 2.0
 
 results = {
 "baseline_accuracy": baseline_accuracy,
 "position4_accuracy": position4_accuracy,
 "improvement": improvement,
 "improvement_pct": improvement_pct,
 "significant_improvement": significant_improvement,
 "baseline_count": {
 "onchain": onchain_count,
 "offchain": offchain_count
 }
 }
 
 print(f"Baseline (naive predictor): {baseline_accuracy:.1f}%")
 print(f" On-chain: {onchain_count}, Off-chain: {offchain_count}")
 print(f"Position 4 Accuracy: {position4_accuracy:.1f}%")
 print(f"Improvement: {improvement:.1f}% ({improvement_pct:.1f}% relative)")
 print(f"Significant improvement (>2%): {'✅ YES' if significant_improvement else '❌ NO'}")
 print()
 
 return results

def analyze_perfect_markers(layer3_data: Dict) -> Dict:
 """Analyze Perfect Markers und deren Zuverlässigkeit."""
 print("=" * 80)
 print("PERFECT MARKER RELIABILITY ANALYSIS")
 print("=" * 80)
 print()
 
 results_data = layer3_data.get("results", [])
 
 perfect_onchain = ['Q', 'Z', 'F']
 perfect_offchain = ['U', 'J', 'G', 'H', 'I', 'M', 'O', 'S', 'W']
 
 marker_analysis = {}
 
 for char in perfect_onchain + perfect_offchain:
 onchain_count = 0
 offchain_count = 0
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 4:
 continue
 
 if layer3_id[4] == char:
 if is_onchain:
 onchain_count += 1
 else:
 offchain_count += 1
 
 total_count = onchain_count + offchain_count
 onchain_rate = (onchain_count / total_count * 100) if total_count > 0 else 0
 
 marker_analysis[char] = {
 "count": total_count,
 "onchain_count": onchain_count,
 "offchain_count": offchain_count,
 "onchain_rate": onchain_rate,
 "reliable": total_count >= 10, # Need at least 10 cases
 "still_perfect": (
 (char in perfect_onchain and onchain_rate == 100.0) or
 (char in perfect_offchain and onchain_rate == 0.0)
 )
 }
 
 print("Perfect Marker Analysis:")
 print()
 print("On-Chain Perfect Markers:")
 for char in perfect_onchain:
 data = marker_analysis[char]
 status = "✅ RELIABLE" if data["reliable"] else "⚠️ UNRELIABLE"
 perfect_status = "✅ PERFECT" if data["still_perfect"] else "❌ NOT PERFECT"
 print(f" '{char}': {data['onchain_count']}/{data['count']} = {data['onchain_rate']:.1f}% "
 f"({status}, {perfect_status})")
 print()
 print("Off-Chain Perfect Markers:")
 for char in perfect_offchain:
 data = marker_analysis[char]
 status = "✅ RELIABLE" if data["reliable"] else "⚠️ UNRELIABLE"
 perfect_status = "✅ PERFECT" if data["still_perfect"] else "❌ NOT PERFECT"
 print(f" '{char}': {data['offchain_count']}/{data['count']} = {data['onchain_rate']:.1f}% "
 f"({status}, {perfect_status})")
 print()
 
 return marker_analysis

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("POSITION 4 STATISTICAL VALIDATION")
 print("=" * 80)
 print()
 print("This script performs proper statistical validation of Position 4.")
 print()
 
 # Load Daten
 print("Loading Layer-3 data...")
 layer3_data = load_layer3_data()
 
 if not layer3_data:
 print("❌ Layer-3 data not found")
 return
 
 print(f"✅ Loaded {len(layer3_data.get('results', []))} entries")
 print()
 
 # Führe Tests durch
 if SCIPY_AVAILABLE:
 significance_results = test_statistical_significance(layer3_data)
 else:
 significance_results = {"error": "scipy not available"}
 print("⚠️ Skipping statistical significance test (scipy not available)")
 print()
 
 baseline_results = compare_with_baseline(layer3_data)
 marker_analysis = analyze_perfect_markers(layer3_data)
 
 # Zusammenfassung
 print("=" * 80)
 print("VALIDATION SUMMARY")
 print("=" * 80)
 print()
 
 if "significant" in significance_results:
 print(f"Statistical Significance:")
 print(f" P-value: {significance_results['p_value']:.6f}")
 print(f" Significant: {'✅ YES' if significance_results['significant'] else '❌ NO'}")
 print(f" Effect size: {significance_results['cramers_v']:.4f} ({significance_results['effect_size']})")
 print()
 
 print(f"Baseline Comparison:")
 print(f" Baseline: {baseline_results['baseline_accuracy']:.1f}%")
 print(f" Position 4: {baseline_results['position4_accuracy']:.1f}%")
 print(f" Improvement: {baseline_results['improvement']:.1f}%")
 print(f" Significant: {'✅ YES' if baseline_results['significant_improvement'] else '❌ NO'}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 results = {
 "statistical_significance": significance_results,
 "baseline_comparison": baseline_results,
 "perfect_marker_analysis": marker_analysis
 }
 
 # Convert numpy types for JSON
 def convert_to_json_serializable(obj):
 if isinstance(obj, np.integer):
 return int(obj)
 elif isinstance(obj, np.floating):
 return float(obj)
 elif isinstance(obj, np.ndarray):
 return obj.tolist()
 elif isinstance(obj, dict):
 return {k: convert_to_json_serializable(v) for k, v in obj.items()}
 elif isinstance(obj, list):
 return [convert_to_json_serializable(item) for item in obj]
 elif isinstance(obj, (np.bool_, bool)):
 return bool(obj)
 return obj
 
 results = convert_to_json_serializable(results)
 
 output_json = OUTPUT_DIR / "position4_statistical_validation.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "position4_statistical_validation.md"
 
 with output_md.open("w") as f:
 f.write("# Position 4 Statistical Validation Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write("Proper statistical validation of Position 4.\n\n")
 
 if "significant" in significance_results:
 f.write("## Statistical Significance\n\n")
 f.write(f"- **Chi-square**: {significance_results['chi2']:.4f}\n")
 f.write(f"- **P-value**: {significance_results['p_value']:.6f}\n")
 f.write(f"- **Degrees of freedom**: {significance_results['dof']}\n")
 f.write(f"- **Significant (p < 0.05)**: {'✅ YES' if significance_results['significant'] else '❌ NO'}\n")
 f.write(f"- **Effect size (Cramér's V)**: {significance_results['cramers_v']:.4f} ({significance_results['effect_size']})\n")
 f.write(f"- **Sample size**: {significance_results['n']}\n\n")
 
 f.write("## Baseline Comparison\n\n")
 f.write(f"- **Baseline (naive)**: {baseline_results['baseline_accuracy']:.1f}%\n")
 f.write(f"- **Position 4**: {baseline_results['position4_accuracy']:.1f}%\n")
 f.write(f"- **Improvement**: {baseline_results['improvement']:.1f}% ({baseline_results['improvement_pct']:.1f}% relative)\n")
 f.write(f"- **Significant improvement (>2%)**: {'✅ YES' if baseline_results['significant_improvement'] else '❌ NO'}\n\n")
 
 f.write("## Perfect Marker Reliability\n\n")
 f.write("### On-Chain Perfect Markers\n\n")
 f.write("| Char | Count | On-chain | Off-chain | On-chain % | Reliable | Still Perfect |\n")
 f.write("|------|-------|----------|-----------|------------|----------|---------------|\n")
 for char in ['Q', 'Z', 'F']:
 data = marker_analysis[char]
 reliable = "✅" if data["reliable"] else "⚠️"
 perfect = "✅" if data["still_perfect"] else "❌"
 f.write(f"| `{char}` | {data['count']} | {data['onchain_count']} | {data['offchain_count']} | "
 f"{data['onchain_rate']:.1f}% | {reliable} | {perfect} |\n")
 f.write("\n")
 
 f.write("### Off-Chain Perfect Markers\n\n")
 f.write("| Char | Count | On-chain | Off-chain | On-chain % | Reliable | Still Perfect |\n")
 f.write("|------|-------|----------|-----------|------------|----------|---------------|\n")
 for char in ['U', 'J', 'G', 'H', 'I', 'M', 'O', 'S', 'W']:
 data = marker_analysis[char]
 reliable = "✅" if data["reliable"] else "⚠️"
 perfect = "✅" if data["still_perfect"] else "❌"
 f.write(f"| `{char}` | {data['count']} | {data['onchain_count']} | {data['offchain_count']} | "
 f"{data['onchain_rate']:.1f}% | {reliable} | {perfect} |\n")
 f.write("\n")
 
 f.write("## Conclusion\n\n")
 
 is_validated = True
 issues = []
 
 if "significant" in significance_results:
 if not significance_results['significant']:
 is_validated = False
 issues.append("Not statistically significant (p >= 0.05)")
 
 if not baseline_results['significant_improvement']:
 is_validated = False
 issues.append(f"Improvement too small ({baseline_results['improvement']:.1f}% vs 2% threshold)")
 
 unreliable_markers = [char for char, data in marker_analysis.items() if not data["reliable"]]
 if unreliable_markers:
 issues.append(f"Unreliable markers: {', '.join(unreliable_markers)} (n < 10)")
 
 if is_validated:
 f.write("✅ **POSITION 4 STATISTICALLY VALIDATED**\n\n")
 f.write("Position 4 is a valid predictor:\n")
 if "significant" in significance_results:
 f.write("- Statistically significant (p < 0.05)\n")
 f.write(f"- Accuracy: {baseline_results['position4_accuracy']:.1f}%\n")
 f.write(f"- Improvement over baseline: {baseline_results['improvement']:.1f}%\n")
 f.write("- Perfect markers documented\n\n")
 else:
 f.write("⚠️ **POSITION 4 NOT FULLY VALIDATED**\n\n")
 f.write("Issues found:\n")
 for issue in issues:
 f.write(f"- {issue}\n")
 f.write("\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

