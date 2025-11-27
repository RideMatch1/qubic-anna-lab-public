#!/usr/bin/env python3
"""
Quick Tick Gap Test: Test just one block with a few tick gaps to verify the approach works.
This avoids the timeout issues with asset checking.
"""

from __future__ import annotations

import time
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

# Test Block #1 with tick gaps around 1649
TEST_BLOCK = {
 "label": "Diagonal #1",
 "block_id": 1,
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
}

# Test only a few tick gaps first: 1647, 1649, 1651
TEST_TICK_GAPS = [1647, 1649, 1651]

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
 print("QUICK TICK GAP TEST")
 print("=" * 80)
 print()
 print(f"Testing Block #{TEST_BLOCK['block_id']} ({TEST_BLOCK['label']})")
 print(f"Tick gaps to test: {TEST_TICK_GAPS}")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 current_tick = rpc.get_latest_tick()
 print(f"Current tick: {current_tick}")
 print()
 
 for tick_gap in TEST_TICK_GAPS:
 payload = f"{TEST_BLOCK['block_id']},2,{tick_gap}"
 print(f"▶️ Testing tick gap: {tick_gap}")
 print(f" Payload: '{payload}'")
 
 try:
 target_tick = current_tick + TARGET_TICK_OFFSET
 tx_bytes = build_tx_with_payload(
 TEST_BLOCK['seed'],
 CONTRACT_ID,
 AMOUNT_QU,
 target_tick,
 payload
 )
 
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId", response.get("transactionHash", "UNKNOWN"))
 print(f" ✅ TX sent: {tx_id}")
 print(f" ⏳ Wait 15 seconds, then check assets manually")
 print()
 
 time.sleep(15) # Wait before next test
 
 except Exception as e:
 print(f" ❌ Error: {e}")
 print()
 
 print("=" * 80)
 print("DONE")
 print("=" * 80)
 print()
 print("Check assets manually with:")
 print(f" python3 -c \"from qubipy.rpc import rpc_client; rpc = rpc_client.QubiPy_RPC(); print(rpc.get_owned_assets('{TEST_BLOCK['identity']}'))\"")
 print()

if __name__ == "__main__":
 main()

