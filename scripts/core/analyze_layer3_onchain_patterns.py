#!/usr/bin/env python3
"""
Layer-3 On-chain Pattern Analysis

Analysiert warum nur 34% der Layer-3 Identities on-chain sind.
Findet Patterns die on-chain von off-chain unterscheiden.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict

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

def analyze_onchain_vs_offchain(layer3_data: Dict) -> Dict:
 """Analyze Unterschiede zwischen on-chain und off-chain Layer-3."""
 results_data = layer3_data.get("results", [])
 
 onchain_ids = []
 offchain_ids = []
 onchain_seeds = []
 offchain_seeds = []
 onchain_layer2 = []
 offchain_layer2 = []
 
 for result in results_data:
 layer3_id = result.get("layer3_identity")
 layer3_seed = result.get("seed", "")
 layer2_id = result.get("layer2_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id:
 continue
 
 if is_onchain:
 onchain_ids.append(layer3_id)
 onchain_seeds.append(layer3_seed)
 onchain_layer2.append(layer2_id)
 else:
 offchain_ids.append(layer3_id)
 offchain_seeds.append(layer3_seed)
 offchain_layer2.append(layer2_id)
 
 # Analyze Character Patterns
 onchain_char_dist = Counter()
 offchain_char_dist = Counter()
 
 for id in onchain_ids:
 onchain_char_dist.update(id)
 
 for id in offchain_ids:
 offchain_char_dist.update(id)
 
 # Analyze Position Patterns
 onchain_pos_patterns = defaultdict(Counter)
 offchain_pos_patterns = defaultdict(Counter)
 
 for id in onchain_ids:
 for pos, char in enumerate(id):
 onchain_pos_patterns[pos][char] += 1
 
 for id in offchain_ids:
 for pos, char in enumerate(id):
 offchain_pos_patterns[pos][char] += 1
 
 # Finde signifikante Unterschiede
 significant_diffs = []
 for pos in range(60):
 onchain_chars = onchain_pos_patterns.get(pos, Counter())
 offchain_chars = offchain_pos_patterns.get(pos, Counter())
 
 if onchain_chars and offchain_chars:
 onchain_top = onchain_chars.most_common(1)[0]
 offchain_top = offchain_chars.most_common(1)[0]
 
 if onchain_top[0] != offchain_top[0]:
 onchain_pct = (onchain_top[1] / len(onchain_ids)) * 100
 offchain_pct = (offchain_top[1] / len(offchain_ids)) * 100
 
 if abs(onchain_pct - offchain_pct) > 10: # >10% Unterschied
 significant_diffs.append({
 "position": pos,
 "onchain_char": onchain_top[0],
 "onchain_pct": onchain_pct,
 "offchain_char": offchain_top[0],
 "offchain_pct": offchain_pct,
 "difference": abs(onchain_pct - offchain_pct)
 })
 
 # Seed Pattern Analysis
 onchain_seed_patterns = analyze_seed_patterns(onchain_seeds)
 offchain_seed_patterns = analyze_seed_patterns(offchain_seeds)
 
 return {
 "onchain_count": len(onchain_ids),
 "offchain_count": len(offchain_ids),
 "onchain_rate": (len(onchain_ids) / len(results_data) * 100) if results_data else 0,
 "onchain_char_distribution": dict(onchain_char_dist.most_common(10)),
 "offchain_char_distribution": dict(offchain_char_dist.most_common(10)),
 "significant_position_differences": significant_diffs,
 "onchain_seed_patterns": onchain_seed_patterns,
 "offchain_seed_patterns": offchain_seed_patterns
 }

def analyze_seed_patterns(seeds: List[str]) -> Dict:
 """Analyze Seed Patterns."""
 if not seeds:
 return {}
 
 char_dist = Counter()
 repeating = Counter()
 
 for seed in seeds:
 if not seed:
 continue
 char_dist.update(seed)
 
 # 2-char repeating
 for i in range(len(seed) - 1):
 if seed[i] == seed[i+1]:
 repeating[seed[i:i+2]] += 1
 
 return {
 "char_distribution": dict(char_dist.most_common(10)),
 "repeating_patterns": dict(repeating.most_common(10))
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("LAYER-3 ON-CHAIN PATTERN ANALYSIS")
 print("=" * 80)
 print()
 
 # Load Daten
 layer3_data = load_layer3_data()
 
 if not layer3_data:
 print("❌ Layer-3 data not found")
 return
 
 print(f"✅ Loaded Layer-3 data: {len(layer3_data.get('results', []))} entries")
 print()
 
 # Analyze
 analysis = analyze_onchain_vs_offchain(layer3_data)
 
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 print(f"On-chain: {analysis['onchain_count']} ({analysis['onchain_rate']:.1f}%)")
 print(f"Off-chain: {analysis['offchain_count']}")
 print()
 
 if analysis['significant_position_differences']:
 print("Significant Position Differences (>10%):")
 for diff in analysis['significant_position_differences'][:10]:
 print(f" Position {diff['position']}: On-chain='{diff['onchain_char']}' ({diff['onchain_pct']:.1f}%), "
 f"Off-chain='{diff['offchain_char']}' ({diff['offchain_pct']:.1f}%)")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_json = OUTPUT_DIR / "layer3_onchain_pattern_analysis.json"
 with output_json.open("w") as f:
 json.dump(analysis, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "layer3_onchain_pattern_analysis_report.md"
 
 with output_md.open("w") as f:
 f.write("# Layer-3 On-chain Pattern Analysis Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write(f"- **On-chain**: {analysis['onchain_count']} ({analysis['onchain_rate']:.1f}%)\n")
 f.write(f"- **Off-chain**: {analysis['offchain_count']}\n\n")
 
 f.write("## Character Distribution\n\n")
 f.write("### On-chain\n\n")
 for char, count in list(analysis['onchain_char_distribution'].items())[:10]:
 f.write(f"- `{char}`: {count} occurrences\n")
 f.write("\n### Off-chain\n\n")
 for char, count in list(analysis['offchain_char_distribution'].items())[:10]:
 f.write(f"- `{char}`: {count} occurrences\n")
 f.write("\n")
 
 if analysis['significant_position_differences']:
 f.write("## Significant Position Differences\n\n")
 f.write("Positions where on-chain and off-chain show >10% difference:\n\n")
 f.write("| Position | On-chain Char | On-chain % | Off-chain Char | Off-chain % | Difference |\n")
 f.write("|----------|---------------|------------|----------------|-------------|------------|\n")
 for diff in analysis['significant_position_differences']:
 f.write(f"| {diff['position']} | `{diff['onchain_char']}` | {diff['onchain_pct']:.1f}% | "
 f"`{diff['offchain_char']}` | {diff['offchain_pct']:.1f}% | {diff['difference']:.1f}% |\n")
 f.write("\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return analysis

if __name__ == "__main__":
 main()

