#!/usr/bin/env python3
"""
Analyze the 179 newly found identities to determine if they're:
1. Intentionally hidden (have balance/assets/special properties)
2. Random coincidences (0 balance, no assets)
3. Part of a larger pattern
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List

from qubipy.rpc import rpc_client

OUTPUT_DIR = Path("outputs/derived")
SCAN_FILE = OUTPUT_DIR / "comprehensive_matrix_scan.json"
OUTPUT_JSON = OUTPUT_DIR / "new_identities_analysis.json"

KNOWN_8 = [
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
]

def analyze_identity(rpc: rpc_client.QubiPy_RPC, identity: str) -> Dict:
 """Get full details about an identity."""
 result = {
 "identity": identity,
 "balance": "0",
 "incoming_amount": "0",
 "outgoing_amount": "0",
 "valid_for_tick": None,
 "owned_assets": [],
 "possessed_assets": [],
 "has_activity": False,
 }
 
 try:
 time.sleep(0.5)
 balance_data = rpc.get_balance(identity)
 if balance_data:
 result["balance"] = balance_data.get("balance", "0")
 result["incoming_amount"] = balance_data.get("incomingAmount", "0")
 result["outgoing_amount"] = balance_data.get("outgoingAmount", "0")
 result["valid_for_tick"] = balance_data.get("validForTick")
 result["has_activity"] = (
 int(result["balance"]) > 0 or
 int(result["incoming_amount"]) > 0 or
 int(result["outgoing_amount"]) > 0
 )
 
 owned = rpc.get_owned_assets(identity)
 if owned and owned.get("assets"):
 result["owned_assets"] = owned["assets"]
 
 possessed = rpc.get_possessed_assets(identity)
 if possessed and possessed.get("assets"):
 result["possessed_assets"] = possessed["assets"]
 except Exception as e:
 result["error"] = str(e)
 
 return result

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=== Analyzing New Identities ===\n")
 
 # Load scan results
 with SCAN_FILE.open("r", encoding="utf-8") as f:
 scan_data = json.load(f)
 
 # Collect all unique identities
 all_identities = set()
 for result in scan_data.get("results", []):
 for identity in result.get("on_chain_identities", []):
 all_identities.add(identity)
 
 # Remove known 8
 new_identities = all_identities - set(KNOWN_8)
 
 print(f"Total identities found: {len(all_identities)}")
 print(f"Known 8: {len(set(KNOWN_8) & all_identities)}")
 print(f"New identities: {len(new_identities)}")
 print(f"\nAnalyzing first 50 new identities...\n")
 
 # Analyze first 50 (to avoid rate limiting)
 analysis_results = []
 for i, identity in enumerate(list(new_identities)[:50], 1):
 print(f"[{i}/50] Analyzing {identity[:30]}...")
 result = analyze_identity(rpc, identity)
 analysis_results.append(result)
 
 if result.get("has_activity") or result.get("owned_assets") or result.get("possessed_assets"):
 print(f" ⚠️ HAS ACTIVITY! Balance: {result['balance']}, Assets: {len(result['owned_assets']) + len(result['possessed_assets'])}")
 
 # Summary
 with_balance = [r for r in analysis_results if int(r["balance"]) > 0]
 with_assets = [r for r in analysis_results if r["owned_assets"] or r["possessed_assets"]]
 with_activity = [r for r in analysis_results if r["has_activity"]]
 
 print(f"\n=== Summary (of 50 analyzed) ===")
 print(f"With balance > 0: {len(with_balance)}")
 print(f"With assets: {len(with_assets)}")
 print(f"With any activity: {len(with_activity)}")
 
 if with_balance or with_assets:
 print(f"\n🎉 FOUND IDENTITIES WITH ACTIVITY!")
 print(f"\nIdentities with balance:")
 for r in with_balance:
 print(f" {r['identity']}: {r['balance']} QU")
 print(f"\nIdentities with assets:")
 for r in with_assets:
 print(f" {r['identity']}: {len(r['owned_assets'])} owned, {len(r['possessed_assets'])} possessed")
 
 # Save results
 output = {
 "total_new_identities": len(new_identities),
 "analyzed_count": len(analysis_results),
 "with_balance": len(with_balance),
 "with_assets": len(with_assets),
 "with_activity": len(with_activity),
 "results": analysis_results,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print(f"\nReport saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
 main()

