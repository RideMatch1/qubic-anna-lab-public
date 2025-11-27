#!/usr/bin/env python3
"""
Send all 8 transactions synchronized to the same target tick.

This ensures all transactions arrive in the same tick, even if sent sequentially.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List

from qubipy.rpc import rpc_client
from qubipy.tx.utils import create_tx

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
AMOUNT_QU = 50
TARGET_TICK_OFFSET = 25

SEED_TABLE = [
 {
 "label": "Diagonal #1 • Layer-2",
 "seed": "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd",
 "identity": "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP",
 "payload": 1,
 },
 {
 "label": "Diagonal #2 • Layer-2",
 "seed": "gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr",
 "identity": "FPEXLMCOGJNYAAELTBSEDHAZCCNAGXJRPRFNBEXUKPDHFTVAHETKPANQCMLM",
 "payload": 2,
 },
 {
 "label": "Diagonal #3 • Layer-2",
 "seed": "acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn",
 "identity": "ABCXUAPWHTDRJDASQEZSNCDAMXNJAXDTNESWQLNWPZBBUXDGNJLGYXETNGHN",
 "payload": 3,
 },
 {
 "label": "Diagonal #4 • Layer-2",
 "seed": "giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht",
 "identity": "AGTIRJYQVZXUEFAUCPEBEYHDAFXZFMFOARDSUKLHHBETDIVPWVZMOORUOXSD",
 "payload": 4,
 },
 {
 "label": "Vortex #1 • Layer-2",
 "seed": "uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml",
 "identity": "GNMLDHIPZJHJDNCCCRFHVDDPEIHJEWOPVVAXQRFIBYDZBNDHTELZIANUDAWB",
 "payload": 5,
 },
 {
 "label": "Vortex #2 • Layer-2",
 "seed": "hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb",
 "identity": "ADVDNZIGNSCXAODGDMEXMKICVHFOHBROQQMVZOGAMVASHQURDBPDNJRJJQRM",
 "payload": 6,
 },
 {
 "label": "Vortex #3 • Layer-2",
 "seed": "jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw",
 "identity": "HFVFDNEHUVRRBIESYPSSRPNJSVVSDBIPNAXAHIKISLAKYZFKMWNJXVVUEUQJ",
 "payload": 7,
 },
 {
 "label": "Vortex #4 • Layer-2",
 "seed": "xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc",
 "identity": "BIARJWYAYURJYJBXXEDMQOKGSJXBFNWCDSHXZILITIDHCMJYUMPPXQZQAXNR",
 "payload": 8,
 },
]

@dataclass
class TxResult:
 label: str
 identity: str
 payload: int
 tx_id: str | None
 target_tick: int
 status: str
 error: str | None = None

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 results: List[TxResult] = []
 
 print("=== Synchronized 8-fold Contract Trigger ===")
 print("All transactions will target the SAME tick for synchronization.\n")
 
 latest_tick = rpc.get_latest_tick()
 target_tick = latest_tick + TARGET_TICK_OFFSET
 
 print(f"Current tick: {latest_tick}")
 print(f"Target tick for all transactions: {target_tick}")
 print(f"Time window: ~{TARGET_TICK_OFFSET * 0.6} seconds\n")
 
 print("Sending all 8 transactions as fast as possible...\n")
 
 start_time = time.time()
 
 for entry in SEED_TABLE:
 label = entry["label"]
 seed = entry["seed"]
 identity = entry["identity"]
 payload = entry["payload"]
 
 try:
 _, tx_bytes, _, tx_hash = create_tx(
 seed=seed,
 dest_id=CONTRACT_ID,
 amount=AMOUNT_QU,
 target_tick=target_tick,
 )
 
 response = rpc.broadcast_transaction(tx_bytes)
 tx_id = response.get("txId", response.get("transactionHash", tx_hash))
 
 results.append(TxResult(label, identity, payload, tx_id, target_tick, "SENT"))
 print(f"✓ {label}: TX {tx_id[:20]}... (payload {payload})")
 except Exception as exc:
 results.append(TxResult(label, identity, payload, None, target_tick, "ERROR", str(exc)))
 print(f"✗ {label}: ERROR - {exc}")
 
 elapsed = time.time() - start_time
 
 print(f"\n=== Summary ===")
 print(f"All transactions sent in {elapsed:.2f} seconds")
 print(f"Target tick: {target_tick}")
 
 success_count = sum(1 for r in results if r.status == "SENT")
 print(f"Successful: {success_count}/8")
 
 if success_count == 8:
 print("\n✓ All 8 transactions sent successfully!")
 print(f" They should all arrive in tick {target_tick}")
 print(" Check contract response in a few ticks...")
 
 print("\n=== Transaction IDs ===")
 for result in results:
 if result.tx_id:
 print(f"{result.label}: {result.tx_id}")

if __name__ == "__main__":
 main()

