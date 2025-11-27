#!/usr/bin/env python3
"""
Critical Validation of Live RPC Results

Prüft die Ergebnisse kritisch:
- Baseline-Vergleich (immer on-chain vorhersagen)
- Daten-Balance (on-chain vs off-chain)
- Echte Genauigkeit vs Baseline
"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def analyze_results_critical():
 """Analyze Ergebnisse kritisch."""
 results_file = OUTPUT_DIR / "position30_position4_combination_live_rpc.json"
 
 if not results_file.exists():
 print("❌ Results file not found")
 return
 
 with results_file.open() as f:
 data = json.load(f)
 
 total = data.get("total_processed", 0)
 onchain = data.get("onchain_count", 0)
 offchain = data.get("offchain_count", 0)
 onchain_rate = data.get("onchain_rate", 0)
 rules = data.get("rules", {})
 
 print("=" * 80)
 print("CRITICAL VALIDATION OF LIVE RPC RESULTS")
 print("=" * 80)
 print()
 
 print("📊 Data Distribution:")
 print(f" Total: {total}")
 print(f" On-chain: {onchain} ({onchain_rate:.1f}%)")
 print(f" Off-chain: {offchain} ({100-onchain_rate:.1f}%)")
 print()
 
 # Baseline: Immer on-chain vorhersagen
 baseline_accuracy = onchain_rate
 
 print("⚠️ CRITICAL ISSUE: Unbalanced Data!")
 print(f" Baseline (always predict on-chain): {baseline_accuracy:.1f}%")
 print(f" This means: Simply predicting 'on-chain' for everything")
 print(f" would achieve {baseline_accuracy:.1f}% accuracy!")
 print()
 
 # Train/Test Split
 train_size = data.get("train_size", 0)
 test_size = data.get("test_size", 0)
 
 # Berechne Test-Set Distribution
 # Annahme: Train/Test Split ist zufällig, also ähnliche Verteilung
 test_onchain_expected = int(test_size * onchain_rate / 100)
 test_offchain_expected = test_size - test_onchain_expected
 
 print("📈 Test Set Analysis:")
 print(f" Test Size: {test_size}")
 print(f" Expected On-chain: ~{test_onchain_expected} ({onchain_rate:.1f}%)")
 print(f" Expected Off-chain: ~{test_offchain_expected} ({100-onchain_rate:.1f}%)")
 print()
 
 # Analyze Rules
 print("🔍 Rule Analysis:")
 print()
 
 for rule_name, rule_data in sorted(rules.items(), key=lambda x: x[1].get('accuracy', 0), reverse=True):
 accuracy = rule_data.get('accuracy', 0)
 correct = rule_data.get('correct', 0)
 total_test = rule_data.get('total', 0)
 
 improvement = accuracy - baseline_accuracy
 
 print(f" {rule_name:25s}: {accuracy:5.1f}% ({correct}/{total_test})")
 print(f" Improvement over baseline: {improvement:+.1f}%")
 
 if improvement < 1.0:
 print(f" ⚠️ WARNING: Less than 1% improvement over baseline!")
 print(f" This is likely not significant.")
 elif improvement < 5.0:
 print(f" ⚠️ CAUTION: Only {improvement:.1f}% improvement")
 print(f" Needs statistical validation.")
 else:
 print(f" ✅ Good improvement: {improvement:.1f}%")
 print()
 
 # Kritische Bewertung
 print("=" * 80)
 print("CRITICAL ASSESSMENT")
 print("=" * 80)
 print()
 
 best_rule = max(rules.items(), key=lambda x: x[1].get('accuracy', 0))
 best_accuracy = best_rule[1].get('accuracy', 0)
 best_improvement = best_accuracy - baseline_accuracy
 
 print(f"Best Rule: {best_rule[0]}")
 print(f" Accuracy: {best_accuracy:.1f}%")
 print(f" Baseline: {baseline_accuracy:.1f}%")
 print(f" Improvement: {best_improvement:+.1f}%")
 print()
 
 if offchain < 10:
 print("❌ CRITICAL PROBLEM:")
 print(f" Only {offchain} off-chain identities in entire dataset!")
 print(f" This is too few for reliable validation.")
 print(f" Need more off-chain identities for proper testing.")
 print()
 
 if best_improvement < 1.0:
 print("❌ CRITICAL PROBLEM:")
 print(f" Best rule only improves by {best_improvement:.1f}% over baseline.")
 print(f" This is likely not statistically significant.")
 print(f" The high accuracy is mostly due to data imbalance.")
 print()
 elif best_improvement < 5.0:
 print("⚠️ CAUTION:")
 print(f" Improvement of {best_improvement:.1f}% is modest.")
 print(f" Needs statistical validation (p-value, chi-square test).")
 print()
 else:
 print("✅ GOOD:")
 print(f" Improvement of {best_improvement:.1f}% is substantial.")
 print(f" Still needs statistical validation, but promising.")
 print()
 
 # Empfehlungen
 print("=" * 80)
 print("RECOMMENDATIONS")
 print("=" * 80)
 print()
 print("1. ⚠️ Data is highly unbalanced (99.4% on-chain)")
 print(" → Need more off-chain identities for proper validation")
 print()
 print("2. ⚠️ Baseline comparison is critical")
 print(" → Always compare against 'always predict on-chain' baseline")
 print()
 print("3. ✅ Statistical validation needed")
 print(" → Chi-square test, p-value, Cramér's V")
 print()
 print("4. ✅ Test on balanced dataset")
 print(" → Sample more off-chain identities")
 print(" → Or use stratified sampling")
 print()

if __name__ == "__main__":
 analyze_results_critical()

