#!/usr/bin/env python3
"""
Crypto-Validierung: Check ob abgeleitete Seeds wirklich funktionieren

WICHTIG: Nur echte, nachgewiesene Ergebnisse - kein LLM Bias!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "crypto_validation_seeds.json"
OUTPUT_MD = OUTPUT_DIR / "CRYPTO_VALIDATION_SEEDS_REPORT.md"

# Import standardisierte Funktion
sys.path.insert(0, str(Path(__file__).parent))
from standardized_conversion import identity_to_seed

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """
 Derive identity from seed using native crypto functions.
 
 Returns: Identity oder None bei Fehler
 """
 try:
 sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")
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

def validate_seed_to_identity(seed: str, expected_identity: str) -> Dict:
 """
 Validate: Seed -> Identity (mit crypto functions)
 
 Returns: {
 "seed": seed,
 "expected_identity": expected_identity,
 "derived_identity": derived_identity,
 "match": bool,
 "error": error_message or None
 }
 """
 result = {
 "seed": seed,
 "expected_identity": expected_identity,
 "derived_identity": None,
 "match": False,
 "error": None,
 }
 
 try:
 derived = derive_identity_from_seed(seed)
 result["derived_identity"] = derived
 
 if derived:
 result["match"] = (derived == expected_identity)
 else:
 result["error"] = "Derivation returned None"
 except Exception as e:
 result["error"] = str(e)
 
 return result

def test_real_layer2_seeds() -> Dict:
 """Teste die 7 echten Layer-2 Seeds."""
 print("=" * 80)
 print("CRYPTO VALIDATION: REAL LAYER-2 SEEDS")
 print("=" * 80)
 print()
 
 real_layer2 = [
 {
 "identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 "label": "Diagonal #1",
 },
 {
 "identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 "label": "Diagonal #2",
 },
 {
 "identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 "label": "Diagonal #4",
 },
 {
 "identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 "label": "Vortex #1",
 },
 {
 "identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 "label": "Vortex #2",
 },
 {
 "identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 "label": "Vortex #3",
 },
 {
 "identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 "label": "Vortex #4",
 },
 ]
 
 results = []
 
 for item in real_layer2:
 identity = item["identity"]
 label = item["label"]
 
 # Ableiten Seed
 seed = identity_to_seed(identity)
 
 print(f"{label}:")
 print(f" Identity: {identity}")
 print(f" Derived Seed: {seed}")
 
 if not seed:
 print(f" ❌ Seed derivation failed")
 results.append({
 "label": label,
 "identity": identity,
 "seed": None,
 "validation": None,
 "error": "Seed derivation failed",
 })
 print()
 continue
 
 # Validate: Seed -> Identity
 validation = validate_seed_to_identity(seed, identity)
 results.append({
 "label": label,
 "identity": identity,
 "seed": seed,
 "validation": validation,
 })
 
 if validation["error"]:
 print(f" ⚠️ Crypto error: {validation['error']}")
 elif validation["derived_identity"]:
 print(f" Derived Identity: {validation['derived_identity']}")
 if validation["match"]:
 print(f" ✅ MATCH! Seed führt zu Identity")
 else:
 print(f" ❌ NO MATCH")
 print(f" Expected: {identity}")
 print(f" Got: {validation['derived_identity']}")
 else:
 print(f" ❌ Derivation returned None")
 
 print()
 
 return {
 "test_type": "real_layer2_seeds",
 "total": len(real_layer2),
 "results": results,
 }

def test_known_layer1_seeds() -> Dict:
 """Teste bekannte Layer-1 Seeds (zum Vergleich)."""
 print("=" * 80)
 print("CRYPTO VALIDATION: KNOWN LAYER-1 SEEDS (COMPARISON)")
 print("=" * 80)
 print()
 
 known_layer1 = {
 "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd": "Diagonal #1",
 "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr": "Diagonal #2",
 "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn": "Diagonal #3",
 "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht": "Diagonal #4",
 "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml": "Vortex #1",
 "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb": "Vortex #2",
 "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw": "Vortex #3",
 "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc": "Vortex #4",
 }
 
 results = []
 
 for seed, label in known_layer1.items():
 print(f"{label}:")
 print(f" Seed: {seed}")
 
 # Derive Identity
 derived_identity = derive_identity_from_seed(seed)
 
 results.append({
 "label": label,
 "seed": seed,
 "derived_identity": derived_identity,
 })
 
 if derived_identity:
 print(f" Derived Identity: {derived_identity}")
 print(f" ✅ Derivation successful")
 else:
 print(f" ❌ Derivation failed")
 
 print()
 
 return {
 "test_type": "known_layer1_seeds",
 "total": len(known_layer1),
 "results": results,
 }

def main():
 print("=" * 80)
 print("CRYPTO VALIDATION: SEED TO IDENTITY")
 print("=" * 80)
 print()
 print("WICHTIG: Nur echte, nachgewiesene Ergebnisse!")
 print()
 
 # Test 1: Echte Layer-2 Seeds
 layer2_results = test_real_layer2_seeds()
 
 # Test 2: Bekannte Layer-1 Seeds (zum Vergleich)
 layer1_results = test_known_layer1_seeds()
 
 # Zusammenfassung
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 layer2_matches = sum(1 for r in layer2_results["results"] if r.get("validation", {}).get("match"))
 layer2_total = len([r for r in layer2_results["results"] if r.get("validation")])
 
 print(f"Layer-2 Seeds:")
 print(f" Total tested: {layer2_total}")
 print(f" Matches: {layer2_matches}")
 if layer2_total > 0:
 print(f" Match rate: {(layer2_matches / layer2_total) * 100:.1f}%")
 print()
 
 layer1_success = sum(1 for r in layer1_results["results"] if r.get("derived_identity"))
 print(f"Layer-1 Seeds:")
 print(f" Total tested: {layer1_results['total']}")
 print(f" Successful derivations: {layer1_success}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 final_results = {
 "layer2_validation": layer2_results,
 "layer1_validation": layer1_results,
 "conclusion": {
 "layer2_seeds_work": layer2_matches == layer2_total if layer2_total > 0 else False,
 "layer1_seeds_work": layer1_success == layer1_results["total"],
 },
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(final_results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# Crypto Validation: Seed to Identity\n\n")
 f.write("## Layer-2 Seeds Validation\n\n")
 f.write(f"- Total tested: {layer2_total}\n")
 f.write(f"- Matches: {layer2_matches}\n")
 if layer2_total > 0:
 f.write(f"- Match rate: {(layer2_matches / layer2_total) * 100:.1f}%\n")
 f.write("\n")
 
 f.write("### Results\n\n")
 for result in layer2_results["results"]:
 f.write(f"#### {result['label']}\n\n")
 f.write(f"- Identity: `{result['identity']}`\n")
 f.write(f"- Seed: `{result['seed']}`\n")
 if result.get("validation"):
 val = result["validation"]
 if val.get("match"):
 f.write(f"- ✅ **MATCH**: Seed führt zu Identity\n")
 elif val.get("error"):
 f.write(f"- ❌ Error: {val['error']}\n")
 else:
 f.write(f"- ❌ NO MATCH\n")
 f.write(f" - Expected: `{val['expected_identity']}`\n")
 f.write(f" - Got: `{val['derived_identity']}`\n")
 f.write("\n")
 
 print("=" * 80)
 print("✅ VALIDATION COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")
 
 # WICHTIGE ERKENNTNIS
 if layer2_matches == layer2_total and layer2_total > 0:
 print()
 print("=" * 80)
 print("✅ ERKENNTNIS: Layer-2 Seeds funktionieren!")
 print("=" * 80)
 print("Die abgeleiteten Seeds führen zu den erwarteten Identities.")
 elif layer2_total > 0:
 print()
 print("=" * 80)
 print("⚠️ ERKENNTNIS: Layer-2 Seeds funktionieren NICHT wie erwartet")
 print("=" * 80)
 print("Die abgeleiteten Seeds führen NICHT zu den erwarteten Identities.")
 print("Dies bedeutet: Die Seeds sind NICHT die Private Keys for diese Identities.")

if __name__ == "__main__":
 main()

