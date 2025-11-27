#!/usr/bin/env python3
"""
Teste direkt: Seed -> Identity Conversion

Check ob die bekannten Seeds zu den echten Identities führen
"""

import sys
sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")

import json
from pathlib import Path

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "seed_to_identity_conversion_test.json"

# Die 7 ECHTEN Identities mit ihren Seeds
REAL_MAPPINGS = [
 {
 "label": "Diagonal #1",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "expected_identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 },
 {
 "label": "Diagonal #2",
 "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr",
 "expected_identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 },
 {
 "label": "Diagonal #4",
 "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 "expected_identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 },
 {
 "label": "Vortex #1",
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml",
 "expected_identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 },
 {
 "label": "Vortex #2",
 "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb",
 "expected_identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 },
 {
 "label": "Vortex #3",
 "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw",
 "expected_identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 },
 {
 "label": "Vortex #4",
 "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc",
 "expected_identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 },
]

def derive_identity_from_seed(seed: str):
 """Derive identity from seed using native crypto functions."""
 try:
 from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
 )
 
 seed_bytes = seed.encode('utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 identity = get_identity_from_public_key(public_key)
 return identity
 except Exception as e:
 return None, str(e)

def main():
 print("=" * 80)
 print("SEED TO IDENTITY CONVERSION TEST")
 print("=" * 80)
 print()
 
 results = []
 
 for mapping in REAL_MAPPINGS:
 label = mapping["label"]
 seed = mapping["seed"]
 expected = mapping["expected_identity"]
 
 print(f"{label}:")
 print(f" Seed: {seed[:30]}...")
 print(f" Expected: {expected}")
 
 derived = derive_identity_from_seed(seed)
 
 if isinstance(derived, tuple):
 identity, error = derived
 if identity:
 derived = identity
 else:
 print(f" ❌ Error: {error}")
 results.append({
 "label": label,
 "seed": seed,
 "expected": expected,
 "derived": None,
 "match": False,
 "error": error,
 })
 continue
 else:
 identity = derived
 
 print(f" Derived: {identity}")
 
 match = (identity == expected)
 
 if match:
 print(f" ✅ MATCH!")
 else:
 print(f" ❌ NO MATCH")
 print(f" Difference: {identity != expected}")
 
 results.append({
 "label": label,
 "seed": seed,
 "expected": expected,
 "derived": identity,
 "match": match,
 })
 
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 matches = [r for r in results if r.get("match")]
 print(f"Matches: {len(matches)}/{len(results)}")
 print()
 
 if len(matches) == len(results):
 print("✅ ALLE SEEDS FUNKTIONIEREN!")
 print()
 print("Der Umrechnungscode ist:")
 print(" Seed -> Subseed -> Private Key -> Public Key -> Identity")
 print()
 print("Das ist die Standard Qubic Derivation!")
 else:
 print("⚠️ Nicht alle Seeds matchen")
 print()
 print("Probleme:")
 for r in results:
 if not r.get("match"):
 print(f" - {r['label']}: {r.get('error', 'No match')}")
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_JSON.open("w") as f:
 json.dump(results, f, indent=2)
 
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
 main()

