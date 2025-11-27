#!/usr/bin/env python3
"""
FINAL CONTRACT TRIGGER: 8 coordinated transactions with Block-ID payload (1-8).

This is the definitive test based on the coordinate-based Block-ID discovery:
- Diagonal #1: Block-ID 1 (r//32 = 0 → +1)
- Diagonal #2: Block-ID 2 (r//32 = 1 → +1)
- Diagonal #3: Block-ID 3 (r//32 = 2 → +1)
- Diagonal #4: Block-ID 4 (r//32 = 3 → +1)
- Vortex #1-4: Block-IDs 5-8 (logically derived)
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List

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
ASSET_CHECK_DELAY = 15

# Layer-2 Seeds with Block-IDs based on coordinate analysis
SEED_TABLE = [
 {
 "label": "Diagonal #1 • Block-ID 1",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 "block_id": 1, # r//32 = 0 → +1
 },
 {
 "label": "Diagonal #2 • Block-ID 2",
 "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr",
 "identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 "block_id": 2, # r//32 = 1 → +1
 },
 {
 "label": "Diagonal #3 • Block-ID 3",
 "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn",
 "identity": "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG",
 "block_id": 3, # r//32 = 2 → +1
 },
 {
 "label": "Diagonal #4 • Block-ID 4",
 "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 "identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 "block_id": 4, # r//32 = 3 → +1
 },
 {
 "label": "Vortex #1 • Block-ID 5",
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml",
 "identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 "block_id": 5, # Logically derived (4+1)
 },
 {
 "label": "Vortex #2 • Block-ID 6",
 "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb",
 "identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 "block_id": 6, # Logically derived (5+1)
 },
 {
 "label": "Vortex #3 • Block-ID 7",
 "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw",
 "identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 "block_id": 7, # Logically derived (6+1)
 },
 {
 "label": "Vortex #4 • Block-ID 8",
 "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc",
 "identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 "block_id": 8, # Logically derived (7+1)
 },
]

@dataclass
class TxResult:
 label: str
 identity: str
 block_id: int
 tx_id: str | None
 status: str
 error: str | None = None

def build_tx_with_block_id(
 seed: str,
 dest_identity: str,
 amount: int,
 target_tick: int,
 block_id: int,
) -> bytes:
 """
 Build transaction with Block-ID as payload.
 
 The payload is the Block-ID (1-8) as a string, inserted BEFORE signing.
 """
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 source_pubkey = get_public_key_from_private_key(private_key)
 dest_pubkey = get_public_key_from_identity(dest_identity)
 
 built_data = bytearray()
 offset = 0

 # 1. Source Public Key (32 bytes)
 built_data.extend(source_pubkey)
 offset += len(source_pubkey)

 # 2. Destination Public Key (32 bytes)
 built_data.extend(dest_pubkey)
 offset += len(dest_pubkey)

 # 3. Amount (8 bytes)
 built_data.extend(amount.to_bytes(8, byteorder='little'))
 offset += 8

 # 4. Target Tick (4 bytes)
 built_data.extend(target_tick.to_bytes(4, byteorder='little'))
 offset += 4

 # 5. Input Type (2 bytes) - always 0 for simple transfers
 input_type = 0
 built_data.extend(input_type.to_bytes(2, byteorder='little'))
 offset += 2

 # 6. Input Size (2 bytes) - size of the payload
 payload_bytes = str(block_id).encode('utf-8')
 input_size = len(payload_bytes)
 built_data.extend(input_size.to_bytes(2, byteorder='little'))
 offset += 2

 # 7. Payload (N bytes) - Block-ID as string, inserted BEFORE signing
 built_data.extend(payload_bytes)
 offset += len(payload_bytes)
 
 # Sign the transaction digest (which now includes the payload)
 tx_digest = kangaroo_twelve(built_data, offset, 32)
 signature = sign(subseed, source_pubkey, tx_digest)

 # 8. Signature (64 bytes)
 built_data.extend(signature)
 offset += len(signature)

 return bytes(built_data)

def send_transaction_with_block_id(
 rpc: rpc_client.QubiPy_RPC,
 seed: str,
 identity: str,
 block_id: int,
) -> str:
 """Send transaction with Block-ID payload to contract."""
 latest_tick = rpc.get_latest_tick()
 target_tick = latest_tick + TARGET_TICK_OFFSET
 
 tx_bytes = build_tx_with_block_id(
 seed=seed,
 dest_identity=CONTRACT_ID,
 amount=AMOUNT_QU * 1_000_000, # Convert to smallest unit
 target_tick=target_tick,
 block_id=block_id,
 )
 
 response = rpc.broadcast_transaction(tx_bytes)
 return response.get("txId", response.get("transactionHash", "UNKNOWN"))

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 results: List[TxResult] = []
 
 print("=" * 80)
 print("🚀 FINAL CONTRACT TRIGGER - COORDINATED 8-FOLD TRANSACTION")
 print("=" * 80)
 print()
 print("Based on coordinate-based Block-ID discovery:")
 print(" - Diagonal #1-4: Block-IDs 1-4 (from r//32 formula)")
 print(" - Vortex #1-4: Block-IDs 5-8 (logically derived)")
 print()
 print(f"Contract: {CONTRACT_ID}")
 print(f"Amount per transaction: {AMOUNT_QU} QU")
 print()
 
 current_tick = rpc.get_latest_tick()
 target_tick = current_tick + TARGET_TICK_OFFSET
 print(f"Current tick: {current_tick}")
 print(f"Target tick for all transactions: {target_tick}")
 print(f"Time window: ~{TARGET_TICK_OFFSET * 0.6:.1f} seconds")
 print()
 print("=" * 80)
 print("SENDING 8 COORDINATED TRANSACTIONS...")
 print("=" * 80)
 print()

 start_time = time.time()
 
 for entry in SEED_TABLE:
 label = entry["label"]
 seed = entry["seed"]
 identity = entry["identity"]
 block_id = entry["block_id"]
 
 print(f"--> {label}: sending {AMOUNT_QU} QU with Block-ID {block_id}")
 try:
 tx_id = send_transaction_with_block_id(rpc, seed, identity, block_id)
 results.append(TxResult(label, identity, block_id, tx_id, "SENT"))
 print(f" ✓ TX sent: {tx_id}")
 except Exception as exc:
 results.append(TxResult(label, identity, block_id, None, "ERROR", str(exc)))
 print(f" ✗ ERROR: {exc}")
 time.sleep(0.1) # Small delay between transactions
 
 end_time = time.time()
 
 print()
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print(f"All transactions sent in {end_time - start_time:.2f} seconds")
 print(f"Successful: {len([r for r in results if r.status == 'SENT'])}/{len(results)}")
 print()

 if all(r.status == "SENT" for r in results):
 print("✅ All 8 transactions with Block-ID payload sent successfully!")
 print()
 print("Transaction IDs:")
 for result in results:
 print(f" {result.label}: {result.tx_id}")
 print()
 print(f"Waiting {ASSET_CHECK_DELAY} seconds for contract response...")
 time.sleep(ASSET_CHECK_DELAY)
 
 print()
 print("=" * 80)
 print("CHECKING FOR ASSETS")
 print("=" * 80)
 print()
 
 for result in results:
 if result.status != "SENT":
 continue
 try:
 assets = rpc.get_owned_assets(result.identity)
 if assets and assets.get("assets"):
 print(f"🎉 [{result.label}] NEW ASSETS: {assets['assets']}")
 else:
 print(f" [{result.label}] No assets yet")
 except Exception as e:
 print(f" [{result.label}] Error checking assets: {e}")
 else:
 print("✗ Some transactions failed. Review errors above.")

 print()
 print("=" * 80)
 print("DONE")
 print("=" * 80)

if __name__ == "__main__":
 main()

