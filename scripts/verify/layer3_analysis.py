#!/usr/bin/env python3
"""
Complete Layer 3 analysis: Check assets, balances, and potential Layer 4.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)
from qubipy.rpc import rpc_client

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "layer3_complete_analysis.json"

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
class Layer3Record:
 label: str
 layer2_identity: str
 layer3_seed: str
 layer3_identity: str
 balance: str
 valid_tick: int | None
 owned_assets: list
 possessed_assets: list
 genesis_count: int
 layer4_identity: str | None = None
 layer4_exists: bool = False

def derive_layer3(identity: str) -> tuple[str, str]:
 """Derive Layer 3 identity from Layer 2 identity."""
 body = identity[:56].lower()[:55]
 seed_bytes = bytes(body, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 layer3_identity = get_identity_from_public_key(public_key)
 return body, layer3_identity

def derive_layer4(identity: str) -> tuple[str, str] | None:
 """Derive Layer 4 identity from Layer 3 identity."""
 body = identity[:56].lower()[:55]
 if len(body) != 55 or not body.isalpha():
 return None
 seed_bytes = bytes(body, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 layer4_identity = get_identity_from_public_key(public_key)
 return body, layer4_identity

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=== Complete Layer 3 Analysis ===\n")
 
 records = []
 
 for label, layer2_identity in LAYER2_IDENTITIES:
 print(f"Processing {label}...")
 
 layer3_seed, layer3_identity = derive_layer3(layer2_identity)
 
 try:
 time.sleep(0.5)
 balance_data = rpc.get_balance(layer3_identity)
 balance = balance_data.get('balance', '0') if balance_data else '0'
 valid_tick = balance_data.get('validForTick') if balance_data else None
 
 time.sleep(0.5)
 owned = rpc.get_owned_assets(layer3_identity)
 owned_list = owned if isinstance(owned, list) else (owned.get('assets', []) if owned else [])
 
 time.sleep(0.5)
 possessed = rpc.get_possessed_assets(layer3_identity)
 possessed_list = possessed if isinstance(possessed, list) else (possessed.get('assets', []) if possessed else [])
 
 genesis_count = sum(
 int(asset.get('data', {}).get('numberOfUnits', '0'))
 for asset in owned_list + possessed_list
 if asset.get('data', {}).get('issuedAsset', {}).get('name') == 'GENESIS' or
 asset.get('data', {}).get('ownedAsset', {}).get('issuedAsset', {}).get('name') == 'GENESIS'
 )
 
 # Check Layer 4
 layer4_result = derive_layer4(layer3_identity)
 layer4_identity = None
 layer4_exists = False
 
 if layer4_result:
 _, layer4_identity = layer4_result
 try:
 time.sleep(0.5)
 layer4_balance = rpc.get_balance(layer4_identity)
 layer4_exists = layer4_balance is not None
 except:
 pass
 
 record = Layer3Record(
 label=label,
 layer2_identity=layer2_identity,
 layer3_seed=layer3_seed,
 layer3_identity=layer3_identity,
 balance=balance,
 valid_tick=valid_tick,
 owned_assets=owned_list,
 possessed_assets=possessed_list,
 genesis_count=genesis_count,
 layer4_identity=layer4_identity,
 layer4_exists=layer4_exists,
 )
 
 records.append(record)
 
 print(f" Layer 3: {layer3_identity}")
 print(f" Balance: {balance} QU, Assets: {len(owned_list) + len(possessed_list)}, GENESIS: {genesis_count}")
 if layer4_identity:
 print(f" Layer 4: {layer4_identity} ({'EXISTS' if layer4_exists else 'NOT FOUND'})")
 print()
 
 except Exception as e:
 print(f" Error: {e}\n")
 
 # Save results
 data = {
 "layer3_records": [asdict(r) for r in records],
 "summary": {
 "total_layer3": len(records),
 "layer3_with_assets": sum(1 for r in records if len(r.owned_assets) + len(r.possessed_assets) > 0),
 "layer3_with_genesis": sum(1 for r in records if r.genesis_count > 0),
 "total_genesis": sum(r.genesis_count for r in records),
 "layer4_found": sum(1 for r in records if r.layer4_exists),
 },
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(data, f, indent=2)
 
 print("=== Summary ===")
 print(f"Layer 3 identities: {data['summary']['total_layer3']}/8")
 print(f"Layer 3 with assets: {data['summary']['layer3_with_assets']}/8")
 print(f"Layer 3 with GENESIS: {data['summary']['layer3_with_genesis']}/8")
 print(f"Total GENESIS on Layer 3: {data['summary']['total_genesis']}")
 print(f"Layer 4 identities found: {data['summary']['layer4_found']}/8")
 
 if data['summary']['layer4_found'] > 0:
 print("\n🎉 LAYER 4 EXISTS! The pattern continues!")
 
 print(f"\nFull report: {OUTPUT_JSON}")

if __name__ == "__main__":
 main()

