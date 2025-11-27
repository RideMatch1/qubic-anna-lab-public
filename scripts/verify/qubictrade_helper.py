#!/usr/bin/env python3
"""
Helper script to prepare Layer-2 identities for QubicTrade purchase.

Outputs all seeds and identities in a format that can be quickly copied
for manual purchase on QubicTrade.
"""

from __future__ import annotations

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

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

def main() -> None:
 print("=" * 80)
 print("QUBICTRADE HELPER - Layer-2 Identities for GENESIS Asset Purchase")
 print("=" * 80)
 print()
 print(f"Contract ID: {CONTRACT_ID}")
 print(f"Asset: GENESIS")
 print()
 print("=" * 80)
 print("COPY-PASTE READY FORMAT")
 print("=" * 80)
 print()
 
 for i, entry in enumerate(SEED_TABLE, 1):
 print(f"--- {entry['label']} ---")
 print(f"Seed: {entry['seed']}")
 print(f"Identity: {entry['identity']}")
 print()
 
 print("=" * 80)
 print("QUICK REFERENCE TABLE")
 print("=" * 80)
 print()
 print("| # | Label | Identity (first 20 chars) |")
 print("| --- | --- | --- |")
 for i, entry in enumerate(SEED_TABLE, 1):
 print(f"| {i} | {entry['label']} | `{entry['identity'][:20]}...` |")
 
 print()
 print("=" * 80)
 print("INSTRUCTIONS")
 print("=" * 80)
 print()
 print("1. Open QubicTrade in 8 browser tabs/windows")
 print("2. For each tab:")
 print(" - Login with the corresponding seed")
 print(" - Navigate to GENESIS asset")
 print(" - Prepare purchase (have it ready, don't confirm yet)")
 print("3. Once all 8 are ready, confirm all purchases as quickly as possible")
 print("4. The synchronized_contract_trigger.py script can help ensure")
 print(" transactions arrive in the same tick")
 print()
 print("=" * 80)

if __name__ == "__main__":
 main()

