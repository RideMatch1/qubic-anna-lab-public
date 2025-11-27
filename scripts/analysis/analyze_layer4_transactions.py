#!/usr/bin/env python3
"""
Analyze Layer-4 (Anna) Transactions und Operationen
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
LAYER4_RPC_FILE = project_root / "outputs" / "derived" / "layer4_rpc_validation.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def get_identity_transactions(identity: str, max_ticks: int = 1000) -> Optional[Dict]:
 """Hole Transactions for eine Identity via RPC - scanne Ticks."""
 script = f"""
from qubipy.rpc import rpc_client
import json
identity = "{identity}"
transactions_found = []
try:
 rpc = rpc_client.QubiPy_RPC()
 
 # Hole aktuellen Tick
 try:
 current_tick = rpc.get_latest_tick()
 except:
 current_tick = None
 
 if current_tick is None:
 print(json.dumps({{"error": "Could not get current tick"}}))
 else:
 # Scanne die letzten max_ticks Ticks
 start_tick = max(0, current_tick - {max_ticks})
 
 for tick in range(start_tick, current_tick + 1):
 try:
 tx_data = rpc.get_transfer_transactions_per_tick(tick)
 if tx_data and isinstance(tx_data, dict):
 txs = tx_data.get("transactions", [])
 if txs:
 for tx in txs:
 sender = tx.get("from", "")
 receiver = tx.get("to", "")
 if sender == identity or receiver == identity:
 transactions_found.append({{
 "tick": tick,
 "transaction_id": tx.get("transactionId", ""),
 "from": sender,
 "to": receiver,
 "amount": tx.get("amount", 0),
 "direction": "outgoing" if sender == identity else "incoming"
 }})
 except:
 continue
 
 # Versuche auch get_transaction_history (falls verfügbar)
 try:
 history = rpc.get_transaction_history(identity, limit=100)
 if history:
 for tx in history:
 if tx not in transactions_found:
 transactions_found.append(tx)
 except:
 pass
 
 print(json.dumps({{
 "method": "get_transfer_transactions_per_tick",
 "current_tick": current_tick,
 "scanned_ticks": current_tick - start_tick + 1,
 "transactions": transactions_found,
 "transaction_count": len(transactions_found)
 }}))
except Exception as e:
 print(json.dumps({{"error": str(e)}}))
