#!/usr/bin/env python3
"""
Analyze patterns in seed strings to find hidden structures:
- Repeating sequences
- Mathematical patterns
- ASCII/Base-26 encoding
- DNA-like patterns
- Cryptographic hints
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set

OUTPUT_DIR = Path("outputs/derived")
SCAN_FILE = OUTPUT_DIR / "comprehensive_matrix_scan.json"
OUTPUT_JSON = OUTPUT_DIR / "seed_pattern_analysis.json"

KNOWN_8 = [
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
]

def identity_to_seed(identity: str) -> str | None:
 """Convert identity to seed."""
 body = identity[:56].lower()[:55]
 if len(body) == 55 and body.isalpha():
 return body
 return None

def find_repeating_patterns(seed: str, min_length: int = 3) -> List[str]:
 """Find repeating patterns in seed string."""
 patterns = []
 for length in range(min_length, len(seed) // 2 + 1):
 for i in range(len(seed) - length * 2 + 1):
 pattern = seed[i:i+length]
 if seed.count(pattern) >= 2:
 patterns.append(pattern)
 return list(set(patterns))

def analyze_character_distribution(seed: str) -> Dict:
 """Analyze character frequency and distribution."""
 counter = Counter(seed)
 return {
 "unique_chars": len(counter),
 "most_common": counter.most_common(5),
 "entropy": -sum((count/len(seed)) * (count/len(seed)).bit_length() for count in counter.values()),
 }

def find_ascii_patterns(seed: str) -> List[str]:
 """Try to decode as ASCII or find ASCII-like patterns."""
 patterns = []
 # Try different offsets
 for offset in range(26):
 decoded = ""
 for char in seed:
 val = ord(char) - ord('a') - offset
 if 32 <= val <= 126: # Printable ASCII
 decoded += chr(val)
 else:
 decoded += "?"
 if decoded.count("?") < len(decoded) * 0.5: # Less than 50% invalid
 patterns.append(f"offset_{offset}: {decoded[:50]}")
 return patterns

def find_sequential_patterns(seed: str) -> List[str]:
 """Find sequential patterns (abc, xyz, etc.)."""
 patterns = []
 for i in range(len(seed) - 2):
 seq = seed[i:i+3]
 if (ord(seq[1]) == ord(seq[0]) + 1 and ord(seq[2]) == ord(seq[1]) + 1) or \
 (ord(seq[1]) == ord(seq[0]) - 1 and ord(seq[2]) == ord(seq[1]) - 1):
 patterns.append(seq)
 return list(set(patterns))

def analyze_all_seeds(identities: List[str]) -> Dict:
 """Analyze patterns across all seed strings."""
 seeds = [identity_to_seed(id) for id in identities if identity_to_seed(id)]
 
 all_repeats = []
 all_sequences = []
 char_freqs = Counter()
 
 for seed in seeds:
 if not seed:
 continue
 
 repeats = find_repeating_patterns(seed)
 all_repeats.extend(repeats)
 
 sequences = find_sequential_patterns(seed)
 all_sequences.extend(sequences)
 
 char_freqs.update(seed)
 
 return {
 "total_seeds": len(seeds),
 "repeating_patterns": Counter(all_repeats).most_common(20),
 "sequential_patterns": Counter(all_sequences).most_common(20),
 "character_frequency": char_freqs.most_common(10),
 "common_substrings": find_common_substrings(seeds),
 }

def find_common_substrings(seeds: List[str], min_length: int = 4) -> List[tuple]:
 """Find substrings that appear in multiple seeds."""
 substring_counts = Counter()
 for seed in seeds:
 if not seed:
 continue
 seen = set()
 for length in range(min_length, len(seed)):
 for i in range(len(seed) - length + 1):
 substr = seed[i:i+length]
 if substr not in seen:
 substring_counts[substr] += 1
 seen.add(substr)
 
 return [(substr, count) for substr, count in substring_counts.most_common(20) if count > 1]

def main() -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=== Seed Pattern Analyzer ===\n")
 
 # Load all identities
 with SCAN_FILE.open("r", encoding="utf-8") as f:
 scan_data = json.load(f)
 
 all_identities = set()
 for result in scan_data.get("results", []):
 for identity in result.get("on_chain_identities", []):
 all_identities.add(identity)
 
 new_identities = list(all_identities - set(KNOWN_8))
 
 print(f"Analyzing patterns in:")
 print(f" - Known 8 identities")
 print(f" - {len(new_identities)} new identities")
 print()
 
 # Analyze known 8
 print("Analyzing known 8...")
 known_analysis = analyze_all_seeds(KNOWN_8)
 
 # Analyze new identities (sample)
 print(f"Analyzing sample of new identities (first 50)...")
 new_analysis = analyze_all_seeds(new_identities[:50])
 
 # Combined analysis
 print("Combined analysis...")
 combined_identities = KNOWN_8 + new_identities[:50]
 combined_analysis = analyze_all_seeds(combined_identities)
 
 output = {
 "known_8_analysis": known_analysis,
 "new_identities_analysis": new_analysis,
 "combined_analysis": combined_analysis,
 }
 
 # Print interesting findings
 print("\n=== Key Findings ===")
 
 if combined_analysis["repeating_patterns"]:
 print("\nMost common repeating patterns:")
 for pattern, count in combined_analysis["repeating_patterns"][:10]:
 print(f" '{pattern}': appears {count} times")
 
 if combined_analysis["common_substrings"]:
 print("\nCommon substrings across multiple seeds:")
 for substr, count in combined_analysis["common_substrings"][:10]:
 print(f" '{substr}': in {count} seeds")
 
 if combined_analysis["sequential_patterns"]:
 print("\nSequential patterns found:")
 for pattern, count in combined_analysis["sequential_patterns"][:10]:
 print(f" '{pattern}': appears {count} times")
 
 # Save
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print(f"\nReport saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
 main()

