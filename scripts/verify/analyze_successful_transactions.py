#!/usr/bin/env python3
"""
Analyze Successful Transactions: Find and analyze the 24,696 successful outgoing transactions
from the Smart Contract to understand what triggers them.

Focus: Find the LAST 5-10 successful transactions and analyze:
- What amounts were sent TO the contract?
- What payloads/memos were used?
- What identities sent successful transactions?
- What timing patterns exist?
"""

from __future__ import annotations

import json
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from qubipy.rpc import rpc_client

CONTRACT_ID = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "successful_transactions_analysis.json"

@dataclass
class TransactionAnalysis:
 tx_id: str
 source_id: str
 amount: int
 tick: int
 payload: Optional[str] = None
 payload_size: int = 0
 is_our_identity: bool = False

def get_recent_incoming_transactions(rpc: rpc_client.QubiPy_RPC, limit: int = 50) -> List[Dict[str, Any]]:
 """Get recent incoming transactions to the contract."""
 transactions = []
 
 try:
 latest_tick = rpc.get_latest_tick()
 # Try different ranges to find transactions
 ranges = [
 (max(0, latest_tick - 1000), latest_tick), # Last 1k ticks
 (max(0, latest_tick - 10000), latest_tick), # Last 10k ticks
 (max(0, latest_tick - 50000), latest_tick), # Last 50k ticks
 ]
 
 for start_tick, end_tick in ranges:
 try:
 tx_data = rpc.get_transfer_transactions_per_tick(
 identity=CONTRACT_ID,
 start_tick=start_tick,
 end_tick=end_tick
 )
 
 if tx_data and tx_data.get("transactions"):
 txs = tx_data["transactions"]
 # Filter for incoming (where contract is destination)
 incoming = [
 tx for tx in txs 
 if tx.get("destinationId") == CONTRACT_ID
 ]
 transactions.extend(incoming)
 
 if len(transactions) >= limit:
 break
 
 time.sleep(0.5) # Rate limiting
 except Exception as e:
 print(f" ⚠️ Error in range {start_tick}-{end_tick}: {e}")
 continue
 
 except Exception as e:
 print(f"Error getting transactions: {e}")
 
 # Sort by tick (newest first)
 transactions.sort(key=lambda x: x.get("tickNumber", 0), reverse=True)
 return transactions[:limit]

def get_recent_outgoing_transactions(rpc: rpc_client.QubiPy_RPC, limit: int = 50) -> List[Dict[str, Any]]:
 """Get recent outgoing transactions from the contract."""
 transactions = []
 
 try:
 latest_tick = rpc.get_latest_tick()
 ranges = [
 (max(0, latest_tick - 1000), latest_tick),
 (max(0, latest_tick - 10000), latest_tick),
 (max(0, latest_tick - 50000), latest_tick),
 ]
 
 for start_tick, end_tick in ranges:
 try:
 tx_data = rpc.get_transfer_transactions_per_tick(
 identity=CONTRACT_ID,
 start_tick=start_tick,
 end_tick=end_tick
 )
 
 if tx_data and tx_data.get("transactions"):
 txs = tx_data["transactions"]
 # Filter for outgoing (where contract is source)
 outgoing = [
 tx for tx in txs 
 if tx.get("sourceId") == CONTRACT_ID
 ]
 transactions.extend(outgoing)
 
 if len(transactions) >= limit:
 break
 
 time.sleep(0.5)
 except Exception as e:
 print(f" ⚠️ Error in range {start_tick}-{end_tick}: {e}")
 continue
 
 except Exception as e:
 print(f"Error getting outgoing transactions: {e}")
 
 transactions.sort(key=lambda x: x.get("tickNumber", 0), reverse=True)
 return transactions[:limit]

