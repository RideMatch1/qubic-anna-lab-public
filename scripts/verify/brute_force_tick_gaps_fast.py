#!/usr/bin/env python3
"""
Fast Brute Force Tick Gap Testing: Sends all transactions without waiting for asset checks.
Assets can be checked manually later.

This avoids timeout issues with get_owned_assets().
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List

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

BASE_TICK_GAP = 1649
TEST_RANGE = 5 # Test from 1644 to 1654

BLOCKS_TO_TEST = [1, 2, 3, 4, 5, 6, 8] # Block 7 already works with 1649

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
 print("🚀 FAST BRUTE FORCE TICK GAP TESTING")
 print("=" * 80)
 print()
 print(f"Testing tick gaps: {BASE_TICK_GAP - TEST_RANGE} to {BASE_TICK_GAP + TEST_RANGE}")
 print(f"Blocks to test: {BLOCKS_TO_TEST}")
 print(f"Total transactions: {len(BLOCKS_TO_TEST) * (TEST_RANGE * 2 + 1)}")
 print()
 print("⚠️ Note: Assets will NOT be checked automatically (to avoid timeouts)")
 print(" Check your wallet manually after completion")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 current_tick = rpc.get_latest_tick()
 print(f"Current tick: {current_tick}")
 print()
 
 blocks_data = {item["block_id"]: item for item in LAYER2_IDENTITIES if item["block_id"] in BLOCKS_TO_TEST}
 
 results = {}
 
 for block_id in BLOCKS_TO_TEST:
 block_data = blocks_data[block_id]
 label = block_data["label"]
 
 print("=" * 80)
 print(f"Testing Block #{block_id} ({label})")
 print("=" * 80)
 print()
 
 block_results = []
 
 for tick_gap in range(BASE_TICK_GAP - TEST_RANGE, BASE_TICK_GAP + TEST_RANGE + 1):
 payload = f"{block_id},2,{tick_gap}"
 print(f" ▶️ Tick gap {tick_gap}: Payload '{payload}'")
 
 try:
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
 
 block_results.append({
 "tick_gap": tick_gap,
 "payload": payload,
 "tx_id": tx_id,
 "status": "sent"
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
 
 time.sleep(0.3) # Small delay between transactions
 
 results[block_id] = block_results
 print()
 
 # Save results
 output_file = Path("outputs/derived/brute_force_tick_gaps_fast.json")
 output_file.parent.mkdir(parents=True, exist_ok=True)
 
 with output_file.open("w", encoding="utf-8") as f:
 json.dump(results, f, indent=2)
 
 print("=" * 80)
 print("✅ ALL TRANSACTIONS SENT")
 print("=" * 80)
 print()
 print(f"Results saved to: {output_file}")
 print()
 print("📋 NEXT: Check your wallet for new GENESIS assets")
 print(" The tick gap that worked will show new assets on that identity")
 print()

if __name__ == "__main__":
 main()

