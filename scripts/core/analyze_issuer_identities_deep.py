#!/usr/bin/env python3
"""
Deep Analysis der 3 Issuer-Identities

Prüft:
- Balance und Assets
- Transaction History
- Smart Contract Status
- Asset-Details
- Mögliche Nachrichten/Patterns
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "issuer_identities_deep_analysis.json"
OUTPUT_MD = OUTPUT_DIR / "issuer_identities_deep_analysis.md"

# Die 3 Issuer-Identities
ISSUERS = {
 "CFB": {
 "identity": "CFBMEMZOIDEXQAUXYYSZIURADQLAPWPMNJXQSNVQZAHYVOPYUKKJBJUCTVJL",
 "asset_name": "CFB",
 "units": 5,
 },
 "CODED": {
 "identity": "CODEDBUUDDYHECBVSUONSSWTOJRCLZSWHFHZIUWVFGNWVCKIWJCSDSWGQAAI",
 "asset_name": "CODED",
 "units": 2,
 },
 "QXMR": {
 "identity": "QXMRTKAIIGLUREPIQPCMHCKWSIPDTUYFCFNYXQLTECSUJVYEMMDELBMDOEYB",
 "asset_name": "QXMR",
 "units": 5,
 },
}

def analyze_issuer(rpc, issuer_data: Dict) -> Dict:
 """Detaillierte Analyse einer Issuer-Identity."""
 identity = issuer_data["identity"]
 asset_name = issuer_data["asset_name"]
 
 print(f"\n{'='*80}")
 print(f"ANALYSE: {asset_name} Issuer")
 print(f"{'='*80}")
 print(f"Identity: {identity}")
 print()
 
 result = {
 "asset_name": asset_name,
 "issuer_identity": identity,
 "balance": None,
 "valid_for_tick": None,
 "owned_assets": [],
 "possessed_assets": [],
 "is_smart_contract": False,
 "contract_index": None,
 "transaction_count": 0,
 "recent_transactions": [],
 "incoming_transactions": [],
 "outgoing_transactions": [],
 "asset_issuances": [],
 "patterns": [],
 "status": "unknown",
 "error": None,
 }
 
 try:
 # 1. Balance Check
 time.sleep(2.0)
 balance_data = rpc.get_balance(identity)
 if balance_data:
 result["balance"] = str(balance_data.get("balance", 0))
 result["valid_for_tick"] = balance_data.get("validForTick", 0)
 print(f"✅ Balance: {result['balance']} QU")
 print(f" Valid for Tick: {result['valid_for_tick']}")
 
 # 2. Assets Check
 try:
 time.sleep(2.0)
 owned_assets = rpc.get_owned_assets(identity)
 result["owned_assets"] = owned_assets if owned_assets else []
 print(f"✅ Owned Assets: {len(result['owned_assets'])}")
 
 time.sleep(2.0)
 possessed_assets = rpc.get_possessed_assets(identity)
 result["possessed_assets"] = possessed_assets if possessed_assets else []
 print(f"✅ Possessed Assets: {len(result['possessed_assets'])}")
 except Exception as e:
 print(f"⚠️ Assets Error: {e}")
 
 # 3. Smart Contract Check
 try:
 time.sleep(2.0)
 # Check, ob es ein Smart Contract ist
 # (Qubic Smart Contracts haben bestimmte Indices)
 contract_info = rpc.get_contract_info(identity)
 if contract_info:
 result["is_smart_contract"] = True
 result["contract_index"] = contract_info.get("index")
 print(f"✅ Smart Contract gefunden! Index: {result['contract_index']}")
 except:
 # Nicht alle Identities sind Contracts
 pass
 
 # 4. Transaction History (wenn verfügbar)
 try:
 time.sleep(2.0)
 # Versuche, Transaction History zu bekommen
 # (kann je nach RPC-Implementierung variieren)
 history = rpc.get_transaction_history(identity, limit=50)
 if history:
 result["recent_transactions"] = history[:20]
 result["transaction_count"] = len(history)
 
 # Analyze Transaktionen
 incoming = [tx for tx in history if tx.get("amount", 0) > 0]
 outgoing = [tx for tx in history if tx.get("amount", 0) < 0]
 
 result["incoming_transactions"] = incoming[:10]
 result["outgoing_transactions"] = outgoing[:10]
 
 print(f"✅ Transaction History: {len(history)} transactions")
 print(f" Incoming: {len(incoming)}, Outgoing: {len(outgoing)}")
 except Exception as e:
 print(f"⚠️ Transaction History nicht verfügbar: {e}")
 
 # 5. Asset Issuances (wenn verfügbar)
 try:
 time.sleep(2.0)
 # Check, welche Assets diese Identity ausgegeben hat
 # (kann je nach RPC-Implementierung variieren)
 issuances = rpc.get_asset_issuances(identity)
 if issuances:
 result["asset_issuances"] = issuances[:20]
 print(f"✅ Asset Issuances: {len(issuances)}")
 except:
 pass
 
 # 6. Pattern Analysis
 patterns = []
 
 # Check auf bekannte Patterns
 if "CFB" in asset_name:
 patterns.append("CFB Reference - Could be Come-from-Beyond")
 
 if int(result.get("balance", 0)) > 1000000000:
 patterns.append("Extremely high balance - Likely official/important")
 
 if result.get("is_smart_contract"):
 patterns.append("Smart Contract - May contain encoded messages")
 
 result["patterns"] = patterns
 
 if patterns:
 print(f"✅ Patterns gefunden:")
 for pattern in patterns:
 print(f" - {pattern}")
 
 result["status"] = "success"
 
 except Exception as e:
 result["error"] = str(e)
 result["status"] = "error"
 print(f"❌ Error: {e}")
 import traceback
 traceback.print_exc()
 
 return result

def main() -> int:
 """Main function."""
 print("=" * 80)
 print("DEEP ANALYSIS: ISSUER IDENTITIES")
 print("=" * 80)
 print()
 
 try:
 from qubipy.rpc import rpc_client
 rpc = rpc_client.QubiPy_RPC()
 print("✅ RPC connection established")
 except Exception as e:
 print(f"❌ RPC connection failed: {e}")
 return 1
 
 print()
 
 results = []
 
 for asset_name, issuer_data in ISSUERS.items():
 result = analyze_issuer(rpc, issuer_data)
 results.append(result)
 time.sleep(3.0) # Rate limiting
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump({
 "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
 "issuers": results,
 }, f, indent=2, ensure_ascii=False)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w", encoding="utf-8") as f:
 f.write("# Deep Analysis: Issuer Identities\n\n")
 f.write(f"**Analysis Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
 
 for result in results:
 asset_name = result["asset_name"]
 f.write(f"## {asset_name} Issuer\n\n")
 f.write(f"**Identity:** `{result['issuer_identity']}`\n\n")
 
 if result["balance"] is not None:
 f.write(f"- **Balance:** {result['balance']} QU\n")
 f.write(f"- **Valid for Tick:** {result['valid_for_tick']}\n")
 
 f.write(f"- **Owned Assets:** {len(result.get('owned_assets', []))}\n")
 f.write(f"- **Possessed Assets:** {len(result.get('possessed_assets', []))}\n")
 
 if result.get("is_smart_contract"):
 f.write(f"- **Smart Contract:** Yes (Index: {result.get('contract_index')})\n")
 
 f.write(f"- **Transaction Count:** {result.get('transaction_count', 0)}\n")
 
 if result.get("patterns"):
 f.write(f"\n### Patterns\n\n")
 for pattern in result["patterns"]:
 f.write(f"- {pattern}\n")
 
 if result.get("error"):
 f.write(f"\n### Error\n\n")
 f.write(f"```\n{result['error']}\n```\n")
 
 f.write("\n")
 
 print()
 print("=" * 80)
 print("✅ ANALYSIS COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to:")
 print(f" {OUTPUT_JSON}")
 print(f" {OUTPUT_MD}")
 print()
 
 # Zusammenfassung
 print("ZUSAMMENFASSUNG:")
 print()
 for result in results:
 asset_name = result["asset_name"]
 balance = result.get("balance", "N/A")
 is_contract = result.get("is_smart_contract", False)
 tx_count = result.get("transaction_count", 0)
 
 print(f"{asset_name}:")
 print(f" Balance: {balance} QU")
 print(f" Smart Contract: {'Yes' if is_contract else 'No'}")
 print(f" Transactions: {tx_count}")
 print()
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

