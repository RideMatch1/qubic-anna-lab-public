#!/usr/bin/env python3
"""Retry RPC Errors - Check die 4-5 Errors erneut."""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict

project_root = Path(__file__).parent.parent.parent
RPC_RESULTS_FILE = project_root / "outputs" / "derived" / "rpc_sample_results.json"
DERIVED_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def check_identity_onchain(identity: str, retries: int = 3) -> Dict:
 """Check Identity on-chain mit Retry."""
 script = f"""
from qubipy.rpc import rpc_client
import json, time
identity = "{identity}"
for attempt in range({retries}):
 try:
 rpc = rpc_client.QubiPy_RPC()
 balance = rpc.get_balance(identity)
 if balance is not None:
 print(json.dumps({{'status': 'ONCHAIN', 'balance': balance}}))
 break
 else:
 print(json.dumps({{'status': 'NOT_FOUND'}}))
 break
 except Exception as e:
 error_str = str(e)
 if "429" in error_str or "Too Many Requests" in error_str:
 if attempt < {retries} - 1:
 time.sleep(3 * (attempt + 1))
 continue
 if "not found" in error_str.lower() or "does not exist" in error_str.lower():
 print(json.dumps({{'status': 'NOT_FOUND'}}))
 break
 if attempt == {retries} - 1:
 print(json.dumps({{'status': 'ERROR', 'error': error_str}}))
"""
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=45,
 cwd=project_root
 )
 return json.loads(result.stdout.strip())
 except Exception as e:
 return {"status": "ERROR", "error": str(e)}

def main():
 """Retry RPC Errors."""
 if not RPC_RESULTS_FILE.exists():
 print("❌ RPC results file not found")
 return
 
 with RPC_RESULTS_FILE.open() as f:
 rpc_data = json.load(f)
 
 errors = [r for r in rpc_data.get("results", []) if r.get("rpc_status") == "ERROR"]
 
 if not errors:
 print("✅ Keine Errors gefunden!")
 return
 
 print("=" * 80)
 print(f"RETRY RPC ERRORS ({len(errors)} Identities)")
 print("=" * 80)
 print()
 
 results = []
 for i, err_entry in enumerate(errors, 1):
 identity = err_entry.get("identity", "")
 print(f"Retry {i}/{len(errors)}: {identity[:40]}...")
 
 result = check_identity_onchain(identity, retries=5)
 status = result.get("status")
 
 results.append({
 "identity": identity,
 "original_status": "ERROR",
 "retry_status": status,
 "balance": result.get("balance"),
 "error": result.get("error"),
 "timestamp": datetime.now().isoformat()
 })
 
 if status == "ONCHAIN":
 print(f" ✅ On-chain! (Balance: {result.get('balance', 'N/A')})")
 elif status == "NOT_FOUND":
 print(f" ❌ Off-chain")
 else:
 print(f" ⚠️ Error: {result.get('error', 'Unknown')}")
 
 time.sleep(2.0) # Delay zwischen Requests
 
 # Speichere Ergebnisse
 retry_file = DERIVED_DIR / "rpc_error_retry_results.json"
 with retry_file.open("w") as f:
 json.dump({
 "total_errors": len(errors),
 "retried": len(results),
 "timestamp": datetime.now().isoformat(),
 "results": results
 }, f, indent=2)
 
 print()
 print(f"💾 Retry-Ergebnisse gespeichert: {retry_file}")
 
 # Statistik
 onchain_retry = sum(1 for r in results if r.get("retry_status") == "ONCHAIN")
 offchain_retry = sum(1 for r in results if r.get("retry_status") == "NOT_FOUND")
 still_errors = sum(1 for r in results if r.get("retry_status") == "ERROR")
 
 print()
 print("=" * 80)
 print("RETRY ERGEBNISSE")
 print("=" * 80)
 print(f"On-chain: {onchain_retry}/{len(results)}")
 print(f"Off-chain: {offchain_retry}/{len(results)}")
 print(f"Still Errors: {still_errors}/{len(results)}")
 print()
 
 if onchain_retry > 0:
 print(f"✅ {onchain_retry} Errors waren tatsächlich on-chain (Rate-Limiting/Timeout)")
 if offchain_retry > 0:
 print(f"❌ {offchain_retry} Errors waren tatsächlich off-chain")
 if still_errors > 0:
 print(f"⚠️ {still_errors} Errors persistieren")

if __name__ == "__main__":
 main()

