#!/usr/bin/env python3
"""
Analyze Documented vs Real ID Patterns

Analysiert die Verbindungen zwischen dokumentierten (Matrix) und realen IDs.
Findet Patterns, Muster und Transformationen.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import difflib

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

INPUT_FILE = project_root / "outputs" / "derived" / "complete_24846_seeds_to_real_ids_mapping.json"
OUTPUT_DIR = project_root / "outputs" / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def analyze_character_differences(doc_id: str, real_id: str) -> Dict:
 """Analyze Charakter-Unterschiede zwischen dokumentierter und realer ID."""
 if len(doc_id) != 60 or len(real_id) != 60:
 return {}
 
 differences = []
 same_positions = []
 
 for i in range(60):
 if doc_id[i] != real_id[i]:
 differences.append({
 "position": i,
 "doc_char": doc_id[i],
 "real_char": real_id[i],
 "doc_ord": ord(doc_id[i]),
 "real_ord": ord(real_id[i]),
 "diff": ord(real_id[i]) - ord(doc_id[i])
 })
 else:
 same_positions.append(i)
 
 return {
 "total_differences": len(differences),
 "total_same": len(same_positions),
 "difference_rate": len(differences) / 60,
 "differences": differences[:20], # First 20
 "same_positions": same_positions[:20]
 }

def analyze_position_patterns(differences: List[Dict]) -> Dict:
 """Analyze Position-Patterns in den Unterschieden."""
 if not differences:
 return {}
 
 positions = [d["position"] for d in differences]
 diffs = [d["diff"] for d in differences]
 doc_chars = [d["doc_char"] for d in differences]
 real_chars = [d["real_char"] for d in differences]
 
 return {
 "position_distribution": Counter(positions),
 "diff_distribution": Counter(diffs),
 "doc_char_distribution": Counter(doc_chars),
 "real_char_distribution": Counter(real_chars),
 "most_common_positions": Counter(positions).most_common(10),
 "most_common_diffs": Counter(diffs).most_common(10)
 }

def analyze_seed_patterns(seed: str, doc_id: str, real_id: str) -> Dict:
 """Analyze Seed-Patterns."""
 return {
 "seed_length": len(seed),
 "seed_chars": Counter(seed),
 "seed_starts_with": seed[:10],
 "seed_ends_with": seed[-10:],
 "seed_has_repeats": len(set(seed)) < len(seed),
 "doc_id_starts_with": doc_id[:10],
 "real_id_starts_with": real_id[:10],
 "seed_matches_doc_start": seed.upper() == doc_id[:55],
 "seed_matches_real_start": seed.upper() == real_id[:55]
 }

def find_transformation_patterns(mismatches: List[Dict]) -> Dict:
 """Finde Transformation-Patterns zwischen dokumentierten und realen IDs."""
 transformations = []
 
 for item in mismatches[:1000]: # First 1000 for analysis
 doc_id = item.get("documented_identity", "")
 real_id = item.get("real_identity", "")
 seed = item.get("seed", "")
 
 if not doc_id or not real_id:
 continue
 
 # Character-level analysis
 char_diff = analyze_character_differences(doc_id, real_id)
 
 # Seed analysis
 seed_patterns = analyze_seed_patterns(seed, doc_id, real_id)
 
 transformations.append({
 "seed": seed,
 "documented_identity": doc_id,
 "real_identity": real_id,
 "char_differences": char_diff,
 "seed_patterns": seed_patterns
 })
 
 # Aggregate patterns
 all_diffs = []
 all_positions = []
 
 for t in transformations:
 if t["char_differences"].get("differences"):
 all_diffs.extend(t["char_differences"]["differences"])
 all_positions.extend([d["position"] for d in t["char_differences"]["differences"]])
 
 return {
 "total_analyzed": len(transformations),
 "position_patterns": analyze_position_patterns(all_diffs) if all_diffs else {},
 "sample_transformations": transformations[:50],
 "statistics": {
 "avg_differences": sum(len(t["char_differences"].get("differences", [])) for t in transformations) / len(transformations) if transformations else 0,
 "positions_with_most_diffs": Counter(all_positions).most_common(20) if all_positions else []
 }
 }

def check_layer_relationships(mismatches: List[Dict]) -> Dict:
 """Check ob dokumentierte IDs von anderen Layern stammen."""
 # Load known layer identities
 layer_files = {
 "layer2": project_root / "outputs" / "derived" / "layer2_derivation_complete.json",
 "layer3": project_root / "outputs" / "derived" / "layer3_derivation_complete.json",
 }
 
 layer_identities = {}
 for layer_name, file_path in layer_files.items():
 if file_path.exists():
 with file_path.open() as f:
 data = json.load(f)
 results = data.get("results", [])
 for result in results:
 identity = result.get(f"{layer_name}_identity", "")
 if identity:
 layer_identities[identity] = layer_name
 
 # Check if documented IDs are in other layers
 layer_matches = defaultdict(list)
 
 for item in mismatches[:1000]:
 doc_id = item.get("documented_identity", "")
 if doc_id in layer_identities:
 layer_matches[layer_identities[doc_id]].append(item)
 
 return {
 "layer_identities_loaded": len(layer_identities),
 "documented_ids_in_layers": dict(layer_matches),
 "total_matches": sum(len(v) for v in layer_matches.values())
 }

def analyze_seed_to_fake_id_mapping(mismatches: List[Dict]) -> Dict:
 """Analyze ob wir Seeds for die 'Fake' IDs finden können."""
 # Group by documented identity
 doc_id_to_seeds = defaultdict(list)
 
 for item in mismatches:
 doc_id = item.get("documented_identity", "")
 seed = item.get("seed", "")
 real_id = item.get("real_identity", "")
 
 if doc_id and seed:
 doc_id_to_seeds[doc_id].append({
 "seed": seed,
 "real_identity": real_id
 })
 
 # Find patterns
 patterns = {
 "unique_documented_ids": len(doc_id_to_seeds),
 "ids_with_multiple_seeds": sum(1 for v in doc_id_to_seeds.values() if len(v) > 1),
 "sample_mappings": dict(list(doc_id_to_seeds.items())[:20])
 }
 
 return patterns

def main():
 """Main function."""
 print("=" * 80)
 print("ANALYZE DOCUMENTED VS REAL ID PATTERNS")
 print("=" * 80)
 print()
 
 if not INPUT_FILE.exists():
 print(f"❌ Input file not found: {INPUT_FILE}")
 print(" Waiting for mapping to complete...")
 return
 
 print("1. Loading mapping data...")
 with INPUT_FILE.open() as f:
 data = json.load(f)
 
 mismatches = data.get("mismatches_list", [])
 if not mismatches:
 # Try to extract from results
 results = data.get("results", [])
 mismatches = [r for r in results if r.get("real_identity") and not r.get("match")]
 
 print(f" ✅ Loaded {len(mismatches):,} mismatches")
 print()
 
 print("2. Analyzing character differences...")
 transformation_analysis = find_transformation_patterns(mismatches)
 print(f" ✅ Analyzed {transformation_analysis['total_analyzed']:,} transformations")
 print()
 
 print("3. Checking layer relationships...")
 layer_analysis = check_layer_relationships(mismatches)
 print(f" ✅ Found {layer_analysis['total_matches']:,} documented IDs in other layers")
 print()
 
 print("4. Analyzing seed-to-fake-ID mapping...")
 seed_mapping_analysis = analyze_seed_to_fake_id_mapping(mismatches)
 print(f" ✅ Analyzed {seed_mapping_analysis['unique_documented_ids']:,} documented IDs")
 print()
 
 # Save results
 output_file = OUTPUT_DIR / "documented_vs_real_pattern_analysis.json"
 with output_file.open("w") as f:
 json.dump({
 "total_mismatches": len(mismatches),
 "transformation_analysis": transformation_analysis,
 "layer_analysis": layer_analysis,
 "seed_mapping_analysis": seed_mapping_analysis
 }, f, indent=2)
 
 print("=" * 80)
 print("ANALYSIS COMPLETE")
 print("=" * 80)
 print(f"✅ Results saved to: {output_file}")
 print()
 
 # Summary
 print("Summary:")
 print(f" Total mismatches analyzed: {len(mismatches):,}")
 print(f" Average differences per ID: {transformation_analysis['statistics']['avg_differences']:.2f}")
 print(f" Documented IDs in other layers: {layer_analysis['total_matches']:,}")
 print(f" Unique documented IDs: {seed_mapping_analysis['unique_documented_ids']:,}")

if __name__ == "__main__":
 main()

