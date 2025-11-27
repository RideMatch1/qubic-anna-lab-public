#!/usr/bin/env python3
"""
Massenkonvertierung: Konvertiere alle gefundenen Identities zu Seeds

Finde alle Identities in den Dateien und konvertiere sie zu Seeds.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "mass_identity_to_seed_conversion.json"
OUTPUT_MD = OUTPUT_DIR / "MASS_IDENTITY_CONVERSION_REPORT.md"

from standardized_conversion import identity_to_seed, validate_identity

def find_all_identities_in_files() -> Dict[str, List[str]]:
 """Finde alle Identities in verschiedenen Dateien."""
 identities_by_file = defaultdict(list)
 
 files = [
 "mass_seed_derivation_optimized.json",
 "seed_derivation_mass_scan.json",
 "identity_deep_scan.json",
 "recursive_layer_map.json",
 "layer1_seeds.json",
 ]
 
 for filename in files:
 file_path = OUTPUT_DIR / filename
 if not file_path.exists():
 continue
 
 try:
 with file_path.open() as f:
 data = json.load(f)
 
 found = set()
 
 def extract_identities(obj):
 if isinstance(obj, str):
 if validate_identity(obj):
 found.add(obj)
 elif isinstance(obj, dict):
 for key, value in obj.items():
 if validate_identity(key):
 found.add(key)
 extract_identities(value)
 elif isinstance(obj, list):
 for item in obj:
 extract_identities(item)
 
 extract_identities(data)
 
 identities_by_file[filename] = sorted(list(found))
 print(f"✅ {filename}: {len(found)} identities")
 
 except Exception as e:
 print(f"⚠️ Error loading {filename}: {e}")
 
 return identities_by_file

def convert_all_identities(identities_by_file: Dict[str, List[str]]) -> Dict:
 """Konvertiere alle Identities zu Seeds."""
 print()
 print("Converting identities to seeds...")
 print()
 
 all_conversions = {}
 stats = {
 "total_identities": 0,
 "successful_conversions": 0,
 "failed_conversions": 0,
 "unique_seeds": set(),
 "duplicate_seeds": 0,
 }
 
 seed_to_identities = defaultdict(list)
 
 for filename, identities in identities_by_file.items():
 for identity in identities:
 stats["total_identities"] += 1
 
 seed = identity_to_seed(identity)
 
 if seed:
 stats["successful_conversions"] += 1
 stats["unique_seeds"].add(seed)
 
 all_conversions[identity] = {
 "seed": seed,
 "source_file": filename,
 "valid": True,
 }
 
 seed_to_identities[seed].append(identity)
 else:
 stats["failed_conversions"] += 1
 all_conversions[identity] = {
 "seed": None,
 "source_file": filename,
 "valid": False,
 }
 
 # Finde Duplikate (mehrere Identities -> gleicher Seed)
 for seed, identities in seed_to_identities.items():
 if len(identities) > 1:
 stats["duplicate_seeds"] += len(identities) - 1
 
 return {
 "conversions": all_conversions,
 "seed_to_identities": {k: v for k, v in seed_to_identities.items() if len(v) > 1},
 "stats": {
 "total_identities": stats["total_identities"],
 "successful_conversions": stats["successful_conversions"],
 "failed_conversions": stats["failed_conversions"],
 "unique_seeds": len(stats["unique_seeds"]),
 "duplicate_seeds": stats["duplicate_seeds"],
 "conversion_rate": (stats["successful_conversions"] / stats["total_identities"] * 100) if stats["total_identities"] > 0 else 0,
 },
 }

def main():
 print("=" * 80)
 print("MASS IDENTITY TO SEED CONVERSION")
 print("=" * 80)
 print()
 
 # Finde alle Identities
 identities_by_file = find_all_identities_in_files()
 
 total_identities = sum(len(ids) for ids in identities_by_file.values())
 print()
 print(f"Total identities found: {total_identities}")
 print()
 
 # Konvertiere alle
 results = convert_all_identities(identities_by_file)
 
 stats = results["stats"]
 
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 print(f"Total identities: {stats['total_identities']}")
 print(f"Successful conversions: {stats['successful_conversions']}")
 print(f"Failed conversions: {stats['failed_conversions']}")
 print(f"Unique seeds: {stats['unique_seeds']}")
 print(f"Duplicate seeds (multiple identities -> same seed): {stats['duplicate_seeds']}")
 print(f"Conversion rate: {stats['conversion_rate']:.2f}%")
 print()
 
 # Zeige Duplikate
 if results["seed_to_identities"]:
 print("=" * 80)
 print("DUPLICATE SEEDS (Multiple identities map to same seed)")
 print("=" * 80)
 print()
 
 for seed, identities in list(results["seed_to_identities"].items())[:10]:
 print(f"Seed: {seed}")
 print(f" Maps to {len(identities)} identities:")
 for identity in identities[:3]:
 print(f" - {identity[:50]}...")
 if len(identities) > 3:
 print(f" ... and {len(identities) - 3} more")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# Mass Identity to Seed Conversion Report\n\n")
 f.write("## Statistics\n\n")
 f.write(f"- **Total identities**: {stats['total_identities']}\n")
 f.write(f"- **Successful conversions**: {stats['successful_conversions']}\n")
 f.write(f"- **Failed conversions**: {stats['failed_conversions']}\n")
 f.write(f"- **Unique seeds**: {stats['unique_seeds']}\n")
 f.write(f"- **Duplicate seeds**: {stats['duplicate_seeds']}\n")
 f.write(f"- **Conversion rate**: {stats['conversion_rate']:.2f}%\n\n")
 
 if results["seed_to_identities"]:
 f.write("## Duplicate Seeds\n\n")
 f.write("These seeds map to multiple identities:\n\n")
 for seed, identities in list(results["seed_to_identities"].items())[:20]:
 f.write(f"### Seed: `{seed}`\n\n")
 f.write(f"Maps to {len(identities)} identities:\n\n")
 for identity in identities:
 f.write(f"- `{identity}`\n")
 f.write("\n")
 
 print("=" * 80)
 print("✅ CONVERSION COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")

if __name__ == "__main__":
 main()

