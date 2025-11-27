#!/usr/bin/env python3

"""

Fire all eight Layer-2 identities (Anna Matrix solution) against the contract.

Für jeden Seed will eine Transaktion (z.B. 50 QU) an den Contract gesendet,

Payload = Seed-Index (1..8). Danach will geprüft, ob Assets/Balance eingetroffen sind.

"""

from __future__ import annotations

import time

from dataclasses import dataclass

from typing import List

from qubipy.rpc import rpc_client
from qubipy.tx.utils import create_tx

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
AMOUNT_QU = 50 # Betrag pro Seed
TARGET_TICK_OFFSET = 25 # wie viele Ticks above dem aktuellen wir ansetzen
ASSET_CHECK_DELAY = 15 # Sekunden warten, bevor Assets gecheckt werden

# Hier trägst du deine Seeds/Identitäten ein (Index 1..8)

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

def send_transaction(rpc, seed: str) -> str:
 latest_tick = int(rpc.get_latest_tick())
 target_tick = latest_tick + TARGET_TICK_OFFSET
 _, tx_bytes, _, tx_hash = create_tx(
 seed=seed,
 dest_id=CONTRACT_ID,
 amount=AMOUNT_QU,
 target_tick=target_tick,
 )
 response = rpc.broadcast_transaction(tx_bytes)
 return response.get("transactionHash", tx_hash)

def check_assets(rpc, identity: str) -> dict:

 return rpc.get_owned_assets(identity)

def main() -> None:

 rpc = rpc_client.QubiPy_RPC()

 results: List[TxResult] = []

 print("=== Starting 8-fold contract trigger ===\n")

 for entry in SEED_TABLE:

 label = entry["label"]

 seed = entry["seed"]

 payload = entry["payload"]

 print(f"--> {label}: sending {AMOUNT_QU} QU with payload {payload}")

 try:

 tx_id = send_transaction(rpc, seed)

 results.append(TxResult(label, entry["identity"], payload, tx_id, "SENT"))

 print(f" TX sent: {tx_id}")

 except Exception as exc:

 results.append(TxResult(label, entry["identity"], payload, None, "ERROR", str(exc)))

 print(f" ERROR: {exc}")

 print("\nWaiting for asset updates...")

 time.sleep(ASSET_CHECK_DELAY)

 for result in results:

 if result.status != "SENT":

 continue

 assets = check_assets(rpc, result.identity)

 if assets:

 print(f"[{result.label}] NEW ASSETS: {assets}")

 else:

 print(f"[{result.label}] no assets yet")

 print("\nDone. Check logs above for TX IDs and asset status.")

if __name__ == "__main__":

 main()

