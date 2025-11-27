#!/usr/bin/env python3
"""
Umfassender Scan: Finde ALLE Adressen, Private Seeds und Identities

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
Verwendet venv-tx for crypto functions.
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict

VENV_PATH = Path(__file__).parent.parent.parent / "venv-tx"
OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "comprehensive_identity_seed_scan.json"
OUTPUT_MD = OUTPUT_DIR / "COMPREHENSIVE_IDENTITY_SEED_SCAN.md"

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Leite Identity aus Seed ab (mit venv-tx)."""
 python_exe = VENV_PATH / "bin" / "python"
 
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

try:
 seed = "{seed}"
 seed_bytes = seed.encode('utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 identity = get_identity_from_public_key(public_key)
 print(identity)
except Exception as e:
 print(f"ERROR: {{e}}")
"""
 
 result = subprocess.run(
 [str(python_exe), "-c", script],
 capture_output=True,
 text=True,
 cwd=Path(__file__).parent.parent.parent
 )
 
 if result.returncode != 0 or result.stdout.startswith("ERROR"):
 return None
 
 return result.stdout.strip()

def load_all_known_seeds() -> Dict[str, Dict]:
 """Load alle bekannten Seeds aus verschiedenen Quellen."""
 all_seeds = {}
 
 # Layer-1 Seeds (bekannt)
 layer1_seeds = {
 "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd": {
 "source": "Layer-1 Diagonal #1",
 "layer1_identity": "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "layer2_identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 },
 "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr": {
 "source": "Layer-1 Diagonal #2",
 "layer1_identity": "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "layer2_identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 },
 "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn": {
 "source": "Layer-1 Diagonal #3",
 "layer1_identity": "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "layer2_identity": None,
 },
 "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht": {
 "source": "Layer-1 Diagonal #4",
 "layer1_identity": "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "layer2_identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 },
 "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml": {
 "source": "Layer-1 Vortex #1",
 "layer1_identity": "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "layer2_identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 },
 "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb": {
 "source": "Layer-1 Vortex #2",
 "layer1_identity": "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "layer2_identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 },
 "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw": {
 "source": "Layer-1 Vortex #3",
 "layer1_identity": "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "layer2_identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 },
 "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc": {
 "source": "Layer-1 Vortex #4",
 "layer1_identity": "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
 "layer2_identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 },
 }
 
 for seed, info in layer1_seeds.items():
 all_seeds[seed] = {
 "source": info["source"],
 "layer": 1,
 "known_identities": {
 1: info["layer1_identity"],
 2: info.get("layer2_identity"),
 },
 }
 
 # Load Seeds aus JSON-Dateien
 json_files = [
 "outputs/derived/mass_seed_derivation_optimized.json",
 "outputs/derived/seed_derivation_mass_scan.json",
 "outputs/derived/identity_deep_scan.json",
 "outputs/derived/mass_identity_to_seed_conversion.json",
 ]
 
 for json_file in json_files:
 file_path = Path(__file__).parent.parent.parent / json_file
 if file_path.exists():
 try:
 with file_path.open() as f:
 data = json.load(f)
 # Extrahiere Seeds aus verschiedenen Strukturen
 if isinstance(data, dict):
 if "seed_map" in data:
 for identity, seed in data["seed_map"].items():
 if seed not in all_seeds:
 all_seeds[seed] = {
 "source": f"seed_map from {json_file}",
 "layer": "unknown",
 "known_identities": {},
 }
 if "seeds" in data:
 for seed in data["seeds"]:
 if seed not in all_seeds:
 all_seeds[seed] = {
 "source": f"seeds from {json_file}",
 "layer": "unknown",
 "known_identities": {},
 }
 except Exception as e:
 print(f"⚠️ Could not load {json_file}: {e}")
 
 return all_seeds

def scan_seed_for_layers(seed: str, max_layers: int = 5) -> Dict:
 """Scanne Seed for alle möglichen Layer-Identities."""
 results = {
 "seed": seed,
 "derived_identities": {},
 "max_layer_found": 0,
 }
 
 # Layer 1: Direkt aus Seed
 identity = derive_identity_from_seed(seed)
 if identity:
 results["derived_identities"][1] = identity
 results["max_layer_found"] = 1
 
 # Layer 2+: Verwende Identity als Seed-Kandidat
 current_seed = seed
 for layer in range(2, max_layers + 1):
 # Versuche Identity aus vorherigem Layer als Seed
 if layer - 1 in results["derived_identities"]:
 prev_identity = results["derived_identities"][layer - 1]
 # Formel: identity.lower()[:55]
 candidate_seed = prev_identity.lower()[:55]
 
 if len(candidate_seed) == 55:
 identity = derive_identity_from_seed(candidate_seed)
 if identity:
 results["derived_identities"][layer] = identity
 results["max_layer_found"] = layer
 current_seed = candidate_seed
 else:
 break
 else:
 break
 else:
 break
 
 return results

def main():
 print("=" * 80)
 print("COMPREHENSIVE IDENTITY & SEED SCAN")
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
 
 # Load alle bekannten Seeds
 print("Loading all known seeds...")
 all_seeds = load_all_known_seeds()
 print(f"✅ Loaded {len(all_seeds)} seeds")
 print()
 
 # Scanne alle Seeds
 print("=" * 80)
 print("SCANNING ALL SEEDS")
 print("=" * 80)
 print()
 
 all_results = []
 all_identities = set()
 identity_to_seed_map = {}
 
 # Load bereits gespeicherte Ergebnisse (for Resume)
 checkpoint_file = OUTPUT_DIR / "comprehensive_scan_checkpoint.json"
 processed_seeds = set()
 if checkpoint_file.exists():
 try:
 with checkpoint_file.open() as f:
 checkpoint = json.load(f)
 processed_seeds = set(checkpoint.get("processed_seeds", []))
 print(f"✅ Resuming from checkpoint: {len(processed_seeds)} seeds already processed")
 except:
 pass
 
 for i, (seed, info) in enumerate(all_seeds.items(), 1):
 # Skip bereits verarbeitete Seeds
 if seed in processed_seeds:
 continue
 print(f"[{i}/{len(all_seeds)}] {info['source']}:")
 print(f" Seed: {seed[:40]}...")
 
 # Scanne Seed
 result = scan_seed_for_layers(seed, max_layers=5)
 result["source"] = info["source"]
 result["layer"] = info.get("layer", "unknown")
 result["known_identities"] = info.get("known_identities", {})
 
 # Validate gegen bekannte Identities
 for layer, known_identity in result["known_identities"].items():
 if known_identity and layer in result["derived_identities"]:
 derived = result["derived_identities"][layer]
 if derived == known_identity:
 print(f" ✅ Layer {layer}: MATCHES known identity")
 else:
 print(f" ⚠️ Layer {layer}: NO MATCH")
 print(f" Known: {known_identity[:40]}...")
 print(f" Derived: {derived[:40]}...")
 
 # Zeige gefundene Identities
 if result["derived_identities"]:
 print(f" Found {len(result['derived_identities'])} identities (max layer: {result['max_layer_found']})")
 for layer, identity in result["derived_identities"].items():
 print(f" Layer {layer}: {identity[:40]}...")
 all_identities.add(identity)
 if identity not in identity_to_seed_map:
 identity_to_seed_map[identity] = []
 identity_to_seed_map[identity].append({
 "seed": seed,
 "layer": layer,
 "source": info["source"],
 })
 else:
 print(f" ❌ No identities found")
 
 all_results.append(result)
 
 # Speichere Checkpoint nach jedem Seed
 processed_seeds.add(seed)
 checkpoint = {
 "processed_seeds": list(processed_seeds),
 "total_found": len(all_identities),
 }
 with checkpoint_file.open("w") as f:
 json.dump(checkpoint, f, indent=2)
 
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 total_seeds = len(all_seeds)
 seeds_with_identities = sum(1 for r in all_results if r["derived_identities"])
 total_identities = len(all_identities)
 max_layer = max((r["max_layer_found"] for r in all_results), default=0)
 
 print(f"Total seeds scanned: {total_seeds}")
 print(f"Seeds with identities: {seeds_with_identities}")
 print(f"Total unique identities found: {total_identities}")
 print(f"Max layer depth: {max_layer}")
 print()
 
 # Layer-Verteilung
 layer_distribution = defaultdict(int)
 for result in all_results:
 for layer in result["derived_identities"].keys():
 layer_distribution[layer] += 1
 
 print("Layer distribution:")
 for layer in sorted(layer_distribution.keys()):
 print(f" Layer {layer}: {layer_distribution[layer]} identities")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 final_results = {
 "summary": {
 "total_seeds": total_seeds,
 "seeds_with_identities": seeds_with_identities,
 "total_unique_identities": total_identities,
 "max_layer_depth": max_layer,
 "layer_distribution": dict(layer_distribution),
 },
 "seed_results": all_results,
 "all_identities": sorted(list(all_identities)),
 "identity_to_seed_map": {
 identity: seeds
 for identity, seeds in identity_to_seed_map.items()
 },
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(final_results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# Comprehensive Identity & Seed Scan\n\n")
 f.write("## Summary\n\n")
 f.write(f"- **Total seeds scanned**: {total_seeds}\n")
 f.write(f"- **Seeds with identities**: {seeds_with_identities}\n")
 f.write(f"- **Total unique identities found**: {total_identities}\n")
 f.write(f"- **Max layer depth**: {max_layer}\n\n")
 
 f.write("## Layer Distribution\n\n")
 for layer in sorted(layer_distribution.keys()):
 f.write(f"- **Layer {layer}**: {layer_distribution[layer]} identities\n")
 f.write("\n")
 
 f.write("## All Identities\n\n")
 for identity in sorted(all_identities):
 f.write(f"- `{identity}`\n")
 f.write("\n")
 
 f.write("## Seed Results\n\n")
 for result in all_results:
 f.write(f"### {result['source']}\n\n")
 f.write(f"- Seed: `{result['seed']}`\n")
 f.write(f"- Max layer: {result['max_layer_found']}\n")
 if result["derived_identities"]:
 f.write(f"- Identities:\n")
 for layer, identity in sorted(result["derived_identities"].items()):
 f.write(f" - Layer {layer}: `{identity}`\n")
 f.write("\n")
 
 print("=" * 80)
 print("✅ SCAN COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")
 print()
 print(f"📊 Found {total_identities} unique identities from {seeds_with_identities} seeds")
 
 return True

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)

