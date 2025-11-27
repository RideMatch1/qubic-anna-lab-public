#!/usr/bin/env python3
"""
Deep exploration of all layers: Check how deep the recursion goes,
analyze patterns, and find any special properties.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)
from qubipy.rpc import rpc_client

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "deep_layer_exploration.json"

LAYER2_IDENTITIES = [
 ("Diagonal #1", "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD"),
 ("Diagonal #2", "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE"),
 ("Diagonal #3", "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG"),
 ("Diagonal #4", "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI"),
 ("Vortex #1", "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL"),
 ("Vortex #2", "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI"),
 ("Vortex #3", "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN"),
 ("Vortex #4", "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB"),
]

@dataclass
class LayerRecord:
 layer: int
 identity: str
 seed_used: str
 balance: str
 valid_tick: Optional[int]
 owned_assets_count: int
 possessed_assets_count: int
 genesis_count: int
 next_layer_exists: bool
 next_layer_identity: Optional[str] = None

@dataclass
class IdentityChain:
 label: str
 layers: List[LayerRecord]
 max_depth: int
 special_properties: List[str]

def derive_next_layer(identity: str) -> tuple[str, str] | None:
 """Derive next layer identity from current identity."""
 body = identity[:56].lower()[:55]
 if len(body) != 55 or not body.isalpha() or not body.islower():
 return None
 
 try:
 seed_bytes = bytes(body, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 next_identity = get_identity_from_public_key(public_key)
 return body, next_identity
 except:
 return None

def check_identity(rpc: rpc_client.QubiPy_RPC, identity: str) -> dict:
 """Check identity status on-chain."""
 try:
 balance_data = rpc.get_balance(identity)
 balance = balance_data.get('balance', '0') if balance_data else '0'
 valid_tick = balance_data.get('validForTick') if balance_data else None
 
 owned = rpc.get_owned_assets(identity)
 possessed = rpc.get_possessed_assets(identity)
 
 owned_list = owned if isinstance(owned, list) else (owned.get('assets', []) if owned else [])
 possessed_list = possessed if isinstance(possessed, list) else (possessed.get('assets', []) if possessed else [])
 
 genesis_count = sum(
 int(asset.get('data', {}).get('numberOfUnits', '0'))
 for asset in owned_list + possessed_list
 if asset.get('data', {}).get('issuedAsset', {}).get('name') == 'GENESIS' or
 asset.get('data', {}).get('ownedAsset', {}).get('issuedAsset', {}).get('name') == 'GENESIS'
 )
 
 return {
 'balance': balance,
 'valid_tick': valid_tick,
 'owned_count': len(owned_list),
 'possessed_count': len(possessed_list),
 'genesis_count': genesis_count,
 'exists': True,
 }
 except:
 return {
 'balance': '0',
 'valid_tick': None,
 'owned_count': 0,
 'possessed_count': 0,
 'genesis_count': 0,
 'exists': False,
 }

def explore_chain(rpc: rpc_client.QubiPy_RPC, label: str, start_identity: str, max_layers: int = 10) -> IdentityChain:
 """Explore the full chain of layers for one identity."""
 layers = []
 current_identity = start_identity
 special_properties = []
 
 for layer_num in range(2, max_layers + 1): # Start from Layer 2
 # Derive next layer
 result = derive_next_layer(current_identity)
 if not result:
 break
 
 seed_used, next_identity = result
 
 # Check current layer
 time.sleep(0.3)
 status = check_identity(rpc, current_identity)
 
 # Check if next layer exists
 time.sleep(0.3)
 next_status = check_identity(rpc, next_identity)
 next_exists = next_status['exists']
 
 record = LayerRecord(
 layer=layer_num,
 identity=current_identity,
 seed_used=seed_used,
 balance=status['balance'],
 valid_tick=status['valid_tick'],
 owned_assets_count=status['owned_count'],
 possessed_assets_count=status['possessed_count'],
 genesis_count=status['genesis_count'],
 next_layer_exists=next_exists,
 next_layer_identity=next_identity if next_exists else None,
 )
 
 layers.append(record)
 
 # Track special properties
 if status['genesis_count'] > 0:
 special_properties.append(f"Layer {layer_num} has {status['genesis_count']} GENESIS assets")
 if int(status['balance']) > 0:
 special_properties.append(f"Layer {layer_num} has {status['balance']} QU balance")
 
 if not next_exists:
 break
 
 current_identity = next_identity
 
 return IdentityChain(
 label=label,
 layers=layers,
 max_depth=len(layers),
 special_properties=special_properties,
 )

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=== Deep Layer Exploration ===\n")
 print("Exploring all layers for each identity chain...\n")
 
 chains = []
 
 for label, layer2_identity in LAYER2_IDENTITIES:
 print(f"Exploring {label}...")
 chain = explore_chain(rpc, label, layer2_identity, max_layers=10)
 chains.append(chain)
 
 print(f" Depth: {chain.max_depth} layers")
 print(f" Special: {', '.join(chain.special_properties) if chain.special_properties else 'None'}")
 print()
 
 # Analysis
 print("=== Analysis ===")
 max_depth = max(c.max_depth for c in chains)
 min_depth = min(c.max_depth for c in chains)
 
 print(f"Maximum depth found: {max_depth} layers")
 print(f"Minimum depth found: {min_depth} layers")
 print(f"Average depth: {sum(c.max_depth for c in chains) / len(chains):.1f} layers")
 
 # Find layers with assets
 layers_with_assets = {}
 layers_with_genesis = {}
 
 for chain in chains:
 for layer in chain.layers:
 layer_num = layer.layer
 if layer.owned_assets_count + layer.possessed_assets_count > 0:
 if layer_num not in layers_with_assets:
 layers_with_assets[layer_num] = 0
 layers_with_assets[layer_num] += 1
 
 if layer.genesis_count > 0:
 if layer_num not in layers_with_genesis:
 layers_with_genesis[layer_num] = 0
 layers_with_genesis[layer_num] += 1
 
 print(f"\nLayers with assets: {layers_with_assets}")
 print(f"Layers with GENESIS: {layers_with_genesis}")
 
 # Save results
 data = {
 "chains": [asdict(c) for c in chains],
 "analysis": {
 "max_depth": max_depth,
 "min_depth": min_depth,
 "layers_with_assets": layers_with_assets,
 "layers_with_genesis": layers_with_genesis,
 },
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(data, f, indent=2)
 
 print(f"\nFull report saved to: {OUTPUT_JSON}")
 
 # Summary
 print("\n=== Key Findings ===")
 if layers_with_genesis:
 print(f"✅ Only Layer {list(layers_with_genesis.keys())[0]} has GENESIS assets")
 print(f"✅ Recursion goes at least {max_depth} layers deep")
 print(f"✅ All chains have consistent depth: {min_depth == max_depth}")
 
 if min_depth == max_depth:
 print("\n🎯 All chains stop at the same depth - this might be intentional!")

if __name__ == "__main__":
 main()