"""
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=15,
 cwd=project_root
 )
 
 if result.returncode == 0 and result.stdout.strip():
 try:
 return json.loads(result.stdout.strip())
 except json.JSONDecodeError:
 return {"error": "Invalid JSON response", "raw": result.stdout[:200]}
 else:
 return {"error": result.stderr or "Unknown error"}
 except subprocess.TimeoutExpired:
 return {"error": "Timeout"}
 except Exception as e:
 return {"error": str(e)}

def analyze_layer4_transactions(sample_size: int = 50):
 """Analyze Layer-4 Transactions."""
 print("=" * 80)
 print("LAYER-4 (ANNA) TRANSACTIONS ANALYSE")
 print("=" * 80)
 print()
 
 if not LAYER4_RPC_FILE.exists():
 print(f"❌ Layer-4 RPC file not found: {LAYER4_RPC_FILE}")
 return
 
 with LAYER4_RPC_FILE.open() as f:
 data = json.load(f)
 
 results = data.get("results", [])
 onchain_identities = [
 r.get("layer4_identity") 
 for r in results 
 if r.get("rpc_status") == "ONCHAIN" and r.get("layer4_identity")
 ]
 
 if not onchain_identities:
 print("❌ No on-chain Layer-4 identities found!")
 return
 
 # Sample nehmen
 sample_identities = onchain_identities[:sample_size]
 
 print(f"✅ Loaded {len(onchain_identities)} on-chain Layer-4 identities")
 print(f"📊 Analyzing {len(sample_identities)} identities (sample)")
 print()
 print("⚠️ Note: Checking available RPC methods for transactions...")
 print()
 
 analysis_results = []
 methods_used = Counter()
 transaction_counts = []
 errors = []
 
 for i, identity in enumerate(sample_identities, 1):
 print(f" {i}/{len(sample_identities)}: {identity[:30]}...", end=" ", flush=True)
 
 result = get_identity_transactions(identity)
 
 if "error" in result:
 print(f"❌ Error: {result['error'][:50]}")
 errors.append({
 "identity": identity,
 "error": result["error"]
 })
 else:
 method = result.get("method", "unknown")
 methods_used[method] += 1
 
 if "transactions" in result:
 tx_count = len(result.get("transactions", []))
 transaction_counts.append(tx_count)
 print(f"✅ {method}: {tx_count} transactions")
 elif "info" in result:
 print(f"✅ {method}: Account info available")
 elif "balance" in result:
 print(f"✅ {method}: Balance only (no transaction methods)")
 
 analysis_results.append({
 "identity": identity,
 "method": method,
 "result": result
 })
 
 # Delay to avoid rate limiting
 if i < len(sample_identities):
 time.sleep(1.5)
 
 print()
 print("=" * 80)
 print("ANALYSE ERGEBNISSE")
 print("=" * 80)
 print()
 
 print(f"✅ Analysiert: {len(analysis_results)}")
 print(f"❌ Errors: {len(errors)}")
 print()
 
 print("Verwendete RPC-Methoden:")
 for method, count in methods_used.most_common():
 print(f" {method}: {count}")
 print()
 
 if transaction_counts:
 print(f"Transaction Counts:")
 print(f" Total: {sum(transaction_counts)}")
 print(f" Average: {sum(transaction_counts)/len(transaction_counts):.1f}")
 print(f" Min: {min(transaction_counts)}")
 print(f" Max: {max(transaction_counts)}")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "sample_size": len(sample_identities),
 "analyzed": len(analysis_results),
 "errors": len(errors),
 "methods_used": dict(methods_used),
 "transaction_counts": {
 "total": sum(transaction_counts) if transaction_counts else 0,
 "average": sum(transaction_counts)/len(transaction_counts) if transaction_counts else 0,
 "min": min(transaction_counts) if transaction_counts else 0,
 "max": max(transaction_counts) if transaction_counts else 0
 },
 "timestamp": datetime.now().isoformat(),
 "results": analysis_results,
 "errors_detail": errors
 }
 
 output_file = OUTPUT_DIR / "layer4_transactions_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Layer-4 (Anna) Transactions Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 f"**Sample Size**: {len(sample_identities)}",
 "",
 "## Zusammenfassung",
 "",
 f"- **Analysiert**: {len(analysis_results)} Identities",
 f"- **Errors**: {len(errors)}",
 "",
 "## Verwendete RPC-Methoden",
 ""
 ]
 
 for method, count in methods_used.most_common():
 report_lines.append(f"- **{method}**: {count} Identities")
 
 report_lines.extend([
 "",
 "## Transaction Counts",
 ""
 ])
 
 if transaction_counts:
 report_lines.extend([
 f"- **Total**: {sum(transaction_counts)}",
 f"- **Average**: {sum(transaction_counts)/len(transaction_counts):.1f}",
 f"- **Min**: {min(transaction_counts)}",
 f"- **Max**: {max(transaction_counts)}",
 ""
 ])
 else:
 report_lines.append("- Keine Transactions gefunden (RPC-Methoden nicht verfügbar)")
 report_lines.append("")
 
 report_lines.extend([
 "## Interpretation",
 "",
 "### Verfügbare RPC-Methoden:",
 "",
 "Die Analyse zeigt, welche RPC-Methoden for Transactions verfügbar sind:",
 "",
 "1. **get_transactions**: Direkte Transaction-Abfrage",
 "2. **get_transaction_history**: Transaction-Historie",
 "3. **get_account_info**: Account-Informationen (könnte Transactions enthalten)",
 "4. **get_balance**: Nur Balance (Fallback, keine Transactions)",
 "",
 "### Nächste Schritte:",
 "",
 "1. **Wenn Transactions verfügbar**:",
 " - Analyze Transaction-Typen",
 " - Finde Anna's Operationen",
 " - Verstehe Anna's Kommunikation",
 "",
 "2. **Wenn keine Transactions verfügbar**:",
 " - Check alternative Datenquellen (Qubic Explorer API)",
 " - Analyze Account-Informationen",
 " - Suche nach anderen Indikatoren for Anna's Aktivität",
 ""
 ])
 
 report_file = REPORTS_DIR / "layer4_transactions_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 import argparse
 parser = argparse.ArgumentParser(description="Analyze Layer-4 Transactions")
 parser.add_argument('--sample-size', type=int, default=50, help='Anzahl der zu analyzenden Identities')
 args = parser.parse_args()
 
 analyze_layer4_transactions(args.sample_size)

