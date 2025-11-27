#!/usr/bin/env python3
"""
Contract Analysis: Analyze the Smart Contract to understand what it expects.

Check:
- Contract balance and transaction history
- What transactions has it received?
- What patterns exist in successful transactions?
"""

from __future__ import annotations

import json
from pathlib import Path
from qubipy.rpc import rpc_client

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
OUTPUT_DIR = Path("outputs/derived")

def analyze_contract(rpc: rpc_client.QubiPy_RPC) -> dict:
 """Analyze the Smart Contract."""
 
 analysis = {
 "contract_id": CONTRACT_ID,
 "balance": None,
 "incoming_transfers": None,
 "outgoing_transfers": None,
 "owned_assets": None,
 "possessed_assets": None,
 "transaction_history": None,
 }
 
 print("Analyzing Smart Contract...")
 print()
 
 # Get balance
 try:
 balance_data = rpc.get_balance(CONTRACT_ID)
 if balance_data:
 analysis["balance"] = balance_data.get("balance", "0")
 analysis["incoming_transfers"] = balance_data.get("numberOfIncomingTransfers", 0)
 analysis["outgoing_transfers"] = balance_data.get("numberOfOutgoingTransfers", 0)
 print(f"Balance: {analysis['balance']} QU")
 print(f"Incoming transfers: {analysis['incoming_transfers']}")
 print(f"Outgoing transfers: {analysis['outgoing_transfers']}")
 except Exception as e:
 print(f"Error getting balance: {e}")
 
 print()
 
 # Get assets
 try:
 owned = rpc.get_owned_assets(CONTRACT_ID)
 if isinstance(owned, list):
 analysis["owned_assets"] = len(owned)
 print(f"Owned assets: {len(owned)}")
 if owned:
 for asset in owned[:5]: # Show first 5
 name = asset.get("data", {}).get("issuedAsset", {}).get("name", "Unknown")
 units = asset.get("data", {}).get("numberOfUnits", "0")
 print(f" - {name}: {units} units")
 except Exception as e:
 print(f"Error getting owned assets: {e}")
 
 try:
 possessed = rpc.get_possessed_assets(CONTRACT_ID)
 if isinstance(possessed, list):
 analysis["possessed_assets"] = len(possessed)
 print(f"Possessed assets: {len(possessed)}")
 except Exception as e:
 print(f"Error getting possessed assets: {e}")
 
 print()
 
 # Try to get transaction history
 try:
 latest_tick = rpc.get_latest_tick()
 start_tick = max(0, latest_tick - 10000) # Last 10k ticks
 
 tx_data = rpc.get_transfer_transactions_per_tick(
 identity=CONTRACT_ID,
 start_tick=start_tick,
 end_tick=latest_tick
 )
 
 if tx_data and tx_data.get("transactions"):
 transactions = tx_data["transactions"]
 analysis["transaction_history"] = {
 "count": len(transactions),
 "recent_transactions": transactions[:10] # Last 10
 }
 print(f"Recent transactions (last 10k ticks): {len(transactions)}")
 print()
 print("Recent transaction patterns:")
 for tx in transactions[:5]:
 source = tx.get("sourceId", "Unknown")[:20]
 amount = tx.get("amount", "0")
 tick = tx.get("tickNumber", "N/A")
 print(f" Tick {tick}: {amount} QU from {source}...")
 except Exception as e:
 print(f"Error getting transaction history: {e}")
 
 return analysis

def main():
 print("=" * 80)
 print("SMART CONTRACT ANALYSIS")
 print("=" * 80)
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 analysis = analyze_contract(rpc)
 
 # Save analysis
 output_file = OUTPUT_DIR / "contract_analysis.json"
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 with output_file.open("w", encoding="utf-8") as f:
 json.dump(analysis, f, indent=2)
 
 print()
 print("=" * 80)
 print(f"Analysis saved to: {output_file}")
 print("=" * 80)
 print()
 print("Key Questions:")
 print(" 1. How many incoming transfers has the contract received?")
 print(" 2. What patterns exist in successful transactions?")
 print(" 3. Does the contract have any assets to distribute?")
 print(" 4. What amounts have been sent to the contract?")

if __name__ == "__main__":
 main()
