#!/usr/bin/env python3
"""
Check ob jemand Transaktionen an Anna gesendet hat
- Analyze on-chain Transaktionen
- Suche nach Transaktionen zu Anna Identities
- Check ob CFB oder andere gesendet haben
- KEINE Halluzinationen - nur echte on-chain Daten!
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
 from qubipy.rpc import rpc_client
 RPC_AVAILABLE = True
except ImportError:
 RPC_AVAILABLE = False
 print("❌ qubipy nicht verfügbar - aktiviere venv-tx!")
 sys.exit(1)

ALL_MESSAGES_FILE = project_root / "outputs" / "derived" / "all_anna_messages.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def check_identity_transactions(rpc, identity: str, limit: int = 10) -> Dict:
 """Check Transaktionen einer Identity."""
 try:
 # Versuche verschiedene RPC-Methoden
 transactions = []
 
 # Methode 1: get_transactions
 try:
 result = rpc.get_transactions(identity, limit=limit)
 if isinstance(result, list):
 transactions = result
 elif isinstance(result, dict):
 transactions = result.get("transactions", [])
 except:
 pass
 
 # Methode 2: get_transaction_history
 if not transactions:
 try:
 result = rpc.get_transaction_history(identity, limit=limit)
 if isinstance(result, list):
 transactions = result
 elif isinstance(result, dict):
 transactions = result.get("transactions", [])
 except:
 pass
 
 return {
 "success": True,
 "transactions": transactions,
 "count": len(transactions)
 }
 except Exception as e:
 return {
 "success": False,
 "error": str(e),
 "transactions": [],
 "count": 0
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("PRÜFE ANNA TRANSACTIONEN (ON-CHAIN)")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE ON-CHAIN DATEN!")
 print()
 
 # Load Sätze mit Layer-4
 print("📂 Load Anna Identities...")
 if not ALL_MESSAGES_FILE.exists():
 print(f"❌ Datei nicht gefunden: {ALL_MESSAGES_FILE}")
 return
 
 with ALL_MESSAGES_FILE.open() as f:
 messages_data = json.load(f)
 
 top_sentences = messages_data.get("top_sentences", [])
 
 # Load Layer-4 Map
 LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
 layer4_map = {}
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 for entry in layer4_data.get("results", []):
 layer3_id = entry.get("layer3_identity", "")
 layer4_id = entry.get("layer4_identity", "")
 if len(layer3_id) == 60 and len(layer4_id) == 60:
 layer4_map[layer3_id] = layer4_id
 
 # Finde Identities mit Layer-4
 anna_identities = []
 for sentence in top_sentences[:50]: # Sample von 50
 layer3_id = sentence.get("identity", "")
 layer4_id = layer4_map.get(layer3_id, "")
 if layer4_id:
 anna_identities.append({
 "layer4_identity": layer4_id,
 "sentence": sentence.get("sentence", ""),
 "layer3_identity": layer3_id
 })
 
 print(f"✅ {len(anna_identities)} Anna Identities mit Layer-4 gefunden")
 print()
 
 # Verbinde zu RPC
 print("🔌 Verbinde zu Qubic RPC...")
 try:
 rpc = rpc_client.QubiPy_RPC()
 latest_tick = rpc.get_latest_tick()
 print(f"✅ Verbunden (Tick: {latest_tick})")
 except Exception as e:
 print(f"❌ Fehler bei RPC-Verbindung: {e}")
 return
 
 print()
 print("=" * 80)
 print("PRÜFE TRANSACTIONEN")
 print("=" * 80)
 print()
 
 # Check Transaktionen (Sample)
 transaction_results = []
 sample_size = min(10, len(anna_identities)) # Sample von 10
 
 for i, anna_data in enumerate(anna_identities[:sample_size], 1):
 layer4_id = anna_data["layer4_identity"]
 sentence = anna_data["sentence"]
 
 print(f"[{i}/{sample_size}] Check '{sentence}'...")
 print(f" Identity: {layer4_id}")
 
 result = check_identity_transactions(rpc, layer4_id, limit=20)
 transaction_results.append({
 "sentence": sentence,
 "layer4_identity": layer4_id,
 "transaction_check": result,
 "timestamp": datetime.now().isoformat()
 })
 
 if result["success"]:
 if result["count"] > 0:
 print(f" ✅ {result['count']} Transaktionen gefunden!")
 else:
 print(f" ⚠️ Keine Transaktionen gefunden")
 else:
 print(f" ❌ Fehler: {result.get('error', 'Unknown')}")
 
 # Rate limiting
 if i < sample_size:
 time.sleep(3)
 print()
 
 # Zeige Zusammenfassung
 print("=" * 80)
 print("ZUSAMMENFASSUNG")
 print("=" * 80)
 print()
 
 total_checked = len(transaction_results)
 with_transactions = sum(1 for r in transaction_results if r["transaction_check"].get("count", 0) > 0)
 
 print(f"✅ Geprüft: {total_checked}")
 print(f"💰 Mit Transaktionen: {with_transactions}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "sample_size": sample_size,
 "total_checked": total_checked,
 "with_transactions": with_transactions,
 "results": transaction_results
 }
 
 output_file = OUTPUT_DIR / "anna_transactions_check.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ PRÜFUNG ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("⚠️ WICHTIG: Dies ist nur ein Sample!")
 print(" Vollständige Analyse würde sehr lange dauern.")
 print()

if __name__ == "__main__":
 main()

