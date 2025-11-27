#!/usr/bin/env python3
"""
Map ALL Seeds to Real IDs - Complete Version

Mappt ALLE Seeds die wir haben (aus allen Quellen) zu ihren echten Identities.
Erstellt eine vollständige Mapping-Datenbank for alle ~25k Wallets.
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
OUTPUT_FILE = project_root / "outputs" / "derived" / "complete_seeds_to_real_ids_mapping.json"
CONNECTION_FILE = project_root / "outputs" / "derived" / "documented_to_real_id_connections.json"

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

def load_all_seeds_from_100_file():
 """Load all seeds from the 100_seeds_and_identities.json file."""
 file_path = project_root / "github_export" / "100_seeds_and_identities.json"
 
 if not file_path.exists():
 return []
 
 with file_path.open() as f:
 data = json.load(f)
 
 if isinstance(data, dict) and "seeds_and_identities" in data:
 items = data["seeds_and_identities"]
 elif isinstance(data, list):
 items = data
 else:
 return []
 
 seeds = []
 for item in items:
 if isinstance(item, dict):
 seed = item.get("seed", "")
 doc_id = item.get("identity", "")
 
 # If we have identity but no seed, extract seed
 if not seed and doc_id and len(doc_id) == 60:
 seed = doc_id.lower()[:55]
 
 if seed and len(seed) == 55:
 seeds.append({
 "seed": seed,
 "documented_identity": doc_id,
 "source": "100_seeds_and_identities.json"
 })
 
 return seeds

def main():
 """Main function."""
 print("=" * 80)
 print("MAP ALL SEEDS TO REAL IDs - COMPLETE")
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
 print("1. Loading all seeds...")
 sys.stdout.flush()
 
 if checkpoint.get("all_seeds"):
 all_seeds = checkpoint["all_seeds"]
 print(f" ✅ Using {len(all_seeds)} seeds from checkpoint")
 else:
 all_seeds = load_all_seeds_from_100_file()
 print(f" ✅ Found {len(all_seeds)} seeds from 100_seeds_and_identities.json")
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
 
 if idx % 10 == 0:
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
 "source": seed_item.get("source", "")
 })
 else:
 results.append({
 "seed": seed,
 "documented_identity": doc_id,
 "error": real_id,
 "source": seed_item.get("source", "")
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
 "mismatches_list": mismatches
 }, f, indent=2)
 
 # Create connection analysis
 if mismatches:
 print()
 print("3. Creating connection analysis...")
 sys.stdout.flush()
 
 connections = []
 for item in mismatches:
 connections.append({
 "documented_identity": item.get("documented_identity", ""),
 "real_identity": item.get("real_identity", ""),
 "seed": item.get("seed", "")
 })
 
 CONNECTION_FILE.parent.mkdir(parents=True, exist_ok=True)
 with CONNECTION_FILE.open("w") as f:
 json.dump({
 "total_connections": len(connections),
 "description": "Mapping between documented identities (from matrix) and real identities (from seeds)",
 "connections": connections
 }, f, indent=2)
 
 print(f" ✅ Connection analysis saved to: {CONNECTION_FILE}")
 
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
 print()
 print(f"✅ Connection file: {CONNECTION_FILE}")

if __name__ == "__main__":
 main()

