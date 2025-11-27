#!/usr/bin/env python3
"""
Test Layer-1 Identities: Maybe we need to send from Layer-1 identities, not Layer-2.

The contract might expect the original matrix-extracted identities, not the derived ones.
"""

from __future__ import annotations

import time
from qubipy.rpc import rpc_client
from qubipy.tx.utils import create_tx

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
AMOUNT_QU = 1
TARGET_TICK_OFFSET = 25

# Layer-1 identities (from matrix extraction)
LAYER1_IDENTITIES = [
 {"label": "Diagonal #1", "block_id": 1, "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd", "identity": "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR"},
 {"label": "Diagonal #2", "block_id": 2, "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr", "identity": "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ"},
 {"label": "Diagonal #3", "block_id": 3, "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn", "identity": "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV"},
 {"label": "Diagonal #4", "block_id": 4, "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht", "identity": "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC"},
 {"label": "Vortex #1", "block_id": 5, "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml", "identity": "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF"},
 {"label": "Vortex #2", "block_id": 6, "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb", "identity": "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD"},
 {"label": "Vortex #3", "block_id": 7, "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw", "identity": "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL"},
 {"label": "Vortex #4", "block_id": 8, "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc", "identity": "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK"},
]

def main():
 print("=" * 80)
 print("TEST: LAYER-1 IDENTITIES (NO PAYLOAD)")
 print("=" * 80)
 print()
 print("Hypothesis: Contract expects Layer-1 identities, not Layer-2")
 print("Strategy: Send from Layer-1 identities, synchronized, no payload")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 current_tick = rpc.get_latest_tick()
 target_tick = current_tick + TARGET_TICK_OFFSET
 
 print(f"Current tick: {current_tick}")
 print(f"Target tick for ALL transactions: {target_tick}")
 print()
 
 print("Sending from Layer-1 identities...")
 print()
 
 tx_ids = []
 for entry in LAYER1_IDENTITIES:
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
 
 time.sleep(0.01)
 
 print()
 print("=" * 80)
 print("TRANSACTIONS SENT")
 print("=" * 80)
 print()
 print("Check your wallet in 20-30 seconds")
 print("If this doesn't work, we need to try other approaches")

if __name__ == "__main__":
 main()

