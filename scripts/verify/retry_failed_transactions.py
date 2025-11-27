#!/usr/bin/env python3
"""
Retry failed transactions (Blocks 4-7) from Hypothesis 1 test.
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
AMOUNT_QU = 50
TARGET_TICK_OFFSET = 25

# Only the failed ones (Blocks 4-7)
RETRY_SEEDS = [
 {
 "label": "Diagonal #4 • Block-ID 4",
 "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 "identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 "block_id": 4,
 "payload": "4,2",
 },
 {
 "label": "Vortex #1 • Block-ID 5",
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml",
 "identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 "block_id": 5,
 "payload": "5,2",
 },
 {
 "label": "Vortex #2 • Block-ID 6",
 "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb",
 "identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 "block_id": 6,
 "payload": "6,2",
 },
 {
 "label": "Vortex #3 • Block-ID 7",
 "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw",
 "identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 "block_id": 7,
 "payload": "7,2",
 },
]

def build_tx_with_payload(
 seed: str,
 dest_identity: str,
 amount: int,
 target_tick: int,
 payload: str,
) -> bytes:
 """Build transaction with payload."""
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 source_pubkey = get_public_key_from_private_key(private_key)
 dest_pubkey = get_public_key_from_identity(dest_identity)
 
 built_data = bytearray()
 offset = 0

 built_data.extend(source_pubkey)
 offset += len(source_pubkey)
 built_data.extend(dest_pubkey)
 offset += len(dest_pubkey)
 built_data.extend(amount.to_bytes(8, byteorder='little'))
 offset += 8
 built_data.extend(target_tick.to_bytes(4, byteorder='little'))
 offset += 4
 built_data.extend((0).to_bytes(2, byteorder='little'))
 offset += 2
 
 payload_bytes = payload.encode('utf-8')
 built_data.extend(len(payload_bytes).to_bytes(2, byteorder='little'))
 offset += 2
 built_data.extend(payload_bytes)
 offset += len(payload_bytes)
 
 tx_digest = kangaroo_twelve(built_data, offset, 32)
 signature = sign(subseed, source_pubkey, tx_digest)
 built_data.extend(signature)
 
 return bytes(built_data)

def main():
 rpc = rpc_client.QubiPy_RPC()
 
 print("=" * 80)
 print("🔄 RETRYING FAILED TRANSACTIONS (Blocks 4-7)")
 print("=" * 80)
 print()
 
 current_tick = rpc.get_latest_tick()
 target_tick = current_tick + TARGET_TICK_OFFSET
 
 print(f"Current tick: {current_tick}")
 print(f"Target tick: {target_tick}")
 print()
 
 for entry in RETRY_SEEDS:
 print(f"▶️ {entry['label']}")
 print(f" Payload: '{entry['payload']}'")
 
 try:
 tx_bytes = build_tx_with_payload(
 seed=entry['seed'],
 dest_identity=CONTRACT_ID,
 amount=AMOUNT_QU,
 target_tick=target_tick,
 payload=entry['payload'],
 )
 
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId", response.get("transactionHash", "UNKNOWN"))
 print(f" ✅ TX sent: {tx_id}")
 except Exception as e:
 print(f" ❌ ERROR: {e}")
 
 time.sleep(0.5) # Longer delay to avoid timeouts
 
 print()
 print("=" * 80)
 print("Waiting 20 seconds for contract payout...")
 print("=" * 80)
 time.sleep(20)
 
 print()
 print("Checking assets...")
 for entry in RETRY_SEEDS:
 try:
 owned = rpc.get_owned_assets(entry['identity'])
 possessed = rpc.get_possessed_assets(entry['identity'])
 
 owned_count = len(owned) if isinstance(owned, list) else len(owned.get("assets", [])) if isinstance(owned, dict) else 0
 possessed_count = len(possessed) if isinstance(possessed, list) else len(possessed.get("assets", [])) if isinstance(possessed, dict) else 0
 
 if owned_count > 0 or possessed_count > 0:
 print(f"🎉 {entry['label']}: Assets found! (Owned: {owned_count}, Possessed: {possessed_count})")
 else:
 print(f" {entry['label']}: No assets yet")
 except Exception as e:
 print(f" {entry['label']}: Error: {e}")

if __name__ == "__main__":
 main()

