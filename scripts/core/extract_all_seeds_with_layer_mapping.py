#!/usr/bin/env python3
"""
Extrahiere alle Seeds/Private Keys mit Layer-Mapping

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
1. Bereinigt Duplikate
2. Leitet Seeds ab (identity.lower()[:55])
3. Findet Layer-Zuordnung
4. Validiert Seeds gegen bekannte Layer-Struktur
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict

OUTPUT_DIR = Path("outputs/derived")
VALIDATION_FILE = OUTPUT_DIR / "onchain_validation_all_identities.json"
SCAN_FILE = OUTPUT_DIR / "comprehensive_identity_seed_scan.json"
OUTPUT_JSON = OUTPUT_DIR / "all_identities_with_seeds_mapped.json"
OUTPUT_MD = OUTPUT_DIR / "ALL_IDENTITIES_WITH_SEEDS_MAPPED.md"

# Import standardized conversion
sys.path.insert(0, str(Path(__file__).parent))
from standardized_conversion import identity_to_seed, validate_identity, validate_seed

def load_layer_mapping() -> Dict[str, Dict]:
 """Load Layer-Mapping aus comprehensive scan."""
 if not SCAN_FILE.exists():
 return {}
 
 with SCAN_FILE.open() as f:
 scan_data = json.load(f)
 
 # Erstelle Identity -> Layer Mapping
 identity_to_layer = {}
 seed_to_identities = defaultdict(list)
 
 seed_results = scan_data.get("seed_results", [])
 for seed_result in seed_results:
 seed = seed_result.get("seed")
 derived_identities = seed_result.get("derived_identities", {})
 
 for layer, identity in derived_identities.items():
 identity_to_layer[identity] = {
 "layer": layer,
 "seed": seed,
 "parent_seed": seed_result.get("parent_seed"),
 }
 seed_to_identities[seed].append({
 "identity": identity,
 "layer": layer,
 })
 
 return {
 "identity_to_layer": identity_to_layer,
 "seed_to_identities": seed_to_identities,
 }

def deduplicate_results(results: List[Dict]) -> List[Dict]:
 """Bereinige Duplikate aus den Ergebnissen."""
 seen = set()
 unique_results = []
 
 for result in results:
 identity = result.get("identity")
 if identity and identity not in seen:
 seen.add(identity)
 unique_results.append(result)
 
 return unique_results

def main():
 print("=" * 80)
 print("EXTRACT ALL SEEDS WITH LAYER MAPPING")
 print("=" * 80)
 print()
 print("WICHTIG: Nur echte, nachgewiesene Erkenntnisse!")
 print()
 
 if not VALIDATION_FILE.exists():
 print(f"❌ Validation file not found: {VALIDATION_FILE}")
 return False
 
 # Load On-Chain Validierungs-Ergebnisse
 print("Loading on-chain validation results...")
 with VALIDATION_FILE.open() as f:
 validation_data = json.load(f)
 
 results = validation_data.get("results", [])
 print(f"✅ Loaded {len(results)} results")
 
 # Bereinige Duplikate
 print("Deduplicating results...")
 unique_results = deduplicate_results(results)
 print(f"✅ {len(unique_results)} unique identities (removed {len(results) - len(unique_results)} duplicates)")
 print()
 
 # Load Layer-Mapping
 print("Loading layer mapping...")
 layer_mapping = load_layer_mapping()
 identity_to_layer = layer_mapping.get("identity_to_layer", {})
 print(f"✅ Loaded {len(identity_to_layer)} identity mappings")
 print()
 
 # Extrahiere Seeds und mappe zu Layern
 print("=" * 80)
 print("EXTRACTING SEEDS & MAPPING TO LAYERS")
 print("=" * 80)
 print()
 
 identities_with_seeds = []
 stats = {
 "total": len(unique_results),
 "seeds_extracted": 0,
 "seeds_valid": 0,
 "layer_mapped": 0,
 "has_known_seed": 0,
 "errors": 0,
 }
 
 batch_size = 100
 total_batches = (len(unique_results) + batch_size - 1) // batch_size
 
 for batch_idx in range(total_batches):
 start_idx = batch_idx * batch_size
 end_idx = min(start_idx + batch_size, len(unique_results))
 batch = unique_results[start_idx:end_idx]
 
 print(f"Batch {batch_idx + 1}/{total_batches} ({start_idx + 1}-{end_idx}/{len(unique_results)})...")
 
 for result in batch:
 identity = result.get("identity")
 if not identity:
 continue
 
 # Extrahiere Seed
 seed = identity_to_seed(identity)
 if not seed:
 stats["errors"] += 1
 continue
 
 stats["seeds_extracted"] += 1
 
 # Validate Seed-Format
 if not validate_seed(seed):
 stats["errors"] += 1
 continue
 
 stats["seeds_valid"] += 1
 
 # Finde Layer-Information
 layer_info = identity_to_layer.get(identity)
 if layer_info:
 stats["layer_mapped"] += 1
 known_seed = layer_info.get("seed")
 if known_seed:
 stats["has_known_seed"] += 1
 else:
 layer_info = None
 known_seed = None
 
 # Speichere Ergebnis
 identity_data = {
 "identity": identity,
 "derived_seed": seed, # Seed abgeleitet von Identity
 "known_seed": known_seed, # Seed aus Layer-Mapping (falls vorhanden)
 "layer": layer_info.get("layer") if layer_info else None,
 "parent_seed": layer_info.get("parent_seed") if layer_info else None,
 "balance": result.get("balance", "0"),
 "validForTick": result.get("validForTick"),
 "incomingAmount": result.get("incomingAmount", "0"),
 "outgoingAmount": result.get("outgoingAmount", "0"),
 "has_layer_mapping": layer_info is not None,
 }
 
 identities_with_seeds.append(identity_data)
 
 if layer_info:
 print(f" ✅ {identity[:40]}... | Layer: {layer_info.get('layer')} | Seed: {seed[:30]}...")
 else:
 print(f" ⚠️ {identity[:40]}... | Layer: ? | Seed: {seed[:30]}...")
 
 # Speichere Zwischenergebnisse
 checkpoint = {
 "stats": stats,
 "identities": identities_with_seeds,
 }
 checkpoint_file = OUTPUT_DIR / "identities_seeds_layer_checkpoint.json"
 with checkpoint_file.open("w") as f:
 json.dump(checkpoint, f, indent=2)
 
 print(f" Progress: {stats['layer_mapped']}/{stats['seeds_valid']} layer-mapped, {stats['has_known_seed']} with known seed")
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 print(f"Total identities: {stats['total']}")
 print(f"Seeds extracted: {stats['seeds_extracted']}")
 print(f"Seeds valid: {stats['seeds_valid']}")
 print(f"Layer mapped: {stats['layer_mapped']} ({stats['layer_mapped']/stats['seeds_valid']*100:.1f}%)")
 print(f"With known seed: {stats['has_known_seed']} ({stats['has_known_seed']/stats['seeds_valid']*100:.1f}%)")
 print(f"Errors: {stats['errors']}")
 print()
 
 # Layer-Statistiken
 layer_stats = defaultdict(lambda: {"total": 0, "with_seed": 0})
 for identity_data in identities_with_seeds:
 layer = identity_data.get("layer")
 if layer:
 layer_stats[layer]["total"] += 1
 if identity_data.get("known_seed"):
 layer_stats[layer]["with_seed"] += 1
 
 print("Layer statistics:")
 for layer in sorted(layer_stats.keys()):
 stats_layer = layer_stats[layer]
 print(f" Layer {layer}: {stats_layer['with_seed']}/{stats_layer['total']} with known seed")
 print()
 
 # Speichere finale Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 final_results = {
 "summary": stats,
 "layer_statistics": {str(k): v for k, v in layer_stats.items()},
 "identities": identities_with_seeds,
 }
 
 with OUTPUT_JSON.open("w") as f:
 json.dump(final_results, f, indent=2)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w") as f:
 f.write("# All Identities with Seeds (Layer Mapped)\n\n")
 f.write("## Summary\n\n")
 f.write(f"- **Total identities**: {stats['total']}\n")
 f.write(f"- **Seeds extracted**: {stats['seeds_extracted']}\n")
 f.write(f"- **Seeds valid**: {stats['seeds_valid']}\n")
 f.write(f"- **Layer mapped**: {stats['layer_mapped']} ({stats['layer_mapped']/stats['seeds_valid']*100:.1f}%)\n")
 f.write(f"- **With known seed**: {stats['has_known_seed']} ({stats['has_known_seed']/stats['seeds_valid']*100:.1f}%)\n")
 f.write(f"- **Errors**: {stats['errors']}\n\n")
 
 f.write("## Layer Statistics\n\n")
 f.write("| Layer | Total | With Known Seed |\n")
 f.write("|-------|-------|-----------------|\n")
 for layer in sorted(layer_stats.keys()):
 stats_layer = layer_stats[layer]
 f.write(f"| {layer} | {stats_layer['total']} | {stats_layer['with_seed']} |\n")
 f.write("\n")
 
 f.write("## Identities with Known Seeds\n\n")
 known_seed_identities = [i for i in identities_with_seeds if i.get("known_seed")]
 f.write(f"**Total**: {len(known_seed_identities)}\n\n")
 f.write("| Identity | Layer | Known Seed | Derived Seed | Balance |\n")
 f.write("|----------|-------|-------------|--------------|---------|\n")
 
 for identity_data in known_seed_identities[:200]: # Erste 200
 f.write(f"| {identity_data['identity']} | {identity_data.get('layer', '?')} | {identity_data['known_seed']} | {identity_data['derived_seed']} | {identity_data['balance']} QU |\n")
 
 if len(known_seed_identities) > 200:
 f.write(f"\n... and {len(known_seed_identities) - 200} more\n")
 
 print(f"💾 Results saved to: {OUTPUT_JSON}")
 print(f"📄 Report saved to: {OUTPUT_MD}")
 print()
 print("=" * 80)
 print("✅ EXTRACTION COMPLETE")
 print("=" * 80)
 
 return True

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)

