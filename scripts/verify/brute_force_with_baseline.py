#!/usr/bin/env python3
"""
Brute Force with Baseline: Captures baseline assets BEFORE testing, then checks for NEW assets only.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Set

from qubipy.rpc import rpc_client
from qubipy.tx.utils import (
 get_public_key_from_identity,
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
)
from qubipy.crypto.utils import sign, kangaroo_twelve

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
AMOUNT_QU = 1
TARGET_TICK_OFFSET = 25
ASSET_CHECK_DELAY = 15

BASE_TICK_GAP = 1649
TEST_RANGE = 5 # 1644 to 1654

BLOCKS_TO_TEST = [1, 2, 3, 4, 5, 6, 8]

LAYER2_IDENTITIES = [
 {"label": "Diagonal #1", "block_id": 1, "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd", "identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD"},
 {"label": "Diagonal #2", "block_id": 2, "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr", "identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE"},
 {"label": "Diagonal #3", "block_id": 3, "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn", "identity": "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG"},
 {"label": "Diagonal #4", "block_id": 4, "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht", "identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI"},
 {"label": "Vortex #1", "block_id": 5, "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml", "identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL"},
 {"label": "Vortex #2", "block_id": 6, "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb", "identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI"},
 {"label": "Vortex #3", "block_id": 7, "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw", "identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN"},
 {"label": "Vortex #4", "block_id": 8, "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc", "identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB"},
]

def get_asset_ids(rpc: rpc_client.QubiPy_RPC, identity: str) -> Set[tuple]:
 """Get set of asset IDs (issuanceIndex, name) for an identity."""
 asset_ids = set()
 
 try:
 owned = rpc.get_owned_assets(identity)
 if isinstance(owned, list):
 for asset in owned:
 issuance_index = asset.get("data", {}).get("issuanceIndex")
 name = asset.get("data", {}).get("issuedAsset", {}).get("name")
 if issuance_index and name:
 asset_ids.add((issuance_index, name))
 except Exception as e:
 print(f" ⚠️ Error getting owned assets: {e}")
 
 try:
 possessed = rpc.get_possessed_assets(identity)
 if isinstance(possessed, list):
 for asset in possessed:
 issuance_index = asset.get("data", {}).get("issuanceIndex")
 name = asset.get("data", {}).get("ownedAsset", {}).get("issuedAsset", {}).get("name")
 if issuance_index and name:
 asset_ids.add((issuance_index, name))
 except Exception as e:
 print(f" ⚠️ Error getting possessed assets: {e}")
 
 return asset_ids

def build_tx_with_payload(seed: str, dest_identity: str, amount: int, target_tick: int, payload: str) -> bytes:
 """Build transaction with payload."""
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 source_pubkey = get_public_key_from_private_key(private_key)
 dest_pubkey = get_public_key_from_identity(dest_identity)
 
 built_data = bytearray()
 built_data.extend(source_pubkey)
 built_data.extend(dest_pubkey)
 built_data.extend(amount.to_bytes(8, byteorder='little'))
 built_data.extend(target_tick.to_bytes(4, byteorder='little'))
 built_data.extend((0).to_bytes(2, byteorder='little'))
 
 payload_bytes = payload.encode('utf-8')
 built_data.extend(len(payload_bytes).to_bytes(2, byteorder='little'))
 built_data.extend(payload_bytes)
 
 tx_digest = kangaroo_twelve(built_data, len(built_data), 32)
 signature = sign(subseed, source_pubkey, tx_digest)
 built_data.extend(signature)
 
 return bytes(built_data)

def main():
 print("=" * 80)
 print("🔬 BRUTE FORCE WITH BASELINE")
 print("=" * 80)
 print()
 print("Step 1: Capture baseline assets for all identities")
 print("Step 2: Send transactions with different tick gaps")
 print("Step 3: Check for NEW assets (not in baseline)")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 current_tick = rpc.get_latest_tick()
 
 blocks_data = {item["block_id"]: item for item in LAYER2_IDENTITIES if item["block_id"] in BLOCKS_TO_TEST}
 
 # Step 1: Capture baseline
 print("=" * 80)
 print("STEP 1: CAPTURING BASELINE ASSETS")
 print("=" * 80)
 print()
 
 baselines = {}
 for block_id in BLOCKS_TO_TEST:
 identity = blocks_data[block_id]["identity"]
 label = blocks_data[block_id]["label"]
 print(f" Capturing baseline for Block #{block_id} ({label})...")
 
 try:
 baseline_assets = get_asset_ids(rpc, identity)
 baselines[block_id] = baseline_assets
 print(f" ✅ Baseline: {len(baseline_assets)} assets")
 except Exception as e:
 print(f" ⚠️ Error: {e}")
 baselines[block_id] = set()
 
 time.sleep(0.5)
 
 print()
 print("=" * 80)
 print("STEP 2: SENDING TRANSACTIONS")
 print("=" * 80)
 print()
 
 results = {}
 
 for block_id in BLOCKS_TO_TEST:
 block_data = blocks_data[block_id]
 label = block_data["label"]
 
 print(f"Testing Block #{block_id} ({label})...")
 block_results = []
 
 for tick_gap in range(BASE_TICK_GAP - TEST_RANGE, BASE_TICK_GAP + TEST_RANGE + 1):
 payload = f"{block_id},2,{tick_gap}"
 print(f" ▶️ Tick gap {tick_gap}: '{payload}'")
 
 try:
 # Get fresh tick for each transaction
 current_tick = rpc.get_latest_tick()
 target_tick = current_tick + TARGET_TICK_OFFSET
 tx_bytes = build_tx_with_payload(
 block_data["seed"],
 CONTRACT_ID,
 AMOUNT_QU,
 target_tick,
 payload
 )
 
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId", response.get("transactionHash", "UNKNOWN"))
 print(f" ✅ TX sent: {tx_id}")
 
 # Wait for contract response
 print(f" ⏳ Waiting {ASSET_CHECK_DELAY} seconds...")
 time.sleep(ASSET_CHECK_DELAY)
 
 # Check for NEW assets
 current_assets = get_asset_ids(rpc, block_data["identity"])
 baseline_assets = baselines[block_id]
 new_assets = current_assets - baseline_assets
 
 success = len(new_assets) > 0
 
 if success:
 print(f" 🎉 SUCCESS! {len(new_assets)} NEW assets found!")
 for asset_id in new_assets:
 print(f" - {asset_id}")
 block_results.append({
 "tick_gap": tick_gap,
 "payload": payload,
 "tx_id": tx_id,
 "status": "SUCCESS",
 "new_assets": len(new_assets)
 })
 print(f" ✅ Block #{block_id} works with tick gap: {tick_gap}")
 break # Stop testing this block
 else:
 print(f" ❌ No new assets (baseline: {len(baseline_assets)}, current: {len(current_assets)})")
 block_results.append({
 "tick_gap": tick_gap,
 "payload": payload,
 "tx_id": tx_id,
 "status": "no_new_assets"
 })
 
 except Exception as e:
 print(f" ❌ Error: {e}")
 block_results.append({
 "tick_gap": tick_gap,
 "payload": payload,
 "tx_id": None,
 "status": "error",
 "error": str(e)
 })
 
 time.sleep(0.5)
 
 results[block_id] = block_results
 print()
 
 # Save results
 output_file = Path("outputs/derived/brute_force_with_baseline.json")
 output_file.parent.mkdir(parents=True, exist_ok=True)
 
 with output_file.open("w", encoding="utf-8") as f:
 json.dump({
 "baselines": {str(k): list(v) for k, v in baselines.items()},
 "results": results
 }, f, indent=2)
 
 print("=" * 80)
 print("✅ COMPLETE")
 print("=" * 80)
 print()
 
 # Summary
 working_gaps = {}
 for block_id, block_results in results.items():
 successful = [r for r in block_results if r.get("status") == "SUCCESS"]
 if successful:
 working_gaps[block_id] = successful[0]["tick_gap"]
 print(f"✅ Block #{block_id}: Tick gap {successful[0]['tick_gap']} worked!")
 else:
 print(f"❌ Block #{block_id}: No working tick gap found")
 
 print()
 print(f"Results saved to: {output_file}")
 
 if len(working_gaps) == len(BLOCKS_TO_TEST):
 print()
 print("🎉 ALL BLOCKS WORKED! Puzzle solved!")
 elif working_gaps:
 print()
 print(f"⚠️ Partial success: {len(working_gaps)}/{len(BLOCKS_TO_TEST)} blocks worked")

if __name__ == "__main__":
 main()

