#!/usr/bin/env python3
"""
Contract Deep Analysis: Use all available RPC methods to understand the contract.

Since transaction history is pruned, we analyze:
- Contract balance and transfer counts
- Asset issuance history
- Contract-owned assets
- Any other available contract information
"""

from __future__ import annotations

import json
from pathlib import Path
from qubipy.rpc import rpc_client

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "contract_deep_analysis.json"

def analyze_contract_comprehensive(rpc: rpc_client.QubiPy_RPC) -> dict:
 """Comprehensive contract analysis using all available methods."""
 
 analysis = {
 "contract_id": CONTRACT_ID,
 "balance_info": {},
 "asset_info": {},
 "transfer_stats": {},
 "insights": [],
 }
 
 print("=" * 80)
 print("COMPREHENSIVE CONTRACT ANALYSIS")
 print("=" * 80)
 print()
 
 # Get balance (most reliable method)
 print("1. Balance Analysis...")
 try:
 balance_data = rpc.get_balance(CONTRACT_ID)
 if balance_data:
 analysis["balance_info"] = {
 "balance": balance_data.get("balance", "0"),
 "incoming_amount": balance_data.get("incomingAmount", "0"),
 "outgoing_amount": balance_data.get("outgoingAmount", "0"),
 "incoming_transfers": balance_data.get("numberOfIncomingTransfers", 0),
 "outgoing_transfers": balance_data.get("numberOfOutgoingTransfers", 0),
 "latest_incoming_tick": balance_data.get("latestIncomingTransferTick"),
 "latest_outgoing_tick": balance_data.get("latestOutgoingTransferTick"),
 "valid_for_tick": balance_data.get("validForTick"),
 }
 
 print(f" Balance: {analysis['balance_info']['balance']} QU")
 print(f" Incoming: {analysis['balance_info']['incoming_transfers']} transfers, {analysis['balance_info']['incoming_amount']} QU total")
 print(f" Outgoing: {analysis['balance_info']['outgoing_transfers']} transfers, {analysis['balance_info']['outgoing_amount']} QU total")
 
 if analysis["balance_info"]["incoming_transfers"] > 0:
 ratio = analysis["balance_info"]["outgoing_transfers"] / analysis["balance_info"]["incoming_transfers"]
 print(f" Ratio: {ratio:.2f}x (1 incoming → {ratio:.1f} outgoing)")
 analysis["transfer_stats"]["ratio"] = ratio
 
 if analysis["balance_info"]["latest_incoming_tick"]:
 latest_tick = rpc.get_latest_tick()
 age_ticks = latest_tick - analysis["balance_info"]["latest_incoming_tick"]
 age_minutes = age_ticks * 0.6 / 60
 print(f" Latest incoming: {age_minutes:.1f} minutes ago (Tick {analysis['balance_info']['latest_incoming_tick']})")
 analysis["insights"].append(f"Latest incoming transaction: {age_minutes:.1f} minutes ago")
 
 if age_minutes < 60:
 analysis["insights"].append("Contract is ACTIVE (recent activity)")
 else:
 analysis["insights"].append("Contract might be INACTIVE (old activity)")
 
 if analysis["balance_info"]["latest_outgoing_tick"]:
 latest_tick = rpc.get_latest_tick()
 age_ticks = latest_tick - analysis["balance_info"]["latest_outgoing_tick"]
 age_minutes = age_ticks * 0.6 / 60
 print(f" Latest outgoing: {age_minutes:.1f} minutes ago (Tick {analysis['balance_info']['latest_outgoing_tick']})")
 except Exception as e:
 print(f" Error: {e}")
 
 print()
 
 # Get assets
 print("2. Asset Analysis...")
 try:
 owned = rpc.get_owned_assets(CONTRACT_ID)
 if isinstance(owned, list) and owned:
 analysis["asset_info"]["owned_count"] = len(owned)
 analysis["asset_info"]["owned_assets"] = []
 
 for asset in owned:
 asset_data = {
 "name": asset.get("data", {}).get("issuedAsset", {}).get("name", "Unknown"),
 "units": asset.get("data", {}).get("numberOfUnits", "0"),
 "issuance_index": asset.get("data", {}).get("issuanceIndex"),
 "tick": asset.get("info", {}).get("tick"),
 }
 analysis["asset_info"]["owned_assets"].append(asset_data)
 print(f" {asset_data['name']}: {asset_data['units']} units (Issuance: {asset_data['issuance_index']})")
 else:
 print(" No owned assets found")
 except Exception as e:
 print(f" Error: {e}")
 
 print()
 
 # Calculate average amounts
 if analysis["balance_info"].get("incoming_transfers", 0) > 0:
 avg_incoming = int(analysis["balance_info"]["incoming_amount"]) // analysis["balance_info"]["incoming_transfers"]
 analysis["transfer_stats"]["average_incoming"] = avg_incoming
 print(f"3. Transfer Statistics:")
 print(f" Average incoming amount: {avg_incoming} QU")
 analysis["insights"].append(f"Average incoming amount: {avg_incoming} QU")
 
 if avg_incoming > 1000:
 analysis["insights"].append("⚠️ We've been testing with too small amounts (1 QU vs {avg_incoming} QU average)")
 
 print()
 
 return analysis

def main() -> int:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 rpc = rpc_client.QubiPy_RPC()
 analysis = analyze_contract_comprehensive(rpc)
 
 # Save
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(analysis, f, indent=2, default=str)
 
 print("=" * 80)
 print("KEY INSIGHTS")
 print("=" * 80)
 print()
 
 for insight in analysis.get("insights", []):
 print(f" • {insight}")
 
 print()
 print("=" * 80)
 print(f"✅ Analysis saved to: {OUTPUT_JSON}")
 print("=" * 80)
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

