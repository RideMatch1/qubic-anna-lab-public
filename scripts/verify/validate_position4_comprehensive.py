#!/usr/bin/env python3
"""
Position 4 Comprehensive Validation

Umfassende Validierung von Position 4:
- Verwendet vorhandene Layer-3 Daten (schneller!)
- Vollständige statistische Tests
- Perfect Marker Analyse
- Cross-Validation
- Alle Positionen Vergleich
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict, Counter
import numpy as np
from scipy.stats import chi2_contingency

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_layer3_data() -> Dict:
 """Load vorhandene Layer-3 Daten."""
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 
 if not layer3_file.exists():
 raise FileNotFoundError(f"Layer-3 data not found: {layer3_file}")
 
 with layer3_file.open() as f:
 return json.load(f)

def analyze_position4_comprehensive(layer3_data: Dict) -> Dict:
 """Umfassende Position 4 Analyse."""
 results = layer3_data.get("results", [])
 
 print("=" * 80)
 print("POSITION 4 COMPREHENSIVE VALIDATION")
 print("=" * 80)
 print()
 print(f"Total Layer-3 identities: {len(results)}")
 print()
 
 # Position 4 Distribution
 pos4_onchain = Counter()
 pos4_offchain = Counter()
 
 # Alle Positionen (for Vergleich)
 all_positions_onchain = defaultdict(Counter)
 all_positions_offchain = defaultdict(Counter)
 
 # Daten sammeln
 for result in results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) < 60:
 continue
 
 # Position 4
 pos4_char = layer3_id[4]
 if is_onchain:
 pos4_onchain[pos4_char] += 1
 else:
 pos4_offchain[pos4_char] += 1
 
 # Alle Positionen (0-59)
 for pos in range(60):
 char = layer3_id[pos]
 if is_onchain:
 all_positions_onchain[pos][char] += 1
 else:
 all_positions_offchain[pos][char] += 1
 
 # Position 4 Accuracy berechnen
 pos4_accuracy = calculate_position4_accuracy(pos4_onchain, pos4_offchain, results)
 
 # Alle Positionen Accuracy
 all_positions_accuracy = calculate_all_positions_accuracy(
 all_positions_onchain, all_positions_offchain, results
 )
 
 # Perfect Marker Analyse
 perfect_markers = analyze_perfect_markers_comprehensive(
 pos4_onchain, pos4_offchain
 )
 
 # Statistische Tests
 statistical_tests = run_statistical_tests(pos4_onchain, pos4_offchain, results)
 
 # Cross-Validation
 cross_validation = run_cross_validation(results)
 
 return {
 "total_identities": len(results),
 "onchain_count": sum(1 for r in results if r.get("layer3_onchain", False)),
 "offchain_count": sum(1 for r in results if not r.get("layer3_onchain", False)),
 "position4_accuracy": pos4_accuracy,
 "all_positions_accuracy": all_positions_accuracy,
 "perfect_markers": perfect_markers,
 "statistical_tests": statistical_tests,
 "cross_validation": cross_validation,
 "position4_distribution": {
 "onchain": dict(pos4_onchain),
 "offchain": dict(pos4_offchain)
 }
 }

def calculate_position4_accuracy(
 pos4_onchain: Counter, pos4_offchain: Counter, results: List[Dict]
) -> Dict:
 """Berechne Position 4 Accuracy."""
 # Train/Test Split (80/20)
 train_size = int(len(results) * 0.8)
 train_results = results[:train_size]
 test_results = results[train_size:]
 
 # Train Model
 train_pos4_onchain = Counter()
 train_pos4_offchain = Counter()
 
 for result in train_results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 4:
 continue
 
 char = layer3_id[4]
 if is_onchain:
 train_pos4_onchain[char] += 1
 else:
 train_pos4_offchain[char] += 1
 
 # Test Model
 correct = 0
 total_tested = 0
 
 for result in test_results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 4:
 continue
 
 char = layer3_id[4]
 on_count = train_pos4_onchain.get(char, 0)
 off_count = train_pos4_offchain.get(char, 0)
 total_char = on_count + off_count
 
 if total_char > 0:
 prob_onchain = (on_count / total_char) * 100
 predicted_onchain = prob_onchain > 50
 
 total_tested += 1
 if predicted_onchain == is_onchain:
 correct += 1
 
 accuracy = (correct / total_tested * 100) if total_tested > 0 else 0
 
 # Baseline
 baseline_onchain = sum(1 for r in train_results if r.get("layer3_onchain", False))
 baseline_offchain = len(train_results) - baseline_onchain
 baseline_accuracy = (max(baseline_onchain, baseline_offchain) / len(train_results)) * 100
 
 return {
 "accuracy": accuracy,
 "correct": correct,
 "total_tested": total_tested,
 "train_size": train_size,
 "test_size": len(test_results),
 "baseline_accuracy": baseline_accuracy,
 "improvement": accuracy - baseline_accuracy,
 "improvement_pct": ((accuracy - baseline_accuracy) / baseline_accuracy * 100) if baseline_accuracy > 0 else 0
 }

def calculate_all_positions_accuracy(
 all_positions_onchain: Dict[int, Counter],
 all_positions_offchain: Dict[int, Counter],
 results: List[Dict]
) -> Dict[int, float]:
 """Berechne Accuracy for alle Positionen."""
 train_size = int(len(results) * 0.8)
 train_results = results[:train_size]
 test_results = results[train_size:]
 
 # Train Models for alle Positionen
 train_positions_onchain = defaultdict(Counter)
 train_positions_offchain = defaultdict(Counter)
 
 for result in train_results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) < 60:
 continue
 
 for pos in range(60):
 char = layer3_id[pos]
 if is_onchain:
 train_positions_onchain[pos][char] += 1
 else:
 train_positions_offchain[pos][char] += 1
 
 # Test Models
 position_accuracies = {}
 
 for pos in range(60):
 correct = 0
 total_tested = 0
 
 for result in test_results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= pos:
 continue
 
 char = layer3_id[pos]
 on_count = train_positions_onchain[pos].get(char, 0)
 off_count = train_positions_offchain[pos].get(char, 0)
 total_char = on_count + off_count
 
 if total_char > 0:
 prob_onchain = (on_count / total_char) * 100
 predicted_onchain = prob_onchain > 50
 
 total_tested += 1
 if predicted_onchain == is_onchain:
 correct += 1
 
 accuracy = (correct / total_tested * 100) if total_tested > 0 else 0
 position_accuracies[pos] = accuracy
 
 return position_accuracies

def analyze_perfect_markers_comprehensive(
 pos4_onchain: Counter, pos4_offchain: Counter
) -> Dict:
 """Umfassende Perfect Marker Analyse."""
 perfect_onchain = ['Q', 'Z', 'F']
 perfect_offchain = ['U', 'J', 'G', 'H', 'I', 'M', 'O', 'S', 'W']
 
 marker_analysis = {}
 
 for char in perfect_onchain + perfect_offchain:
 on_count = pos4_onchain.get(char, 0)
 off_count = pos4_offchain.get(char, 0)
 total_count = on_count + off_count
 onchain_rate = (on_count / total_count * 100) if total_count > 0 else 0
 
 marker_analysis[char] = {
 "count": total_count,
 "onchain_count": on_count,
 "offchain_count": off_count,
 "onchain_rate": onchain_rate,
 "reliable": total_count >= 10,
 "still_perfect": (
 (char in perfect_onchain and onchain_rate == 100.0) or
 (char in perfect_offchain and onchain_rate == 0.0)
 )
 }
 
 return marker_analysis

def run_statistical_tests(
 pos4_onchain: Counter, pos4_offchain: Counter, results: List[Dict]
) -> Dict:
 """Führe statistische Tests durch."""
 # Chi-Square Test
 # Baue Contingency Table
 all_chars = set(pos4_onchain.keys()) | set(pos4_offchain.keys())
 
 contingency = []
 onchain_row = []
 offchain_row = []
 
 for char in sorted(all_chars):
 onchain_row.append(pos4_onchain.get(char, 0))
 offchain_row.append(pos4_offchain.get(char, 0))
 
 contingency = [onchain_row, offchain_row]
 
 # Entferne Spalten mit nur Nullen
 filtered_contingency = []
 for row in contingency:
 filtered_row = [row[i] for i in range(len(row)) 
 if sum([r[i] for r in contingency]) > 0]
 if filtered_row:
 filtered_contingency.append(filtered_row)
 
 if len(filtered_contingency) >= 2 and len(filtered_contingency[0]) > 0:
 chi2, p_value, dof, expected = chi2_contingency(filtered_contingency)
 
 # Cramér's V
 n = sum(sum(row) for row in filtered_contingency)
 min_dim = min(len(filtered_contingency), len(filtered_contingency[0]))
 cramers_v = np.sqrt(chi2 / (n * (min_dim - 1))) if n > 0 and min_dim > 1 else 0
 
 effect_size = "large" if cramers_v > 0.5 else "medium" if cramers_v > 0.3 else "small"
 else:
 chi2 = 0
 p_value = 1.0
 dof = 0
 cramers_v = 0
 effect_size = "none"
 
 return {
 "chi2": float(chi2),
 "p_value": float(p_value),
 "dof": int(dof),
 "significant": bool(p_value < 0.05),
 "cramers_v": float(cramers_v),
 "effect_size": effect_size
 }

def run_cross_validation(results: List[Dict], n_folds: int = 5) -> Dict:
 """Führe Cross-Validation durch."""
 fold_size = len(results) // n_folds
 accuracies = []
 
 for fold in range(n_folds):
 # Split data
 test_start = fold * fold_size
 test_end = test_start + fold_size if fold < n_folds - 1 else len(results)
 
 test_results = results[test_start:test_end]
 train_results = results[:test_start] + results[test_end:]
 
 # Train Model
 train_pos4_onchain = Counter()
 train_pos4_offchain = Counter()
 
 for result in train_results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 4:
 continue
 
 char = layer3_id[4]
 if is_onchain:
 train_pos4_onchain[char] += 1
 else:
 train_pos4_offchain[char] += 1
 
 # Test Model
 correct = 0
 total_tested = 0
 
 for result in test_results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 4:
 continue
 
 char = layer3_id[4]
 on_count = train_pos4_onchain.get(char, 0)
 off_count = train_pos4_offchain.get(char, 0)
 total_char = on_count + off_count
 
 if total_char > 0:
 prob_onchain = (on_count / total_char) * 100
 predicted_onchain = prob_onchain > 50
 
 total_tested += 1
 if predicted_onchain == is_onchain:
 correct += 1
 
 accuracy = (correct / total_tested * 100) if total_tested > 0 else 0
 accuracies.append(accuracy)
 
 return {
 "n_folds": n_folds,
 "accuracies": [float(a) for a in accuracies],
 "mean": float(np.mean(accuracies)),
 "std": float(np.std(accuracies)),
 "min": float(np.min(accuracies)),
 "max": float(np.max(accuracies)),
 "stable": bool(np.std(accuracies) < 5.0)
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("POSITION 4 COMPREHENSIVE VALIDATION")
 print("=" * 80)
 print()
 
 # Load Layer-3 Daten
 print("Loading Layer-3 data...")
 layer3_data = load_layer3_data()
 print(f"✅ Loaded {len(layer3_data.get('results', []))} Layer-3 identities")
 print()
 
 # Führe umfassende Analyse durch
 print("Running comprehensive analysis...")
 print()
 results = analyze_position4_comprehensive(layer3_data)
 
 # Ausgabe
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 
 print(f"Total identities: {results['total_identities']}")
 print(f"On-chain: {results['onchain_count']} ({results['onchain_count']/results['total_identities']*100:.1f}%)")
 print(f"Off-chain: {results['offchain_count']} ({results['offchain_count']/results['total_identities']*100:.1f}%)")
 print()
 
 print("Position 4 Accuracy:")
 print(f" Accuracy: {results['position4_accuracy']['accuracy']:.1f}%")
 print(f" Correct: {results['position4_accuracy']['correct']}/{results['position4_accuracy']['total_tested']}")
 print(f" Baseline: {results['position4_accuracy']['baseline_accuracy']:.1f}%")
 print(f" Improvement: {results['position4_accuracy']['improvement']:.1f}% ({results['position4_accuracy']['improvement_pct']:.1f}% relative)")
 print()
 
 print("Statistical Tests:")
 stats = results['statistical_tests']
 print(f" Chi-square: {stats['chi2']:.4f}")
 print(f" P-value: {stats['p_value']:.6f}")
 print(f" Significant: {'✅ YES' if stats['significant'] else '❌ NO'}")
 print(f" Cramér's V: {stats['cramers_v']:.4f} ({stats['effect_size']} effect)")
 print()
 
 print("Cross-Validation (5-fold):")
 cv = results['cross_validation']
 print(f" Mean accuracy: {cv['mean']:.1f}%")
 print(f" Std deviation: {cv['std']:.1f}%")
 print(f" Range: {cv['min']:.1f}% - {cv['max']:.1f}%")
 print(f" Stable: {'✅ YES' if cv['stable'] else '⚠️ NO'}")
 print()
 
 # Top 10 Positionen
 print("Top 10 Positions by Accuracy:")
 sorted_positions = sorted(
 results['all_positions_accuracy'].items(),
 key=lambda x: x[1],
 reverse=True
 )
 for pos, acc in sorted_positions[:10]:
 marker = "⭐" if pos == 4 else " "
 print(f" {marker} Position {pos}: {acc:.1f}%")
 print()
 
 # Perfect Markers
 print("Perfect Marker Analysis:")
 print()
 print("On-Chain Perfect Markers:")
 for char in ['Q', 'Z', 'F']:
 data = results['perfect_markers'][char]
 status = "✅ RELIABLE" if data["reliable"] else "⚠️ UNRELIABLE"
 perfect = "✅ PERFECT" if data["still_perfect"] else "❌ NOT PERFECT"
 print(f" '{char}': {data['onchain_count']}/{data['count']} = {data['onchain_rate']:.1f}% "
 f"({status}, {perfect})")
 print()
 print("Off-Chain Perfect Markers:")
 for char in ['U', 'J', 'G', 'H', 'I', 'M', 'O', 'S', 'W']:
 data = results['perfect_markers'][char]
 status = "✅ RELIABLE" if data["reliable"] else "⚠️ UNRELIABLE"
 perfect = "✅ PERFECT" if data["still_perfect"] else "❌ NOT PERFECT"
 print(f" '{char}': {data['onchain_count']}/{data['count']} = {data['onchain_rate']:.1f}% "
 f"({status}, {perfect})")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_json = OUTPUT_DIR / "position4_comprehensive_validation.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "position4_comprehensive_validation.md"
 
 with output_md.open("w") as f:
 f.write("# Position 4 Comprehensive Validation Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write(f"Comprehensive validation of Position 4 on {results['total_identities']} Layer-3 identities.\n\n")
 
 f.write("## Results\n\n")
 f.write(f"- **Total identities**: {results['total_identities']}\n")
 f.write(f"- **On-chain**: {results['onchain_count']} ({results['onchain_count']/results['total_identities']*100:.1f}%)\n")
 f.write(f"- **Off-chain**: {results['offchain_count']} ({results['offchain_count']/results['total_identities']*100:.1f}%)\n\n")
 
 f.write("## Position 4 Accuracy\n\n")
 acc = results['position4_accuracy']
 f.write(f"- **Accuracy**: {acc['accuracy']:.1f}%\n")
 f.write(f"- **Correct**: {acc['correct']}/{acc['total_tested']}\n")
 f.write(f"- **Baseline**: {acc['baseline_accuracy']:.1f}%\n")
 f.write(f"- **Improvement**: {acc['improvement']:.1f}% ({acc['improvement_pct']:.1f}% relative)\n\n")
 
 f.write("## Statistical Tests\n\n")
 stats = results['statistical_tests']
 f.write(f"- **Chi-square**: {stats['chi2']:.4f}\n")
 f.write(f"- **P-value**: {stats['p_value']:.6f}\n")
 f.write(f"- **Significant**: {'✅ YES' if stats['significant'] else '❌ NO'}\n")
 f.write(f"- **Cramér's V**: {stats['cramers_v']:.4f} ({stats['effect_size']} effect)\n\n")
 
 f.write("## Cross-Validation\n\n")
 cv = results['cross_validation']
 f.write(f"- **Mean accuracy**: {cv['mean']:.1f}%\n")
 f.write(f"- **Std deviation**: {cv['std']:.1f}%\n")
 f.write(f"- **Range**: {cv['min']:.1f}% - {cv['max']:.1f}%\n")
 f.write(f"- **Stable**: {'✅ YES' if cv['stable'] else '⚠️ NO'}\n\n")
 
 f.write("## Top 10 Positions\n\n")
 f.write("| Position | Accuracy |\n")
 f.write("|----------|----------|\n")
 for pos, acc in sorted_positions[:10]:
 marker = "⭐" if pos == 4 else ""
 f.write(f"| {pos} {marker} | {acc:.1f}% |\n")
 f.write("\n")
 
 f.write("## Perfect Marker Analysis\n\n")
 f.write("### On-Chain Perfect Markers\n\n")
 f.write("| Char | Count | On-chain | Off-chain | On-chain % | Reliable | Still Perfect |\n")
 f.write("|------|-------|----------|-----------|------------|----------|---------------|\n")
 for char in ['Q', 'Z', 'F']:
 data = results['perfect_markers'][char]
 reliable = "✅" if data["reliable"] else "⚠️"
 perfect = "✅" if data["still_perfect"] else "❌"
 f.write(f"| `{char}` | {data['count']} | {data['onchain_count']} | {data['offchain_count']} | "
 f"{data['onchain_rate']:.1f}% | {reliable} | {perfect} |\n")
 f.write("\n")
 
 f.write("### Off-Chain Perfect Markers\n\n")
 f.write("| Char | Count | On-chain | Off-chain | On-chain % | Reliable | Still Perfect |\n")
 f.write("|------|-------|----------|-----------|------------|----------|---------------|\n")
 for char in ['U', 'J', 'G', 'H', 'I', 'M', 'O', 'S', 'W']:
 data = results['perfect_markers'][char]
 reliable = "✅" if data["reliable"] else "⚠️"
 perfect = "✅" if data["still_perfect"] else "❌"
 f.write(f"| `{char}` | {data['count']} | {data['onchain_count']} | {data['offchain_count']} | "
 f"{data['onchain_rate']:.1f}% | {reliable} | {perfect} |\n")
 f.write("\n")
 
 f.write("## Conclusion\n\n")
 if results['position4_accuracy']['accuracy'] > 70 and stats['significant']:
 f.write("✅ **Position 4 is validated**\n\n")
 f.write("- Statistically significant\n")
 f.write("- High accuracy (>70%)\n")
 f.write("- Significant improvement over baseline\n")
 else:
 f.write("⚠️ **Position 4 needs more validation**\n\n")
 f.write("\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

