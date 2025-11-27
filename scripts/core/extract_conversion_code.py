#!/usr/bin/env python3
"""
Extrahiere den Umrechnungscode aus mass_seed_derivation_optimized.json

Die Datei enthält Mappings von Identities zu Seeds und umgekehrt.
"""

import json
from pathlib import Path

OUTPUT_DIR = Path("outputs/derived")
INPUT_FILE = OUTPUT_DIR / "mass_seed_derivation_optimized.json"
OUTPUT_JSON = OUTPUT_DIR / "conversion_code_extracted.json"

# Die 7 echten Identities
REAL_IDENTITIES = [
 "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
]

# Die 7 bekannten Seeds (Layer-1)
KNOWN_SEEDS = {
 "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd": "Diagonal #1",
 "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr": "Diagonal #2",
 "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht": "Diagonal #4",
 "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml": "Vortex #1",
 "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb": "Vortex #2",
 "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw": "Vortex #3",
 "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc": "Vortex #4",
}

def main():
 print("=" * 80)
 print("EXTRACT CONVERSION CODE")
 print("=" * 80)
 print()
 
 if not INPUT_FILE.exists():
 print(f"❌ File not found: {INPUT_FILE}")
 return
 
 with INPUT_FILE.open() as f:
 data = json.load(f)
 
 # Suche nach identity_to_seed mapping
 identity_to_seed = {}
 seed_to_identity = {}
 
 # Check verschiedene Strukturen
 if isinstance(data, dict):
 # Suche nach identity_to_seed mapping (Identity -> lowercase seed)
 for key, value in data.items():
 if isinstance(key, str) and len(key) == 60 and key.isupper():
 if isinstance(value, str) and len(value) == 55 and value.islower():
 identity_to_seed[key] = value
 
 # Suche nach seed_to_identity mapping (Seed -> Identity)
 for key, value in data.items():
 if isinstance(key, str) and len(key) == 55 and key.islower():
 if isinstance(value, str) and len(value) == 60 and value.isupper():
 seed_to_identity[key] = value
 
 print(f"Found {len(identity_to_seed)} identity -> seed mappings")
 print(f"Found {len(seed_to_identity)} seed -> identity mappings")
 print()
 
 # Check die echten Identities
 print("=" * 80)
 print("CHECKING REAL IDENTITIES")
 print("=" * 80)
 print()
 
 results = []
 
 for identity in REAL_IDENTITIES:
 # Methode 1: Identity -> Seed (lowercase)
 seed_from_identity = identity_to_seed.get(identity)
 
 # Methode 2: Identity lowercase -> Seed
 identity_lower = identity.lower()
 if len(identity_lower) == 60:
 # Nimm nur die ersten 55 Zeichen
 seed_from_lower = identity_lower[:55]
 else:
 seed_from_lower = None
 
 print(f"Identity: {identity}")
 print(f" Method 1 (direct mapping): {seed_from_identity}")
 print(f" Method 2 (lowercase[:55]): {seed_from_lower}")
 
 # Check ob dieser Seed zu einer Identity führt
 if seed_from_identity:
 derived_identity = seed_to_identity.get(seed_from_identity)
 print(f" Derived Identity: {derived_identity}")
 print(f" Match: {derived_identity == identity}")
 
 if seed_from_lower:
 derived_identity2 = seed_to_identity.get(seed_from_lower)
 print(f" Derived Identity (Method 2): {derived_identity2}")
 print(f" Match: {derived_identity2 == identity}")
 
 results.append({
 "identity": identity,
 "seed_from_mapping": seed_from_identity,
 "seed_from_lowercase": seed_from_lower,
 "derived_identity_method1": seed_to_identity.get(seed_from_identity) if seed_from_identity else None,
 "derived_identity_method2": seed_to_identity.get(seed_from_lower) if seed_from_lower else None,
 })
 
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("CONVERSION CODE SUMMARY")
 print("=" * 80)
 print()
 
 print("Method 1: Identity -> Seed (via mapping)")
 method1_matches = sum(1 for r in results if r["derived_identity_method1"] == r["identity"])
 print(f" Matches: {method1_matches}/{len(results)}")
 print()
 
 print("Method 2: Identity -> lowercase[:55] -> Seed")
 method2_matches = sum(1 for r in results if r["derived_identity_method2"] == r["identity"])
 print(f" Matches: {method2_matches}/{len(results)}")
 print()
 
 if method1_matches == len(results):
 print("✅ Method 1 works for all identities!")
 print(" Conversion: Identity -> Lookup in mapping -> Seed")
 elif method2_matches == len(results):
 print("✅ Method 2 works for all identities!")
 print(" Conversion: Identity -> lowercase -> [:55] -> Seed")
 else:
 print("⚠️ Need to investigate further...")
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 final_results = {
 "conversion_methods": {
 "method1": "Identity -> Mapping lookup -> Seed",
 "method2": "Identity -> lowercase -> [:55] -> Seed",
 },
 "identity_to_seed_mappings": len(identity_to_seed),
 "seed_to_identity_mappings": len(seed_to_identity),
 "real_identities_analysis": results,
 "sample_mappings": {
 "identity_to_seed": dict(list(identity_to_seed.items())[:10]),
 "seed_to_identity": dict(list(seed_to_identity.items())[:10]),
 },
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(final_results, f, indent=2)
 
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
 main()

