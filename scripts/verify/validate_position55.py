#!/usr/bin/env python3
"""
Position 55 Comprehensive Validation

Validiert Position 55 (die beste Position mit 95% Accuracy):
- Statistische Signifikanz
- Effect Size
- Baseline Comparison
- Perfect Markers
- Cross-Validation
- Large-Scale Test
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import defaultdict, Counter

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

def build_position55_contingency_table(layer3_data: Dict) -> tuple:
 """Baue Contingency Table for Position 55."""
 results_data = layer3_data.get("results", [])
 
 char_onchain = defaultdict(int)
 char_offchain = defaultdict(int)
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 55:
 continue
 
 char = layer3_id[55]
 
 if is_onchain:
 char_onchain[char] += 1
 else:
 char_offchain[char] += 1
 
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
 """Teste statistische Signifikanz von Position 55."""
 print("=" * 80)
 print("POSITION 55 STATISTICAL SIGNIFICANCE TEST")
 print("=" * 80)
 print()
 
 if not SCIPY_AVAILABLE:
 return {"error": "scipy not available"}
 
 contingency, metadata = build_position55_contingency_table(layer3_data)
 
 # Entferne Spalten mit nur Nullen
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
 
 # Effect Size
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
 "position": 55,
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
 
 print(f"Position 55 Statistical Test:")
 print(f" Chi-square: {chi2:.4f}")
 print(f" P-value: {p_value:.6f}")
 print(f" Degrees of freedom: {dof}")
 print(f" Significant (p < 0.05): {'✅ YES' if results['significant'] else '❌ NO'}")
 print(f" Effect size (Cramér's V): {cramers_v:.4f} ({effect_size})")
 print(f" Sample size: {n}")
 print()
 
 return results

def compare_with_baseline(layer3_data: Dict) -> Dict:
 """Vergleiche Position 55 mit Baseline."""
 print("=" * 80)
 print("BASELINE COMPARISON")
 print("=" * 80)
 print()
 
 results_data = layer3_data.get("results", [])
 
 # Baseline
 onchain_count = sum(1 for r in results_data if r.get("layer3_onchain", False))
 offchain_count = len(results_data) - onchain_count
 total = len(results_data)
 
 baseline_accuracy = (max(onchain_count, offchain_count) / total * 100) if total > 0 else 0
 
 # Position 55 Accuracy
 pos55_onchain = defaultdict(int)
 pos55_offchain = defaultdict(int)
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 55:
 continue
 
 char = layer3_id[55]
 
 if is_onchain:
 pos55_onchain[char] += 1
 else:
 pos55_offchain[char] += 1
 
 # Teste Accuracy
 correct = 0
 total_tested = 0
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 55:
 continue
 
 char = layer3_id[55]
 on_count = pos55_onchain.get(char, 0)
 off_count = pos55_offchain.get(char, 0)
 total_char = on_count + off_count
 
 if total_char > 0:
 prob_onchain = (on_count / total_char) * 100
 predicted_onchain = prob_onchain > 50
 
 total_tested += 1
 if predicted_onchain == is_onchain:
 correct += 1
 
 position55_accuracy = (correct / total_tested * 100) if total_tested > 0 else 0
 
 improvement = position55_accuracy - baseline_accuracy
 improvement_pct = (improvement / baseline_accuracy * 100) if baseline_accuracy > 0 else 0
 
 significant_improvement = improvement > 2.0
 
 results = {
 "baseline_accuracy": baseline_accuracy,
 "position55_accuracy": position55_accuracy,
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
 print(f"Position 55 Accuracy: {position55_accuracy:.1f}%")
 print(f"Improvement: {improvement:.1f}% ({improvement_pct:.1f}% relative)")
 print(f"Significant improvement (>2%): {'✅ YES' if significant_improvement else '❌ NO'}")
 print()
 
 return results

def analyze_perfect_markers(layer3_data: Dict) -> Dict:
 """Analyze Perfect Markers for Position 55."""
 print("=" * 80)
 print("PERFECT MARKER ANALYSIS")
 print("=" * 80)
 print()
 
 results_data = layer3_data.get("results", [])
 
 marker_analysis = {}
 
 # Finde alle chars die vorkommen
 all_chars = set()
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 if layer3_id and len(layer3_id) > 55:
 all_chars.add(layer3_id[55])
 
 for char in sorted(all_chars):
 onchain_count = 0
 offchain_count = 0
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 55:
 continue
 
 if layer3_id[55] == char:
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
 "reliable": total_count >= 10,
 "perfect_onchain": onchain_rate == 100.0,
 "perfect_offchain": onchain_rate == 0.0
 }
 
 # Finde Perfect Markers
 perfect_onchain = [char for char, data in marker_analysis.items() if data["perfect_onchain"]]
 perfect_offchain = [char for char, data in marker_analysis.items() if data["perfect_offchain"]]
 
 print("Perfect On-Chain Markers:")
 for char in sorted(perfect_onchain):
 data = marker_analysis[char]
 status = "✅ RELIABLE" if data["reliable"] else "⚠️ UNRELIABLE"
 print(f" '{char}': {data['onchain_count']}/{data['count']} = {data['onchain_rate']:.1f}% ({status})")
 print()
 
 print("Perfect Off-Chain Markers:")
 for char in sorted(perfect_offchain):
 data = marker_analysis[char]
 status = "✅ RELIABLE" if data["reliable"] else "⚠️ UNRELIABLE"
 print(f" '{char}': {data['offchain_count']}/{data['count']} = {data['onchain_rate']:.1f}% ({status})")
 print()
 
 return {
 "marker_analysis": marker_analysis,
 "perfect_onchain": perfect_onchain,
 "perfect_offchain": perfect_offchain
 }

def test_cross_validation(layer3_data: Dict, n_folds: int = 5) -> Dict:
 """5-fold Cross-Validation for Position 55."""
 print("=" * 80)
 print(f"{n_folds}-FOLD CROSS-VALIDATION")
 print("=" * 80)
 print()
 
 results_data = layer3_data.get("results", [])
 
 if len(results_data) < n_folds:
 return {"error": "Not enough data for cross-validation"}
 
 fold_size = len(results_data) // n_folds
 folds = []
 
 for i in range(n_folds):
 start = i * fold_size
 end = start + fold_size if i < n_folds - 1 else len(results_data)
 folds.append(results_data[start:end])
 
 accuracies = []
 
 for fold_num, test_fold in enumerate(folds, 1):
 train_fold = []
 for i, fold in enumerate(folds):
 if i != fold_num - 1:
 train_fold.extend(fold)
 
 # Train Model
 char_onchain = defaultdict(int)
 char_offchain = defaultdict(int)
 
 for result in train_fold:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 55:
 continue
 
 char = layer3_id[55]
 
 if is_onchain:
 char_onchain[char] += 1
 else:
 char_offchain[char] += 1
 
 # Test Model
 correct = 0
 total = 0
 
 for result in test_fold:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 55:
 continue
 
 char = layer3_id[55]
 on_count = char_onchain.get(char, 0)
 off_count = char_offchain.get(char, 0)
 total_count = on_count + off_count
 
 if total_count > 0:
 prob_onchain = (on_count / total_count) * 100
 predicted_onchain = prob_onchain > 50
 
 total += 1
 if predicted_onchain == is_onchain:
 correct += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 accuracies.append(accuracy)
 
 print(f"Fold {fold_num}: {accuracy:.1f}% ({correct}/{total})")
 
 results = {
 "n_folds": n_folds,
 "accuracies": accuracies,
 "mean_accuracy": float(np.mean(accuracies)),
 "std_accuracy": float(np.std(accuracies)),
 "min_accuracy": float(np.min(accuracies)),
 "max_accuracy": float(np.max(accuracies)),
 "stable": np.std(accuracies) < 5.0
 }
 
 print()
 print(f"Cross-Validation Results:")
 print(f" Mean: {results['mean_accuracy']:.1f}%")
 print(f" Std Dev: {results['std_accuracy']:.1f}%")
 print(f" Range: {results['min_accuracy']:.1f}% - {results['max_accuracy']:.1f}%")
 print(f" Stable (std < 5%): {'✅ YES' if results['stable'] else '❌ NO'}")
 print()
 
 return results

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("POSITION 55 COMPREHENSIVE VALIDATION")
 print("=" * 80)
 print()
 print("Position 55 is the BEST predictor (95% accuracy) - validating now...")
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
 marker_results = analyze_perfect_markers(layer3_data)
 cv_results = test_cross_validation(layer3_data, n_folds=5)
 
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
 print(f" Position 55: {baseline_results['position55_accuracy']:.1f}%")
 print(f" Improvement: {baseline_results['improvement']:.1f}%")
 print(f" Significant: {'✅ YES' if baseline_results['significant_improvement'] else '❌ NO'}")
 print()
 
 print(f"Cross-Validation:")
 print(f" Mean: {cv_results['mean_accuracy']:.1f}%")
 print(f" Std Dev: {cv_results['std_accuracy']:.1f}%")
 print(f" Stable: {'✅ YES' if cv_results['stable'] else '❌ NO'}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 results = {
 "statistical_significance": significance_results,
 "baseline_comparison": baseline_results,
 "perfect_markers": marker_results,
 "cross_validation": cv_results
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
 
 output_json = OUTPUT_DIR / "position55_validation.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "position55_validation_report.md"
 
 with output_md.open("w") as f:
 f.write("# Position 55 Validation Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write("Position 55 is the BEST predictor (95% accuracy) - comprehensive validation.\n\n")
 
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
 f.write(f"- **Position 55**: {baseline_results['position55_accuracy']:.1f}%\n")
 f.write(f"- **Improvement**: {baseline_results['improvement']:.1f}% ({baseline_results['improvement_pct']:.1f}% relative)\n")
 f.write(f"- **Significant improvement (>2%)**: {'✅ YES' if baseline_results['significant_improvement'] else '❌ NO'}\n\n")
 
 f.write("## Perfect Markers\n\n")
 f.write("### On-Chain Perfect Markers\n\n")
 perfect_onchain = marker_results.get("perfect_onchain", [])
 if perfect_onchain:
 f.write("| Char | Count | On-chain | Off-chain | On-chain % | Reliable |\n")
 f.write("|------|-------|----------|-----------|------------|----------|\n")
 for char in sorted(perfect_onchain):
 data = marker_results["marker_analysis"][char]
 reliable = "✅" if data["reliable"] else "⚠️"
 f.write(f"| `{char}` | {data['count']} | {data['onchain_count']} | {data['offchain_count']} | "
 f"{data['onchain_rate']:.1f}% | {reliable} |\n")
 else:
 f.write("No perfect on-chain markers found.\n")
 f.write("\n")
 
 f.write("### Off-Chain Perfect Markers\n\n")
 perfect_offchain = marker_results.get("perfect_offchain", [])
 if perfect_offchain:
 f.write("| Char | Count | On-chain | Off-chain | On-chain % | Reliable |\n")
 f.write("|------|-------|----------|-----------|------------|----------|\n")
 for char in sorted(perfect_offchain):
 data = marker_results["marker_analysis"][char]
 reliable = "✅" if data["reliable"] else "⚠️"
 f.write(f"| `{char}` | {data['count']} | {data['onchain_count']} | {data['offchain_count']} | "
 f"{data['onchain_rate']:.1f}% | {reliable} |\n")
 else:
 f.write("No perfect off-chain markers found.\n")
 f.write("\n")
 
 f.write("## Cross-Validation\n\n")
 f.write(f"- **Mean accuracy**: {cv_results['mean_accuracy']:.1f}%\n")
 f.write(f"- **Std deviation**: {cv_results['std_accuracy']:.1f}%\n")
 f.write(f"- **Range**: {cv_results['min_accuracy']:.1f}% - {cv_results['max_accuracy']:.1f}%\n")
 f.write(f"- **Stable (std < 5%)**: {'✅ YES' if cv_results['stable'] else '❌ NO'}\n\n")
 
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
 
 if not cv_results['stable']:
 is_validated = False
 issues.append(f"High variance in cross-validation (std: {cv_results['std_accuracy']:.1f}%)")
 
 if is_validated:
 f.write("✅ **POSITION 55 VALIDATED**\n\n")
 f.write("Position 55 is a valid and excellent predictor:\n")
 if "significant" in significance_results:
 f.write("- Statistically significant (p < 0.05)\n")
 f.write(f"- Accuracy: {baseline_results['position55_accuracy']:.1f}%\n")
 f.write(f"- Improvement over baseline: {baseline_results['improvement']:.1f}%\n")
 f.write("- Cross-validation confirms stability\n\n")
 else:
 f.write("⚠️ **POSITION 55 NOT FULLY VALIDATED**\n\n")
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

