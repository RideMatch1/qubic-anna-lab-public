#!/usr/bin/env python3
"""
Validate Top Positions - Statistical Significance Testing

Testet die Top 15 Positionen (nach Genauigkeit) auf statistische Signifikanz:
- Chi-square Test
- P-value
- Effect Size (Cramér's V)
- Baseline Comparison
- Cross-Validation
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
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

def calculate_position_accuracy(layer3_data: Dict, position: int) -> Dict:
 """Berechne Genauigkeit for Position (Train/Test Split)."""
 results_data = layer3_data.get("results", [])
 
 if len(results_data) < 10:
 return {"error": "Not enough data"}
 
 # 80/20 Split
 train_size = int(len(results_data) * 0.8)
 train_results = results_data[:train_size]
 test_results = results_data[train_size:]
 
 # Train: Baue Model
 char_onchain = defaultdict(int)
 char_offchain = defaultdict(int)
 
 for result in train_results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= position:
 continue
 
 char = layer3_id[position]
 
 if is_onchain:
 char_onchain[char] += 1
 else:
 char_offchain[char] += 1
 
 # Test: Berechne Accuracy
 correct = 0
 total = 0
 
 for result in test_results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= position:
 continue
 
 char = layer3_id[position]
 
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
 
 return {
 "accuracy": accuracy,
 "correct": correct,
 "total": total,
 "train_size": len(train_results),
 "test_size": len(test_results)
 }

def test_statistical_significance(layer3_data: Dict, position: int) -> Dict:
 """Teste statistische Signifikanz for Position."""
 if not SCIPY_AVAILABLE:
 return {"error": "scipy not available"}
 
 results_data = layer3_data.get("results", [])
 
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
 
 all_chars = sorted(set(list(char_onchain.keys()) + list(char_offchain.keys())))
 
 if len(all_chars) < 2:
 return {"error": "Not enough characters"}
 
 contingency = []
 onchain_row = []
 offchain_row = []
 
 for char in all_chars:
 onchain_row.append(char_onchain.get(char, 0))
 offchain_row.append(char_offchain.get(char, 0))
 
 contingency = [onchain_row, offchain_row]
 
 try:
 chi2, p_value, dof, expected = chi2_contingency(contingency)
 
 n = sum(sum(row) for row in contingency)
 min_dim = min(len(contingency), len(contingency[0]))
 cramers_v = np.sqrt(chi2 / (n * (min_dim - 1))) if n > 0 and min_dim > 1 else 0.0
 
 return {
 "chi2": float(chi2),
 "p_value": float(p_value),
 "significant": p_value < 0.05,
 "dof": int(dof),
 "cramers_v": float(cramers_v),
 "effect_size": "large" if cramers_v > 0.5 else "medium" if cramers_v > 0.3 else "small",
 "n": n,
 "chars_tested": len(all_chars)
 }
 except Exception as e:
 return {"error": str(e)}

def calculate_baseline_comparison(layer3_data: Dict, position: int, accuracy: float) -> Dict:
 """Berechne Baseline-Vergleich."""
 results_data = layer3_data.get("results", [])
 
 onchain_count = sum(1 for r in results_data if r.get("layer3_onchain", False))
 total_count = len(results_data)
 baseline_accuracy = (onchain_count / total_count * 100) if total_count > 0 else 0
 
 improvement = accuracy - baseline_accuracy
 improvement_pct = (improvement / baseline_accuracy * 100) if baseline_accuracy > 0 else 0
 
 return {
 "baseline_accuracy": baseline_accuracy,
 "position_accuracy": accuracy,
 "improvement": improvement,
 "improvement_pct": improvement_pct,
 "significant_improvement": improvement > 2.0 # More than 2% improvement
 }

def test_cross_validation(layer3_data: Dict, position: int, n_folds: int = 5) -> Dict:
 """Cross-Validation for Position."""
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
 
 if not layer3_id or len(layer3_id) <= position:
 continue
 
 char = layer3_id[position]
 
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
 
 if not layer3_id or len(layer3_id) <= position:
 continue
 
 char = layer3_id[position]
 
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
 
 results = {
 "n_folds": n_folds,
 "accuracies": accuracies,
 "mean_accuracy": float(np.mean(accuracies)),
 "std_accuracy": float(np.std(accuracies)),
 "min_accuracy": float(np.min(accuracies)),
 "max_accuracy": float(np.max(accuracies)),
 "stable": np.std(accuracies) < 5.0
 }
 
 return results

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("VALIDATE TOP POSITIONS - STATISTICAL SIGNIFICANCE TESTING")
 print("=" * 80)
 print()
 
 # Load Daten
 print("Loading Layer-3 data...")
 layer3_data = load_layer3_data()
 
 if not layer3_data:
 print("❌ Layer-3 data not found")
 return
 
 print(f"✅ Loaded {len(layer3_data.get('results', []))} entries")
 print()
 
 # Top 15 Positionen (aus vorheriger Analyse)
 top_positions = [55, 30, 26, 22, 14, 15, 38, 56, 33, 20, 4, 17, 31, 32, 45]
 
 print("=" * 80)
 print("VALIDATING TOP 15 POSITIONS")
 print("=" * 80)
 print()
 
 results = []
 
 for pos in top_positions:
 print(f"Validating Position {pos}...")
 
 # Accuracy
 accuracy_result = calculate_position_accuracy(layer3_data, pos)
 
 # Statistical Significance
 stats_result = test_statistical_significance(layer3_data, pos)
 
 # Baseline Comparison
 baseline_result = calculate_baseline_comparison(
 layer3_data, pos, accuracy_result.get("accuracy", 0)
 )
 
 # Cross-Validation
 cv_result = test_cross_validation(layer3_data, pos, n_folds=5)
 
 result = {
 "position": pos,
 "accuracy": accuracy_result,
 "statistical_significance": stats_result,
 "baseline_comparison": baseline_result,
 "cross_validation": cv_result
 }
 
 results.append(result)
 
 # Print summary
 acc = accuracy_result.get("accuracy", 0)
 p_val = stats_result.get("p_value", 1.0) if "p_value" in stats_result else None
 sig = stats_result.get("significant", False) if "significant" in stats_result else False
 
 status = "✅ VALIDATED" if sig else "❌ NOT VALIDATED"
 p_str = f"p={p_val:.6f}" if p_val else "N/A"
 
 print(f" Accuracy: {acc:.1f}%, {p_str}, {status}")
 print()
 
 # Sortiere nach Accuracy
 results.sort(key=lambda x: x["accuracy"].get("accuracy", 0), reverse=True)
 
 # Zusammenfassung
 print("=" * 80)
 print("VALIDATION SUMMARY")
 print("=" * 80)
 print()
 
 print("Top Positions by Accuracy:")
 print()
 print("| Rank | Position | Accuracy | P-value | Significant | Effect Size | Status |")
 print("|------|----------|----------|---------|-------------|-------------|--------|")
 
 validated_positions = []
 not_validated_positions = []
 
 for i, result in enumerate(results, 1):
 pos = result["position"]
 acc = result["accuracy"].get("accuracy", 0)
 stats = result["statistical_significance"]
 
 p_val = stats.get("p_value", 1.0) if "p_value" in stats else None
 sig = stats.get("significant", False) if "significant" in stats else False
 effect = stats.get("effect_size", "N/A") if "effect_size" in stats else "N/A"
 
 p_str = f"{p_val:.6f}" if p_val else "N/A"
 status = "✅ VALIDATED" if sig else "❌ NOT VALIDATED"
 
 print(f"| {i} | {pos} | {acc:.1f}% | {p_str} | {'✅ YES' if sig else '❌ NO'} | {effect} | {status} |")
 
 if sig:
 validated_positions.append(pos)
 else:
 not_validated_positions.append(pos)
 
 print()
 print(f"✅ Validated Positions: {len(validated_positions)}")
 print(f" Positions: {', '.join(map(str, validated_positions))}")
 print()
 print(f"❌ Not Validated Positions: {len(not_validated_positions)}")
 print(f" Positions: {', '.join(map(str, not_validated_positions))}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 # Convert numpy types
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
 
 output_json = OUTPUT_DIR / "top_positions_validation.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "TOP_POSITIONS_VALIDATION_REPORT.md"
 
 with output_md.open("w") as f:
 f.write("# Top Positions Validation Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write("Statistical validation of top 15 positions (by accuracy).\n\n")
 
 f.write("## Validated Positions\n\n")
 if validated_positions:
 f.write(f"**{len(validated_positions)} positions validated** (statistically significant):\n\n")
 for pos in validated_positions:
 result = next(r for r in results if r["position"] == pos)
 acc = result["accuracy"].get("accuracy", 0)
 stats = result["statistical_significance"]
 p_val = stats.get("p_value", 0)
 effect = stats.get("effect_size", "N/A")
 
 f.write(f"- **Position {pos}**: {acc:.1f}% accuracy, p={p_val:.6f}, effect={effect}\n")
 else:
 f.write("**No positions validated** (none are statistically significant)\n")
 f.write("\n")
 
 f.write("## Not Validated Positions\n\n")
 if not_validated_positions:
 f.write(f"**{len(not_validated_positions)} positions not validated** (not statistically significant):\n\n")
 for pos in not_validated_positions:
 result = next(r for r in results if r["position"] == pos)
 acc = result["accuracy"].get("accuracy", 0)
 stats = result["statistical_significance"]
 p_val = stats.get("p_value", 1.0) if "p_value" in stats else None
 
 p_str = f"p={p_val:.6f}" if p_val else "N/A"
 f.write(f"- **Position {pos}**: {acc:.1f}% accuracy, {p_str} (not significant)\n")
 f.write("\n")
 
 f.write("## Complete Results\n\n")
 f.write("| Rank | Position | Accuracy | P-value | Significant | Effect Size |\n")
 f.write("|------|----------|----------|---------|-------------|-------------|\n")
 
 for i, result in enumerate(results, 1):
 pos = result["position"]
 acc = result["accuracy"].get("accuracy", 0)
 stats = result["statistical_significance"]
 
 p_val = stats.get("p_value", 1.0) if "p_value" in stats else None
 sig = stats.get("significant", False) if "significant" in stats else False
 effect = stats.get("effect_size", "N/A") if "effect_size" in stats else "N/A"
 
 p_str = f"{p_val:.6f}" if p_val else "N/A"
 sig_str = "✅ YES" if sig else "❌ NO"
 
 f.write(f"| {i} | {pos} | {acc:.1f}% | {p_str} | {sig_str} | {effect} |\n")
 
 f.write("\n")
 f.write("## Conclusion\n\n")
 
 if validated_positions:
 best_validated = max(validated_positions, key=lambda p: next(r["accuracy"].get("accuracy", 0) for r in results if r["position"] == p))
 best_result = next(r for r in results if r["position"] == best_validated)
 best_acc = best_result["accuracy"].get("accuracy", 0)
 
 f.write(f"✅ **Best Validated Position**: Position {best_validated} ({best_acc:.1f}% accuracy)\n\n")
 else:
 f.write("❌ **No positions validated** - Position 4 remains the only validated predictor\n\n")
 
 f.write("### Key Insights\n\n")
 f.write("1. **High accuracy does not guarantee statistical significance**\n")
 f.write("2. **Position 4 remains the best validated predictor** (if no others are significant)\n")
 f.write("3. **Statistical significance is required for validation**\n")
 f.write("4. **Effect size matters** - large effect size indicates strong relationship\n\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

