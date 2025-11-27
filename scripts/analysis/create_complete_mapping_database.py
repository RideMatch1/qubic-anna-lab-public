#!/usr/bin/env python3
"""
Create Complete Mapping Database

Erstellt eine vollständige Datenbank mit:
- Seed -> Real ID
- Seed -> Documented ID (Fake)
- Real ID -> Seed
- Documented ID -> Seed (falls gefunden)
- Layer-Zuordnungen
- Pattern-Analysen
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

INPUT_FILE = project_root / "outputs" / "derived" / "complete_24846_seeds_to_real_ids_mapping.json"
OUTPUT_DIR = project_root / "outputs" / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def create_mapping_database(mapping_data: Dict) -> Dict:
 """Erstelle vollständige Mapping-Datenbank."""
 results = mapping_data.get("results", [])
 
 # Forward mappings
 seed_to_real_id = {}
 seed_to_doc_id = {}
 real_id_to_seed = {}
 doc_id_to_seed = {}
 
 # Layer mappings
 seed_to_layer = {}
 real_id_to_layer = {}
 doc_id_to_layer = {}
 
 # Statistics
 matches = []
 mismatches = []
 
 for item in results:
 seed = item.get("seed", "")
 doc_id = item.get("documented_identity", "")
 real_id = item.get("real_identity", "")
 match = item.get("match", False)
 
 if seed:
 seed_to_doc_id[seed] = doc_id
 if real_id:
 seed_to_real_id[seed] = real_id
 real_id_to_seed[real_id] = seed
 
 if doc_id:
 doc_id_to_seed[doc_id] = seed
 
 if match:
 matches.append(item)
 else:
 mismatches.append(item)
 
 return {
 "seed_to_real_id": seed_to_real_id,
 "seed_to_doc_id": seed_to_doc_id,
 "real_id_to_seed": real_id_to_seed,
 "doc_id_to_seed": doc_id_to_seed,
 "statistics": {
 "total_seeds": len(seed_to_real_id),
 "total_real_ids": len(real_id_to_seed),
 "total_doc_ids": len(doc_id_to_seed),
 "matches": len(matches),
 "mismatches": len(mismatches),
 "match_rate": f"{len(matches)*100/len(results):.1f}%" if results else "0%"
 },
 "matches": matches,
 "mismatches": mismatches
 }

def add_layer_information(database: Dict) -> Dict:
 """Füge Layer-Informationen hinzu."""
 # Load layer data
 layer_files = {
 "layer1": project_root / "github_export" / "100_seeds_and_identities.json",
 "layer2": project_root / "outputs" / "derived" / "layer2_derivation_complete.json",
 "layer3": project_root / "outputs" / "derived" / "layer3_derivation_complete.json",
 }
 
 layer_mappings = {
 "seed_to_layer": {},
 "identity_to_layer": {}
 }
 
 for layer_name, file_path in layer_files.items():
 if not file_path.exists():
 continue
 
 with file_path.open() as f:
 data = json.load(f)
 
 if layer_name == "layer1":
 items = data.get("seeds_and_identities", []) if isinstance(data, dict) else data
 for item in items:
 seed = item.get("seed", "")
 identity = item.get("identity", "")
 if seed:
 layer_mappings["seed_to_layer"][seed] = layer_name
 if identity:
 layer_mappings["identity_to_layer"][identity] = layer_name
 else:
 results = data.get("results", [])
 for result in results:
 identity = result.get(f"{layer_name}_identity", "")
 seed = result.get(f"{layer_name}_seed", "")
 if identity:
 layer_mappings["identity_to_layer"][identity] = layer_name
 if seed:
 layer_mappings["seed_to_layer"][seed] = layer_name
 
 database["layer_mappings"] = layer_mappings
 return database

def create_search_functions(database: Dict) -> Dict:
 """Erstelle Suchfunktionen for die Datenbank."""
 return {
 "get_real_id_by_seed": lambda seed: database["seed_to_real_id"].get(seed),
 "get_doc_id_by_seed": lambda seed: database["seed_to_doc_id"].get(seed),
 "get_seed_by_real_id": lambda real_id: database["real_id_to_seed"].get(real_id),
 "get_seed_by_doc_id": lambda doc_id: database["doc_id_to_seed"].get(doc_id),
 "get_layer_by_seed": lambda seed: database.get("layer_mappings", {}).get("seed_to_layer", {}).get(seed),
 "get_layer_by_identity": lambda identity: database.get("layer_mappings", {}).get("identity_to_layer", {}).get(identity)
 }

def main():
 """Main function."""
 print("=" * 80)
 print("CREATE COMPLETE MAPPING DATABASE")
 print("=" * 80)
 print()
 
 if not INPUT_FILE.exists():
 print(f"❌ Input file not found: {INPUT_FILE}")
 print(" Waiting for mapping to complete...")
 return
 
 print("1. Loading mapping data...")
 with INPUT_FILE.open() as f:
 mapping_data = json.load(f)
 
 print(f" ✅ Loaded {mapping_data.get('processed', 0):,} results")
 print()
 
 print("2. Creating mapping database...")
 database = create_mapping_database(mapping_data)
 print(f" ✅ Created database with {database['statistics']['total_seeds']:,} seeds")
 print()
 
 print("3. Adding layer information...")
 database = add_layer_information(database)
 print(f" ✅ Added layer mappings")
 print()
 
 print("4. Creating search functions...")
 search_functions = create_search_functions(database)
 database["search_functions"] = {k: "function" for k in search_functions.keys()}
 print(f" ✅ Created search functions")
 print()
 
 # Save database
 output_file = OUTPUT_DIR / "complete_mapping_database.json"
 with output_file.open("w") as f:
 json.dump(database, f, indent=2)
 
 # Create summary
 summary_file = OUTPUT_DIR / "mapping_database_summary.md"
 with summary_file.open("w") as f:
 f.write("# Complete Mapping Database Summary\n\n")
 f.write(f"**Total Seeds**: {database['statistics']['total_seeds']:,}\n")
 f.write(f"**Total Real IDs**: {database['statistics']['total_real_ids']:,}\n")
 f.write(f"**Total Doc IDs**: {database['statistics']['total_doc_ids']:,}\n")
 f.write(f"**Matches**: {database['statistics']['matches']:,}\n")
 f.write(f"**Mismatches**: {database['statistics']['mismatches']:,}\n")
 f.write(f"**Match Rate**: {database['statistics']['match_rate']}\n\n")
 f.write("## Mappings\n\n")
 f.write("- `seed_to_real_id`: {:,} entries\n".format(len(database['seed_to_real_id'])))
 f.write("- `seed_to_doc_id`: {:,} entries\n".format(len(database['seed_to_doc_id'])))
 f.write("- `real_id_to_seed`: {:,} entries\n".format(len(database['real_id_to_seed'])))
 f.write("- `doc_id_to_seed`: {:,} entries\n".format(len(database['doc_id_to_seed'])))
 
 print("=" * 80)
 print("DATABASE CREATED")
 print("=" * 80)
 print(f"✅ Database saved to: {output_file}")
 print(f"✅ Summary saved to: {summary_file}")
 print()
 print("Statistics:")
 for key, value in database["statistics"].items():
 print(f" {key}: {value}")

if __name__ == "__main__":
 main()

