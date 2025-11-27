#!/usr/bin/env python3
"""
Selection Mechanism Validation

Proper statistical validation of the Layer-3 selection mechanism:
- Statistical significance (chi-square, p-value)
- Large-scale test (all identities)
- Baseline comparison
- Cross-validation
- All positions tested
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
import numpy as np

try:
 from scipy.stats import chi2_contingency
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

def build_contingency_table(layer3_data: Dict, position: int = 27) -> Tuple[List[List[int]], Dict]:
 """Baue Contingency Table for statistischen Test."""
 results_data = layer3_data.get("results", [])
 
 # Sammle Daten
 char_onchain = defaultdict(int)
 char_offchain = defaultdict(int)
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= position:
 continue
 
 char = layer3_id[position]
 
 if is_onchain:
 char_onchain[char] += 1
 else:
 char_offchain[char] += 1
 
 # Baue Contingency Table
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

def test_statistical_significance(layer3_data: Dict, position: int = 27) -> Dict:
 """Teste statistische Signifikanz."""
 print("=" * 80)
 print("STATISTICAL SIGNIFICANCE TEST")
 print("=" * 80)
 print()
 
 if not SCIPY_AVAILABLE:
 return {"error": "scipy not available"}
 
 contingency, metadata = build_contingency_table(layer3_data, position)
 
 # Chi-square Test
 chi2, p_value, dof, expected = chi2_contingency(contingency)
 
 results = {
 "position": position,
 "chi2": float(chi2),
 "p_value": float(p_value),
 "dof": int(dof),
 "significant": p_value < 0.05,
 "metadata": metadata
 }
 
 print(f"Position {position} Statistical Test:")
 print(f" Chi-square: {chi2:.4f}")
 print(f" P-value: {p_value:.6f}")
 print(f" Degrees of freedom: {dof}")
 print(f" Significant (p < 0.05): {'✅ YES' if results['significant'] else '❌ NO'}")
 print()
 
 return results

def test_all_positions(layer3_data: Dict) -> Dict:
 """Teste alle Positionen (0-59)."""
 print("=" * 80)
 print("TEST ALL POSITIONS")
 print("=" * 80)
 print()
 
 results_data = layer3_data.get("results", [])
 
 position_accuracies = {}
 
 for pos in range(60):
 # Baue einfaches Prediction Model
 char_onchain = defaultdict(int)
 char_offchain = defaultdict(int)
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= pos:
 continue
 
 char = layer3_id[pos]
 
 if is_onchain:
 char_onchain[char] += 1
 else:
 char_offchain[char] += 1
 
 # Berechne Accuracy
 correct = 0
 total = 0
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= pos:
 continue
 
 char = layer3_id[pos]
 onchain_count = char_onchain.get(char, 0)
 offchain_count = char_offchain.get(char, 0)
 total_count = onchain_count + offchain_count
 
 if total_count > 0:
 prob_onchain = (onchain_count / total_count) * 100
 predicted_onchain = prob_onchain > 50
 
 total += 1
 if predicted_onchain == is_onchain:
 correct += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 position_accuracies[pos] = {
 "accuracy": accuracy,
 "correct": correct,
 "total": total
 }
 
 # Finde beste Position
 best_pos = max(position_accuracies.keys(), key=lambda x: position_accuracies[x]["accuracy"])
 
 print(f"Best position: {best_pos} (accuracy: {position_accuracies[best_pos]['accuracy']:.1f}%)")
 print()
 print("Top 10 positions by accuracy:")
 sorted_positions = sorted(position_accuracies.items(), key=lambda x: x[1]["accuracy"], reverse=True)
 for pos, data in sorted_positions[:10]:
 print(f" Position {pos}: {data['accuracy']:.1f}% ({data['correct']}/{data['total']})")
 print()
 
 return {
 "position_accuracies": position_accuracies,
 "best_position": best_pos,
 "best_accuracy": position_accuracies[best_pos]["accuracy"]
 }

def test_baseline_comparison(layer3_data: Dict) -> Dict:
 """Vergleiche mit Baseline (naive predictor)."""
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
 
 # Model Accuracy (Position 27)
 pos27_results = test_all_positions(layer3_data)
 model_accuracy = pos27_results["position_accuracies"].get(27, {}).get("accuracy", 0)
 
 improvement = model_accuracy - baseline_accuracy
 
 results = {
 "baseline_accuracy": baseline_accuracy,
 "model_accuracy": model_accuracy,
 "improvement": improvement,
 "improvement_pct": (improvement / baseline_accuracy * 100) if baseline_accuracy > 0 else 0,
 "significant_improvement": improvement > 1.0 # More than 1% improvement
 }
 
 print(f"Baseline (naive predictor): {baseline_accuracy:.1f}%")
 print(f"Model (Position 27): {model_accuracy:.1f}%")
 print(f"Improvement: {improvement:.1f}% ({results['improvement_pct']:.1f}% relative)")
 print(f"Significant improvement (>1%): {'✅ YES' if results['significant_improvement'] else '❌ NO'}")
 print()
 
 return results

def test_cross_validation(layer3_data: Dict, n_folds: int = 5) -> Dict:
 """5-fold Cross-Validation."""
 print("=" * 80)
 print(f"{n_folds}-FOLD CROSS-VALIDATION")
 print("=" * 80)
 print()
 
 results_data = layer3_data.get("results", [])
 
 if len(results_data) < n_folds:
 return {"error": "Not enough data for cross-validation"}
 
 # Split data
 fold_size = len(results_data) // n_folds
 folds = []
 
 for i in range(n_folds):
 start = i * fold_size
 end = start + fold_size if i < n_folds - 1 else len(results_data)
 folds.append(results_data[start:end])
 
 accuracies = []
 
 for fold_num, test_fold in enumerate(folds, 1):
 # Training set = all other folds
 train_fold = []
 for i, fold in enumerate(folds):
 if i != fold_num - 1:
 train_fold.extend(fold)
 
 # Train model on training set
 char_onchain = defaultdict(int)
 char_offchain = defaultdict(int)
 
 for result in train_fold:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 27:
 continue
 
 char = layer3_id[27]
 
 if is_onchain:
 char_onchain[char] += 1
 else:
 char_offchain[char] += 1
 
 # Test on test fold
 correct = 0
 total = 0
 
 for result in test_fold:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 27:
 continue
 
 char = layer3_id[27]
 onchain_count = char_onchain.get(char, 0)
 offchain_count = char_offchain.get(char, 0)
 total_count = onchain_count + offchain_count
 
 if total_count > 0:
 prob_onchain = (onchain_count / total_count) * 100
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
 "max_accuracy": float(np.max(accuracies))
 }
 
 print()
 print(f"Cross-Validation Results:")
 print(f" Mean: {results['mean_accuracy']:.1f}%")
 print(f" Std Dev: {results['std_accuracy']:.1f}%")
 print(f" Range: {results['min_accuracy']:.1f}% - {results['max_accuracy']:.1f}%")
 print()
 
 return results

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("SELECTION MECHANISM VALIDATION")
 print("=" * 80)
 print()
 print("This script performs PROPER statistical validation of the selection mechanism.")
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
 significance_results = test_statistical_significance(layer3_data, position=27)
 else:
 significance_results = {"error": "scipy not available"}
 print("⚠️ Skipping statistical significance test (scipy not available)")
 print()
 
 all_positions_results = test_all_positions(layer3_data)
 baseline_results = test_baseline_comparison(layer3_data)
 cv_results = test_cross_validation(layer3_data, n_folds=5)
 
 # Zusammenfassung
 print("=" * 80)
 print("VALIDATION SUMMARY")
 print("=" * 80)
 print()
 
 if "significant" in significance_results:
 print(f"Statistical Significance (Position 27):")
 print(f" P-value: {significance_results['p_value']:.6f}")
 print(f" Significant: {'✅ YES' if significance_results['significant'] else '❌ NO'}")
 print()
 
 print(f"Best Position: {all_positions_results['best_position']} ({all_positions_results['best_accuracy']:.1f}%)")
 print(f"Position 27 Accuracy: {all_positions_results['position_accuracies'][27]['accuracy']:.1f}%")
 print()
 
 print(f"Baseline Comparison:")
 print(f" Baseline: {baseline_results['baseline_accuracy']:.1f}%")
 print(f" Model: {baseline_results['model_accuracy']:.1f}%")
 print(f" Improvement: {baseline_results['improvement']:.1f}%")
 print(f" Significant: {'✅ YES' if baseline_results['significant_improvement'] else '❌ NO'}")
 print()
 
 print(f"Cross-Validation:")
 print(f" Mean: {cv_results['mean_accuracy']:.1f}%")
 print(f" Std Dev: {cv_results['std_accuracy']:.1f}%")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 # Convert numpy types to native Python types for JSON
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
 
 results = {
 "statistical_significance": significance_results,
 "all_positions": all_positions_results,
 "baseline_comparison": baseline_results,
 "cross_validation": cv_results
 }
 
 results = convert_to_json_serializable(results)
 
 output_json = OUTPUT_DIR / "selection_validation_results.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "selection_validation_report.md"
 
 with output_md.open("w") as f:
 f.write("# Selection Mechanism Validation Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write("Proper statistical validation of the Layer-3 selection mechanism.\n\n")
 
 if "significant" in significance_results:
 f.write("## Statistical Significance\n\n")
 f.write(f"- **Chi-square**: {significance_results['chi2']:.4f}\n")
 f.write(f"- **P-value**: {significance_results['p_value']:.6f}\n")
 f.write(f"- **Degrees of freedom**: {significance_results['dof']}\n")
 f.write(f"- **Significant (p < 0.05)**: {'✅ YES' if significance_results['significant'] else '❌ NO'}\n\n")
 
 f.write("## All Positions Test\n\n")
 f.write(f"- **Best position**: {all_positions_results['best_position']} ({all_positions_results['best_accuracy']:.1f}%)\n")
 f.write(f"- **Position 27 accuracy**: {all_positions_results['position_accuracies'][27]['accuracy']:.1f}%\n\n")
 
 f.write("**Top 10 positions by accuracy:**\n\n")
 f.write("| Position | Accuracy | Correct | Total |\n")
 f.write("|----------|----------|---------|-------|\n")
 sorted_positions = sorted(all_positions_results['position_accuracies'].items(), 
 key=lambda x: x[1]["accuracy"], reverse=True)
 for pos, data in sorted_positions[:10]:
 f.write(f"| {pos} | {data['accuracy']:.1f}% | {data['correct']} | {data['total']} |\n")
 f.write("\n")
 
 f.write("## Baseline Comparison\n\n")
 f.write(f"- **Baseline (naive)**: {baseline_results['baseline_accuracy']:.1f}%\n")
 f.write(f"- **Model (Position 27)**: {baseline_results['model_accuracy']:.1f}%\n")
 f.write(f"- **Improvement**: {baseline_results['improvement']:.1f}% ({baseline_results['improvement_pct']:.1f}% relative)\n")
 f.write(f"- **Significant improvement (>1%)**: {'✅ YES' if baseline_results['significant_improvement'] else '❌ NO'}\n\n")
 
 f.write("## Cross-Validation\n\n")
 f.write(f"- **Mean accuracy**: {cv_results['mean_accuracy']:.1f}%\n")
 f.write(f"- **Std deviation**: {cv_results['std_accuracy']:.1f}%\n")
 f.write(f"- **Range**: {cv_results['min_accuracy']:.1f}% - {cv_results['max_accuracy']:.1f}%\n\n")
 
 f.write("## Conclusion\n\n")
 
 # Determine validation status
 is_validated = True
 issues = []
 
 if "significant" in significance_results:
 if not significance_results['significant']:
 is_validated = False
 issues.append("Not statistically significant (p >= 0.05)")
 
 if not baseline_results['significant_improvement']:
 is_validated = False
 issues.append(f"Improvement too small ({baseline_results['improvement']:.1f}% vs 1% threshold)")
 
 if cv_results['std_accuracy'] > 10:
 is_validated = False
 issues.append(f"High variance in cross-validation (std: {cv_results['std_accuracy']:.1f}%)")
 
 if is_validated:
 f.write("✅ **SELECTION MECHANISM VALIDATED**\n\n")
 f.write("Position 27 is a valid predictor:\n")
 if "significant" in significance_results:
 f.write("- Statistically significant (p < 0.05)\n")
 f.write(f"- Accuracy: {all_positions_results['position_accuracies'][27]['accuracy']:.1f}%\n")
 f.write(f"- Improvement over baseline: {baseline_results['improvement']:.1f}%\n")
 f.write("- Cross-validation confirms stability\n\n")
 else:
 f.write("⚠️ **SELECTION MECHANISM NOT FULLY VALIDATED**\n\n")
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

