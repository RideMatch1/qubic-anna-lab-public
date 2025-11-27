#!/usr/bin/env python3
"""
Resolve All Contradictions - Comprehensive Analysis

Löst alle Widersprüche auf:
1. Position 55: 95% vs 66% - welche Methode ist korrekt?
2. Position 4: "Beste" vs "Nicht in Top 10" - Ranking verifizieren
3. Multi-Position Models: 100% vs unzuverlässig - Large-Scale Test
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

def calculate_position_accuracy_method1(layer3_data: Dict, position: int) -> Dict:
 """
 Methode 1: Train/Test Split (wie in comprehensive validation)
 - 80/20 Split
 - Train auf 80%, Test auf 20%
 - Berechne Accuracy auf Test-Set
 """
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
 "method": "train_test_split_80_20",
 "accuracy": accuracy,
 "correct": correct,
 "total": total,
 "train_size": len(train_results),
 "test_size": len(test_results)
 }

def calculate_position_accuracy_method2(layer3_data: Dict, position: int) -> Dict:
 """
 Methode 2: Statistical Validation (wie in validate_position55.py)
 - Verwende alle Daten
 - Berechne Accuracy basierend auf Mehrheitsklasse pro Charakter
 - Kein Train/Test Split
 """
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
 
 # Berechne Accuracy: Für jeden Charakter, verwende Mehrheitsklasse
 correct = 0
 total = 0
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= position:
 continue
 
 char = layer3_id[position]
 
 on_count = char_onchain.get(char, 0)
 off_count = char_offchain.get(char, 0)
 total_count = on_count + off_count
 
 if total_count > 0:
 predicted_onchain = on_count > off_count
 
 total += 1
 if predicted_onchain == is_onchain:
 correct += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 return {
 "method": "statistical_all_data",
 "accuracy": accuracy,
 "correct": correct,
 "total": total
 }

def test_all_positions_ranking(layer3_data: Dict) -> List[Dict]:
 """Teste alle Positionen (0-59) und ranke sie."""
 all_results = []
 
 for pos in range(60):
 # Methode 1: Train/Test Split
 result1 = calculate_position_accuracy_method1(layer3_data, pos)
 
 # Methode 2: Statistical (alle Daten)
 result2 = calculate_position_accuracy_method2(layer3_data, pos)
 
 all_results.append({
 "position": pos,
 "method1_train_test": result1,
 "method2_statistical": result2
 })
 
 # Sortiere nach Method 1 Accuracy
 all_results.sort(key=lambda x: x["method1_train_test"].get("accuracy", 0), reverse=True)
 
 return all_results

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
 "effect_size": "large" if cramers_v > 0.5 else "medium" if cramers_v > 0.3 else "small"
 }
 except Exception as e:
 return {"error": str(e)}

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("RESOLVE ALL CONTRADICTIONS - COMPREHENSIVE ANALYSIS")
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
 
 # 1. Teste Position 55 mit beiden Methoden
 print("=" * 80)
 print("1. POSITION 55 CONTRADICTION RESOLUTION")
 print("=" * 80)
 print()
 
 pos55_method1 = calculate_position_accuracy_method1(layer3_data, 55)
 pos55_method2 = calculate_position_accuracy_method2(layer3_data, 55)
 pos55_stats = test_statistical_significance(layer3_data, 55)
 
 print(f"Position 55 - Method 1 (Train/Test Split):")
 print(f" Accuracy: {pos55_method1.get('accuracy', 0):.1f}%")
 print(f" Correct: {pos55_method1.get('correct', 0)}/{pos55_method1.get('total', 0)}")
 print(f" Test size: {pos55_method1.get('test_size', 0)}")
 print()
 
 print(f"Position 55 - Method 2 (Statistical, All Data):")
 print(f" Accuracy: {pos55_method2.get('accuracy', 0):.1f}%")
 print(f" Correct: {pos55_method2.get('correct', 0)}/{pos55_method2.get('total', 0)}")
 print()
 
 if pos55_stats and "p_value" in pos55_stats:
 print(f"Position 55 - Statistical Significance:")
 print(f" P-value: {pos55_stats['p_value']:.6f}")
 print(f" Significant: {'✅ YES' if pos55_stats['significant'] else '❌ NO'}")
 print(f" Effect Size: {pos55_stats['cramers_v']:.4f} ({pos55_stats['effect_size']})")
 print()
 
 # 2. Teste Position 4 mit beiden Methoden
 print("=" * 80)
 print("2. POSITION 4 CONTRADICTION RESOLUTION")
 print("=" * 80)
 print()
 
 pos4_method1 = calculate_position_accuracy_method1(layer3_data, 4)
 pos4_method2 = calculate_position_accuracy_method2(layer3_data, 4)
 pos4_stats = test_statistical_significance(layer3_data, 4)
 
 print(f"Position 4 - Method 1 (Train/Test Split):")
 print(f" Accuracy: {pos4_method1.get('accuracy', 0):.1f}%")
 print(f" Correct: {pos4_method1.get('correct', 0)}/{pos4_method1.get('total', 0)}")
 print()
 
 print(f"Position 4 - Method 2 (Statistical, All Data):")
 print(f" Accuracy: {pos4_method2.get('accuracy', 0):.1f}%")
 print(f" Correct: {pos4_method2.get('correct', 0)}/{pos4_method2.get('total', 0)}")
 print()
 
 if pos4_stats and "p_value" in pos4_stats:
 print(f"Position 4 - Statistical Significance:")
 print(f" P-value: {pos4_stats['p_value']:.6f}")
 print(f" Significant: {'✅ YES' if pos4_stats['significant'] else '❌ NO'}")
 print(f" Effect Size: {pos4_stats['cramers_v']:.4f} ({pos4_stats['effect_size']})")
 print()
 
 # 3. Teste alle Positionen for Ranking
 print("=" * 80)
 print("3. ALL POSITIONS RANKING")
 print("=" * 80)
 print()
 
 print("Testing all 60 positions...")
 all_positions = test_all_positions_ranking(layer3_data)
 
 print("Top 15 Positions (by Method 1 - Train/Test Split):")
 for i, result in enumerate(all_positions[:15], 1):
 pos = result["position"]
 acc1 = result["method1_train_test"].get("accuracy", 0)
 acc2 = result["method2_statistical"].get("accuracy", 0)
 print(f" {i:2d}. Position {pos:2d}: {acc1:.1f}% (Method 1), {acc2:.1f}% (Method 2)")
 
 # Finde Position 4 und Position 55 im Ranking
 pos4_rank = next((i+1 for i, r in enumerate(all_positions) if r["position"] == 4), None)
 pos55_rank = next((i+1 for i, r in enumerate(all_positions) if r["position"] == 55), None)
 
 print()
 print(f"Position 4 Rank: {pos4_rank} out of 60")
 print(f"Position 55 Rank: {pos55_rank} out of 60")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 results = {
 "position55": {
 "method1": pos55_method1,
 "method2": pos55_method2,
 "statistical": pos55_stats
 },
 "position4": {
 "method1": pos4_method1,
 "method2": pos4_method2,
 "statistical": pos4_stats
 },
 "all_positions_ranking": [
 {
 "position": r["position"],
 "rank": i+1,
 "method1_accuracy": r["method1_train_test"].get("accuracy", 0),
 "method2_accuracy": r["method2_statistical"].get("accuracy", 0)
 }
 for i, r in enumerate(all_positions)
 ],
 "position4_rank": pos4_rank,
 "position55_rank": pos55_rank
 }
 
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
 
 output_json = OUTPUT_DIR / "contradictions_resolved.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "CONTRADICTIONS_RESOLVED_REPORT.md"
 
 with output_md.open("w") as f:
 f.write("# Contradictions Resolved - Final Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write("Comprehensive analysis resolving all contradictions.\n\n")
 
 f.write("## Position 55 Contradiction Resolution\n\n")
 f.write("### Method 1: Train/Test Split (80/20)\n\n")
 f.write(f"- **Accuracy**: {pos55_method1.get('accuracy', 0):.1f}%\n")
 f.write(f"- **Correct**: {pos55_method1.get('correct', 0)}/{pos55_method1.get('total', 0)}\n")
 f.write(f"- **Test size**: {pos55_method1.get('test_size', 0)}\n\n")
 
 f.write("### Method 2: Statistical (All Data)\n\n")
 f.write(f"- **Accuracy**: {pos55_method2.get('accuracy', 0):.1f}%\n")
 f.write(f"- **Correct**: {pos55_method2.get('correct', 0)}/{pos55_method2.get('total', 0)}\n\n")
 
 if pos55_stats and "p_value" in pos55_stats:
 f.write("### Statistical Significance\n\n")
 f.write(f"- **P-value**: {pos55_stats['p_value']:.6f}\n")
 f.write(f"- **Significant**: {'✅ YES' if pos55_stats['significant'] else '❌ NO'}\n")
 f.write(f"- **Effect Size**: {pos55_stats['cramers_v']:.4f} ({pos55_stats['effect_size']})\n\n")
 
 f.write("**Resolution**: ")
 if pos55_method1.get('accuracy', 0) > 80:
 f.write("Method 1 shows high accuracy, but Method 2 shows baseline. ")
 f.write("Statistical test determines significance.\n\n")
 
 f.write("## Position 4 Contradiction Resolution\n\n")
 f.write("### Method 1: Train/Test Split (80/20)\n\n")
 f.write(f"- **Accuracy**: {pos4_method1.get('accuracy', 0):.1f}%\n")
 f.write(f"- **Correct**: {pos4_method1.get('correct', 0)}/{pos4_method1.get('total', 0)}\n\n")
 
 f.write("### Method 2: Statistical (All Data)\n\n")
 f.write(f"- **Accuracy**: {pos4_method2.get('accuracy', 0):.1f}%\n")
 f.write(f"- **Correct**: {pos4_method2.get('correct', 0)}/{pos4_method2.get('total', 0)}\n\n")
 
 if pos4_stats and "p_value" in pos4_stats:
 f.write("### Statistical Significance\n\n")
 f.write(f"- **P-value**: {pos4_stats['p_value']:.6f}\n")
 f.write(f"- **Significant**: {'✅ YES' if pos4_stats['significant'] else '❌ NO'}\n")
 f.write(f"- **Effect Size**: {pos4_stats['cramers_v']:.4f} ({pos4_stats['effect_size']})\n\n")
 
 f.write(f"**Rank**: Position 4 is ranked **#{pos4_rank}** out of 60 positions\n\n")
 
 f.write("## All Positions Ranking\n\n")
 f.write("| Rank | Position | Method 1 Accuracy | Method 2 Accuracy |\n")
 f.write("|------|----------|-------------------|------------------|\n")
 
 for i, result in enumerate(all_positions[:20], 1):
 pos = result["position"]
 acc1 = result["method1_train_test"].get("accuracy", 0)
 acc2 = result["method2_statistical"].get("accuracy", 0)
 f.write(f"| {i} | {pos} | {acc1:.1f}% | {acc2:.1f}% |\n")
 
 f.write("\n")
 f.write("## Conclusion\n\n")
 f.write("### Position 55\n\n")
 if pos55_stats and pos55_stats.get("significant", False):
 f.write("✅ **VALIDATED**: Statistically significant predictor\n")
 else:
 f.write("❌ **NOT VALIDATED**: Not statistically significant\n")
 f.write(f"- Method 1 (Train/Test): {pos55_method1.get('accuracy', 0):.1f}%\n")
 f.write(f"- Method 2 (Statistical): {pos55_method2.get('accuracy', 0):.1f}%\n")
 f.write(f"- Rank: #{pos55_rank}\n\n")
 
 f.write("### Position 4\n\n")
 if pos4_stats and pos4_stats.get("significant", False):
 f.write("✅ **VALIDATED**: Statistically significant predictor\n")
 else:
 f.write("❌ **NOT VALIDATED**: Not statistically significant\n")
 f.write(f"- Method 1 (Train/Test): {pos4_method1.get('accuracy', 0):.1f}%\n")
 f.write(f"- Method 2 (Statistical): {pos4_method2.get('accuracy', 0):.1f}%\n")
 f.write(f"- Rank: #{pos4_rank}\n\n")
 
 f.write("### Key Insights\n\n")
 f.write("1. **Method 1 (Train/Test Split)** is more reliable for accuracy estimation\n")
 f.write("2. **Method 2 (Statistical)** can show overfitting if accuracy is too high\n")
 f.write("3. **Statistical significance** is the key validator\n")
 f.write("4. **Ranking** shows relative performance, not absolute validation\n\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

