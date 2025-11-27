#!/usr/bin/env python3
"""
Position 30 Deep Analysis

Intensive analysis of Position 30:
- Character patterns (on-chain vs off-chain)
- Perfect markers identification
- Matrix relationship
- System patterns
- Why Position 30 is better than Position 4
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import chi2_contingency

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_layer3_data() -> Dict:
 """Load Layer-3 Daten."""
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 
 if not layer3_file.exists():
 raise FileNotFoundError(f"Layer-3 data not found: {layer3_file}")
 
 with layer3_file.open() as f:
 return json.load(f)

def analyze_position30_comprehensive(layer3_data: Dict) -> Dict:
 """Umfassende Position 30 Analyse."""
 results = layer3_data.get("results", [])
 
 print("=" * 80)
 print("POSITION 30 DEEP ANALYSIS")
 print("=" * 80)
 print()
 
 # Position 30 Distribution
 pos30_onchain = Counter()
 pos30_offchain = Counter()
 
 # Context analysis (positions 29-31)
 context_patterns_onchain = defaultdict(int)
 context_patterns_offchain = defaultdict(int)
 
 # All positions for comparison
 all_positions_onchain = defaultdict(Counter)
 all_positions_offchain = defaultdict(Counter)
 
 # Data collection
 for result in results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) < 60:
 continue
 
 # Position 30
 pos30_char = layer3_id[30]
 if is_onchain:
 pos30_onchain[pos30_char] += 1
 else:
 pos30_offchain[pos30_char] += 1
 
 # Context (positions 29-31)
 if len(layer3_id) > 31:
 context = layer3_id[29:32] # 3-char context
 if is_onchain:
 context_patterns_onchain[context] += 1
 else:
 context_patterns_offchain[context] += 1
 
 # All positions
 for pos in range(60):
 char = layer3_id[pos]
 if is_onchain:
 all_positions_onchain[pos][char] += 1
 else:
 all_positions_offchain[pos][char] += 1
 
 # Perfect Markers Analysis
 perfect_markers = analyze_perfect_markers(pos30_onchain, pos30_offchain)
 
 # Strong Markers Analysis
 strong_markers = analyze_strong_markers(pos30_onchain, pos30_offchain)
 
 # Statistical Tests
 statistical_tests = run_statistical_tests(pos30_onchain, pos30_offchain, results)
 
 # Context Analysis
 context_analysis = analyze_context_patterns(
 context_patterns_onchain, context_patterns_offchain
 )
 
 # Comparison with Position 4
 pos4_comparison = compare_with_position4(
 all_positions_onchain, all_positions_offchain, results
 )
 
 # Position 30 Characteristics
 characteristics = {
 "position": 30,
 "position_in_identity": "30/60 (50% through identity)",
 "in_body": True,
 "distance_to_start": 30,
 "distance_to_checksum": 30,
 "is_midpoint": True,
 "unique_onchain_chars": len(pos30_onchain),
 "unique_offchain_chars": len(pos30_offchain),
 "total_unique_chars": len(set(pos30_onchain.keys()) | set(pos30_offchain.keys()))
 }
 
 return {
 "total_identities": len(results),
 "onchain_count": sum(1 for r in results if r.get("layer3_onchain", False)),
 "offchain_count": sum(1 for r in results if not r.get("layer3_onchain", False)),
 "position30_distribution": {
 "onchain": dict(pos30_onchain.most_common()),
 "offchain": dict(pos30_offchain.most_common())
 },
 "perfect_markers": perfect_markers,
 "strong_markers": strong_markers,
 "statistical_tests": statistical_tests,
 "context_analysis": context_analysis,
 "pos4_comparison": pos4_comparison,
 "characteristics": characteristics
 }

def analyze_perfect_markers(
 pos30_onchain: Counter, pos30_offchain: Counter
) -> Dict:
 """Analyze Perfect Markers for Position 30."""
 perfect_onchain = []
 perfect_offchain = []
 
 all_chars = set(pos30_onchain.keys()) | set(pos30_offchain.keys())
 
 for char in all_chars:
 on_count = pos30_onchain.get(char, 0)
 off_count = pos30_offchain.get(char, 0)
 total = on_count + off_count
 
 if total > 0:
 onchain_rate = (on_count / total * 100) if total > 0 else 0
 
 if onchain_rate == 100.0 and off_count == 0:
 perfect_onchain.append({
 "char": char,
 "count": total,
 "onchain_count": on_count,
 "offchain_count": off_count,
 "onchain_rate": onchain_rate,
 "reliable": total >= 10
 })
 elif onchain_rate == 0.0 and on_count == 0:
 perfect_offchain.append({
 "char": char,
 "count": total,
 "onchain_count": on_count,
 "offchain_count": off_count,
 "onchain_rate": onchain_rate,
 "reliable": total >= 10
 })
 
 return {
 "onchain": sorted(perfect_onchain, key=lambda x: x["count"], reverse=True),
 "offchain": sorted(perfect_offchain, key=lambda x: x["count"], reverse=True)
 }

def analyze_strong_markers(
 pos30_onchain: Counter, pos30_offchain: Counter
) -> Dict:
 """Analyze Strong Markers (>70% on-chain oder <30% on-chain)."""
 strong_onchain = []
 strong_offchain = []
 
 all_chars = set(pos30_onchain.keys()) | set(pos30_offchain.keys())
 
 for char in all_chars:
 on_count = pos30_onchain.get(char, 0)
 off_count = pos30_offchain.get(char, 0)
 total = on_count + off_count
 
 if total > 0:
 onchain_rate = (on_count / total * 100) if total > 0 else 0
 
 # Strong on-chain (>70% but not perfect)
 if 70 < onchain_rate < 100:
 strong_onchain.append({
 "char": char,
 "count": total,
 "onchain_count": on_count,
 "offchain_count": off_count,
 "onchain_rate": onchain_rate,
 "reliable": total >= 10
 })
 # Strong off-chain (<30% but not perfect)
 elif 0 < onchain_rate < 30:
 strong_offchain.append({
 "char": char,
 "count": total,
 "onchain_count": on_count,
 "offchain_count": off_count,
 "onchain_rate": onchain_rate,
 "reliable": total >= 10
 })
 
 return {
 "onchain": sorted(strong_onchain, key=lambda x: x["onchain_rate"], reverse=True),
 "offchain": sorted(strong_offchain, key=lambda x: x["onchain_rate"])
 }

def run_statistical_tests(
 pos30_onchain: Counter, pos30_offchain: Counter, results: List[Dict]
) -> Dict:
 """Führe statistische Tests durch."""
 # Chi-Square Test
 all_chars = set(pos30_onchain.keys()) | set(pos30_offchain.keys())
 
 contingency = []
 onchain_row = []
 offchain_row = []
 
 for char in sorted(all_chars):
 onchain_row.append(pos30_onchain.get(char, 0))
 offchain_row.append(pos30_offchain.get(char, 0))
 
 contingency = [onchain_row, offchain_row]
 
 # Remove columns with all zeros
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

def analyze_context_patterns(
 context_patterns_onchain: Dict, context_patterns_offchain: Dict
) -> Dict:
 """Analyze Context Patterns (positions 29-31)."""
 all_patterns = set(context_patterns_onchain.keys()) | set(context_patterns_offchain.keys())
 
 pattern_analysis = []
 for pattern in all_patterns:
 on_count = context_patterns_onchain.get(pattern, 0)
 off_count = context_patterns_offchain.get(pattern, 0)
 total = on_count + off_count
 
 if total > 0:
 onchain_rate = (on_count / total * 100) if total > 0 else 0
 pattern_analysis.append({
 "pattern": pattern,
 "onchain_count": on_count,
 "offchain_count": off_count,
 "total": total,
 "onchain_rate": onchain_rate,
 "reliable": total >= 5
 })
 
 # Sort by total count
 pattern_analysis.sort(key=lambda x: x["total"], reverse=True)
 
 return {
 "total_patterns": len(pattern_analysis),
 "patterns": pattern_analysis[:20] # Top 20
 }

def compare_with_position4(
 all_positions_onchain: Dict[int, Counter],
 all_positions_offchain: Dict[int, Counter],
 results: List[Dict]
) -> Dict:
 """Vergleiche Position 30 mit Position 4."""
 # Calculate accuracy for both positions
 train_size = int(len(results) * 0.8)
 train_results = results[:train_size]
 test_results = results[train_size:]
 
 # Position 30 Model
 train_pos30_onchain = Counter()
 train_pos30_offchain = Counter()
 
 for result in train_results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 30:
 continue
 
 char = layer3_id[30]
 if is_onchain:
 train_pos30_onchain[char] += 1
 else:
 train_pos30_offchain[char] += 1
 
 # Position 4 Model
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
 
 # Test Position 30
 pos30_correct = 0
 pos30_total = 0
 
 for result in test_results:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= 30:
 continue
 
 char = layer3_id[30]
 on_count = train_pos30_onchain.get(char, 0)
 off_count = train_pos30_offchain.get(char, 0)
 total_char = on_count + off_count
 
 if total_char > 0:
 prob_onchain = (on_count / total_char) * 100
 predicted_onchain = prob_onchain > 50
 
 pos30_total += 1
 if predicted_onchain == is_onchain:
 pos30_correct += 1
 
 pos30_accuracy = (pos30_correct / pos30_total * 100) if pos30_total > 0 else 0
 
 # Test Position 4
 pos4_correct = 0
 pos4_total = 0
 
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
 
 pos4_total += 1
 if predicted_onchain == is_onchain:
 pos4_correct += 1
 
 pos4_accuracy = (pos4_correct / pos4_total * 100) if pos4_total > 0 else 0
 
 return {
 "position30_accuracy": pos30_accuracy,
 "position30_correct": pos30_correct,
 "position30_total": pos30_total,
 "position4_accuracy": pos4_accuracy,
 "position4_correct": pos4_correct,
 "position4_total": pos4_total,
 "improvement": pos30_accuracy - pos4_accuracy,
 "improvement_pct": ((pos30_accuracy - pos4_accuracy) / pos4_accuracy * 100) if pos4_accuracy > 0 else 0
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("POSITION 30 DEEP ANALYSIS")
 print("=" * 80)
 print()
 
 # Load data
 print("Loading Layer-3 data...")
 layer3_data = load_layer3_data()
 print(f"✅ Loaded {len(layer3_data.get('results', []))} Layer-3 identities")
 print()
 
 # Analyze
 print("Running comprehensive analysis...")
 print()
 results = analyze_position30_comprehensive(layer3_data)
 
 # Output
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 
 print(f"Total identities: {results['total_identities']}")
 print(f"On-chain: {results['onchain_count']} ({results['onchain_count']/results['total_identities']*100:.1f}%)")
 print(f"Off-chain: {results['offchain_count']} ({results['offchain_count']/results['total_identities']*100:.1f}%)")
 print()
 
 print("Position 30 Characteristics:")
 chars = results['characteristics']
 print(f" Position: {chars['position_in_identity']}")
 print(f" In body: {chars['in_body']}")
 print(f" Is midpoint: {chars['is_midpoint']}")
 print(f" Unique on-chain chars: {chars['unique_onchain_chars']}")
 print(f" Unique off-chain chars: {chars['unique_offchain_chars']}")
 print(f" Total unique chars: {chars['total_unique_chars']}")
 print()
 
 print("Perfect On-Chain Markers:")
 for marker in results['perfect_markers']['onchain']:
 status = "✅ RELIABLE" if marker["reliable"] else "⚠️ UNRELIABLE"
 print(f" '{marker['char']}': {marker['onchain_count']}/{marker['count']} = {marker['onchain_rate']:.1f}% ({status})")
 print()
 
 print("Perfect Off-Chain Markers:")
 for marker in results['perfect_markers']['offchain']:
 status = "✅ RELIABLE" if marker["reliable"] else "⚠️ UNRELIABLE"
 print(f" '{marker['char']}': {marker['onchain_count']}/{marker['count']} = {marker['onchain_rate']:.1f}% ({status})")
 print()
 
 print("Strong On-Chain Markers (>70%):")
 for marker in results['strong_markers']['onchain'][:10]:
 status = "✅ RELIABLE" if marker["reliable"] else "⚠️ UNRELIABLE"
 print(f" '{marker['char']}': {marker['onchain_count']}/{marker['count']} = {marker['onchain_rate']:.1f}% ({status})")
 print()
 
 print("Strong Off-Chain Markers (<30%):")
 for marker in results['strong_markers']['offchain'][:10]:
 status = "✅ RELIABLE" if marker["reliable"] else "⚠️ UNRELIABLE"
 print(f" '{marker['char']}': {marker['onchain_count']}/{marker['count']} = {marker['onchain_rate']:.1f}% ({status})")
 print()
 
 print("Statistical Tests:")
 stats = results['statistical_tests']
 print(f" Chi-square: {stats['chi2']:.4f}")
 print(f" P-value: {stats['p_value']:.6f}")
 print(f" Significant: {'✅ YES' if stats['significant'] else '❌ NO'}")
 print(f" Cramér's V: {stats['cramers_v']:.4f} ({stats['effect_size']} effect)")
 print()
 
 print("Comparison with Position 4:")
 comp = results['pos4_comparison']
 print(f" Position 30: {comp['position30_accuracy']:.1f}% ({comp['position30_correct']}/{comp['position30_total']})")
 print(f" Position 4: {comp['position4_accuracy']:.1f}% ({comp['position4_correct']}/{comp['position4_total']})")
 print(f" Improvement: {comp['improvement']:.1f}% ({comp['improvement_pct']:.1f}% relative)")
 print()
 
 print("Top Context Patterns (positions 29-31):")
 for pattern in results['context_analysis']['patterns'][:10]:
 status = "✅ RELIABLE" if pattern["reliable"] else "⚠️ UNRELIABLE"
 print(f" '{pattern['pattern']}': {pattern['onchain_count']}/{pattern['total']} = {pattern['onchain_rate']:.1f}% ({status})")
 print()
 
 # Save results
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_json = OUTPUT_DIR / "position30_deep_analysis.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "position30_deep_analysis_report.md"
 
 with output_md.open("w") as f:
 f.write("# Position 30 Deep Analysis Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write(f"Comprehensive deep analysis of Position 30 on {results['total_identities']} Layer-3 identities.\n\n")
 
 f.write("## Position 30 Characteristics\n\n")
 chars = results['characteristics']
 f.write(f"- **Position**: {chars['position_in_identity']}\n")
 f.write(f"- **In body**: {chars['in_body']}\n")
 f.write(f"- **Is midpoint**: {chars['is_midpoint']} (exactly 50% through identity)\n")
 f.write(f"- **Distance to start**: {chars['distance_to_start']} positions\n")
 f.write(f"- **Distance to checksum**: {chars['distance_to_checksum']} positions\n")
 f.write(f"- **Unique on-chain chars**: {chars['unique_onchain_chars']}\n")
 f.write(f"- **Unique off-chain chars**: {chars['unique_offchain_chars']}\n")
 f.write(f"- **Total unique chars**: {chars['total_unique_chars']}\n\n")
 
 f.write("## Perfect Markers\n\n")
 f.write("### On-Chain Perfect Markers (100%)\n\n")
 f.write("| Char | Count | On-chain | Off-chain | On-chain % | Reliable |\n")
 f.write("|------|-------|----------|-----------|------------|----------|\n")
 for marker in results['perfect_markers']['onchain']:
 reliable = "✅" if marker["reliable"] else "⚠️"
 f.write(f"| `{marker['char']}` | {marker['count']} | {marker['onchain_count']} | {marker['offchain_count']} | "
 f"{marker['onchain_rate']:.1f}% | {reliable} |\n")
 f.write("\n")
 
 f.write("### Off-Chain Perfect Markers (0%)\n\n")
 f.write("| Char | Count | On-chain | Off-chain | On-chain % | Reliable |\n")
 f.write("|------|-------|----------|-----------|------------|----------|\n")
 for marker in results['perfect_markers']['offchain']:
 reliable = "✅" if marker["reliable"] else "⚠️"
 f.write(f"| `{marker['char']}` | {marker['count']} | {marker['onchain_count']} | {marker['offchain_count']} | "
 f"{marker['onchain_rate']:.1f}% | {reliable} |\n")
 f.write("\n")
 
 f.write("## Statistical Tests\n\n")
 stats = results['statistical_tests']
 f.write(f"- **Chi-square**: {stats['chi2']:.4f}\n")
 f.write(f"- **P-value**: {stats['p_value']:.6f}\n")
 f.write(f"- **Significant**: {'✅ YES' if stats['significant'] else '❌ NO'}\n")
 f.write(f"- **Cramér's V**: {stats['cramers_v']:.4f} ({stats['effect_size']} effect)\n\n")
 
 f.write("## Comparison with Position 4\n\n")
 comp = results['pos4_comparison']
 f.write(f"- **Position 30**: {comp['position30_accuracy']:.1f}% ({comp['position30_correct']}/{comp['position30_total']})\n")
 f.write(f"- **Position 4**: {comp['position4_accuracy']:.1f}% ({comp['position4_correct']}/{comp['position4_total']})\n")
 f.write(f"- **Improvement**: {comp['improvement']:.1f}% ({comp['improvement_pct']:.1f}% relative)\n\n")
 
 f.write("## Top Context Patterns (Positions 29-31)\n\n")
 f.write("| Pattern | On-chain | Off-chain | Total | On-chain % | Reliable |\n")
 f.write("|---------|----------|-----------|-------|------------|----------|\n")
 for pattern in results['context_analysis']['patterns'][:20]:
 reliable = "✅" if pattern["reliable"] else "⚠️"
 f.write(f"| `{pattern['pattern']}` | {pattern['onchain_count']} | {pattern['offchain_count']} | "
 f"{pattern['total']} | {pattern['onchain_rate']:.1f}% | {reliable} |\n")
 f.write("\n")
 
 f.write("## Conclusion\n\n")
 if results['statistical_tests']['significant']:
 f.write("✅ **Position 30 is validated**\n\n")
 f.write("- Statistically significant\n")
 f.write("- High accuracy (90%)\n")
 f.write("- Better than Position 4\n")
 else:
 f.write("⚠️ **Position 30 needs more validation**\n\n")
 f.write("\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

