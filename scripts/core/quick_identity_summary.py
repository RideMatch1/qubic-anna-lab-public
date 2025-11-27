#!/usr/bin/env python3
"""
Schnelle Zusammenfassung: Zeige was wir bisher haben

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
"""

import json
from pathlib import Path

OUTPUT_DIR = Path("outputs/derived")

def main():
 print("=" * 80)
 print("QUICK IDENTITY & SEED SUMMARY")
 print("=" * 80)
 print()
 
 # Load bekannte Layer-1 Seeds
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
 
 print("✅ Layer-1 Seeds (8):")
 for seed, label in layer1_seeds.items():
 print(f" - {label}: {seed[:40]}...")
 print()
 
 # Load Ergebnisse aus full_crypto_validation
 validation_file = OUTPUT_DIR / "full_crypto_validation.json"
 if validation_file.exists():
 with validation_file.open() as f:
 data = json.load(f)
 print("✅ Layer-1 → Layer-2 Mappings:")
 for result in data.get("results", []):
 if result.get("matches_layer2"):
 print(f" - {result['label']}: {result['derived_identity'][:40]}...")
 print()
 
 # Check Checkpoint
 checkpoint_file = OUTPUT_DIR / "comprehensive_scan_checkpoint.json"
 if checkpoint_file.exists():
 with checkpoint_file.open() as f:
 checkpoint = json.load(f)
 processed = len(checkpoint.get("processed_seeds", []))
 total_found = checkpoint.get("total_found", 0)
 print(f"📊 Comprehensive Scan Progress:")
 print(f" - Processed: {processed} seeds")
 print(f" - Identities found: {total_found}")
 print()
 
 # Load finale Ergebnisse wenn vorhanden
 final_file = OUTPUT_DIR / "comprehensive_identity_seed_scan.json"
 if final_file.exists():
 with final_file.open() as f:
 data = json.load(f)
 summary = data.get("summary", {})
 print("✅ Comprehensive Scan Results:")
 print(f" - Total seeds: {summary.get('total_seeds', 0)}")
 print(f" - Seeds with identities: {summary.get('seeds_with_identities', 0)}")
 print(f" - Total unique identities: {summary.get('total_unique_identities', 0)}")
 print(f" - Max layer depth: {summary.get('max_layer_depth', 0)}")
 print()
 
 layer_dist = summary.get("layer_distribution", {})
 if layer_dist:
 print(" Layer distribution:")
 for layer in sorted(layer_dist.keys()):
 print(f" - Layer {layer}: {layer_dist[layer]} identities")
 
 print("=" * 80)

if __name__ == "__main__":
 main()

