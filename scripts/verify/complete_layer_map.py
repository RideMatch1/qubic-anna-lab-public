#!/usr/bin/env python3
"""
Complete mapping of all layers with proper rate limiting.
Creates a full map of the recursive structure.
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
OUTPUT_JSON = OUTPUT_DIR / "complete_layer_map.json"
OUTPUT_MD = OUTPUT_DIR / "complete_layer_map.md"

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
class LayerInfo:
 layer_num: int
 identity: str
 seed: str
 balance: str
 valid_tick: Optional[int]
 assets_count: int
 genesis_count: int
 next_layer_identity: Optional[str] = None
 next_layer_exists: bool = False

@dataclass
class ChainMap:
 label: str
 layers: List[LayerInfo]
 max_depth: int
 has_genesis: bool
 genesis_layer: Optional[int] = None

def derive_next(identity: str) -> tuple[str, str] | None:
 """Derive next layer from identity."""
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

def check_identity_safe(rpc: rpc_client.QubiPy_RPC, identity: str, delay: float = 1.0) -> dict:
 """Check identity with proper rate limiting."""
 time.sleep(delay)
 try:
 balance_data = rpc.get_balance(identity)
 balance = balance_data.get('balance', '0') if balance_data else '0'
 valid_tick = balance_data.get('validForTick') if balance_data else None
 
 time.sleep(delay)
 owned = rpc.get_owned_assets(identity)
 owned_list = owned if isinstance(owned, list) else (owned.get('assets', []) if owned else [])
 
 time.sleep(delay)
 possessed = rpc.get_possessed_assets(identity)
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
 'assets_count': len(owned_list) + len(possessed_list),
 'genesis_count': genesis_count,
 'exists': True,
 }
 except Exception as e:
 if '429' in str(e) or 'Too Many Requests' in str(e):
 return {'error': 'rate_limited', 'exists': None}
 return {'error': str(e), 'exists': False}

def map_chain(rpc: rpc_client.QubiPy_RPC, label: str, start_identity: str, max_depth: int = 15) -> ChainMap:
 """Map the complete chain for one identity."""
 layers = []
 current = start_identity
 has_genesis = False
 genesis_layer = None
 
 for layer_num in range(2, max_depth + 1):
 result = derive_next(current)
 if not result:
 break
 
 seed, next_identity = result
 
 # Check current layer
 status = check_identity_safe(rpc, current, delay=1.5)
 
 if status.get('exists') is None: # Rate limited
 break
 
 if not status.get('exists', False):
 break
 
 # Check next layer
 next_status = check_identity_safe(rpc, next_identity, delay=1.5)
 next_exists = next_status.get('exists', False) if next_status.get('exists') is not None else False
 
 layer_info = LayerInfo(
 layer_num=layer_num,
 identity=current,
 seed=seed,
 balance=status.get('balance', '0'),
 valid_tick=status.get('valid_tick'),
 assets_count=status.get('assets_count', 0),
 genesis_count=status.get('genesis_count', 0),
 next_layer_identity=next_identity if next_exists else None,
 next_layer_exists=next_exists,
 )
 
 layers.append(layer_info)
 
 if status.get('genesis_count', 0) > 0:
 has_genesis = True
 if genesis_layer is None:
 genesis_layer = layer_num
 
 if not next_exists:
 break
 
 current = next_identity
 
 return ChainMap(
 label=label,
 layers=layers,
 max_depth=len(layers),
 has_genesis=has_genesis,
 genesis_layer=genesis_layer,
 )

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=== Complete Layer Mapping ===\n")
 print("This will take several minutes due to rate limiting...\n")
 
 chains = []
 
 for label, identity in LAYER2_IDENTITIES:
 print(f"Mapping {label}...")
 chain = map_chain(rpc, label, identity, max_depth=15)
 chains.append(chain)
 
 print(f" Depth: {chain.max_depth} layers")
 if chain.has_genesis:
 print(f" GENESIS on Layer {chain.genesis_layer}")
 print()
 
 # Analysis
 print("=== Complete Analysis ===")
 
 max_depth = max(c.max_depth for c in chains) if chains else 0
 min_depth = min(c.max_depth for c in chains) if chains else 0
 
 print(f"Maximum depth: {max_depth} layers")
 print(f"Minimum depth: {min_depth} layers")
 
 genesis_layers = [c.genesis_layer for c in chains if c.has_genesis and c.genesis_layer]
 if genesis_layers:
 print(f"GENESIS assets found on layers: {set(genesis_layers)}")
 if len(set(genesis_layers)) == 1:
 print(f"✅ All GENESIS assets are on Layer {genesis_layers[0]} only!")
 
 # Save
 data = {
 "chains": [asdict(c) for c in chains],
 "summary": {
 "max_depth": max_depth,
 "min_depth": min_depth,
 "total_chains": len(chains),
 "chains_with_genesis": sum(1 for c in chains if c.has_genesis),
 "genesis_layers": list(set(genesis_layers)),
 },
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(data, f, indent=2)
 
 # Create markdown report
 lines = [
 "# Complete Layer Map",
 "",
 f"**Total Chains:** {len(chains)}",
 f"**Max Depth:** {max_depth} layers",
 f"**Min Depth:** {min_depth} layers",
 "",
 "## Chains",
 "",
 ]
 
 for chain in chains:
 lines.append(f"### {chain.label}")
 lines.append("")
 lines.append(f"- **Depth:** {chain.max_depth} layers")
 if chain.has_genesis:
 lines.append(f"- **GENESIS:** Layer {chain.genesis_layer}")
 lines.append("")
 lines.append("| Layer | Identity | Balance | Assets | GENESIS | Next Exists |")
 lines.append("| --- | --- | --- | --- | --- | --- |")
 
 for layer in chain.layers:
 lines.append(
 f"| {layer.layer_num} | `{layer.identity[:30]}...` | {layer.balance} | "
 f"{layer.assets_count} | {layer.genesis_count} | {'✓' if layer.next_layer_exists else '✗'} |"
 )
 lines.append("")
 
 OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
 
 print(f"\nReports saved:")
 print(f" JSON: {OUTPUT_JSON}")
 print(f" Markdown: {OUTPUT_MD}")

if __name__ == "__main__":
 main()

