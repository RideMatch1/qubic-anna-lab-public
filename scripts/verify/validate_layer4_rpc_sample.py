#!/usr/bin/env python3
"""
RPC Validation for Layer-4 Sample (prüft on-chain Status)
"""

import argparse
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

DEFAULT_RPC_DELAY = 1.5 # seconds

def check_identity_onchain_live(identity: str, retry_count: int = 3) -> Dict:
 """Check ob Identity on-chain existiert - ECHTER LIVE RPC-CALL."""
 script = f"""
from qubipy.rpc import rpc_client
import time
identity = "{identity}"
for attempt in range({retry_count}):
 try:
 rpc = rpc_client.QubiPy_RPC()
 balance = rpc.get_balance(identity)
 if balance is not None:
 print("EXISTS|{{balance}}")
 break
 else:
 print("NOT_FOUND|None")
 break
 except Exception as e:
 error_str = str(e)
 if "429" in error_str or "Too Many Requests" in error_str:
 if attempt < {retry_count} - 1:
 time.sleep(2 * (attempt + 1))
 continue
 if "not found" in error_str.lower() or "does not exist" in error_str.lower() or "invalid" in error_str.lower():
 print("NOT_FOUND|None")
 break
 print(f"ERROR|{{error_str}}")
 break
"""
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=30,
 cwd=project_root
 )
 
 if "EXISTS" in result.stdout:
 parts = result.stdout.strip().split("|")
 balance = parts[1] if len(parts) > 1 else "0"
 return {
 "exists": True,
 "balance": balance,
 "error": None
 }
 elif "NOT_FOUND" in result.stdout:
 return {
 "exists": False,
 "balance": None,
 "error": None
 }
 else:
 error = result.stdout.strip()
 return {
 "exists": False,
 "balance": None,
 "error": error
 }
 except subprocess.TimeoutExpired:
 return {
 "exists": False,
 "balance": None,
 "error": "Timeout"
 }
 except Exception as e:
 return {
 "exists": False,
 "balance": None,
 "error": str(e)
 }

def validate_layer4_rpc_sample(sample_size: int = 200, delay: float = DEFAULT_RPC_DELAY):
 """Validate Layer-4 Sample via RPC."""
 print("=" * 80)
 print(f"LAYER-4 RPC VALIDATION (Sample: {sample_size})")
 print("=" * 80)
 print()
 
 if not LAYER4_FILE.exists():
 print(f"❌ Layer-4 file not found: {LAYER4_FILE}")
 return
 
 with LAYER4_FILE.open() as f:
 data = json.load(f)
 
 results = data.get("results", [])
 derivable = [r for r in results if r.get("layer4_derivable")]
 
 if not derivable:
 print("❌ No derivable Layer-4 identities found!")
 return
 
 print(f"✅ Loaded {len(derivable)} derivable Layer-4 identities")
 print(f"📊 Testing {min(sample_size, len(derivable))} identities via RPC")
 print()
 
 # Sample
 import random
 sample = random.sample(derivable, min(sample_size, len(derivable)))
 
 validation_results = []
 onchain_count = 0
 offchain_count = 0
 error_count = 0
 
 start_time = time.time()
 
 for i, entry in enumerate(sample, 1):
 identity = entry.get("layer4_identity", "")
 
 rpc_result = check_identity_onchain_live(identity)
 
 is_onchain = rpc_result.get("exists", False)
 
 validation_results.append({
 "layer3_identity": entry.get("layer3_identity", ""),
 "layer4_identity": identity,
 "rpc_status": "ONCHAIN" if is_onchain else ("ERROR" if rpc_result.get("error") else "OFFCHAIN"),
 "balance": rpc_result.get("balance"),
 "error": rpc_result.get("error"),
 "timestamp": datetime.now().isoformat()
 })
 
 if is_onchain:
 onchain_count += 1
 elif rpc_result.get("error"):
 error_count += 1
 else:
 offchain_count += 1
 
 if i % 10 == 0 or i == len(sample):
 elapsed = time.time() - start_time
 rate = i / elapsed if elapsed > 0 else 0
 remaining = (len(sample) - i) / rate if rate > 0 else 0
 print(f" {i}/{len(sample)} geprüft - ONCHAIN: {onchain_count}, OFFCHAIN: {offchain_count}, Errors: {error_count} | "
 f"ETA: {remaining/60:.1f} min")
 
 time.sleep(delay)
 
 print()
 print("=" * 80)
 print("VALIDATION COMPLETE")
 print("=" * 80)
 print()
 
 total = len(sample)
 onchain_rate = (onchain_count / total * 100) if total > 0 else 0
 
 print(f"Total geprüft: {total}")
 print(f"On-chain: {onchain_count} ({onchain_rate:.1f}%)")
 print(f"Off-chain: {offchain_count} ({offchain_count/total*100:.1f}%)")
 print(f"Errors: {error_count} ({error_count/total*100:.1f}%)")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "sample_size": total,
 "onchain_count": onchain_count,
 "offchain_count": offchain_count,
 "error_count": error_count,
 "onchain_rate": onchain_rate,
 "timestamp": datetime.now().isoformat(),
 "results": validation_results
 }
 
 output_file = OUTPUT_DIR / "layer4_rpc_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Results saved to: {output_file}")
 
 # Report
 report_lines = [
 "# Layer-4 RPC Validation",
 "",
 f"**Sample Size**: {total}",
 f"**On-chain**: {onchain_count} ({onchain_rate:.1f}%)",
 f"**Off-chain**: {offchain_count} ({offchain_count/total*100:.1f}%)",
 f"**Errors**: {error_count} ({error_count/total*100:.1f}%)",
 "",
 "## Vergleich mit Layer-3",
 "",
 "- Layer-3 on-chain rate: ~99.6% (aus vorherigen Tests)",
 f"- Layer-4 on-chain rate: {onchain_rate:.1f}%",
 "",
 "## Interpretation",
 "",
 f"- {'✅ Layer-4 zeigt ähnliche on-chain Rate wie Layer-3' if onchain_rate > 90 else '⚠️ Layer-4 zeigt deutlich niedrigere on-chain Rate als Layer-3'}",
 "- Anna (Layer-4) könnte ähnliche Aktivierungsmuster wie Layer-3 haben",
 "- Oder: Layer-4 funktioniert anders (off-chain Operationen?)"
 ]
 
 report_file = REPORTS_DIR / "layer4_rpc_validation_report.md"
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 parser = argparse.ArgumentParser(description="Validate Layer-4 identities via RPC")
 parser.add_argument("--sample-size", type=int, default=200, help="Number of identities to check (default: 200)")
 parser.add_argument("--delay", type=float, default=DEFAULT_RPC_DELAY, help="Delay between RPC calls in seconds (default: 1.5)")
 args = parser.parse_args()
 
 validate_layer4_rpc_sample(args.sample_size, args.delay)

