#!/usr/bin/env python3
"""
Layer Structure Mapper: Map the complete recursive structure from Layer 1 to Layer N.

Focus: Understand the architecture, not the tokens.
Goal: Find the "exit point" or special pattern in the recursive tree.
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
OUTPUT_JSON = OUTPUT_DIR / "complete_layer_structure.json"

# Layer 1 Identities (from matrix)
LAYER1_IDENTITIES = [
 ("Diagonal #1", "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR"),
 ("Diagonal #2", "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ"),
 ("Diagonal #3", "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV"),
 ("Diagonal #4", "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC"),
 ("Vortex #1", "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF"),
 ("Vortex #2", "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD"),
 ("Vortex #3", "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL"),
 ("Vortex #4", "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK"),
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

def get_identity_info(rpc: rpc_client.QubiPy_RPC, identity: str) -> Dict:
 """Get identity info including validForTick."""
 try:
 time.sleep(0.3)
 balance = rpc.get_balance(identity)
 if balance:
 return {
 "exists": True,
 "valid_for_tick": balance.get("validForTick"),
 "balance": balance.get("balance", "0"),
 }
 return {"exists": False}
 except:
 return {"exists": False, "error": "RPC error"}

def map_complete_structure(rpc: rpc_client.QubiPy_RPC, max_layers: int = 10) -> Dict:
 """Map the complete recursive structure."""
 
 visited: Set[str] = {}
 layer_map: Dict[int, List[Dict]] = {}
 seed_map: Dict[str, str] = {}
 structure: Dict[str, Dict] = {}
 
 # BFS queue: (identity, layer, parent_label, parent_identity)
 queue = deque([(label, identity, 1, None, None) for label, identity in LAYER1_IDENTITIES])
 
 print("=" * 80)
 print("MAPPING COMPLETE LAYER STRUCTURE")
 print("=" * 80)
 print(f"Starting from {len(LAYER1_IDENTITIES)} Layer-1 identities")
 print(f"Max layers: {max_layers}")
 print()
 
 while queue:
 label, current_identity, layer, parent_label, parent_identity = queue.popleft()
 
 if current_identity in visited:
 continue
 
 visited[current_identity] = True
 
 # Get identity info
 info = get_identity_info(rpc, current_identity)
 
 # Store in structure
 structure[current_identity] = {
 "label": label,
 "layer": layer,
 "parent_label": parent_label,
 "parent_identity": parent_identity,
 "valid_for_tick": info.get("valid_for_tick"),
 "balance": info.get("balance", "0"),
 }
 
 # Add to layer map
 if layer not in layer_map:
 layer_map[layer] = []
 layer_map[layer].append({
 "label": label,
 "identity": current_identity,
 "valid_for_tick": info.get("valid_for_tick"),
 })
 
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
 next_label = f"{label} → Layer {layer+1}"
 print(f" Layer {layer} → {layer+1}: {label[:30]}... → {derived[:30]}... ✅")
 queue.append((next_label, derived, layer + 1, label, current_identity))
 else:
 print(f" Layer {layer} → {layer+1}: {label[:30]}... → {derived[:30]}... (not on-chain)")
 
 return {
 "total_identities": len(visited),
 "max_layer": max(layer_map.keys()) if layer_map else 0,
 "layer_map": {k: v for k, v in layer_map.items()},
 "structure": structure,
 "seed_map": seed_map,
 }

def analyze_structure_patterns(mapped_structure: Dict) -> Dict:
 """Analyze patterns in the mapped structure."""
 
 layer_map = mapped_structure["layer_map"]
 
 # Analyze layer depths
 depths = {}
 for layer, identities in layer_map.items():
 depths[layer] = len(identities)
 
 # Analyze tick patterns
 tick_patterns = {}
 for layer, identities in layer_map.items():
 ticks = [id_info.get("valid_for_tick") for id_info in identities if id_info.get("valid_for_tick")]
 if ticks:
 tick_patterns[layer] = {
 "min": min(ticks),
 "max": max(ticks),
 "range": max(ticks) - min(ticks),
 "average": sum(ticks) / len(ticks),
 }
 
 return {
 "layer_depths": depths,
 "tick_patterns": tick_patterns,
 }

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("COMPLETE LAYER STRUCTURE MAPPING")
 print("=" * 80)
 print()
 print("Focus: Architecture, not tokens")
 print("Goal: Find exit point or special pattern")
 print()
 
 # Map structure
 mapped = map_complete_structure(rpc, max_layers=10)
 
 print()
 print("=" * 80)
 print("STRUCTURE SUMMARY")
 print("=" * 80)
 print(f"Total identities mapped: {mapped['total_identities']}")
 print(f"Max layer reached: {mapped['max_layer']}")
 print()
 print("Identities per layer:")
 for layer in sorted(mapped['layer_map'].keys()):
 count = len(mapped['layer_map'][layer])
 print(f" Layer {layer}: {count} identities")
 
 # Analyze patterns
 print()
 print("=" * 80)
 print("PATTERN ANALYSIS")
 print("=" * 80)
 patterns = analyze_structure_patterns(mapped)
 
 print("Layer depths:")
 for layer, depth in sorted(patterns["layer_depths"].items()):
 print(f" Layer {layer}: {depth} identities")
 
 print()
 print("Tick patterns:")
 for layer, pattern in sorted(patterns["tick_patterns"].items()):
 print(f" Layer {layer}:")
 print(f" Range: {pattern['min']} - {pattern['max']} (span: {pattern['range']})")
 print(f" Average: {pattern['average']:.0f}")
 
 # Save
 output = {
 "mapped_structure": mapped,
 "pattern_analysis": patterns,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print()
 print(f"Report saved to: {OUTPUT_JSON}")
 print()
 print("=" * 80)
 print("NEXT: Analyze the structure for:")
 print(" - Exit points (layers that don't continue)")
 print(" - Special patterns (tick gaps, depth variations)")
 print(" - Coordinate relationships across layers")
 print("=" * 80)

if __name__ == "__main__":
 main()