def analyze_transaction_patterns(incoming: List[Dict], outgoing: List[Dict]) -> Dict[str, Any]:
 """Analyze patterns in successful transactions."""
 
 analysis = {
 "incoming_count": len(incoming),
 "outgoing_count": len(outgoing),
 "ratio": len(outgoing) / len(incoming) if incoming else 0,
 "amount_analysis": {},
 "tick_analysis": {},
 "recent_incoming": [],
 "recent_outgoing": [],
 }
 
 # Analyze amounts in incoming transactions
 if incoming:
 amounts = [int(tx.get("amount", 0)) for tx in incoming if tx.get("amount")]
 if amounts:
 analysis["amount_analysis"]["incoming"] = {
 "min": min(amounts),
 "max": max(amounts),
 "average": sum(amounts) / len(amounts),
 "most_common": Counter(amounts).most_common(5),
 }
 
 # Analyze amounts in outgoing transactions
 if outgoing:
 amounts = [int(tx.get("amount", 0)) for tx in outgoing if tx.get("amount")]
 if amounts:
 analysis["amount_analysis"]["outgoing"] = {
 "min": min(amounts),
 "max": max(amounts),
 "average": sum(amounts) / len(amounts),
 "most_common": Counter(amounts).most_common(5),
 }
 
 # Analyze ticks
 if incoming:
 ticks = [tx.get("tickNumber", 0) for tx in incoming if tx.get("tickNumber")]
 if ticks:
 analysis["tick_analysis"]["incoming"] = {
 "oldest": min(ticks),
 "newest": max(ticks),
 "range": max(ticks) - min(ticks),
 }
 
 if outgoing:
 ticks = [tx.get("tickNumber", 0) for tx in outgoing if tx.get("tickNumber")]
 if ticks:
 analysis["tick_analysis"]["outgoing"] = {
 "oldest": min(ticks),
 "newest": max(ticks),
 "range": max(ticks) - min(ticks),
 }
 
 # Store recent transactions (last 10)
 analysis["recent_incoming"] = incoming[:10]
 analysis["recent_outgoing"] = outgoing[:10]
 
 return analysis

def check_if_our_identities(source_id: str) -> bool:
 """Check if this is one of our Layer-1 or Layer-2 identities."""
 our_identities = [
 # Layer-1
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
 # Layer-2
 "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD",
 "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE",
 "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG",
 "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI",
 "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL",
 "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI",
 "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN",
 "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB",
 ]
 return source_id in our_identities

