#!/usr/bin/env python3
"""
Send transactions with payload - FIXED VERSION.

This version properly includes the payload BEFORE signing, so the signature is valid.
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
from qubipy.crypto.utils import sign, kangaroo_twelve, get_identity_from_public_key

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
 status: str
 error: str | None = None

def build_tx_with_payload_correct(
 seed: str,
 dest_identity: str,
 amount: int,
 target_tick: int,
 payload: int,
) -> bytes:
 """
 Build transaction with payload - CORRECT VERSION.
 
 The payload is inserted BEFORE signing, so the signature includes it.
 """
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 source_pubkey = get_public_key_from_private_key(private_key)
 dest_pubkey = get_public_key_from_identity(dest_identity)
 
 built_data = bytearray()
 offset = 0
 
 # 1. Source public key (32 bytes)
 built_data[offset:offset+32] = source_pubkey
 offset += 32
 
 # 2. Destination public key (32 bytes)
 built_data[offset:offset+32] = dest_pubkey
 offset += 32
 
 # 3. Amount (8 bytes, little-endian)
 built_data[offset:offset+8] = amount.to_bytes(8, byteorder='little')
 offset += 8
 
 # 4. Target tick (4 bytes, little-endian)
 built_data[offset:offset+4] = target_tick.to_bytes(4, byteorder='little')
 offset += 4
 
 # 5. Input type (2 bytes, little-endian)
 built_data[offset:offset+2] = (0).to_bytes(2, byteorder='little')
 offset += 2
 
 # 6. Input size (2 bytes, little-endian)
 payload_bytes = str(payload).encode('utf-8')
 payload_size = len(payload_bytes)
 built_data[offset:offset+2] = payload_size.to_bytes(2, byteorder='little')
 offset += 2
 
 # 7. PAYLOAD (N bytes) - MUST BE BEFORE SIGNATURE!
 built_data.extend(payload_bytes)
 offset += payload_size
 
 # 8. Now sign the transaction (including payload)
 # kangaroo_twelve hashes the first 'offset' bytes of the data
 tx_digest = kangaroo_twelve(built_data, offset, 32)
 signature = sign(subseed, source_pubkey, tx_digest)
 
 # 9. Append signature (64 bytes)
 built_data.extend(signature)
 
 return bytes(built_data)

def send_transaction_with_payload(
 rpc: rpc_client.QubiPy_RPC,
 seed: str,
 identity: str,
 payload: int,
) -> str:
 """Send transaction with payload to contract."""
 latest_tick = rpc.get_latest_tick()
 target_tick = latest_tick + TARGET_TICK_OFFSET
 
 tx_bytes = build_tx_with_payload_correct(
 seed=seed,
 dest_identity=CONTRACT_ID,
 amount=AMOUNT_QU,
 target_tick=target_tick,
 payload=payload,
 )
 
 response = rpc.broadcast_transaction(tx_bytes)
 return response.get("txId", response.get("transactionHash", "UNKNOWN"))

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 results: List[TxResult] = []
 
 print("=== Contract Trigger WITH PAYLOAD (Fixed Version) ===")
 print("All transactions include payload (1-8) in the transaction data.\n")
 
 latest_tick = rpc.get_latest_tick()
 target_tick = latest_tick + TARGET_TICK_OFFSET
 
 print(f"Current tick: {latest_tick}")
 print(f"Target tick: {target_tick}\n")
 
 start_time = time.time()
 
 for entry in SEED_TABLE:
 label = entry["label"]
 seed = entry["seed"]
 identity = entry["identity"]
 payload = entry["payload"]
 
 print(f"--> {label}: sending {AMOUNT_QU} QU with payload {payload}")
 try:
 tx_id = send_transaction_with_payload(rpc, seed, identity, payload)
 results.append(TxResult(label, identity, payload, tx_id, "SENT"))
 print(f" ✓ TX sent: {tx_id}")
 except Exception as exc:
 results.append(TxResult(label, identity, payload, None, "ERROR", str(exc)))
 print(f" ✗ ERROR: {exc}")
 
 elapsed = time.time() - start_time
 
 print(f"\n=== Summary ===")
 print(f"All transactions sent in {elapsed:.2f} seconds")
 success_count = sum(1 for r in results if r.status == "SENT")
 print(f"Successful: {success_count}/8")
 
 if success_count == 8:
 print("\n✓ All 8 transactions with payload sent successfully!")
 print(" Waiting for contract response...")
 time.sleep(15)
 
 print("\n=== Checking for Assets ===")
 for result in results:
 if result.status != "SENT":
 continue
 try:
 assets = rpc.get_owned_assets(result.identity)
 owned_list = assets if isinstance(assets, list) else (assets.get('assets', []) if assets else [])
 if owned_list:
 print(f"✓ {result.label}: {len(owned_list)} assets found!")
 else:
 print(f"- {result.label}: No assets yet")
 except Exception as e:
 print(f"✗ {result.label}: Error checking assets: {e}")

if __name__ == "__main__":
 main()

