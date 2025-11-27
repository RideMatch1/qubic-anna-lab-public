#!/usr/bin/env python3
"""
Analyze Seed Patterns: Find patterns in the discovered seeds.

This script analyzes:
- Seed similarities and transformations
- Character frequency patterns
- Base-26 patterns
- Seed-to-seed relationships
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "seed_pattern_analysis.json"
OUTPUT_MD = OUTPUT_DIR / "seed_pattern_analysis.md"

def load_seeds() -> Dict[str, str]:
 """Load all discovered seeds from various sources."""
 seeds = {}
 
 # From mass_seed_derivation_optimized.json
 path1 = Path("outputs/derived/mass_seed_derivation_optimized.json")
 if path1.exists():
 with path1.open() as f:
 data1 = json.load(f)
 seeds.update(data1.get("seed_map", {}))
 
 # From identity_deep_scan.json
 path2 = Path("outputs/derived/identity_deep_scan.json")
 if path2.exists():
 with path2.open() as f:
 data2 = json.load(f)
 if "records" in data2:
 for record in data2["records"]:
 identity = record.get("identity")
 seed = record.get("seed")
 if identity and seed:
 seeds[identity] = seed
 
 return seeds

def analyze_character_frequency(seeds: List[str]) -> Dict:
 """Analyze character frequency in seeds."""
 all_chars = []
 for seed in seeds:
 all_chars.extend(list(seed))
 
 char_freq = Counter(all_chars)
 
 return {
 "total_characters": len(all_chars),
 "unique_characters": len(char_freq),
 "most_common": char_freq.most_common(10),
 "least_common": char_freq.most_common()[-10:],
 }

def analyze_seed_similarities(seeds: Dict[str, str]) -> Dict:
 """Analyze similarities between seeds."""
 seed_list = list(seeds.values())
 similarities = []
 
 for i, seed1 in enumerate(seed_list):
 for j, seed2 in enumerate(seed_list[i+1:], i+1):
 # Calculate character-by-character similarity
 matches = sum(c1 == c2 for c1, c2 in zip(seed1, seed2))
 similarity = matches / len(seed1) if seed1 else 0
 
 if similarity > 0.5: # More than 50% similar
 similarities.append({
 "seed1": seed1,
 "seed2": seed2,
 "similarity": similarity,
 "matches": matches,
 })
 
 # Sort by similarity
 similarities.sort(key=lambda x: x["similarity"], reverse=True)
 
 return {
 "total_comparisons": len(seed_list) * (len(seed_list) - 1) // 2,
 "high_similarity_pairs": similarities[:20], # Top 20
 }

def analyze_base26_patterns(seeds: List[str]) -> Dict:
 """Analyze Base-26 patterns in seeds."""
 patterns = {
 "repeating_sequences": [],
 "character_runs": [],
 }
 
 for seed in seeds:
 # Find repeating sequences (3+ chars)
 for i in range(len(seed) - 2):
 seq = seed[i:i+3]
 if seed.count(seq) > 1:
 patterns["repeating_sequences"].append({
 "seed": seed,
 "sequence": seq,
 "positions": [j for j in range(len(seed) - 2) if seed[j:j+3] == seq],
 })
 
 # Find character runs (same char 3+ times)
 current_char = None
 run_length = 0
 for char in seed:
 if char == current_char:
 run_length += 1
 else:
 if run_length >= 3:
 patterns["character_runs"].append({
 "seed": seed,
 "char": current_char,
 "length": run_length,
 })
 current_char = char
 run_length = 1
 
 return patterns

def main() -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("SEED PATTERN ANALYSIS")
 print("=" * 80)
 print()
 
 print("Loading seeds...")
 seeds = load_seeds()
 print(f"✅ {len(seeds)} seeds loaded")
 print()
 
 if not seeds:
 print("❌ No seeds found")
 return
 
 seed_list = list(seeds.values())
 
 print("Analyzing character frequency...")
 char_freq = analyze_character_frequency(seed_list)
 print(f" Total characters: {char_freq['total_characters']}")
 print(f" Unique characters: {char_freq['unique_characters']}")
 print(f" Most common: {char_freq['most_common'][:5]}")
 print()
 
 print("Analyzing seed similarities...")
 similarities = analyze_seed_similarities(seeds)
 print(f" Total comparisons: {similarities['total_comparisons']}")
 print(f" High similarity pairs: {len(similarities['high_similarity_pairs'])}")
 if similarities['high_similarity_pairs']:
 top = similarities['high_similarity_pairs'][0]
 print(f" Top similarity: {top['similarity']:.2%} ({top['matches']}/55 chars)")
 print()
 
 print("Analyzing Base-26 patterns...")
 patterns = analyze_base26_patterns(seed_list)
 print(f" Repeating sequences: {len(patterns['repeating_sequences'])}")
 print(f" Character runs: {len(patterns['character_runs'])}")
 print()
 
 # Save results
 results = {
 "total_seeds": len(seeds),
 "character_frequency": char_freq,
 "similarities": similarities,
 "base26_patterns": patterns,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(results, f, indent=2)
 
 # Create markdown report
 with OUTPUT_MD.open("w", encoding="utf-8") as f:
 f.write("# Seed Pattern Analysis\n\n")
 f.write(f"**Total Seeds Analyzed:** {len(seeds)}\n\n")
 f.write("## Character Frequency\n\n")
 f.write(f"- Total characters: {char_freq['total_characters']}\n")
 f.write(f"- Unique characters: {char_freq['unique_characters']}\n")
 f.write(f"- Most common: {dict(char_freq['most_common'][:10])}\n\n")
 f.write("## Seed Similarities\n\n")
 f.write(f"- High similarity pairs: {len(similarities['high_similarity_pairs'])}\n")
 if similarities['high_similarity_pairs']:
 f.write("\nTop 10 most similar pairs:\n\n")
 for pair in similarities['high_similarity_pairs'][:10]:
 f.write(f"- Similarity: {pair['similarity']:.2%} ({pair['matches']}/55)\n")
 f.write(f" - `{pair['seed1']}`\n")
 f.write(f" - `{pair['seed2']}`\n\n")
 f.write("## Base-26 Patterns\n\n")
 f.write(f"- Repeating sequences: {len(patterns['repeating_sequences'])}\n")
 f.write(f"- Character runs: {len(patterns['character_runs'])}\n")
 
 print(f"Results saved:")
 print(f" - {OUTPUT_JSON}")
 print(f" - {OUTPUT_MD}")

if __name__ == "__main__":
 main()

