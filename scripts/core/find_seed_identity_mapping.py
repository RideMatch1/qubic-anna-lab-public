#!/usr/bin/env python3
"""
Finde Seed -> Identity Mapping in allen Dateien

Suche nach den bekannten Seeds und check welche Identities daraus abgeleitet wurden
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "seed_identity_mapping_found.json"

# Die 7 bekannten Seeds
KNOWN_SEEDS = {
 "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd": "Diagonal #1",
 "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr": "Diagonal #2",
 "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht": "Diagonal #4",
 "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml": "Vortex #1",
 "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb": "Vortex #2",
 "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw": "Vortex #3",
 "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc": "Vortex #4",
}

# Die 7 erwarteten Identities
EXPECTED_IDENTITIES = {
 "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD": "Diagonal #1",
 "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE": "Diagonal #2",
 "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI": "Diagonal #4",
 "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL": "Vortex #1",
 "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI": "Vortex #2",
 "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN": "Vortex #3",
 "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB": "Vortex #4",
}

def search_in_file(file_path: Path) -> List[Dict]:
 """Suche in einer Datei nach Seeds und Identities."""
 results = []
 
 if not file_path.exists():
 return results
 
 try:
 with file_path.open() as f:
 data = json.load(f)
 
 # Rekursiv durch die Datenstruktur gehen
 def search_recursive(obj, path=""):
 if isinstance(obj, dict):
 # Check ob Seed und Identity zusammen vorkommen
 seed = None
 identity = None
 
 for key, value in obj.items():
 if isinstance(value, str):
 if len(value) == 55 and value.islower() and value.isalpha():
 seed = value
 elif len(value) == 60 and value.isupper():
 identity = value
 
 # Rekursiv weitersuchen
 search_recursive(value, f"{path}.{key}")
 
 # Wenn Seed gefunden, check ob Identity auch da ist
 if seed and seed in KNOWN_SEEDS:
 # Suche nach Identity im gleichen Objekt
 for key, value in obj.items():
 if isinstance(value, str) and len(value) == 60 and value.isupper():
 identity = value
 break
 
 if identity:
 results.append({
 "seed": seed,
 "label": KNOWN_SEEDS[seed],
 "identity": identity,
 "expected_identity": None, # Will später gefüllt
 "match": False,
 "source_file": str(file_path),
 "path": path,
 })
 
 elif isinstance(obj, list):
 for i, item in enumerate(obj):
 search_recursive(item, f"{path}[{i}]")
 
 search_recursive(data)
 
 except Exception as e:
 pass
 
 return results

def main():
 print("=" * 80)
 print("FIND SEED -> IDENTITY MAPPING")
 print("=" * 80)
 print()
 
 # Suche in allen JSON-Dateien
 json_files = list(OUTPUT_DIR.glob("*.json"))
 
 print(f"Searching in {len(json_files)} files...")
 print()
 
 all_results = []
 
 for json_file in json_files:
 results = search_in_file(json_file)
 if results:
 print(f"✅ {json_file.name}: {len(results)} matches")
 all_results.extend(results)
 
 print()
 print(f"Total matches: {len(all_results)}")
 print()
 
 # Check ob die Identities zu den erwarteten passen
 print("=" * 80)
 print("MATCHING TO EXPECTED IDENTITIES")
 print("=" * 80)
 print()
 
 for result in all_results:
 seed = result["seed"]
 identity = result["identity"]
 label = result["label"]
 
 # Finde erwartete Identity
 expected_identity = None
 for exp_id, exp_label in EXPECTED_IDENTITIES.items():
 if exp_label == label:
 expected_identity = exp_id
 break
 
 result["expected_identity"] = expected_identity
 result["match"] = (identity == expected_identity)
 
 print(f"{label}:")
 print(f" Seed: {seed[:30]}...")
 print(f" Found Identity: {identity}")
 print(f" Expected Identity: {expected_identity}")
 
 if result["match"]:
 print(f" ✅ MATCH!")
 else:
 print(f" ❌ NO MATCH")
 
 print(f" Source: {result['source_file']}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_JSON.open("w") as f:
 json.dump(all_results, f, indent=2)
 
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 matches = [r for r in all_results if r.get("match")]
 print(f"Matches: {len(matches)}/{len(all_results)}")
 
 if matches:
 print()
 print("✅ GEFUNDENE MATCHES:")
 for match in matches:
 print(f" {match['label']}: {match['seed'][:30]}... -> {match['identity']}")
 print(f" Source: {match['source_file']}")
 
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
 main()

