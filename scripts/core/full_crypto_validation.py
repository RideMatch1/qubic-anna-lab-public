#!/usr/bin/env python3
"""
Vollständige Crypto-Validierung aller Layer-1 → Layer-2 Mappings

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
Verwendet venv-tx for crypto functions.
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List

VENV_PATH = Path(__file__).parent.parent.parent / "venv-tx"
OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "full_crypto_validation.json"
OUTPUT_MD = OUTPUT_DIR / "FULL_CRYPTO_VALIDATION.md"

# Bekannte Layer-1 Seeds und ihre Layer-2 Identities
LAYER1_TO_LAYER2 = {
 "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd": {
 "label": "Diagonal #1",
 "layer1_identity": "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "layer2_identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 },
 "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr": {
 "label": "Diagonal #2",
 "layer1_identity": "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "layer2_identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 },
 "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn": {
 "label": "Diagonal #3",
 "layer1_identity": "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "layer2_identity": None, # Nicht bekannt
 },
 "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht": {
 "label": "Diagonal #4",
 "layer1_identity": "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "layer2_identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 },
 "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml": {
 "label": "Vortex #1",
 "layer1_identity": "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "layer2_identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 },
 "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb": {
 "label": "Vortex #2",
 "layer1_identity": "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "layer2_identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 },
 "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw": {
 "label": "Vortex #3",
 "layer1_identity": "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "layer2_identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 },
 "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc": {
 "label": "Vortex #4",
 "layer1_identity": "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
 "layer2_identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 },
}

def derive_identity_from_seed(seed: str) -> str:
 """Leite Identity aus Seed ab (mit venv-tx)."""
 python_exe = VENV_PATH / "bin" / "python"
 
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{seed}"
seed_bytes = seed.encode('utf-8')
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
"""
 
 result = subprocess.run(
 [str(python_exe), "-c", script],
 capture_output=True,
 text=True,
 cwd=Path(__file__).parent.parent.parent
 )
 
 if result.returncode != 0:
 return None
 
 return result.stdout.strip()

def main():
 print("=" * 80)
 print("FULL CRYPTO VALIDATION: LAYER-1 → LAYER-2")
 print("=" * 80)
 print()
 print("WICHTIG: Nur echte, nachgewiesene Erkenntnisse!")
 print()
 
 if not VENV_PATH.exists():
 print(f"❌ venv-tx not found at: {VENV_PATH}")
 return False
 
 python_exe = VENV_PATH / "bin" / "python"
 if not python_exe.exists():
 print(f"❌ Python executable not found at: {python_exe}")
 return False
 
 print(f"✅ Using venv-tx: {python_exe}")
 print()
 
 results = []
 
 for seed, info in LAYER1_TO_LAYER2.items():
 label = info["label"]
 l1_identity = info["layer1_identity"]
 l2_identity = info["layer2_identity"]
 
 print(f"{label}:")
 print(f" Seed: {seed[:40]}...")
 print(f" Layer-1 Identity: {l1_identity}")
 
 # Leite Identity aus Seed ab
 derived_identity = derive_identity_from_seed(seed)
 
 if not derived_identity:
 print(f" ❌ Could not derive identity")
 results.append({
 "label": label,
 "seed": seed,
 "layer1_identity": l1_identity,
 "layer2_identity": l2_identity,
 "derived_identity": None,
 "matches_layer1": False,
 "matches_layer2": False,
 "error": "Could not derive identity",
 })
 print()
 continue
 
 print(f" Derived Identity: {derived_identity}")
 
 # Check Matches
 matches_l1 = (derived_identity == l1_identity)
 matches_l2 = (derived_identity == l2_identity) if l2_identity else False
 
 if matches_l1:
 print(f" ✅ MATCHES Layer-1 Identity")
 elif matches_l2:
 print(f" ✅ MATCHES Layer-2 Identity")
 else:
 print(f" ❌ NO MATCH (neither L1 nor L2)")
 
 results.append({
 "label": label,
 "seed": seed,
 "layer1_identity": l1_identity,
 "layer2_identity": l2_identity,
 "derived_identity": derived_identity,
 "matches_layer1": matches_l1,
 "matches_layer2": matches_l2,
 })
 
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 l1_matches = sum(1 for r in results if r.get("matches_layer1"))
 l2_matches = sum(1 for r in results if r.get("matches_layer2"))
 total_tested = len([r for r in results if r.get("derived_identity")])
 
 print(f"Total tested: {total_tested}/{len(LAYER1_TO_LAYER2)}")
 print(f"Matches Layer-1: {l1_matches}/{total_tested}")
 print(f"Matches Layer-2: {l2_matches}/{total_tested}")
 print()
 
 # WICHTIGE ERKENNTNIS
 if l2_matches > 0:
 print("=" * 80)
 print("✅ ERKENNTNIS: Layer-1 Seeds funktionieren for Layer-2 Identities!")
 print("=" * 80)
 print(f"{l2_matches} von {total_tested} Layer-1 Seeds führen zu Layer-2 Identities.")
 print("Dies ist die Verbindung zwischen Layer-1 und Layer-2!")
 elif l1_matches > 0:
 print("=" * 80)
 print("✅ ERKENNTNIS: Layer-1 Seeds funktionieren for Layer-1 Identities")
 print("=" * 80)
 print(f"{l1_matches} von {total_tested} Layer-1 Seeds führen zu Layer-1 Identities.")
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 final_results = {
 "total_tested": total_tested,
 "matches_layer1": l1_matches,
 "matches_layer2": l2_matches,
 "results": results,
 "conclusion": {
 "layer1_seeds_are_layer1_private_keys": l1_matches == total_tested,
 "layer1_seeds_are_layer2_private_keys": l2_matches > 0,
 },
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(final_results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# Full Crypto Validation: Layer-1 → Layer-2\n\n")
 f.write("## Summary\n\n")
 f.write(f"- **Total tested**: {total_tested}/{len(LAYER1_TO_LAYER2)}\n")
 f.write(f"- **Matches Layer-1**: {l1_matches}/{total_tested}\n")
 f.write(f"- **Matches Layer-2**: {l2_matches}/{total_tested}\n\n")
 
 f.write("## Results\n\n")
 for result in results:
 f.write(f"### {result['label']}\n\n")
 f.write(f"- Seed: `{result['seed']}`\n")
 f.write(f"- Layer-1 Identity: `{result['layer1_identity']}`\n")
 if result.get("layer2_identity"):
 f.write(f"- Layer-2 Identity: `{result['layer2_identity']}`\n")
 f.write(f"- Derived Identity: `{result['derived_identity']}`\n")
 f.write(f"- Matches Layer-1: **{result['matches_layer1']}**\n")
 f.write(f"- Matches Layer-2: **{result['matches_layer2']}**\n")
 f.write("\n")
 
 f.write("## Conclusion\n\n")
 if l2_matches > 0:
 f.write(f"✅ **Layer-1 Seeds funktionieren for Layer-2 Identities!**\n\n")
 f.write(f"{l2_matches} von {total_tested} Layer-1 Seeds führen zu Layer-2 Identities.\n")
 f.write("Dies ist die Verbindung zwischen Layer-1 und Layer-2!\n")
 elif l1_matches > 0:
 f.write(f"✅ **Layer-1 Seeds funktionieren for Layer-1 Identities**\n\n")
 f.write(f"{l1_matches} von {total_tested} Layer-1 Seeds führen zu Layer-1 Identities.\n")
 
 print("=" * 80)
 print("✅ VALIDATION COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")
 
 return True

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)

