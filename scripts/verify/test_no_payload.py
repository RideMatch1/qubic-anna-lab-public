#!/usr/bin/env python3
"""
Test Without Payload: Send transactions WITHOUT any payload field.

Maybe the Smart Contract recognizes the identities by their public keys alone,
or maybe the payload format is completely different.
"""

from __future__ import annotations

import time
from qubipy.rpc import rpc_client
from qubipy.tx.utils import create_tx

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
AMOUNT_QU = 1
TARGET_TICK_OFFSET = 25

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

def main():
 print("=" * 80)
 print("TEST: NO PAYLOAD - SYNCHRONIZED SENDING")
 print("=" * 80)
 print()
 print("Hypothesis: Smart Contract recognizes identities by public key alone")
 print("Strategy: Send all 8 transactions in the SAME tick, NO payload")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 current_tick = rpc.get_latest_tick()
 target_tick = current_tick + TARGET_TICK_OFFSET
 
 print(f"Current tick: {current_tick}")
 print(f"Target tick for ALL transactions: {target_tick}")
 print()
 
 print("Sending all 8 transactions as fast as possible...")
 print()
 
 tx_ids = []
 for entry in LAYER2_IDENTITIES:
 label = entry["label"]
 seed = entry["seed"]
 
 try:
 tx_bytes, _, _, tx_hash = create_tx(
 seed=seed,
 dest_id=CONTRACT_ID,
 amount=AMOUNT_QU,
 target_tick=target_tick,
 )
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId", tx_hash)
 tx_ids.append(tx_id)
 print(f"✅ {label}: TX {tx_id[:20]}...")
 except Exception as e:
 print(f"❌ {label}: Error - {e}")
 tx_ids.append(None)
 
 time.sleep(0.01) # Minimal delay
 
 print()
 print("=" * 80)
 print("TRANSACTIONS SENT")
 print("=" * 80)
 print()
 print(f"All 8 transactions sent to tick {target_tick}")
 print("Check your wallet in 20-30 seconds for new assets")
 print()
 print("If this doesn't work, we need to try:")
 print(" 1. Different transaction amounts")
 print(" 2. Layer-1 identities instead of Layer-2")
 print(" 3. Different transaction types")
 print(" 4. Analyze the contract itself")

if __name__ == "__main__":
 main()

