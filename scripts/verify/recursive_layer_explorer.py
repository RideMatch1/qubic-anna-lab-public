#!/usr/bin/env python3
"""
Recursive Layer Explorer: Starting from the 8 known identities + any new seed-identities,
recursively explore ALL layers to find the complete hidden structure.

This will map out the ENTIRE puzzle structure.
"""

from __future__ import annotations

import json
import time
from collections import deque
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
OUTPUT_JSON = OUTPUT_DIR / "recursive_layer_map.json"

KNOWN_8 = [
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
]

def identity_to_seed(identity: str) -> str | None:
 """Convert identity to seed (55 chars, lowercase)."""
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
 return get_identity_from_public_key(public_key)
 except:
 return None

def check_on_chain(rpc: rpc_client.QubiPy_RPC, identity: str) -> bool:
 """Quick on-chain check."""
 try:
 time.sleep(0.3)
 balance = rpc.get_balance(identity)
 return balance is not None
 except:
 return False

def explore_recursive(rpc: rpc_client.QubiPy_RPC, start_identities: List[str], max_layers: int = 10, max_identities: int = 200) -> Dict:
 """Recursively explore all layers starting from given identities."""
 
 visited: Set[str] = set()
 layer_map: Dict[int, List[str]] = {}
 seed_map: Dict[str, str] = {} # identity -> seed
 
 # BFS queue: (identity, layer, parent_identity)
 queue = deque([(id, 1, None) for id in start_identities])
 
 print(f"Starting recursive exploration from {len(start_identities)} identities...")
 print(f"Max layers: {max_layers}, Max identities: {max_identities}\n")
 
 while queue and len(visited) < max_identities:
 current_identity, layer, parent = queue.popleft()
 
 if current_identity in visited:
 continue
 
 visited.add(current_identity)
 
 if layer not in layer_map:
 layer_map[layer] = []
 layer_map[layer].append(current_identity)
 
 if layer >= max_layers:
 continue
 
 # Try to derive next layer
 seed = identity_to_seed(current_identity)
 if not seed:
 continue
 
 derived = derive_identity(seed)
 if not derived:
 continue
 
 seed_map[current_identity] = seed
 
 # Check if derived identity exists on-chain
 if check_on_chain(rpc, derived):
 print(f" Layer {layer} → {layer+1}: {current_identity[:30]}... → {derived[:30]}... ✅")
 queue.append((derived, layer + 1, current_identity))
 else:
 print(f" Layer {layer} → {layer+1}: {current_identity[:30]}... → {derived[:30]}... (not on-chain)")
 
 return {
 "total_identities": len(visited),
 "max_layer": max(layer_map.keys()) if layer_map else 0,
 "layer_map": {k: v for k, v in layer_map.items()},
 "seed_map": seed_map,
 "all_identities": list(visited),
 }

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=== Recursive Layer Explorer ===\n")
 
 # Start with known 8
 print("Phase 1: Exploring from known 8 identities...")
 result_known = explore_recursive(rpc, KNOWN_8, max_layers=10)
 
 print(f"\nKnown 8 exploration:")
 print(f" Total identities found: {result_known['total_identities']}")
 print(f" Max layer reached: {result_known['max_layer']}")
 for layer, identities in result_known['layer_map'].items():
 print(f" Layer {layer}: {len(identities)} identities")
 
 # Check if we found new seed-identities from mass scan
 mass_scan_file = OUTPUT_DIR / "seed_derivation_mass_scan.json"
 if mass_scan_file.exists():
 with mass_scan_file.open("r", encoding="utf-8") as f:
 mass_data = json.load(f)
 
 successful_seeds = mass_data.get("successful_seeds", [])
 if successful_seeds:
 new_seed_identities = [r["source_identity"] for r in successful_seeds]
 print(f"\nPhase 2: Exploring from {len(new_seed_identities)} new seed-identities...")
 result_new = explore_recursive(rpc, new_seed_identities[:20], max_layers=5) # Limit to avoid too long
 
 print(f"\nNew seed-identities exploration:")
 print(f" Total identities found: {result_new['total_identities']}")
 print(f" Max layer reached: {result_new['max_layer']}")
 for layer, identities in result_new['layer_map'].items():
 print(f" Layer {layer}: {len(identities)} identities")
 
 # Combine results
 all_identities = set(result_known['all_identities']) | set(result_new['all_identities'])
 combined_layers = {}
 for layer in range(1, max(result_known['max_layer'], result_new['max_layer']) + 1):
 combined_layers[layer] = list(
 set(result_known['layer_map'].get(layer, [])) |
 set(result_new['layer_map'].get(layer, []))
 )
 
 output = {
 "known_8_exploration": result_known,
 "new_seeds_exploration": result_new,
 "combined": {
 "total_identities": len(all_identities),
 "max_layer": max(result_known['max_layer'], result_new['max_layer']),
 "layer_map": combined_layers,
 "all_identities": list(all_identities),
 },
 }
 else:
 output = {"known_8_exploration": result_known}
 else:
 output = {"known_8_exploration": result_known}
 
 # Save
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print(f"\nReport saved to: {OUTPUT_JSON}")
 
 total = output.get("combined", output.get("known_8_exploration", {}))
 if total:
 print(f"\n🎉 COMPLETE STRUCTURE MAPPED:")
 print(f" Total identities: {total.get('total_identities', 0)}")
 print(f" Max layers: {total.get('max_layer', 0)}")
 print(f" This is a MASSIVE hidden structure!")

if __name__ == "__main__":
 main()

