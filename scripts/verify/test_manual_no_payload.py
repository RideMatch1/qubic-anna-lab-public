#!/usr/bin/env python3
"""
Test Manual Building WITHOUT Payload: 8 synchronized transactions.

Now that we know manual building works, test if the contract triggers
with synchronized transactions from all 8 identities, no payload.
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

LAYER2_IDENTITIES = [
 {"label": "Diagonal #1", "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd", "identity": "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD"},
 {"label": "Diagonal #2", "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr", "identity": "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE"},
 {"label": "Diagonal #3", "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn", "identity": "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG"},
 {"label": "Diagonal #4", "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht", "identity": "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI"},
 {"label": "Vortex #1", "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml", "identity": "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL"},
 {"label": "Vortex #2", "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb", "identity": "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI"},
 {"label": "Vortex #3", "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw", "identity": "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN"},
 {"label": "Vortex #4", "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc", "identity": "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB"},
]

def build_tx_manual_no_payload(
 seed: str,
 dest_identity: str,
 amount: int,
 target_tick: int,
) -> bytes:
 """Build transaction manually WITHOUT payload."""
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 dest_pubkey = get_public_key_from_identity(dest_identity)
 
 built_data = bytearray()
 
 # 1. Source Public Key (32 bytes)
 built_data.extend(public_key)
 
 # 2. Destination Public Key (32 bytes)
 built_data.extend(dest_pubkey)
 
 # 3. Amount (8 bytes, little-endian)
 built_data.extend(amount.to_bytes(8, byteorder='little'))
 
 # 4. Target Tick (4 bytes, little-endian)
 built_data.extend(target_tick.to_bytes(4, byteorder='little'))
 
 # 5. Input Type (2 bytes) - 0 for simple transfers
 built_data.extend((0).to_bytes(2, byteorder='little'))
 
 # 6. Input Size (2 bytes) - 0 (no payload)
 built_data.extend((0).to_bytes(2, byteorder='little'))
 
 # Sign transaction
 offset = len(built_data)
 tx_digest = kangaroo_twelve(built_data, offset, 32)
 signature = sign(subseed, public_key, tx_digest)
 
 # 7. Signature (64 bytes)
 built_data.extend(signature)
 
 return bytes(built_data)

def main():
 print("=" * 80)
 print("TEST: MANUAL BUILDING - NO PAYLOAD (8 SYNCHRONIZED)")
 print("=" * 80)
 print()
 print("Hypothesis: Contract triggers with synchronized transactions, no payload needed")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 current_tick = rpc.get_latest_tick()
 target_tick = current_tick + TARGET_TICK_OFFSET
 
 print(f"Current tick: {current_tick}")
 print(f"Target tick for ALL: {target_tick}")
 print()
 
 print("Sending all 8 transactions as fast as possible...")
 print()
 
 tx_ids = []
 for entry in LAYER2_IDENTITIES:
 label = entry["label"]
 seed = entry["seed"]
 
 try:
 tx_bytes = build_tx_manual_no_payload(
 seed=seed,
 dest_identity=CONTRACT_ID,
 amount=AMOUNT_QU,
 target_tick=target_tick,
 )
 
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("transactionId", "unknown")
 tx_ids.append(tx_id)
 print(f"✅ {label}: {tx_id[:30]}...")
 except Exception as e:
 print(f"❌ {label}: Error - {e}")
 tx_ids.append(None)
 
 time.sleep(0.1) # Small delay
 
 print()
 print("=" * 80)
 print("TRANSACTIONS SENT")
 print("=" * 80)
 print()
 print(f"All 8 transactions sent to tick {target_tick}")
 print("Check wallets in 20-30 seconds for new assets")
 print()
 print("If this doesn't work, we'll test WITH payload next")

if __name__ == "__main__":
 raise SystemExit(main())

