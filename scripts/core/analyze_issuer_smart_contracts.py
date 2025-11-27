#!/usr/bin/env python3
"""
Deep Analysis: Issuer Identities als Smart Contracts

Prüft:
- Smart Contract Code (wenn vorhanden)
- Transaktionsmuster
- Auszahlungsbedingungen
- Code-Logik
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "issuer_smart_contract_analysis.json"
OUTPUT_MD = OUTPUT_DIR / "issuer_smart_contract_analysis.md"

# Die 3 Issuer-Identities
ISSUERS = {
 "CFB": {
 "identity": "CFBMEMZOIDEXQAUXYYSZIURADQLAPWPMNJXQSNVQZAHYVOPYUKKJBJUCTVJL",
 "asset_name": "CFB",
 "balance": "2232346253", # 2.2 Milliarden QU
 },
 "CODED": {
 "identity": "CODEDBUUDDYHECBVSUONSSWTOJRCLZSWHFHZIUWVFGNWVCKIWJCSDSWGQAAI",
 "asset_name": "CODED",
 "balance": "305",
 },
 "QXMR": {
 "identity": "QXMRTKAIIGLUREPIQPCMHCKWSIPDTUYFCFNYXQLTECSUJVYEMMDELBMDOEYB",
 "asset_name": "QXMR",
 "balance": "801",
 },
}

# Master Identity
MASTER_IDENTITY = "BZBQFLLBNCXEMGLOBHUVFTLUPLVCPQUASSILFABOFFBCADQSSUPNWLZBQEXK"

def analyze_smart_contract(rpc, issuer_data: Dict) -> Dict:
 """Detaillierte Smart Contract Analyse einer Issuer-Identity."""
 identity = issuer_data["identity"]
 asset_name = issuer_data["asset_name"]
 
 print(f"\n{'='*80}")
 print(f"SMART CONTRACT ANALYSE: {asset_name} Issuer")
 print(f"{'='*80}")
 print(f"Identity: {identity}")
 print()
 
 result = {
 "asset_name": asset_name,
 "issuer_identity": identity,
 "is_smart_contract": False,
 "contract_code": None,
 "contract_index": None,
 "contract_functions": [],
 "transaction_patterns": [],
 "payout_conditions": [],
 "master_identity_connection": False,
 "balance": issuer_data.get("balance"),
 "status": "unknown",
 "error": None,
 }
 
 try:
 # 1. Check ob es ein Smart Contract ist
 time.sleep(2.0)
 try:
 # Versuche Contract Info zu bekommen
 contract_info = rpc.get_contract_info(identity)
 if contract_info:
 result["is_smart_contract"] = True
 result["contract_index"] = contract_info.get("index")
 result["contract_code"] = contract_info.get("code")
 result["contract_functions"] = contract_info.get("functions", [])
 print(f"✅ Smart Contract gefunden! Index: {result['contract_index']}")
 
 if result["contract_code"]:
 print(f" Code verfügbar: {len(result['contract_code'])} bytes")
 if result["contract_functions"]:
 print(f" Functions: {len(result['contract_functions'])}")
 except Exception as e:
 # Nicht alle Identities sind Contracts
 print(f"⚠️ Kein Smart Contract (oder nicht verfügbar): {e}")
 
 # 2. Check Balance und Assets
 time.sleep(2.0)
 balance_data = rpc.get_balance(identity)
 if balance_data:
 result["balance"] = str(balance_data.get("balance", 0))
 print(f"✅ Balance: {result['balance']} QU")
 
 # 3. Check Assets
 try:
 time.sleep(2.0)
 owned_assets = rpc.get_owned_assets(identity)
 result["owned_assets"] = owned_assets if owned_assets else []
 print(f"✅ Owned Assets: {len(result['owned_assets'])}")
 except:
 pass
 
 # 4. Check Verbindung zur Master Identity
 try:
 time.sleep(2.0)
 # Check ob die Master Identity Transaktionen mit diesem Issuer hat
 master_balance = rpc.get_balance(MASTER_IDENTITY)
 if master_balance:
 master_assets = rpc.get_owned_assets(MASTER_IDENTITY)
 if master_assets:
 # Check ob Master Identity Assets von diesem Issuer hat
 for asset in master_assets:
 asset_data = asset.get("data", {})
 issued_asset = asset_data.get("issuedAsset", {})
 if issued_asset.get("issuerIdentity") == identity:
 result["master_identity_connection"] = True
 print(f"✅ Master Identity hat {asset_name} Assets von diesem Issuer!")
 except:
 pass
 
 # 5. Analyze Transaktionsmuster (wenn verfügbar)
 try:
 time.sleep(2.0)
 # Versuche Transaction History zu bekommen
 # (kann je nach RPC-Implementierung variieren)
 history = rpc.get_transaction_history(identity, limit=100)
 if history:
 result["transaction_patterns"] = analyze_transaction_patterns(history, MASTER_IDENTITY)
 print(f"✅ Transaction Patterns analysiert: {len(result['transaction_patterns'])}")
 except Exception as e:
 print(f"⚠️ Transaction History nicht verfügbar: {e}")
 
 result["status"] = "success"
 
 except Exception as e:
 result["error"] = str(e)
 result["status"] = "error"
 print(f"❌ Error: {e}")
 import traceback
 traceback.print_exc()
 
 return result

def analyze_transaction_patterns(history: List, master_identity: str) -> List[Dict]:
 """Analyze Transaktionsmuster."""
 patterns = []
 
 # Check auf Transaktionen mit Master Identity
 master_txs = [tx for tx in history if master_identity in str(tx)]
 if master_txs:
 patterns.append({
 "type": "master_identity_transactions",
 "count": len(master_txs),
 "description": f"Found {len(master_txs)} transactions involving Master Identity",
 })
 
 # Check auf Asset-Auszahlungen
 asset_payouts = [tx for tx in history if tx.get("asset") or tx.get("asset_id")]
 if asset_payouts:
 patterns.append({
 "type": "asset_payouts",
 "count": len(asset_payouts),
 "description": f"Found {len(asset_payouts)} asset payout transactions",
 })
 
 return patterns

def main() -> int:
 """Main function."""
 print("=" * 80)
 print("SMART CONTRACT ANALYSE: ISSUER IDENTITIES")
 print("=" * 80)
 print()
 print(f"Master Identity: {MASTER_IDENTITY}")
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
 result = analyze_smart_contract(rpc, issuer_data)
 results.append(result)
 time.sleep(3.0) # Rate limiting
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump({
 "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
 "master_identity": MASTER_IDENTITY,
 "issuers": results,
 }, f, indent=2, ensure_ascii=False)
 
 # Erstelle Markdown Report
 with OUTPUT_MD.open("w", encoding="utf-8") as f:
 f.write("# Smart Contract Analysis: Issuer Identities\n\n")
 f.write(f"**Analysis Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
 f.write(f"**Master Identity:** `{MASTER_IDENTITY}`\n\n")
 
 for result in results:
 asset_name = result["asset_name"]
 f.write(f"## {asset_name} Issuer\n\n")
 f.write(f"**Identity:** `{result['issuer_identity']}`\n\n")
 
 if result.get("balance"):
 f.write(f"- **Balance:** {result['balance']} QU\n")
 
 if result.get("is_smart_contract"):
 f.write(f"- **Smart Contract:** Yes (Index: {result.get('contract_index')})\n")
 if result.get("contract_code"):
 f.write(f"- **Contract Code:** {len(result['contract_code'])} bytes\n")
 if result.get("contract_functions"):
 f.write(f"- **Functions:** {len(result['contract_functions'])}\n")
 else:
 f.write(f"- **Smart Contract:** No\n")
 
 if result.get("master_identity_connection"):
 f.write(f"- **🔗 Master Identity Connection:** Yes\n")
 
 if result.get("transaction_patterns"):
 f.write(f"\n### Transaction Patterns\n\n")
 for pattern in result["transaction_patterns"]:
 f.write(f"- {pattern['description']}\n")
 
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
 is_contract = result.get("is_smart_contract", False)
 has_connection = result.get("master_identity_connection", False)
 
 print(f"{asset_name}:")
 print(f" Smart Contract: {'Yes' if is_contract else 'No'}")
 print(f" Master Connection: {'Yes' if has_connection else 'No'}")
 print()
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

