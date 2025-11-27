#!/usr/bin/env python3
"""
Map ALL Seeds to Real IDs

Mappt ALLE Seeds/Keys die wir haben zu ihren echten Identities.
Ziel: ~25k Wallets alle RICHTIG haben.
"""

import json
import sys
import subprocess
from pathlib import Path
from collections import defaultdict
import time

project_root = Path(__file__).parent.parent.parent
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"
CHECKPOINT_FILE = project_root / "outputs" / "derived" / "map_all_seeds_checkpoint.json"
OUTPUT_FILE = project_root / "outputs" / "derived" / "all_seeds_to_real_ids_mapping.json"

def derive_identity_from_seed(seed: str) -> tuple[bool, str]:
 """Derive identity from seed using venv-tx."""
 script = f'''
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)
seed = "{seed}"
seed_bytes = seed.encode("utf-8")
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
'''
 
 if not VENV_PYTHON.exists():
 return False, "venv-tx not found"
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), '-c', script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 
 if result.returncode == 0 and result.stdout.strip():
 identity = result.stdout.strip()
 if len(identity) == 60:
 return True, identity
 return False, result.stderr.strip() or "Failed"
 except Exception as e:
 return False, str(e)

def find_all_seed_files():
 """Find all files containing seeds/identities."""
 seed_files = []
 
 # Known files - prioritize the large checkpoint file
 known_files = [
 project_root / "outputs" / "onchain_validation_checkpoint.json", # ~25k identities
 project_root / "github_export" / "100_seeds_and_identities.json",
 project_root / "outputs" / "verified_identities.json",
 ]
 
 for file_path in known_files:
 if file_path.exists():
 seed_files.append(file_path)
 
 # Search in outputs
 outputs_dir = project_root / "outputs"
 if outputs_dir.exists():
 for json_file in outputs_dir.rglob("*.json"):
 if json_file.stat().st_size > 1000: # Skip small files
 try:
 with json_file.open() as f:
 data = json.load(f)
 # Check if it contains seeds/identities
 if isinstance(data, (dict, list)):
 if any(key in str(data).lower() for key in ['seed', 'identity', 'identities']):
 seed_files.append(json_file)
 except:
 pass
 
 return seed_files

def load_all_seeds():
 """Load all seeds from all files."""
 all_seeds = []
 seed_files = find_all_seed_files()
 
 print(f"Found {len(seed_files)} potential seed files")
 
 for file_path in seed_files:
 try:
 with file_path.open() as f:
 data = json.load(f)
 
 # Try different structures
 items = []
 if isinstance(data, list):
 items = data
 elif isinstance(data, dict):
 if "seeds_and_identities" in data:
 items = data["seeds_and_identities"]
 elif "identities" in data:
 items = data["identities"]
 elif "results" in data:
 items = data["results"]
 else:
 # Try to extract from dict values
 for key, value in data.items():
 if isinstance(value, list):
 items.extend(value)
 
 # Extract seeds
 for item in items:
 if isinstance(item, dict):
 seed = item.get("seed", "")
 doc_id = item.get("identity", "") or item.get("documented_identity", "")
 source = str(file_path.relative_to(project_root))
 
 # If we have identity but no seed, extract seed from identity
 if not seed and doc_id and len(doc_id) == 60:
 seed = doc_id.lower()[:55]
 
 if seed and len(seed) == 55:
 all_seeds.append({
 "seed": seed,
 "documented_identity": doc_id,
 "source_file": source
 })
 elif isinstance(item, str) and len(item) == 60:
 # Item is an identity string, extract seed
 seed = item.lower()[:55]
 all_seeds.append({
 "seed": seed,
 "documented_identity": item,
 "source_file": str(file_path.relative_to(project_root))
 })
 except Exception as e:
 print(f"Error loading {file_path}: {e}")
 
 # Remove duplicates
 seen = set()
 unique_seeds = []
 for item in all_seeds:
 seed = item["seed"]
 if seed not in seen:
 seen.add(seed)
 unique_seeds.append(item)
 
 return unique_seeds

