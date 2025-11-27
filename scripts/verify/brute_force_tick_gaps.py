#!/usr/bin/env python3
"""
Brute Force Tick Gap Testing: Test Hypothesis 2 with tick gaps around 1649.

Since Block #7 worked with 1649, we test variations around this value for all blocks.
Strategy: Test 1649 +/- 10 ticks (1639-1659) for blocks that didn't work.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

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
ASSET_CHECK_DELAY = 10 # Reduced from 20 to 10 seconds for faster testing

# Known working: Block #7 with 1649
KNOWN_WORKING = {7: 1649}

# Test range: 1649 +/- 5 (reduced for faster testing, can expand if needed)
BASE_TICK_GAP = 1649
TEST_RANGE = 5 # Test from 1644 to 1654 (reduced from 10 to speed up)

# Blocks that need testing (excluding Block #7 which already worked)
BLOCKS_TO_TEST = [1, 2, 3, 4, 5, 6, 8]

# Layer 2 identities
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

@dataclass
class TestResult:
 block_id: int
 tick_gap: int
 success: bool
 assets_before: int
 assets_after: int

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

def send_transaction(rpc: rpc_client.QubiPy_RPC, seed: str, identity: str, payload: str) -> str:
 """Send transaction with payload."""
 latest_tick = rpc.get_latest_tick()
 target_tick = latest_tick + TARGET_TICK_OFFSET
 
 tx_bytes = build_tx_with_payload(seed, CONTRACT_ID, AMOUNT_QU, target_tick, payload)
 response = rpc.broadcast_transaction(tx_bytes)
 return response.get("txId", response.get("transactionHash", "UNKNOWN"))

def count_assets(rpc: rpc_client.QubiPy_RPC, identity: str, timeout_retries: int = 2) -> int:
 """Count total assets for an identity with retry logic."""
 owned_count = 0
 possessed_count = 0
 
 # Try owned assets with retries
 for attempt in range(timeout_retries):
 try:
 owned = rpc.get_owned_assets(identity)
 owned_count = len(owned) if isinstance(owned, list) else len(owned.get("assets", [])) if isinstance(owned, dict) else 0
 break
 except Exception as e:
 if "timeout" in str(e).lower() or "timed out" in str(e).lower():
 if attempt < timeout_retries - 1:
 print(f" ⚠️ Timeout getting owned assets (attempt {attempt+1}/{timeout_retries}), retrying...")
 time.sleep(2)
 continue
 print(f" ⚠️ Error getting owned assets: {e}")
 owned_count = 0
 break
 
 # Try possessed assets with retries
 for attempt in range(timeout_retries):
 try:
 possessed = rpc.get_possessed_assets(identity)
 possessed_count = len(possessed) if isinstance(possessed, list) else len(possessed.get("assets", [])) if isinstance(possessed, dict) else 0
 break
 except Exception as e:
 if "timeout" in str(e).lower() or "timed out" in str(e).lower():
 if attempt < timeout_retries - 1:
 print(f" ⚠️ Timeout getting possessed assets (attempt {attempt+1}/{timeout_retries}), retrying...")
 time.sleep(2)
 continue
 print(f" ⚠️ Error getting possessed assets: {e}")
 possessed_count = 0
 break
 
 return owned_count + possessed_count

def test_block_with_tick_gap(rpc: rpc_client.QubiPy_RPC, block_data: Dict, tick_gap: int) -> TestResult:
 """Test a single block with a specific tick gap."""
 block_id = block_data["block_id"]
 label = block_data["label"]
 seed = block_data["seed"]
 identity = block_data["identity"]
 
 payload = f"{block_id},2,{tick_gap}"
 
 # Get baseline assets
 print(f" Getting baseline assets...")
 try:
 assets_before = count_assets(rpc, identity)
 print(f" Baseline: {assets_before} assets")
 except Exception as e:
 print(f" ⚠️ Error counting baseline assets: {e}")
 assets_before = 0
 
 # Send transaction
 try:
 tx_id = send_transaction(rpc, seed, identity, payload)
 print(f" ✅ TX sent: {tx_id[:20] if len(tx_id) > 20 else tx_id}...")
 except Exception as e:
 print(f" ❌ Error sending transaction: {e}")
 return TestResult(block_id, tick_gap, False, assets_before, assets_before)
 
 # Wait for contract response
 print(f" ⏳ Waiting {ASSET_CHECK_DELAY} seconds for contract response...")
 time.sleep(ASSET_CHECK_DELAY)
 
 # Check for new assets
 try:
 assets_after = count_assets(rpc, identity)
 except Exception as e:
 print(f" ⚠️ Error counting assets after: {e}")
 assets_after = assets_before
 
 success = assets_after > assets_before
 
 return TestResult(block_id, tick_gap, success, assets_before, assets_after)

def main() -> int:
 print("=" * 80)
 print("🔬 BRUTE FORCE TICK GAP TESTING")
 print("=" * 80)
 print()
 print(f"Strategy: Test tick gaps from {BASE_TICK_GAP - TEST_RANGE} to {BASE_TICK_GAP + TEST_RANGE}")
 print(f"Known working: Block #7 with {KNOWN_WORKING[7]}")
 print(f"Blocks to test: {BLOCKS_TO_TEST}")
 print()
 
 print("Initializing RPC connection...")
 try:
 rpc = rpc_client.QubiPy_RPC()
 # Test connection with timeout simulation
 print(" Testing connection...")
 latest_tick = rpc.get_latest_tick()
 print(f"✅ RPC connected. Latest tick: {latest_tick}")
 print()
 except Exception as e:
 print(f"❌ Failed to initialize RPC: {e}")
 import traceback
 traceback.print_exc()
 return 1
 
 # Get identities for blocks to test
 blocks_data = {item["block_id"]: item for item in LAYER2_IDENTITIES if item["block_id"] in BLOCKS_TO_TEST}
 
 results: Dict[int, List[TestResult]] = {block_id: [] for block_id in BLOCKS_TO_TEST}
 
 # Test each block with each tick gap value
 for block_id in BLOCKS_TO_TEST:
 block_data = blocks_data[block_id]
 label = block_data["label"]
 
 print("=" * 80)
 print(f"Testing Block #{block_id} ({label})")
 print("=" * 80)
 print()
 
 found_working_gap = False
 for tick_gap in range(BASE_TICK_GAP - TEST_RANGE, BASE_TICK_GAP + TEST_RANGE + 1):
 print(f" ▶️ Testing tick gap: {tick_gap}")
 result = test_block_with_tick_gap(rpc, block_data, tick_gap)
 results[block_id].append(result)
 
 if result.success:
 print(f" 🎉 SUCCESS! Assets: {result.assets_before} → {result.assets_after}")
 print(f" ✅ Block #{block_id} works with tick gap: {tick_gap}")
 found_working_gap = True
 break # Stop testing this block once we find a working gap
 else:
 print(f" ❌ No new assets (before: {result.assets_before}, after: {result.assets_after})")
 
 time.sleep(0.5) # Reduced delay between tests
 
 if not found_working_gap:
 print(f" ⚠️ No working tick gap found for Block #{block_id} in range {BASE_TICK_GAP - TEST_RANGE} to {BASE_TICK_GAP + TEST_RANGE}")
 
 # Find best result for this block
 successful = [r for r in results[block_id] if r.success]
 if successful:
 best = successful[0]
 print()
 print(f"✅ Block #{block_id} worked with tick gap: {best.tick_gap}")
 else:
 print()
 print(f"❌ Block #{block_id} did not work with any tick gap in range")
 print()
 
 # Summary
 print("=" * 80)
 print("FINAL SUMMARY")
 print("=" * 80)
 print()
 
 working_gaps = {}
 for block_id, test_results in results.items():
 successful = [r for r in test_results if r.success]
 if successful:
 working_gaps[block_id] = successful[0].tick_gap
 print(f"✅ Block #{block_id}: Tick gap {successful[0].tick_gap} worked")
 else:
 print(f"❌ Block #{block_id}: No working tick gap found")
 
 # Save results
 output_file = Path("outputs/derived/brute_force_tick_gaps.json")
 output_file.parent.mkdir(parents=True, exist_ok=True)
 
 with output_file.open("w", encoding="utf-8") as f:
 json.dump({
 "working_gaps": working_gaps,
 "all_results": {
 str(block_id): [
 {
 "tick_gap": r.tick_gap,
 "success": r.success,
 "assets_before": r.assets_before,
 "assets_after": r.assets_after,
 }
 for r in results[block_id]
 ]
 for block_id in BLOCKS_TO_TEST
 }
 }, f, indent=2)
 
 print()
 print(f"✅ Results saved to: {output_file}")
 
 if len(working_gaps) == len(BLOCKS_TO_TEST):
 print()
 print("🎉 ALL BLOCKS WORKED! Puzzle solved!")
 elif working_gaps:
 print()
 print(f"⚠️ Partial success: {len(working_gaps)}/{len(BLOCKS_TO_TEST)} blocks worked")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

