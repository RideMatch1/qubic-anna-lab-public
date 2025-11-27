#!/usr/bin/env python3
"""
Finde den Umrechnungscode: Matche 300+ gefundene Seeds/Private Keys zu den 7 echten Identities

Ziel: Finde heraus, wie man von einem Seed/Private Key zu einer Identity kommt
"""

import sys
sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "conversion_code_analysis.json"

# Die 7 ECHTEN Identities (vom Benutzer bestätigt)
REAL_IDENTITIES = {
 "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI": {
 "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb",
 "label": "Vortex #2",
 },
 "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL": {
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml",
 "label": "Vortex #1",
 },
 "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN": {
 "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw",
 "label": "Vortex #3",
 },
 "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI": {
 "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 "label": "Diagonal #4",
 },
 "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB": {
 "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc",
 "label": "Vortex #4",
 },
 "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE": {
 "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr",
 "label": "Diagonal #2",
 },
 "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD": {
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "label": "Diagonal #1",
 },
}

def derive_identity_from_seed(seed: str) -> Optional[str]:
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
 return None

def load_all_seeds() -> List[Dict]:
 """Load alle gefundenen Seeds aus verschiedenen Dateien."""
 all_seeds = []
 seen_seeds = set() # Deduplizierung
 
 # Liste aller möglichen Dateien
 seed_files = [
 "all_possible_seeds.json",
 "mass_seed_derivation_optimized.json",
 "seed_derivation_mass_scan.json",
 "layer1_seeds.json",
 "seed_pattern_analysis.json",
 "matrix_seed_mapping.json",
 "seed_delta_analysis.json",
 ]
 
 for filename in seed_files:
 file_path = OUTPUT_DIR / filename
 if not file_path.exists():
 continue
 
 try:
 with file_path.open() as f:
 data = json.load(f)
 
 # Verschiedene Datenstrukturen handhaben
 items = []
 
 if isinstance(data, list):
 items = data
 elif isinstance(data, dict):
 # Versuche verschiedene Keys
 for key in ["seeds", "results", "identities", "data", "layer1", "layer2", "layer3"]:
 if key in data:
 val = data[key]
 if isinstance(val, list):
 items.extend(val)
 elif isinstance(val, dict):
 # Wenn es ein Dict von Dicts ist
 for subkey, subval in val.items():
 if isinstance(subval, dict):
 items.append(subval)
 elif isinstance(subval, str) and len(subval) == 55:
 items.append({"seed": subval})
 
 # Extrahiere Seeds
 for item in items:
 seed = None
 
 if isinstance(item, str) and len(item) == 55:
 seed = item
 elif isinstance(item, dict):
 seed = item.get("seed") or item.get("seed_candidate") or item.get("private_seed") or item.get("layer2_seed") or item.get("layer3_seed")
 
 if seed and len(seed) == 55 and seed not in seen_seeds:
 seen_seeds.add(seed)
 all_seeds.append({"seed": seed, "source": filename})
 
 except Exception as e:
 print(f"⚠️ Error loading {filename}: {e}")
 continue
 
 return all_seeds

def find_matching_seeds(all_seeds: List[Dict], real_identities: Dict) -> Dict:
 """Finde Seeds, die zu den echten Identities matchen."""
 matches = {}
 
 print("=" * 80)
 print("MATCHING SEEDS TO REAL IDENTITIES")
 print("=" * 80)
 print()
 
 # Teste jeden gefundenen Seed
 for i, seed_data in enumerate(all_seeds):
 if i % 100 == 0:
 print(f"Progress: {i}/{len(all_seeds)} seeds tested...")
 
 # Extrahiere Seed
 seed = None
 if isinstance(seed_data, str):
 seed = seed_data
 elif isinstance(seed_data, dict):
 seed = seed_data.get("seed") or seed_data.get("seed_candidate") or seed_data.get("private_seed")
 
 if not seed or len(seed) != 55:
 continue
 
 # Derive Identity
 derived_identity = derive_identity_from_seed(seed)
 if not derived_identity:
 continue
 
 # Check ob es zu einer echten Identity passt
 if derived_identity in real_identities:
 real_info = real_identities[derived_identity]
 expected_seed = real_info["seed"]
 
 if seed == expected_seed:
 matches[derived_identity] = {
 "seed": seed,
 "label": real_info["label"],
 "source": seed_data,
 "match_type": "exact",
 }
 print(f"✅ MATCH: {real_info['label']}")
 print(f" Seed: {seed[:30]}...")
 print(f" Identity: {derived_identity}")
 print()
 
 return matches

def analyze_conversion_pattern(matches: Dict, all_seeds: List[Dict]) -> Dict:
 """Analyze das Umrechnungsmuster."""
 print("=" * 80)
 print("CONVERSION PATTERN ANALYSIS")
 print("=" * 80)
 print()
 
 analysis = {
 "matches_found": len(matches),
 "conversion_method": "standard_qubic_derivation",
 "pattern": {},
 }
 
 # Teste die Standard-Derivation
 print("Testing standard Qubic derivation:")
 print()
 
 for identity, match_info in matches.items():
 seed = match_info["seed"]
 label = match_info["label"]
 
 derived = derive_identity_from_seed(seed)
 if derived == identity:
 print(f"✅ {label}: Standard derivation works")
 print(f" Seed -> Subseed -> Private Key -> Public Key -> Identity")
 else:
 print(f"❌ {label}: Standard derivation failed")
 print(f" Expected: {identity}")
 print(f" Got: {derived}")
 
 return analysis

def main():
 print("=" * 80)
 print("FIND CONVERSION CODE")
 print("=" * 80)
 print()
 print(f"Real Identities: {len(REAL_IDENTITIES)}")
 print()
 
 # Load alle Seeds
 print("Loading all found seeds...")
 all_seeds = load_all_seeds()
 print(f"✅ Loaded {len(all_seeds)} seed candidates")
 print()
 
 # Finde Matches
 matches = find_matching_seeds(all_seeds, REAL_IDENTITIES)
 
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 print(f"Matches found: {len(matches)}/{len(REAL_IDENTITIES)}")
 print()
 
 # Analyze Pattern
 analysis = analyze_conversion_pattern(matches, all_seeds)
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 results = {
 "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
 "real_identities": REAL_IDENTITIES,
 "matches": matches,
 "analysis": analysis,
 "total_seeds_tested": len(all_seeds),
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(results, f, indent=2, ensure_ascii=False)
 
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print()
 
 if len(matches) == len(REAL_IDENTITIES):
 print("✅ ALL MATCHES FOUND!")
 print(" The conversion code is: Standard Qubic derivation")
 print(" Seed -> Subseed -> Private Key -> Public Key -> Identity")
 else:
 print(f"⚠️ Only {len(matches)}/{len(REAL_IDENTITIES)} matches found")
 print(" Need to investigate further...")

if __name__ == "__main__":
 main()

