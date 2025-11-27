#!/usr/bin/env python3
"""
Statistical Analysis

Statistische Analysen der Mapping-Daten:
- Verteilungen
- Korrelationen
- Anomalien
- Signifikanz-Tests
"""

import json
import sys
from pathlib import Path
from collections import Counter
from typing import Dict, List
import statistics

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

INPUT_FILE = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
OUTPUT_DIR = project_root / "outputs" / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def analyze_distributions(mismatches: List[Dict]) -> Dict:
 """Analyze Verteilungen."""
 # Character distributions
 doc_chars = []
 real_chars = []
 seed_chars = []
 
 for item in mismatches[:1000]:
 doc_id = item.get("documented_identity", "")
 real_id = item.get("real_identity", "")
 seed = item.get("seed", "")
 
 if doc_id:
 doc_chars.extend(list(doc_id))
 if real_id:
 real_chars.extend(list(real_id))
 if seed:
 seed_chars.extend(list(seed))
 
 return {
 "doc_char_distribution": dict(Counter(doc_chars)),
 "real_char_distribution": dict(Counter(real_chars)),
 "seed_char_distribution": dict(Counter(seed_chars)),
 "doc_char_entropy": calculate_entropy(doc_chars),
 "real_char_entropy": calculate_entropy(real_chars),
 "seed_char_entropy": calculate_entropy(seed_chars)
 }

def calculate_entropy(chars: List[str]) -> float:
 """Berechne Entropie."""
 if not chars:
 return 0.0
 
 counter = Counter(chars)
 total = len(chars)
 entropy = 0.0
 
 for count in counter.values():
 prob = count / total
 if prob > 0:
 entropy -= prob * (prob.bit_length() - 1) if prob > 0 else 0
 
 return entropy

def analyze_correlations(mismatches: List[Dict]) -> Dict:
 """Analyze Korrelationen."""
 # Position-based correlations
 position_diffs = defaultdict(list)
 
 for item in mismatches[:1000]:
 doc_id = item.get("documented_identity", "")
 real_id = item.get("real_identity", "")
 
 if len(doc_id) == 60 and len(real_id) == 60:
 for i in range(60):
 doc_ord = ord(doc_id[i])
 real_ord = ord(real_id[i])
 diff = real_ord - doc_ord
 position_diffs[i].append(diff)
 
 # Calculate statistics per position
 position_stats = {}
 for pos, diffs in position_diffs.items():
 if diffs:
 position_stats[pos] = {
 "mean": statistics.mean(diffs),
 "median": statistics.median(diffs),
 "stdev": statistics.stdev(diffs) if len(diffs) > 1 else 0,
 "min": min(diffs),
 "max": max(diffs)
 }
 
 return {
 "position_statistics": position_stats,
 "most_variable_positions": sorted(position_stats.items(), key=lambda x: x[1]["stdev"], reverse=True)[:10]
 }

def find_anomalies(mismatches: List[Dict]) -> Dict:
 """Finde Anomalien."""
 anomalies = {
 "perfect_matches": [],
 "complete_mismatches": [],
 "unusual_patterns": []
 }
 
 for item in mismatches[:1000]:
 doc_id = item.get("documented_identity", "")
 real_id = item.get("real_identity", "")
 
 if len(doc_id) == 60 and len(real_id) == 60:
 # Count differences
 diff_count = sum(1 for i in range(60) if doc_id[i] != real_id[i])
 
 if diff_count == 0:
 anomalies["perfect_matches"].append(item)
 elif diff_count == 60:
 anomalies["complete_mismatches"].append(item)
 elif diff_count < 5 or diff_count > 55:
 anomalies["unusual_patterns"].append({
 "item": item,
 "diff_count": diff_count
 })
 
 return anomalies

def main():
 """Main function."""
 print("=" * 80)
 print("STATISTICAL ANALYSIS")
 print("=" * 80)
 print()
 
 if not INPUT_FILE.exists():
 print(f"❌ Input file not found: {INPUT_FILE}")
 return
 
 print("1. Loading database...")
 with INPUT_FILE.open() as f:
 database = json.load(f)
 
 mismatches = database.get("mismatches", [])
 print(f" ✅ Loaded {len(mismatches):,} mismatches")
 print()
 
 print("2. Analyzing distributions...")
 distributions = analyze_distributions(mismatches)
 print(f" ✅ Analyzed distributions")
 print()
 
 print("3. Analyzing correlations...")
 correlations = analyze_correlations(mismatches)
 print(f" ✅ Analyzed correlations")
 print()
 
 print("4. Finding anomalies...")
 anomalies = find_anomalies(mismatches)
 print(f" ✅ Found {len(anomalies['perfect_matches'])} perfect matches")
 print(f" ✅ Found {len(anomalies['complete_mismatches'])} complete mismatches")
 print(f" ✅ Found {len(anomalies['unusual_patterns'])} unusual patterns")
 print()
 
 # Save results
 output_file = OUTPUT_DIR / "statistical_analysis_results.json"
 with output_file.open("w") as f:
 json.dump({
 "distributions": distributions,
 "correlations": correlations,
 "anomalies": anomalies
 }, f, indent=2)
 
 print("=" * 80)
 print("STATISTICAL ANALYSIS COMPLETE")
 print("=" * 80)
 print(f"✅ Results saved to: {output_file}")

if __name__ == "__main__":
 main()

