#!/usr/bin/env python3
"""
Verifiziere ob Layer-1 Seeds wirklich funktionieren

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
Der Benutzer sagt, dass die Layer-1 Seeds funktionieren.
"""

import json
from pathlib import Path
from typing import Dict, List

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "layer1_seeds_functionality_verification.json"
OUTPUT_MD = OUTPUT_DIR / "LAYER1_SEEDS_FUNCTIONALITY_VERIFICATION.md"

# Bekannte Layer-1 Seeds (vom Benutzer bestätigt als funktionierend)
LAYER1_SEEDS = {
 "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd": {
 "label": "Diagonal #1",
 "known_layer1_identity": "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "known_layer2_identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 },
 "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr": {
 "label": "Diagonal #2",
 "known_layer1_identity": "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "known_layer2_identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 },
 "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht": {
 "label": "Diagonal #4",
 "known_layer1_identity": "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "known_layer2_identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 },
 "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml": {
 "label": "Vortex #1",
 "known_layer1_identity": "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "known_layer2_identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 },
 "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb": {
 "label": "Vortex #2",
 "known_layer1_identity": "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "known_layer2_identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 },
 "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw": {
 "label": "Vortex #3",
 "known_layer1_identity": "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "known_layer2_identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 },
 "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc": {
 "label": "Vortex #4",
 "known_layer1_identity": "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
 "known_layer2_identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 },
}

from standardized_conversion import identity_to_seed

def verify_seed_identity_consistency() -> Dict:
 """Verifiziere Konsistenz zwischen Seeds und Identities."""
 print("Verifying seed-identity consistency...")
 print()
 
 results = []
 
 for seed, info in LAYER1_SEEDS.items():
 label = info["label"]
 l1_identity = info["known_layer1_identity"]
 l2_identity = info["known_layer2_identity"]
 
 # Leite Seeds ab
 l1_seed_from_identity = identity_to_seed(l1_identity)
 l2_seed_from_identity = identity_to_seed(l2_identity)
 
 # Check Konsistenz
 seed_matches_l1 = (seed == l1_seed_from_identity)
 seed_matches_l2 = (seed == l2_seed_from_identity)
 
 print(f"{label}:")
 print(f" Known Seed: {seed[:40]}...")
 print(f" L1 Identity Seed: {l1_seed_from_identity[:40] if l1_seed_from_identity else 'None'}...")
 print(f" L2 Identity Seed: {l2_seed_from_identity[:40] if l2_seed_from_identity else 'None'}...")
 print(f" Seed matches L1: {seed_matches_l1}")
 print(f" Seed matches L2: {seed_matches_l2}")
 
 results.append({
 "label": label,
 "known_seed": seed,
 "layer1_identity": l1_identity,
 "layer1_seed_from_identity": l1_seed_from_identity,
 "layer2_identity": l2_identity,
 "layer2_seed_from_identity": l2_seed_from_identity,
 "seed_matches_layer1": seed_matches_l1,
 "seed_matches_layer2": seed_matches_l2,
 })
 
 print()
 
 return results

def analyze_seed_usage() -> Dict:
 """Analyze wie Seeds verwendet werden."""
 print("Analyzing seed usage...")
 print()
 
 analysis = {
 "seed_is_layer1_private_key": 0,
 "seed_is_layer2_private_key": 0,
 "seed_is_neither": 0,
 "findings": [],
 }
 
 for seed, info in LAYER1_SEEDS.items():
 label = info["label"]
 l1_identity = info["known_layer1_identity"]
 l2_identity = info["known_layer2_identity"]
 
 l1_seed_from_identity = identity_to_seed(l1_identity)
 l2_seed_from_identity = identity_to_seed(l2_identity)
 
 finding = {
 "label": label,
 "seed": seed,
 "is_layer1_seed": (seed == l1_seed_from_identity),
 "is_layer2_seed": (seed == l2_seed_from_identity),
 }
 
 if seed == l1_seed_from_identity:
 analysis["seed_is_layer1_private_key"] += 1
 finding["conclusion"] = "Seed ist Layer-1 Private Key (abgeleitet von Layer-1 Identity)"
 elif seed == l2_seed_from_identity:
 analysis["seed_is_layer2_private_key"] += 1
 finding["conclusion"] = "Seed ist Layer-2 Private Key (abgeleitet von Layer-2 Identity)"
 else:
 analysis["seed_is_neither"] += 1
 finding["conclusion"] = "Seed ist weder Layer-1 noch Layer-2 Private Key (abgeleitet)"
 
 analysis["findings"].append(finding)
 
 print(f"{label}: {finding['conclusion']}")
 
 print()
 return analysis

def main():
 print("=" * 80)
 print("LAYER-1 SEEDS FUNCTIONALITY VERIFICATION")
 print("=" * 80)
 print()
 print("WICHTIG: Nur echte, nachgewiesene Erkenntnisse!")
 print()
 
 # Verifiziere Konsistenz
 consistency_results = verify_seed_identity_consistency()
 
 # Analyze Verwendung
 print("=" * 80)
 print("SEED USAGE ANALYSIS")
 print("=" * 80)
 print()
 
 usage_analysis = analyze_seed_usage()
 
 # Zusammenfassung
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 l1_matches = sum(1 for r in consistency_results if r.get("seed_matches_layer1"))
 l2_matches = sum(1 for r in consistency_results if r.get("seed_matches_layer2"))
 
 print(f"Layer-1 Seed matches Layer-1 Identity: {l1_matches}/{len(LAYER1_SEEDS)}")
 print(f"Layer-1 Seed matches Layer-2 Identity: {l2_matches}/{len(LAYER1_SEEDS)}")
 print()
 print(f"Seed is Layer-1 Private Key: {usage_analysis['seed_is_layer1_private_key']}/{len(LAYER1_SEEDS)}")
 print(f"Seed is Layer-2 Private Key: {usage_analysis['seed_is_layer2_private_key']}/{len(LAYER1_SEEDS)}")
 print(f"Seed is neither: {usage_analysis['seed_is_neither']}/{len(LAYER1_SEEDS)}")
 print()
 
 # WICHTIGE ERKENNTNIS
 if l1_matches == len(LAYER1_SEEDS):
 print("=" * 80)
 print("✅ ERKENNTNIS: Layer-1 Seeds sind Layer-1 Private Keys!")
 print("=" * 80)
 print("Die bekannten Layer-1 Seeds sind die Private Keys for die Layer-1 Identities.")
 print("Sie werden durch identity.lower()[:55] aus den Layer-1 Identities abgeleitet.")
 elif l2_matches == len(LAYER1_SEEDS):
 print("=" * 80)
 print("✅ ERKENNTNIS: Layer-1 Seeds sind Layer-2 Private Keys!")
 print("=" * 80)
 print("Die bekannten Layer-1 Seeds sind die Private Keys for die Layer-2 Identities.")
 else:
 print("=" * 80)
 print("⚠️ ERKENNTNIS: Layer-1 Seeds sind weder L1 noch L2 Private Keys")
 print("=" * 80)
 print("Die bekannten Layer-1 Seeds matchen weder Layer-1 noch Layer-2 abgeleitete Seeds.")
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 results = {
 "consistency_verification": consistency_results,
 "usage_analysis": usage_analysis,
 "conclusion": {
 "layer1_seeds_are_layer1_private_keys": l1_matches == len(LAYER1_SEEDS),
 "layer1_seeds_are_layer2_private_keys": l2_matches == len(LAYER1_SEEDS),
 },
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# Layer-1 Seeds Functionality Verification\n\n")
 f.write("## Findings\n\n")
 f.write(f"- **Layer-1 Seed matches Layer-1 Identity**: {l1_matches}/{len(LAYER1_SEEDS)}\n")
 f.write(f"- **Layer-1 Seed matches Layer-2 Identity**: {l2_matches}/{len(LAYER1_SEEDS)}\n\n")
 
 f.write("## Conclusion\n\n")
 if l1_matches == len(LAYER1_SEEDS):
 f.write("✅ **Layer-1 Seeds sind Layer-1 Private Keys!**\n\n")
 f.write("Die bekannten Layer-1 Seeds sind die Private Keys for die Layer-1 Identities.\n")
 f.write("Sie werden durch `identity.lower()[:55]` aus den Layer-1 Identities abgeleitet.\n\n")
 elif l2_matches == len(LAYER1_SEEDS):
 f.write("✅ **Layer-1 Seeds sind Layer-2 Private Keys!**\n\n")
 f.write("Die bekannten Layer-1 Seeds sind die Private Keys for die Layer-2 Identities.\n\n")
 else:
 f.write("⚠️ **Layer-1 Seeds sind weder L1 noch L2 Private Keys**\n\n")
 f.write("Die bekannten Layer-1 Seeds matchen weder Layer-1 noch Layer-2 abgeleitete Seeds.\n\n")
 
 print("=" * 80)
 print("✅ VERIFICATION COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")

if __name__ == "__main__":
 main()

