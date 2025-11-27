#!/usr/bin/env python3
"""
Send transactions with payload using Tx_Builder (extended version).

This version properly includes the payload (seed index 1-8) in the transaction.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List

from qubipy.rpc import rpc_client
from qubipy.tx.utils import (
 Tx_Builder,
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
 status: str
 error: str | None = None

def build_tx_with_payload(
 seed: str,
 dest_identity: str,
 amount: int,
 target_tick: int,
 payload: int,
) -> bytes:
 """Build transaction with payload using Tx_Builder and manual payload injection."""
 builder = Tx_Builder()
 
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 source_pubkey = get_public_key_from_private_key(private_key)
 
 dest_pubkey = get_public_key_from_identity(dest_identity)
 
 builder.set_source_public_key(source_pubkey)
 builder.set_destination_public_key(dest_pubkey)
 builder.set_amount(amount)
 builder.set_target_tick(target_tick)
 builder.set_input_type(0)
 
 payload_bytes = str(payload).encode('utf-8')
 builder.set_input_size(len(payload_bytes))
 
 built_80, built_full, sig, tx_hash = builder.build(seed)
 
 built_with_payload = bytearray(built_full)
 built_with_payload.extend(payload_bytes)
 
 return bytes(built_with_payload)

def send_transaction_with_payload(
 rpc: rpc_client.QubiPy_RPC,
 seed: str,
 identity: str,
 payload: int,
) -> str:
 """Send transaction with payload to contract."""
 latest_tick = rpc.get_latest_tick()
 target_tick = latest_tick + TARGET_TICK_OFFSET
 
 tx_bytes = build_tx_with_payload(
 seed=seed,
 dest_identity=CONTRACT_ID,
 amount=int(AMOUNT_QU * 1_000_000),
 target_tick=target_tick,
 payload=payload,
 )
 
 response = rpc.broadcast_transaction(tx_bytes)
 return response.get("txId", response.get("transactionHash", "UNKNOWN"))

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 results: List[TxResult] = []
 
 print("=== Starting 8-fold contract trigger WITH PAYLOAD ===\n")
 
 for entry in SEED_TABLE:
 label = entry["label"]
 seed = entry["seed"]
 identity = entry["identity"]
 payload = entry["payload"]
 
 print(f"--> {label}: sending {AMOUNT_QU} QU with payload {payload}")
 try:
 tx_id = send_transaction_with_payload(rpc, seed, identity, payload)
 results.append(TxResult(label, identity, payload, tx_id, "SENT"))
 print(f" TX sent: {tx_id}")
 except Exception as exc:
 results.append(TxResult(label, identity, payload, None, "ERROR", str(exc)))
 print(f" ERROR: {exc}")
 
 print("\nWaiting for asset updates...")
 time.sleep(ASSET_CHECK_DELAY)
 
 for result in results:
 if result.status != "SENT":
 continue
 try:
 assets = rpc.get_owned_assets(result.identity)
 if assets and assets.get("assets"):
 print(f"[{result.label}] NEW ASSETS: {assets['assets']}")
 else:
 print(f"[{result.label}] no assets yet")
 except Exception as e:
 print(f"[{result.label}] error checking assets: {e}")
 
 print("\nDone. Check logs above for TX IDs and asset status.")

if __name__ == "__main__":
 main()