def main() -> int:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("🔍 ANALYZING SUCCESSFUL TRANSACTIONS")
 print("=" * 80)
 print()
 print("Goal: Find what triggers the 24,696 successful outgoing transactions")
 print("Focus: Last 5-10 incoming transactions and their patterns")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 
 # Get contract status
 print("Getting contract status...")
 try:
 balance_data = rpc.get_balance(CONTRACT_ID)
 if balance_data:
 incoming_count = balance_data.get("numberOfIncomingTransfers", 0)
 outgoing_count = balance_data.get("numberOfOutgoingTransfers", 0)
 print(f" Incoming: {incoming_count}")
 print(f" Outgoing: {outgoing_count}")
 print(f" Ratio: {outgoing_count / incoming_count:.2f}x" if incoming_count > 0 else " Ratio: N/A")
 except Exception as e:
 print(f" Error: {e}")
 
 print()
 print("=" * 80)
 print("ANALYZING RECENT INCOMING TRANSACTIONS")
 print("=" * 80)
 print()
 
 incoming_txs = get_recent_incoming_transactions(rpc, limit=20)
 print(f"Found {len(incoming_txs)} recent incoming transactions")
 
 if incoming_txs:
 print()
 print("Last 10 incoming transactions:")
 for i, tx in enumerate(incoming_txs[:10], 1):
 source = tx.get("sourceId", "Unknown")
 amount = tx.get("amount", "0")
 tick = tx.get("tickNumber", "N/A")
 is_ours = check_if_our_identities(source)
 marker = "🎯 OUR IDENTITY" if is_ours else ""
 print(f" {i}. Tick {tick}: {amount} QU from {source[:30]}... {marker}")
 else:
 print(" ⚠️ No incoming transactions found in recent history")
 
 print()
 print("=" * 80)
 print("ANALYZING RECENT OUTGOING TRANSACTIONS")
 print("=" * 80)
 print()
 
 outgoing_txs = get_recent_outgoing_transactions(rpc, limit=20)
 print(f"Found {len(outgoing_txs)} recent outgoing transactions")
 
 if outgoing_txs:
 print()
 print("Last 10 outgoing transactions:")
 for i, tx in enumerate(outgoing_txs[:10], 1):
 dest = tx.get("destinationId", "Unknown")
 amount = tx.get("amount", "0")
 tick = tx.get("tickNumber", "N/A")
 print(f" {i}. Tick {tick}: {amount} QU to {dest[:30]}...")
 else:
 print(" ⚠️ No outgoing transactions found in recent history")
 
 print()
 print("=" * 80)
 print("PATTERN ANALYSIS")
 print("=" * 80)
 print()
 
 analysis = analyze_transaction_patterns(incoming_txs, outgoing_txs)
 
 if analysis["amount_analysis"].get("incoming"):
 inc_amt = analysis["amount_analysis"]["incoming"]
 print("Incoming Amount Analysis:")
 print(f" Min: {inc_amt['min']} QU")
 print(f" Max: {inc_amt['max']} QU")
 print(f" Average: {inc_amt['average']:.0f} QU")
 print(f" Most common: {inc_amt['most_common']}")
 print()
 
 if analysis["amount_analysis"].get("outgoing"):
 out_amt = analysis["amount_analysis"]["outgoing"]
 print("Outgoing Amount Analysis:")
 print(f" Min: {out_amt['min']} QU")
 print(f" Max: {out_amt['max']} QU")
 print(f" Average: {out_amt['average']:.0f} QU")
 print(f" Most common: {out_amt['most_common']}")
 print()
 
 if analysis["tick_analysis"].get("incoming"):
 inc_tick = analysis["tick_analysis"]["incoming"]
 print("Incoming Tick Analysis:")
 print(f" Oldest: {inc_tick['oldest']}")
 print(f" Newest: {inc_tick['newest']}")
 print(f" Range: {inc_tick['range']} ticks (~{inc_tick['range'] * 0.6 / 60:.1f} minutes)")
 print()
 
 # Check if any of our identities appear
 print("=" * 80)
 print("CHECKING FOR OUR IDENTITIES")
 print("=" * 80)
 print()
 
 our_identity_txs = [tx for tx in incoming_txs if check_if_our_identities(tx.get("sourceId", ""))]
 
 if our_identity_txs:
 print(f"✅ Found {len(our_identity_txs)} transactions from OUR identities!")
 for tx in our_identity_txs[:5]:
 source = tx.get("sourceId", "Unknown")
 amount = tx.get("amount", "0")
 tick = tx.get("tickNumber", "N/A")
 print(f" - Tick {tick}: {amount} QU from {source[:30]}...")
 else:
 print("❌ None of our identities appear in recent incoming transactions")
 print(" This means our transactions haven't triggered the contract")
 
 # Save analysis
 output_data = {
 "contract_id": CONTRACT_ID,
 "analysis": analysis,
 "our_identity_transactions": our_identity_txs,
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output_data, f, indent=2, default=str)
 
 print()
 print("=" * 80)
 print(f"✅ Analysis saved to: {OUTPUT_JSON}")
 print("=" * 80)
 print()
 
 # Key insights
 print("KEY INSIGHTS:")
 if incoming_txs:
 latest_tick = max(tx.get("tickNumber", 0) for tx in incoming_txs)
 current_tick = rpc.get_latest_tick()
 age_ticks = current_tick - latest_tick
 age_minutes = age_ticks * 0.6 / 60
 print(f" - Latest incoming transaction: {age_minutes:.1f} minutes ago")
 if age_minutes < 60:
 print(f" → Contract is ACTIVE (recent activity)")
 else:
 print(f" → Contract might be INACTIVE (old activity)")
 
 if analysis["amount_analysis"].get("incoming"):
 avg_amount = analysis["amount_analysis"]["incoming"]["average"]
 print(f" - Average incoming amount: {avg_amount:.0f} QU")
 if avg_amount > 1000:
 print(f" → We've been testing with too small amounts (1 QU)")
 
 if our_identity_txs:
 print(f" - Our identities HAVE sent transactions")
 print(f" → But they didn't trigger payouts (wrong format/amount?)")
 else:
 print(f" - Our identities have NOT sent successful transactions")
 print(f" → We need to find what makes transactions successful")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