def main():
 """Main function."""
 print("=" * 80)
 print("MAP ALL SEEDS TO REAL IDs")
 print("=" * 80)
 print()
 
 if not VENV_PYTHON.exists():
 print("❌ venv-tx not found!")
 return
 
 # Load checkpoint
 checkpoint = {}
 if CHECKPOINT_FILE.exists():
 with CHECKPOINT_FILE.open() as f:
 checkpoint = json.load(f)
 print(f"📂 Loaded checkpoint: {checkpoint.get('processed', 0)}/{checkpoint.get('total', 0)}")
 print()
 
 # Load all seeds
 print("1. Loading all seeds from all files...")
 sys.stdout.flush()
 
 all_seeds = load_all_seeds()
 
 if checkpoint.get("all_seeds"):
 # Use seeds from checkpoint if available
 all_seeds = checkpoint["all_seeds"]
 print(f" ✅ Using {len(all_seeds)} seeds from checkpoint")
 else:
 print(f" ✅ Found {len(all_seeds)} unique seeds")
 checkpoint["all_seeds"] = all_seeds
 
 print()
 sys.stdout.flush()
 
 # Process seeds
 print("2. Deriving real identities from seeds...")
 print()
 sys.stdout.flush()
 
 results = checkpoint.get("results", [])
 processed = checkpoint.get("processed", 0)
 start_time = time.time()
 
 for idx, seed_item in enumerate(all_seeds[processed:], start=processed + 1):
 seed = seed_item["seed"]
 doc_id = seed_item.get("documented_identity", "")
 source = seed_item.get("source_file", "")
 
 if idx % 100 == 0:
 elapsed = time.time() - start_time
 rate = idx / elapsed if elapsed > 0 else 0
 remaining = (len(all_seeds) - idx) / rate if rate > 0 else 0
 print(f"Progress: {idx}/{len(all_seeds)} ({idx*100/len(all_seeds):.1f}%)")
 print(f" Rate: {rate:.1f} seeds/sec")
 print(f" ETA: {remaining/60:.1f} minutes")
 sys.stdout.flush()
 
 # Save checkpoint
 CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
 with CHECKPOINT_FILE.open("w") as f:
 json.dump({
 "processed": idx,
 "total": len(all_seeds),
 "all_seeds": all_seeds,
 "results": results
 }, f, indent=2)
 
 # Derive real identity
 success, real_id = derive_identity_from_seed(seed)
 
 if success:
 match = (real_id == doc_id)
 results.append({
 "seed": seed,
 "documented_identity": doc_id,
 "real_identity": real_id,
 "match": match,
 "source_file": source
 })
 else:
 results.append({
 "seed": seed,
 "documented_identity": doc_id,
 "error": real_id,
 "source_file": source
 })
 
 # Save final results
 OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
 
 matches = [r for r in results if r.get("match")]
 mismatches = [r for r in results if r.get("real_identity") and not r.get("match")]
 
 with OUTPUT_FILE.open("w") as f:
 json.dump({
 "total_seeds": len(all_seeds),
 "processed": len(results),
 "matches": len(matches),
 "mismatches": len(mismatches),
 "match_rate": f"{len(matches)*100/len(results):.1f}%" if results else "0%",
 "results": results,
 "matches_list": matches,
 "mismatches_sample": mismatches[:100] # First 100 for analysis
 }, f, indent=2)
 
 print()
 print("=" * 80)
 print("MAPPING COMPLETE")
 print("=" * 80)
 print(f"✅ Results saved to: {OUTPUT_FILE}")
 print()
 print(f"Summary:")
 print(f" Total seeds: {len(all_seeds)}")
 print(f" Processed: {len(results)}")
 print(f" Matches: {len(matches)} ({len(matches)*100/len(results):.1f}%)" if results else "0")
 print(f" Mismatches: {len(mismatches)}")
 
 # Create connection analysis
 if mismatches:
 print()
 print("Creating connection analysis...")
 connection_file = project_root / "outputs" / "derived" / "documented_to_real_id_connections.json"
 
 connections = []
 for item in mismatches[:1000]: # First 1000 for analysis
 connections.append({
 "documented_identity": item.get("documented_identity", ""),
 "real_identity": item.get("real_identity", ""),
 "seed": item.get("seed", "")
 })
 
 with connection_file.open("w") as f:
 json.dump({
 "total_connections": len(connections),
 "connections": connections
 }, f, indent=2)
 
 print(f"✅ Connection analysis saved to: {connection_file}")

if __name__ == "__main__":
 main()

