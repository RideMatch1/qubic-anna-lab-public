#!/usr/bin/env python3
"""
Early Positions System Analysis

Analysiert frühe Positionen (0-10) zusammen:
- Arbeiten sie zusammen?
- Gibt es System-Patterns?
- Welche Kombinationen sind am besten?
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter

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

def analyze_position_combinations(layer3_data: Dict, positions: List[int]) -> Dict:
 """Analyze Kombinationen von Positionen."""
 results_data = layer3_data.get("results", [])
 
 onchain_patterns = defaultdict(int)
 offchain_patterns = defaultdict(int)
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if len(layer3_id) <= max(positions):
 continue
 
 # Build pattern key
 pattern_key = "".join([layer3_id[pos] for pos in positions])
 
 if is_onchain:
 onchain_patterns[pattern_key] += 1
 else:
 offchain_patterns[pattern_key] += 1
 
 # Calculate accuracy for each pattern
 pattern_accuracy = {}
 for pattern in set(list(onchain_patterns.keys()) + list(offchain_patterns.keys())):
 on_count = onchain_patterns.get(pattern, 0)
 off_count = offchain_patterns.get(pattern, 0)
 total = on_count + off_count
 
 if total > 0:
 accuracy = (on_count / total) * 100
 pattern_accuracy[pattern] = {
 "onchain": on_count,
 "offchain": off_count,
 "total": total,
 "accuracy": accuracy,
 "prediction": "ON-CHAIN" if accuracy > 50 else "OFF-CHAIN"
 }
 
 return {
 "positions": positions,
 "patterns": pattern_accuracy,
 "total_patterns": len(pattern_accuracy),
 "onchain_patterns": dict(onchain_patterns),
 "offchain_patterns": dict(offchain_patterns)
 }

def find_best_combinations(layer3_data: Dict, max_positions: int = 3) -> Dict:
 """Finde beste Kombinationen von frühen Positionen."""
 early_positions = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
 
 best_combinations = []
 
 # Test single positions
 for pos in early_positions:
 result = analyze_position_combinations(layer3_data, [pos])
 if result["patterns"]:
 # Calculate overall accuracy
 correct = 0
 total = 0
 for pattern, data in result["patterns"].items():
 if data["prediction"] == "ON-CHAIN":
 correct += data["onchain"]
 else:
 correct += data["offchain"]
 total += data["total"]
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 best_combinations.append({
 "positions": [pos],
 "accuracy": accuracy,
 "correct": correct,
 "total": total,
 "unique_patterns": result["total_patterns"]
 })
 
 # Test pairs
 for i, pos1 in enumerate(early_positions):
 for pos2 in early_positions[i+1:]:
 result = analyze_position_combinations(layer3_data, [pos1, pos2])
 if result["patterns"]:
 correct = 0
 total = 0
 for pattern, data in result["patterns"].items():
 if data["prediction"] == "ON-CHAIN":
 correct += data["onchain"]
 else:
 correct += data["offchain"]
 total += data["total"]
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 best_combinations.append({
 "positions": [pos1, pos2],
 "accuracy": accuracy,
 "correct": correct,
 "total": total,
 "unique_patterns": result["total_patterns"]
 })
 
 # Sort by accuracy
 best_combinations.sort(key=lambda x: x["accuracy"], reverse=True)
 
 return {
 "best_combinations": best_combinations[:20], # Top 20
 "total_tested": len(best_combinations)
 }

def analyze_system_patterns(layer3_data: Dict) -> Dict:
 """Analyze System-Patterns in frühen Positionen."""
 results_data = layer3_data.get("results", [])
 
 # Analyze transitions between positions
 transitions = defaultdict(int)
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if len(layer3_id) < 10:
 continue
 
 # Analyze transitions
 for i in range(9):
 transition = layer3_id[i:i+2]
 transitions[(transition, is_onchain)] += 1
 
 # Convert tuple keys to strings for JSON serialization
 transitions_dict = {}
 for (transition, is_onchain), count in transitions.items():
 key = f"{transition}_{'onchain' if is_onchain else 'offchain'}"
 transitions_dict[key] = count
 
 return {
 "transitions": transitions_dict
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("EARLY POSITIONS SYSTEM ANALYSIS")
 print("=" * 80)
 print()
 
 # Load Layer-3 Daten
 print("Loading Layer-3 data...")
 layer3_data = load_layer3_data()
 
 if not layer3_data:
 print("❌ Layer-3 data not found")
 return
 
 print(f"✅ Loaded {len(layer3_data.get('results', []))} entries")
 print()
 
 # 1. Finde beste Kombinationen
 print("=" * 80)
 print("1. FINDING BEST COMBINATIONS")
 print("=" * 80)
 print()
 
 best_result = find_best_combinations(layer3_data, max_positions=2)
 
 print("Top 10 Combinations:")
 for i, combo in enumerate(best_result["best_combinations"][:10], 1):
 pos_str = "+".join(map(str, combo["positions"]))
 print(f" {i}. Positions {pos_str}: {combo['accuracy']:.1f}% ({combo['correct']}/{combo['total']}), "
 f"{combo['unique_patterns']} unique patterns")
 print()
 
 # 2. Analyze System-Patterns
 print("=" * 80)
 print("2. ANALYZING SYSTEM PATTERNS")
 print("=" * 80)
 print()
 
 system_result = analyze_system_patterns(layer3_data)
 
 # Top transitions
 onchain_transitions = {k: v for k, v in system_result["transitions"].items() if k[1]}
 offchain_transitions = {k: v for k, v in system_result["transitions"].items() if not k[1]}
 
 print("Top On-chain Transitions:")
 top_onchain = sorted(onchain_transitions.items(), key=lambda x: x[1], reverse=True)[:10]
 for transition, count in top_onchain:
 print(f" {transition[0]}: {count}")
 print()
 
 print("Top Off-chain Transitions:")
 top_offchain = sorted(offchain_transitions.items(), key=lambda x: x[1], reverse=True)[:10]
 for transition, count in top_offchain:
 print(f" {transition[0]}: {count}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 results = {
 "best_combinations": best_result,
 "system_patterns": system_result
 }
 
 output_json = OUTPUT_DIR / "early_positions_system_analysis.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "early_positions_system_analysis_report.md"
 
 with output_md.open("w") as f:
 f.write("# Early Positions System Analysis\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write("Analysis of early positions (0-10) working together.\n\n")
 
 f.write("## Best Combinations\n\n")
 f.write("| Rank | Positions | Accuracy | Correct/Total | Unique Patterns |\n")
 f.write("|------|-----------|---------|---------------|-----------------|\n")
 
 for i, combo in enumerate(best_result["best_combinations"][:10], 1):
 pos_str = "+".join(map(str, combo["positions"]))
 f.write(f"| {i} | {pos_str} | {combo['accuracy']:.1f}% | {combo['correct']}/{combo['total']} | {combo['unique_patterns']} |\n")
 
 f.write("\n")
 f.write("## System Patterns\n\n")
 f.write("### Top On-chain Transitions\n\n")
 for transition, count in top_onchain[:10]:
 f.write(f"- `{transition[0]}`: {count}\n")
 f.write("\n")
 f.write("### Top Off-chain Transitions\n\n")
 for transition, count in top_offchain[:10]:
 f.write(f"- `{transition[0]}`: {count}\n")
 f.write("\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

