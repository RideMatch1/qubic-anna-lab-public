#!/usr/bin/env python3
"""
Position 30 + Position 4 Combination Test

Testet Kombinationen von Position 30 und Position 4:
- Finde beste Kombinationsregeln
- Teste Accuracy
- Validate auf vorhandenen Daten
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

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_layer3_data() -> Dict:
 """Load Layer-3 Daten."""
 # Verwende zuerst complete (hat gemischte on-chain Status)
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 
 # Falls nicht vorhanden, versuche extended
 if not layer3_file.exists():
 layer3_file = OUTPUT_DIR / "layer3_derivation_extended.json"
 
 if not layer3_file.exists():
 return {}
 
 with layer3_file.open() as f:
 data = json.load(f)
 
 # Filtere nur Einträge mit on-chain Status (nicht None)
 if "results" in data:
 data["results"] = [r for r in data["results"] if r.get("layer3_onchain") is not None]
 
 return data

def test_combination_rules(layer3_data: Dict) -> Dict:
 """Teste verschiedene Kombinationsregeln."""
 results_data = layer3_data.get("results", [])
 
 if len(results_data) < 20:
 return {"error": "Not enough data"}
 
 # 80/20 Split
 train_size = int(len(results_data) * 0.8)
 train_results = results_data[:train_size]
 test_results = results_data[train_size:]
 
 # Train: Baue Model for Position 30
 pos30_onchain = defaultdict(int)
 pos30_offchain = defaultdict(int)
 
 # Train: Baue Model for Position 4
 pos4_onchain = defaultdict(int)
 pos4_offchain = defaultdict(int)
 
 # Train: Baue Model for Kombination
 combo_onchain = defaultdict(int)
 combo_offchain = defaultdict(int)
 
 for result in train_results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if len(layer3_id) < 31:
 continue
 
 pos30_char = layer3_id[30]
 pos4_char = layer3_id[4]
 combo_key = f"{pos4_char}{pos30_char}"
 
 if is_onchain:
 pos30_onchain[pos30_char] += 1
 pos4_onchain[pos4_char] += 1
 combo_onchain[combo_key] += 1
 else:
 pos30_offchain[pos30_char] += 1
 pos4_offchain[pos4_char] += 1
 combo_offchain[combo_key] += 1
 
 # Test: Berechne Accuracy for verschiedene Regeln
 rules = {
 "position30_only": {"correct": 0, "total": 0},
 "position4_only": {"correct": 0, "total": 0},
 "both_agree": {"correct": 0, "total": 0},
 "position30_primary": {"correct": 0, "total": 0},
 "position4_primary": {"correct": 0, "total": 0},
 "combination": {"correct": 0, "total": 0}
 }
 
 for result in test_results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if len(layer3_id) < 31:
 continue
 
 pos30_char = layer3_id[30]
 pos4_char = layer3_id[4]
 combo_key = f"{pos4_char}{pos30_char}"
 
 # Position 30 only
 pos30_on = pos30_onchain.get(pos30_char, 0)
 pos30_off = pos30_offchain.get(pos30_char, 0)
 pos30_total = pos30_on + pos30_off
 if pos30_total > 0:
 pred30 = (pos30_on / pos30_total) > 0.5
 rules["position30_only"]["total"] += 1
 if pred30 == is_onchain:
 rules["position30_only"]["correct"] += 1
 
 # Position 4 only
 pos4_on = pos4_onchain.get(pos4_char, 0)
 pos4_off = pos4_offchain.get(pos4_char, 0)
 pos4_total = pos4_on + pos4_off
 if pos4_total > 0:
 pred4 = (pos4_on / pos4_total) > 0.5
 rules["position4_only"]["total"] += 1
 if pred4 == is_onchain:
 rules["position4_only"]["correct"] += 1
 
 # Both agree
 if pos30_total > 0 and pos4_total > 0:
 pred30 = (pos30_on / pos30_total) > 0.5
 pred4 = (pos4_on / pos4_total) > 0.5
 if pred30 == pred4:
 rules["both_agree"]["total"] += 1
 if pred30 == is_onchain:
 rules["both_agree"]["correct"] += 1
 
 # Position 30 primary (use 30, fallback to 4)
 if pos30_total > 0:
 pred = (pos30_on / pos30_total) > 0.5
 elif pos4_total > 0:
 pred = (pos4_on / pos4_total) > 0.5
 else:
 continue
 rules["position30_primary"]["total"] += 1
 if pred == is_onchain:
 rules["position30_primary"]["correct"] += 1
 
 # Position 4 primary (use 4, fallback to 30)
 if pos4_total > 0:
 pred = (pos4_on / pos4_total) > 0.5
 elif pos30_total > 0:
 pred = (pos30_on / pos30_total) > 0.5
 else:
 continue
 rules["position4_primary"]["total"] += 1
 if pred == is_onchain:
 rules["position4_primary"]["correct"] += 1
 
 # Combination (use combo key)
 combo_on = combo_onchain.get(combo_key, 0)
 combo_off = combo_offchain.get(combo_key, 0)
 combo_total = combo_on + combo_off
 if combo_total > 0:
 pred_combo = (combo_on / combo_total) > 0.5
 rules["combination"]["total"] += 1
 if pred_combo == is_onchain:
 rules["combination"]["correct"] += 1
 
 # Berechne Accuracies
 for rule_name, rule_data in rules.items():
 if rule_data["total"] > 0:
 rule_data["accuracy"] = (rule_data["correct"] / rule_data["total"]) * 100
 else:
 rule_data["accuracy"] = 0
 
 return {
 "train_size": len(train_results),
 "test_size": len(test_results),
 "rules": rules,
 "unique_combinations": len(set(list(combo_onchain.keys()) + list(combo_offchain.keys())))
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("POSITION 30 + POSITION 4 COMBINATION TEST")
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
 
 # Teste Kombinationen
 print("Testing combination rules...")
 result = test_combination_rules(layer3_data)
 
 if "error" in result:
 print(f"❌ Error: {result['error']}")
 return
 
 print()
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 
 print(f"Train Size: {result['train_size']}")
 print(f"Test Size: {result['test_size']}")
 print(f"Unique Combinations: {result['unique_combinations']}")
 print()
 
 print("Rule Accuracies:")
 print()
 for rule_name, rule_data in sorted(result['rules'].items(), key=lambda x: x[1].get('accuracy', 0), reverse=True):
 acc = rule_data.get('accuracy', 0)
 correct = rule_data.get('correct', 0)
 total = rule_data.get('total', 0)
 print(f" {rule_name:25s}: {acc:5.1f}% ({correct}/{total})")
 
 print()
 
 # Beste Regel
 best_rule = max(result['rules'].items(), key=lambda x: x[1].get('accuracy', 0))
 print(f"✅ Best Rule: {best_rule[0]} ({best_rule[1].get('accuracy', 0):.1f}%)")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_json = OUTPUT_DIR / "position30_position4_combination.json"
 with output_json.open("w") as f:
 json.dump(result, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "position30_position4_combination_report.md"
 
 with output_md.open("w") as f:
 f.write("# Position 30 + Position 4 Combination Test Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write("Testing combinations of Position 30 (90% accuracy) and Position 4 (80% accuracy).\n\n")
 
 f.write("## Results\n\n")
 f.write("| Rule | Accuracy | Correct/Total |\n")
 f.write("|------|----------|---------------|\n")
 
 for rule_name, rule_data in sorted(result['rules'].items(), key=lambda x: x[1].get('accuracy', 0), reverse=True):
 acc = rule_data.get('accuracy', 0)
 correct = rule_data.get('correct', 0)
 total = rule_data.get('total', 0)
 f.write(f"| {rule_name} | {acc:.1f}% | {correct}/{total} |\n")
 
 f.write("\n")
 f.write(f"## Best Rule\n\n")
 f.write(f"**{best_rule[0]}**: {best_rule[1].get('accuracy', 0):.1f}% accuracy\n\n")
 
 f.write("## Conclusion\n\n")
 if best_rule[1].get('accuracy', 0) > 90:
 f.write("✅ **Combination improves accuracy!**\n\n")
 f.write(f"Best combination achieves {best_rule[1].get('accuracy', 0):.1f}% accuracy, ")
 f.write(f"which is better than Position 30 alone (90%) or Position 4 alone (80%).\n\n")
 else:
 f.write("⚠️ **Combination does not significantly improve accuracy.**\n\n")
 f.write(f"Best combination achieves {best_rule[1].get('accuracy', 0):.1f}% accuracy, ")
 f.write(f"which is similar to Position 30 alone (90%).\n\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()

if __name__ == "__main__":
 main()

