#!/usr/bin/env python3
"""
Tiefere Analyse des Umrechnungscodes

- Check ob abgeleitete Seeds wirklich funktionieren
- Finde Verbindungen zwischen Layer-1 und Layer-2
- Analyze weitere Muster
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "deep_conversion_analysis.json"
OUTPUT_MD = OUTPUT_DIR / "DEEP_CONVERSION_ANALYSIS.md"

# Import standardisierte Funktion
sys.path.insert(0, str(Path(__file__).parent))
from standardized_conversion import identity_to_seed, validate_identity, validate_seed

def load_layer_data() -> Dict:
 """Load Layer-1 und Layer-2 Daten."""
 data = {
 "layer1_identities": [],
 "layer1_seeds": {},
 "layer2_identities": [],
 "layer2_seeds": {},
 }
 
 # Layer-1 Seeds (bekannt)
 layer1_seeds = {
 "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd": "Diagonal #1",
 "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr": "Diagonal #2",
 "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn": "Diagonal #3",
 "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht": "Diagonal #4",
 "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml": "Vortex #1",
 "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb": "Vortex #2",
 "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw": "Vortex #3",
 "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc": "Vortex #4",
 }
 
 data["layer1_seeds"] = layer1_seeds
 
 # Layer-2 Identities (echt)
 layer2_identities = [
 "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 ]
 
 data["layer2_identities"] = layer2_identities
 
 # Layer-2 Seeds ableiten
 for identity in layer2_identities:
 seed = identity_to_seed(identity)
 if seed:
 data["layer2_seeds"][identity] = seed
 
 return data

def analyze_seed_relationships(layer_data: Dict) -> Dict:
 """Analyze Beziehungen zwischen Layer-1 und Layer-2 Seeds."""
 print("Analyzing seed relationships...")
 print()
 
 analysis = {
 "layer1_to_layer2_matches": [],
 "seed_similarities": [],
 "character_analysis": {},
 }
 
 layer1_seeds = set(layer_data["layer1_seeds"].keys())
 layer2_seeds = set(layer_data["layer2_seeds"].values())
 
 # Check ob Layer-2 Seeds zu Layer-1 Seeds passen
 for identity, seed in layer_data["layer2_seeds"].items():
 if seed in layer1_seeds:
 analysis["layer1_to_layer2_matches"].append({
 "layer2_identity": identity,
 "layer2_seed": seed,
 "layer1_label": layer_data["layer1_seeds"][seed],
 "match": True,
 })
 print(f"✅ {identity[:30]}... -> Seed matches Layer-1: {layer_data['layer1_seeds'][seed]}")
 else:
 # Analyze Ähnlichkeiten
 best_match = None
 best_similarity = 0
 
 for l1_seed in layer1_seeds:
 similarity = sum(1 for a, b in zip(seed, l1_seed) if a == b)
 if similarity > best_similarity:
 best_similarity = similarity
 best_match = l1_seed
 
 if best_match:
 analysis["seed_similarities"].append({
 "layer2_identity": identity,
 "layer2_seed": seed,
 "layer1_seed": best_match,
 "similarity": best_similarity,
 "similarity_percent": (best_similarity / 55) * 100,
 })
 
 print()
 return analysis

def analyze_character_patterns(layer_data: Dict) -> Dict:
 """Analyze Zeichenmuster in Seeds."""
 print("Analyzing character patterns...")
 print()
 
 all_seeds = list(layer_data["layer1_seeds"].keys()) + list(layer_data["layer2_seeds"].values())
 
 analysis = {
 "position_frequency": {},
 "common_prefixes": {},
 "common_suffixes": {},
 }
 
 # Position-Frequenz
 for pos in range(55):
 chars = [seed[pos] for seed in all_seeds if len(seed) > pos]
 char_freq = {}
 for char in chars:
 char_freq[char] = char_freq.get(char, 0) + 1
 analysis["position_frequency"][pos] = dict(sorted(char_freq.items(), key=lambda x: x[1], reverse=True)[:5])
 
 # Gemeinsame Präfixe
 prefixes = {}
 for seed in all_seeds:
 for length in [3, 5, 10]:
 prefix = seed[:length]
 prefixes[prefix] = prefixes.get(prefix, 0) + 1
 
 analysis["common_prefixes"] = dict(sorted(prefixes.items(), key=lambda x: x[1], reverse=True)[:10])
 
 # Gemeinsame Suffixe
 suffixes = {}
 for seed in all_seeds:
 for length in [3, 5, 10]:
 suffix = seed[-length:]
 suffixes[suffix] = suffixes.get(suffix, 0) + 1
 
 analysis["common_suffixes"] = dict(sorted(suffixes.items(), key=lambda x: x[1], reverse=True)[:10])
 
 return analysis

def find_derivation_patterns(layer_data: Dict) -> Dict:
 """Finde Muster in der Ableitung Layer-1 -> Layer-2."""
 print("Finding derivation patterns...")
 print()
 
 patterns = {
 "direct_matches": 0,
 "transformations": [],
 }
 
 # Check ob Layer-1 Seeds direkt zu Layer-2 Identities führen
 # (durch Identity -> Seed -> Identity Zyklus)
 
 for l1_seed, l1_label in layer_data["layer1_seeds"].items():
 # Wenn dieser Seed eine Identity wäre, was wäre der abgeleitete Seed?
 # (Das ist hypothetisch, da Seeds nicht direkt zu Identities werden)
 pass
 
 return patterns

def main():
 print("=" * 80)
 print("DEEP CONVERSION ANALYSIS")
 print("=" * 80)
 print()
 
 # Load Daten
 layer_data = load_layer_data()
 
 print(f"Layer-1 Seeds: {len(layer_data['layer1_seeds'])}")
 print(f"Layer-2 Identities: {len(layer_data['layer2_identities'])}")
 print(f"Layer-2 Seeds (derived): {len(layer_data['layer2_seeds'])}")
 print()
 
 # Analysen
 print("=" * 80)
 print("SEED RELATIONSHIPS")
 print("=" * 80)
 print()
 
 seed_relationships = analyze_seed_relationships(layer_data)
 
 print("=" * 80)
 print("CHARACTER PATTERNS")
 print("=" * 80)
 print()
 
 character_patterns = analyze_character_patterns(layer_data)
 
 print("=" * 80)
 print("DERIVATION PATTERNS")
 print("=" * 80)
 print()
 
 derivation_patterns = find_derivation_patterns(layer_data)
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 results = {
 "layer_data": layer_data,
 "seed_relationships": seed_relationships,
 "character_patterns": character_patterns,
 "derivation_patterns": derivation_patterns,
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# Deep Conversion Analysis\n\n")
 f.write("## Seed Relationships\n\n")
 f.write(f"- Layer-1 to Layer-2 matches: {len(seed_relationships['layer1_to_layer2_matches'])}\n")
 f.write(f"- Seed similarities found: {len(seed_relationships['seed_similarities'])}\n\n")
 
 if seed_relationships['layer1_to_layer2_matches']:
 f.write("### Direct Matches\n\n")
 for match in seed_relationships['layer1_to_layer2_matches']:
 f.write(f"- {match['layer2_identity'][:40]}...\n")
 f.write(f" - Seed: `{match['layer2_seed']}`\n")
 f.write(f" - Matches Layer-1: {match['layer1_label']}\n\n")
 
 if seed_relationships['seed_similarities']:
 f.write("### Similar Seeds\n\n")
 for sim in seed_relationships['seed_similarities'][:5]:
 f.write(f"- Layer-2 Seed: `{sim['layer2_seed']}`\n")
 f.write(f" - Most similar Layer-1: `{sim['layer1_seed']}`\n")
 f.write(f" - Similarity: {sim['similarity']}/55 ({sim['similarity_percent']:.1f}%)\n\n")
 
 print("=" * 80)
 print("✅ ANALYSIS COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")

if __name__ == "__main__":
 main()

