#!/usr/bin/env python3
"""
Analyze was die Seeds wirklich sind

WICHTIG: Nur echte, nachgewiesene Erkenntnisse - keine Spekulationen!
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "seed_meaning_analysis.json"
OUTPUT_MD = OUTPUT_DIR / "SEED_MEANING_ANALYSIS.md"

from standardized_conversion import identity_to_seed

def analyze_seed_structure(seeds: List[str]) -> Dict:
 """Analyze die Struktur der Seeds."""
 print("Analyzing seed structure...")
 print()
 
 analysis = {
 "lengths": Counter(len(s) for s in seeds),
 "character_set": set(),
 "position_analysis": {},
 "entropy_estimate": {},
 }
 
 # Character Set
 for seed in seeds:
 analysis["character_set"].update(seed)
 
 analysis["character_set"] = sorted(list(analysis["character_set"]))
 
 # Position Analysis (erste 10 Positionen)
 for pos in range(min(10, len(seeds[0]) if seeds else 0)):
 chars_at_pos = [seed[pos] for seed in seeds if len(seed) > pos]
 char_freq = Counter(chars_at_pos)
 analysis["position_analysis"][pos] = {
 "most_common": char_freq.most_common(5),
 "unique_chars": len(char_freq),
 }
 
 # Entropy-Schätzung (vereinfacht)
 if seeds:
 sample_seed = seeds[0]
 unique_chars = len(set(sample_seed))
 analysis["entropy_estimate"] = {
 "unique_characters": unique_chars,
 "possible_values_per_position": unique_chars,
 "total_possibilities": unique_chars ** len(sample_seed),
 }
 
 return analysis

def compare_seed_sets(layer1_seeds: List[str], layer2_seeds: List[str]) -> Dict:
 """Vergleiche Layer-1 und Layer-2 Seeds."""
 print("Comparing Layer-1 and Layer-2 seeds...")
 print()
 
 comparison = {
 "layer1_count": len(layer1_seeds),
 "layer2_count": len(layer2_seeds),
 "common_seeds": [],
 "differences": {},
 }
 
 layer1_set = set(layer1_seeds)
 layer2_set = set(layer2_seeds)
 
 # Gemeinsame Seeds
 common = layer1_set & layer2_set
 comparison["common_seeds"] = list(common)
 
 print(f"Layer-1 Seeds: {len(layer1_seeds)}")
 print(f"Layer-2 Seeds: {len(layer2_seeds)}")
 print(f"Common Seeds: {len(common)}")
 print()
 
 if common:
 print("⚠️ WICHTIG: Es gibt gemeinsame Seeds zwischen Layer-1 und Layer-2!")
 for seed in common:
 print(f" - {seed[:40]}...")
 print()
 else:
 print("✅ Keine gemeinsamen Seeds zwischen Layer-1 und Layer-2")
 print()
 
 # Unterschiede
 only_layer1 = layer1_set - layer2_set
 only_layer2 = layer2_set - layer1_set
 
 comparison["differences"] = {
 "only_in_layer1": len(only_layer1),
 "only_in_layer2": len(only_layer2),
 }
 
 return comparison

def analyze_seed_patterns(seeds: List[str]) -> Dict:
 """Analyze Muster in Seeds."""
 print("Analyzing seed patterns...")
 print()
 
 patterns = {
 "common_prefixes": Counter(),
 "common_suffixes": Counter(),
 "repeating_sequences": Counter(),
 }
 
 # Präfixe (3, 5, 10 Zeichen)
 for seed in seeds:
 for length in [3, 5, 10]:
 if len(seed) >= length:
 prefix = seed[:length]
 patterns["common_prefixes"][prefix] += 1
 
 # Suffixe (3, 5, 10 Zeichen)
 for seed in seeds:
 for length in [3, 5, 10]:
 if len(seed) >= length:
 suffix = seed[-length:]
 patterns["common_suffixes"][suffix] += 1
 
 # Wiederholende Sequenzen (2-4 Zeichen)
 for seed in seeds:
 for seq_len in [2, 3, 4]:
 for i in range(len(seed) - seq_len):
 seq = seed[i:i+seq_len]
 if seq.count(seq[0]) == len(seq): # Alle Zeichen gleich
 patterns["repeating_sequences"][seq] += 1
 
 # Top 10
 patterns["common_prefixes"] = dict(patterns["common_prefixes"].most_common(10))
 patterns["common_suffixes"] = dict(patterns["common_suffixes"].most_common(10))
 patterns["repeating_sequences"] = dict(patterns["repeating_sequences"].most_common(10))
 
 return patterns

def main():
 print("=" * 80)
 print("SEED MEANING ANALYSIS")
 print("=" * 80)
 print()
 print("WICHTIG: Nur echte, nachgewiesene Erkenntnisse!")
 print()
 
 # Load Layer-1 Seeds
 layer1_seeds = [
 "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr",
 "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn",
 "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml",
 "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb",
 "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw",
 "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc",
 ]
 
 # Load Layer-2 Identities und leite Seeds ab
 layer2_identities = [
 "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 ]
 
 layer2_seeds = [identity_to_seed(id) for id in layer2_identities if identity_to_seed(id)]
 
 print(f"Layer-1 Seeds: {len(layer1_seeds)}")
 print(f"Layer-2 Seeds: {len(layer2_seeds)}")
 print()
 
 # Analysen
 print("=" * 80)
 print("SEED STRUCTURE ANALYSIS")
 print("=" * 80)
 print()
 
 all_seeds = layer1_seeds + layer2_seeds
 structure_analysis = analyze_seed_structure(all_seeds)
 
 print(f"Lengths: {dict(structure_analysis['lengths'])}")
 print(f"Character set: {''.join(structure_analysis['character_set'])}")
 print(f"Unique characters: {len(structure_analysis['character_set'])}")
 print()
 
 print("Position analysis (first 10 positions):")
 for pos, data in list(structure_analysis["position_analysis"].items())[:10]:
 print(f" Position {pos}: {data['most_common'][:3]}")
 print()
 
 print("=" * 80)
 print("LAYER COMPARISON")
 print("=" * 80)
 print()
 
 comparison = compare_seed_sets(layer1_seeds, layer2_seeds)
 
 print("=" * 80)
 print("PATTERN ANALYSIS")
 print("=" * 80)
 print()
 
 pattern_analysis = analyze_seed_patterns(all_seeds)
 
 print("Common prefixes (top 5):")
 for prefix, count in list(pattern_analysis["common_prefixes"].items())[:5]:
 print(f" '{prefix}': {count} times")
 print()
 
 print("Common suffixes (top 5):")
 for suffix, count in list(pattern_analysis["common_suffixes"].items())[:5]:
 print(f" '{suffix}': {count} times")
 print()
 
 print("Repeating sequences (top 5):")
 for seq, count in list(pattern_analysis["repeating_sequences"].items())[:5]:
 print(f" '{seq}': {count} times")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 results = {
 "layer1_seeds": layer1_seeds,
 "layer2_seeds": layer2_seeds,
 "structure_analysis": {
 "lengths": dict(structure_analysis["lengths"]),
 "character_set": structure_analysis["character_set"],
 "position_analysis": {str(k): v for k, v in structure_analysis["position_analysis"].items()},
 },
 "comparison": comparison,
 "pattern_analysis": pattern_analysis,
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# Seed Meaning Analysis\n\n")
 f.write("## Structure Analysis\n\n")
 f.write(f"- **Lengths**: {dict(structure_analysis['lengths'])}\n")
 f.write(f"- **Character set**: `{''.join(structure_analysis['character_set'])}`\n")
 f.write(f"- **Unique characters**: {len(structure_analysis['character_set'])}\n\n")
 
 f.write("## Layer Comparison\n\n")
 f.write(f"- **Layer-1 Seeds**: {comparison['layer1_count']}\n")
 f.write(f"- **Layer-2 Seeds**: {comparison['layer2_count']}\n")
 f.write(f"- **Common Seeds**: {len(comparison['common_seeds'])}\n\n")
 
 if comparison["common_seeds"]:
 f.write("### ⚠️ WICHTIG: Common Seeds Found\n\n")
 for seed in comparison["common_seeds"]:
 f.write(f"- `{seed}`\n")
 f.write("\n")
 
 f.write("## Pattern Analysis\n\n")
 f.write("### Common Prefixes\n\n")
 for prefix, count in list(pattern_analysis["common_prefixes"].items())[:10]:
 f.write(f"- `{prefix}`: {count} times\n")
 f.write("\n")
 
 print("=" * 80)
 print("✅ ANALYSIS COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")

if __name__ == "__main__":
 main()

