#!/usr/bin/env python3
"""
Finde die Verbindung zwischen Layer-1 Seeds und Layer-2 Identities

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "layer1_to_layer2_connection.json"
OUTPUT_MD = OUTPUT_DIR / "LAYER1_TO_LAYER2_CONNECTION.md"

# Bekannte Layer-1 Seeds (vom Benutzer bestätigt)
LAYER1_SEEDS = {
 "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd": {
 "label": "Diagonal #1",
 "known_layer1_identity": "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 },
 "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr": {
 "label": "Diagonal #2",
 "known_layer1_identity": "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 },
 "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn": {
 "label": "Diagonal #3",
 "known_layer1_identity": "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 },
 "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht": {
 "label": "Diagonal #4",
 "known_layer1_identity": "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 },
 "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml": {
 "label": "Vortex #1",
 "known_layer1_identity": "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 },
 "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb": {
 "label": "Vortex #2",
 "known_layer1_identity": "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 },
 "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw": {
 "label": "Vortex #3",
 "known_layer1_identity": "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 },
 "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc": {
 "label": "Vortex #4",
 "known_layer1_identity": "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
 },
}

# Echte Layer-2 Identities
LAYER2_IDENTITIES = {
 "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD": "Diagonal #1",
 "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE": "Diagonal #2",
 "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI": "Diagonal #4",
 "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL": "Vortex #1",
 "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI": "Vortex #2",
 "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN": "Vortex #3",
 "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB": "Vortex #4",
}

from standardized_conversion import identity_to_seed

def analyze_identity_relationships() -> Dict:
 """Analyze Beziehungen zwischen Layer-1 und Layer-2 Identities."""
 print("Analyzing identity relationships...")
 print()
 
 results = []
 
 for l1_seed, l1_info in LAYER1_SEEDS.items():
 l1_label = l1_info["label"]
 l1_identity = l1_info["known_layer1_identity"]
 
 # Finde entsprechende Layer-2 Identity
 l2_identity = None
 for id, label in LAYER2_IDENTITIES.items():
 if label == l1_label:
 l2_identity = id
 break
 
 if not l2_identity:
 continue
 
 # Leite Seeds ab
 l1_seed_from_identity = identity_to_seed(l1_identity)
 l2_seed_from_identity = identity_to_seed(l2_identity)
 
 print(f"{l1_label}:")
 print(f" Layer-1 Identity: {l1_identity[:40]}...")
 print(f" Layer-1 Seed (known): {l1_seed[:40]}...")
 print(f" Layer-1 Seed (from identity): {l1_seed_from_identity[:40] if l1_seed_from_identity else 'None'}...")
 print(f" Layer-2 Identity: {l2_identity[:40]}...")
 print(f" Layer-2 Seed (from identity): {l2_seed_from_identity[:40] if l2_seed_from_identity else 'None'}...")
 
 # Check ob Layer-1 Seed zu Layer-2 Identity führt
 seed_matches = (l1_seed == l1_seed_from_identity)
 print(f" Layer-1 Seed matches identity-derived: {seed_matches}")
 
 # Check Ähnlichkeiten
 if l1_seed_from_identity and l2_seed_from_identity:
 similarity = sum(1 for a, b in zip(l1_seed_from_identity, l2_seed_from_identity) if a == b)
 similarity_pct = (similarity / 55) * 100
 print(f" Seed similarity (L1 vs L2): {similarity}/55 ({similarity_pct:.1f}%)")
 
 results.append({
 "label": l1_label,
 "layer1_seed_known": l1_seed,
 "layer1_identity": l1_identity,
 "layer1_seed_from_identity": l1_seed_from_identity,
 "layer2_identity": l2_identity,
 "layer2_seed_from_identity": l2_seed_from_identity,
 "seed_matches": seed_matches,
 "seed_similarity": similarity if l1_seed_from_identity and l2_seed_from_identity else None,
 })
 
 print()
 
 return results

def find_transformation_pattern() -> Dict:
 """Versuche Transformationsmuster zu finden."""
 print("Searching for transformation patterns...")
 print()
 
 patterns = {
 "character_shifts": [],
 "position_changes": [],
 "substitutions": [],
 }
 
 for l1_seed, l1_info in LAYER1_SEEDS.items():
 l1_label = l1_info["label"]
 
 # Finde Layer-2 Identity
 l2_identity = None
 for id, label in LAYER2_IDENTITIES.items():
 if label == l1_label:
 l2_identity = id
 break
 
 if not l2_identity:
 continue
 
 l2_seed = identity_to_seed(l2_identity)
 
 if not l2_seed:
 continue
 
 # Analyze Unterschiede
 differences = []
 for i, (c1, c2) in enumerate(zip(l1_seed, l2_seed)):
 if c1 != c2:
 diff = ord(c2) - ord(c1)
 differences.append({
 "position": i,
 "l1_char": c1,
 "l2_char": c2,
 "shift": diff,
 })
 
 if differences:
 print(f"{l1_label}: {len(differences)} differences")
 print(f" First 5: {differences[:5]}")
 patterns["character_shifts"].append({
 "label": l1_label,
 "differences": differences,
 })
 print()
 
 return patterns

def main():
 print("=" * 80)
 print("LAYER-1 TO LAYER-2 CONNECTION ANALYSIS")
 print("=" * 80)
 print()
 print("WICHTIG: Nur echte, nachgewiesene Erkenntnisse!")
 print()
 
 # Analyze Beziehungen
 relationships = analyze_identity_relationships()
 
 # Suche Transformationsmuster
 print("=" * 80)
 print("TRANSFORMATION PATTERNS")
 print("=" * 80)
 print()
 
 transformation_patterns = find_transformation_pattern()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 results = {
 "relationships": relationships,
 "transformation_patterns": transformation_patterns,
 "findings": {
 "layer1_seeds_match_identity_derived": sum(1 for r in relationships if r.get("seed_matches")),
 "total_relationships": len(relationships),
 },
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# Layer-1 to Layer-2 Connection Analysis\n\n")
 f.write("## Findings\n\n")
 f.write(f"- **Total relationships analyzed**: {len(relationships)}\n")
 f.write(f"- **Layer-1 seeds match identity-derived**: {results['findings']['layer1_seeds_match_identity_derived']}/{len(relationships)}\n\n")
 
 f.write("## Relationships\n\n")
 for rel in relationships:
 f.write(f"### {rel['label']}\n\n")
 f.write(f"- Layer-1 Seed (known): `{rel['layer1_seed_known']}`\n")
 f.write(f"- Layer-1 Seed (from identity): `{rel['layer1_seed_from_identity']}`\n")
 f.write(f"- Layer-2 Seed (from identity): `{rel['layer2_seed_from_identity']}`\n")
 f.write(f"- Seeds match: {rel['seed_matches']}\n")
 if rel.get("seed_similarity") is not None:
 f.write(f"- Seed similarity: {rel['seed_similarity']}/55 ({(rel['seed_similarity']/55)*100:.1f}%)\n")
 f.write("\n")
 
 print("=" * 80)
 print("✅ ANALYSIS COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")

if __name__ == "__main__":
 main()

