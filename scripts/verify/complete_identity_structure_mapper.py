#!/usr/bin/env python3
"""
Complete Identity Structure Mapper

Systematically tests ALL found identities as seeds and maps the complete structure.
This will find ALL possible identities we can derive from what we have.

Goal: Understand the EXACT data foundation before making assumptions.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Set

from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)
from qubipy.rpc import rpc_client

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "complete_identity_structure.json"

# Load all known identities from various sources
def load_all_identities() -> Set[str]:
 """Load all identities from all JSON files."""
 identities = set()
 
 files = [
 "outputs/derived/recursive_layer_map.json",
 "outputs/derived/identity_deep_scan.json",
 "outputs/derived/deep_layer_exploration.json",
 "outputs/derived/layer3_complete_analysis.json",
 "outputs/derived/seed_derivation_mass_scan.json",
 ]
 
 for file_path in files:
 path = Path(file_path)
 if not path.exists():
 continue
 
 try:
 with path.open() as f:
 data = json.load(f)
 
 # Extract identities based on structure
 if isinstance(data, dict):
 # recursive_layer_map
 for key in ["known_8_exploration", "new_seeds_exploration"]:
 if key in data:
 exp = data[key]
 if "all_identities" in exp:
 identities.update(exp["all_identities"])
 if "layer_map" in exp:
 for layer_ids in exp["layer_map"].values():
 identities.update(layer_ids)
 
 # identity_deep_scan
 if "records" in data:
 for record in data["records"]:
 if "identity" in record:
 identities.add(record["identity"])
 
 # deep_layer_exploration
 if "chains" in data:
 for chain in data["chains"]:
 for layer in chain.get("layers", []):
 if "identity" in layer:
 identities.add(layer["identity"])
 
 # layer3_complete_analysis
 if "layer3_records" in data:
 for record in data["layer3_records"]:
 if "layer3_identity" in record:
 identities.add(record["layer3_identity"])
 if "layer4_identity" in record:
 identities.add(record["layer4_identity"])
 
 # seed_derivation_mass_scan
 if "tested_identities" in data:
 for item in data["tested_identities"]:
 if "identity" in item:
 identities.add(item["identity"])
 if "original_identity" in item:
 identities.add(item["original_identity"])
 if "derived_identity" in item:
 identities.add(item["derived_identity"])
 
 except Exception as e:
 print(f"⚠️ Error loading {file_path}: {e}")
 
 return identities

def identity_to_seed(identity: str) -> str | None:
 """Convert identity to seed (55 chars, lowercase)."""
 if len(identity) < 56:
 return None
 body = identity[:56].lower()[:55]
 if len(body) == 55 and body.isalpha():
 return body
 return None

def derive_identity(seed: str) -> str | None:
 """Derive Qubic identity from seed."""
 try:
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 identity = get_identity_from_public_key(public_key)
 return identity
 except:
 return None

def check_on_chain(rpc: rpc_client.QubiPy_RPC, identity: str) -> bool:
 """Check if identity exists on-chain."""
 try:
 balance = rpc.get_balance(identity)
 return balance is not None
 except:
 return False

def map_complete_structure(rpc: rpc_client.QubiPy_RPC, start_identities: Set[str], max_depth: int = 15) -> Dict:
 """Map the complete structure starting from all known identities."""
 
 visited: Set[str] = set()
 layer_map: Dict[int, List[str]] = defaultdict(list)
 seed_map: Dict[str, str] = {} # identity -> seed used
 parent_map: Dict[str, str] = {} # identity -> parent identity
 depth_map: Dict[str, int] = {} # identity -> depth
 
 # BFS queue: (identity, depth, parent)
 queue = deque([(id, 1, None) for id in start_identities])
 
 print(f"Starting from {len(start_identities)} identities...")
 print(f"Max depth: {max_depth}\n")
 
 total_checked = 0
 total_derived = 0
 
 while queue:
 current_identity, depth, parent = queue.popleft()
 
 if current_identity in visited:
 continue
 
 if depth > max_depth:
 continue
 
 visited.add(current_identity)
 layer_map[depth].append(current_identity)
 depth_map[current_identity] = depth
 
 if parent:
 parent_map[current_identity] = parent
 
 total_checked += 1
 if total_checked % 50 == 0:
 print(f" Checked {total_checked}, found {len(visited)} identities, {total_derived} derived on-chain")
 
 # Try to derive next layer
 seed = identity_to_seed(current_identity)
 if not seed:
 continue
 
 seed_map[current_identity] = seed
 
 derived = derive_identity(seed)
 if not derived:
 continue
 
 # Check if derived identity exists on-chain
 if check_on_chain(rpc, derived):
 total_derived += 1
 if total_derived % 10 == 0:
 print(f" Layer {depth} → {depth+1}: {current_identity[:30]}... → {derived[:30]}... ✅")
 queue.append((derived, depth + 1, current_identity))
 
 return {
 "total_identities": len(visited),
 "max_depth": max(depth_map.values()) if depth_map else 0,
 "layer_map": {k: v for k, v in sorted(layer_map.items())},
 "seed_map": seed_map,
 "parent_map": parent_map,
 "depth_map": depth_map,
 "all_identities": list(visited),
 "total_checked": total_checked,
 "total_derived_on_chain": total_derived,
 }

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("COMPLETE IDENTITY STRUCTURE MAPPER")
 print("=" * 80)
 print()
 print("Loading all known identities from all sources...")
 
 all_identities = load_all_identities()
 
 print(f"✅ Loaded {len(all_identities)} unique identities")
 print()
 print("Mapping complete structure...")
 print("(This will test each identity as a seed and follow the chain)")
 print()
 
 result = map_complete_structure(rpc, all_identities, max_depth=15)
 
 print()
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 print(f"Total identities found: {result['total_identities']}")
 print(f"Max depth: {result['max_depth']}")
 print(f"Total checked: {result['total_checked']}")
 print(f"Total derived on-chain: {result['total_derived_on_chain']}")
 print()
 
 print("Identities per layer:")
 for layer in sorted(result['layer_map'].keys()):
 count = len(result['layer_map'][layer])
 print(f" Layer {layer}: {count} identities")
 
 print()
 print(f"Saving to: {OUTPUT_JSON}")
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(result, f, indent=2)
 
 print("✅ Done!")

if __name__ == "__main__":
 main()

