#!/usr/bin/env python3
"""
Pattern Discovery Engine

Entdeckt Patterns, Muster und Zusammenhänge in den Mapping-Daten.
- Charakter-Patterns
- Position-Patterns
- Seed-Patterns
- Transformation-Patterns
- Layer-Patterns
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List
import re

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

INPUT_FILE = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
OUTPUT_DIR = project_root / "outputs" / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def discover_character_patterns(mismatches: List[Dict]) -> Dict:
 """Entdecke Charakter-Patterns."""
 patterns = {
 "common_doc_chars": Counter(),
 "common_real_chars": Counter(),
 "char_transitions": defaultdict(int),
 "position_char_frequency": defaultdict(lambda: Counter())
 }
 
 for item in mismatches[:1000]:
 doc_id = item.get("documented_identity", "")
 real_id = item.get("real_identity", "")
 
 if len(doc_id) == 60 and len(real_id) == 60:
 for i in range(60):
 doc_char = doc_id[i]
 real_char = real_id[i]
 
 patterns["common_doc_chars"][doc_char] += 1
 patterns["common_real_chars"][real_char] += 1
 patterns["char_transitions"][f"{doc_char}->{real_char}"] += 1
 patterns["position_char_frequency"][i][doc_char] += 1
 patterns["position_char_frequency"][i][real_char] += 1
 
 return {
 "most_common_doc_chars": patterns["common_doc_chars"].most_common(20),
 "most_common_real_chars": patterns["common_real_chars"].most_common(20),
 "most_common_transitions": Counter(patterns["char_transitions"]).most_common(20),
 "position_patterns": {pos: freq.most_common(5) for pos, freq in list(patterns["position_char_frequency"].items())[:10]}
 }

def discover_seed_patterns(mismatches: List[Dict]) -> Dict:
 """Entdecke Seed-Patterns."""
 seed_patterns = {
 "common_substrings": Counter(),
 "repeating_patterns": Counter(),
 "seed_lengths": Counter(),
 "char_frequency": Counter()
 }
 
 for item in mismatches[:1000]:
 seed = item.get("seed", "")
 if len(seed) == 55:
 # Substrings
 for length in [3, 4, 5]:
 for i in range(len(seed) - length + 1):
 substring = seed[i:i+length]
 seed_patterns["common_substrings"][substring] += 1
 
 # Character frequency
 for char in seed:
 seed_patterns["char_frequency"][char] += 1
 
 # Repeating patterns
 for pattern_len in [2, 3]:
 for i in range(len(seed) - pattern_len):
 pattern = seed[i:i+pattern_len]
 if seed.count(pattern) > 1:
 seed_patterns["repeating_patterns"][pattern] += 1
 
 return {
 "most_common_substrings_3": seed_patterns["common_substrings"].most_common(20),
 "most_common_substrings_4": [s for s in seed_patterns["common_substrings"].most_common(50) if len(s[0]) == 4][:20],
 "most_common_repeating_patterns": seed_patterns["repeating_patterns"].most_common(20),
 "char_frequency": seed_patterns["char_frequency"].most_common(26)
 }

def discover_transformation_patterns(mismatches: List[Dict]) -> Dict:
 """Entdecke Transformation-Patterns."""
 transformations = []
 
 for item in mismatches[:1000]:
 doc_id = item.get("documented_identity", "")
 real_id = item.get("real_identity", "")
 seed = item.get("seed", "")
 
 if len(doc_id) == 60 and len(real_id) == 60:
 # Calculate differences
 diffs = []
 for i in range(60):
 doc_ord = ord(doc_id[i])
 real_ord = ord(real_id[i])
 diff = real_ord - doc_ord
 diffs.append(diff)
 
 transformations.append({
 "seed": seed,
 "diffs": diffs,
 "avg_diff": sum(diffs) / len(diffs),
 "diff_pattern": "".join(str(d) for d in diffs[:20])
 })
 
 # Analyze patterns
 avg_diffs = [t["avg_diff"] for t in transformations]
 diff_patterns = Counter(t["diff_pattern"] for t in transformations)
 
 return {
 "total_analyzed": len(transformations),
 "avg_diff_distribution": Counter(round(d) for d in avg_diffs).most_common(20),
 "common_diff_patterns": diff_patterns.most_common(10),
 "sample_transformations": transformations[:20]
 }

def discover_layer_patterns(database: Dict) -> Dict:
 """Entdecke Layer-Patterns."""
 layer_mappings = database.get("layer_mappings", {})
 seed_to_layer = layer_mappings.get("seed_to_layer", {})
 identity_to_layer = layer_mappings.get("identity_to_layer", {})
 
 # Count by layer
 layer_counts = Counter(seed_to_layer.values())
 layer_identity_counts = Counter(identity_to_layer.values())
 
 # Find cross-layer connections
 mismatches = database.get("mismatches", [])
 cross_layer = []
 
 for item in mismatches[:100]:
 doc_id = item.get("documented_identity", "")
 real_id = item.get("real_identity", "")
 
 doc_layer = identity_to_layer.get(doc_id)
 real_layer = identity_to_layer.get(real_id)
 
 if doc_layer and real_layer and doc_layer != real_layer:
 cross_layer.append({
 "documented_id": doc_id,
 "real_id": real_id,
 "doc_layer": doc_layer,
 "real_layer": real_layer
 })
 
 return {
 "seed_layer_distribution": dict(layer_counts),
 "identity_layer_distribution": dict(layer_identity_counts),
 "cross_layer_connections": cross_layer,
 "total_cross_layer": len(cross_layer)
 }

def main():
 """Main function."""
 print("=" * 80)
 print("PATTERN DISCOVERY ENGINE")
 print("=" * 80)
 print()
 
 if not INPUT_FILE.exists():
 print(f"❌ Input file not found: {INPUT_FILE}")
 print(" Run create_complete_mapping_database.py first")
 return
 
 print("1. Loading database...")
 with INPUT_FILE.open() as f:
 database = json.load(f)
 
 mismatches = database.get("mismatches", [])
 print(f" ✅ Loaded {len(mismatches):,} mismatches")
 print()
 
 print("2. Discovering character patterns...")
 char_patterns = discover_character_patterns(mismatches)
 print(f" ✅ Found character patterns")
 print()
 
 print("3. Discovering seed patterns...")
 seed_patterns = discover_seed_patterns(mismatches)
 print(f" ✅ Found seed patterns")
 print()
 
 print("4. Discovering transformation patterns...")
 transformation_patterns = discover_transformation_patterns(mismatches)
 print(f" ✅ Found transformation patterns")
 print()
 
 print("5. Discovering layer patterns...")
 layer_patterns = discover_layer_patterns(database)
 print(f" ✅ Found layer patterns")
 print()
 
 # Save results
 output_file = OUTPUT_DIR / "pattern_discovery_results.json"
 with output_file.open("w") as f:
 json.dump({
 "character_patterns": char_patterns,
 "seed_patterns": seed_patterns,
 "transformation_patterns": transformation_patterns,
 "layer_patterns": layer_patterns
 }, f, indent=2)
 
 print("=" * 80)
 print("PATTERN DISCOVERY COMPLETE")
 print("=" * 80)
 print(f"✅ Results saved to: {output_file}")
 print()
 
 # Summary
 print("Summary:")
 print(f" Most common doc chars: {char_patterns['most_common_doc_chars'][:5]}")
 print(f" Most common real chars: {char_patterns['most_common_real_chars'][:5]}")
 print(f" Most common seed substrings: {seed_patterns['most_common_substrings_3'][:5]}")
 print(f" Cross-layer connections: {layer_patterns['total_cross_layer']}")

if __name__ == "__main__":
 main()

