#!/usr/bin/env python3
"""
Scan Smart Contracts for Identity Connections

Prüft ob die Matrix-Identities mit Smart Contracts verbunden sind.
Könnte Genesis Token, Rewards, etc. enthalten.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
import subprocess

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def load_onchain_identities() -> List[str]:
 """Load alle on-chain Identities."""
 identities = []
 
 # Versuche verschiedene Quellen
 complete_file = OUTPUT_DIR / "checksum_identities_onchain_validation_complete.json"
 if complete_file.exists():
 with complete_file.open() as f:
 data = json.load(f)
 # Load aus Batches
 num_batches = data.get("total_batches", 0)
 for i in range(num_batches):
 batch_file = OUTPUT_DIR / f"onchain_identities_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch_data = json.load(f)
 if isinstance(batch_data, list):
 identities.extend(batch_data)
 
 # Fallback: Load aus 100_seeds_and_identities.json
 if not identities:
 seeds_file = project_root / "github_export" / "100_seeds_and_identities.json"
 if seeds_file.exists():
 with seeds_file.open() as f:
 data = json.load(f)
 for item in data.get("seeds_and_identities", []):
 identities.append(item["identity"])
 
 return identities[:100] # Limit for Test

def check_identity_assets(identity: str) -> Optional[Dict]:
 """Check Assets einer Identity."""
 if not VENV_PYTHON.exists():
 return None
 
 script = f"""
from qubipy.rpc import rpc_client
identity = "{identity}"
try:
 rpc = rpc_client.QubiPy_RPC()
 balance_data = rpc.get_balance(identity)
 if balance_data:
 assets = balance_data.get('assets', [])
 print(f"BALANCE:{{balance_data.get('balance', 0)}}")
 print(f"ASSETS:{{len(assets)}}")
 for asset in assets:
 print(f"ASSET:{{asset.get('assetCode', 'N/A')}}|{{asset.get('amount', 0)}}")
 else:
 print("NOT_FOUND")
except Exception as e:
 print(f"ERROR:{{e}}")
"""
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 
 if result.returncode == 0:
 assets = []
 balance = 0
 
 for line in result.stdout.split('\n'):
 if line.startswith('BALANCE:'):
 balance = int(line.split(':', 1)[1].strip())
 elif line.startswith('ASSET:'):
 parts = line.split(':', 1)[1].split('|')
 if len(parts) == 2:
 assets.append({
 "assetCode": parts[0],
 "amount": int(parts[1])
 })
 
 return {
 "identity": identity,
 "balance": balance,
 "assets": assets,
 "has_assets": len(assets) > 0
 }
 return None
 except Exception:
 return None

def check_identity_transactions(identity: str, limit: int = 10) -> Optional[Dict]:
 """Check Transaktionen einer Identity."""
 if not VENV_PYTHON.exists():
 return None
 
 script = f"""
from qubipy.rpc import rpc_client
identity = "{identity}"
try:
 rpc = rpc_client.QubiPy_RPC()
 # Versuche Transaktionen zu bekommen
 # Note: RPC might not have direct transaction history
 print("TRANSACTIONS:0")
except Exception as e:
 print(f"ERROR:{{e}}")
"""
 
 # Placeholder - RPC might not support transaction history directly
 return {
 "identity": identity,
 "transaction_count": 0,
 "note": "Transaction history not available via RPC"
 }

def main():
 print("=" * 80)
 print("SCAN SMART CONTRACTS FOR IDENTITY CONNECTIONS")
 print("=" * 80)
 print()
 
 print("Loading on-chain identities...")
 identities = load_onchain_identities()
 print(f"✅ Loaded {len(identities)} identities")
 print()
 
 print("Scanning identities for assets and contract connections...")
 print("(This may take a while...)")
 print()
 
 results = []
 identities_with_assets = 0
 
 for idx, identity in enumerate(identities, 1):
 if idx % 10 == 0:
 print(f"Progress: {idx}/{len(identities)} ({idx/len(identities)*100:.1f}%)")
 
 asset_data = check_identity_assets(identity)
 
 if asset_data:
 results.append(asset_data)
 if asset_data.get("has_assets"):
 identities_with_assets += 1
 print(f" ✅ {identity[:40]}... has {len(asset_data['assets'])} asset(s)")
 for asset in asset_data['assets']:
 print(f" - {asset['assetCode']}: {asset['amount']}")
 
 print()
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 print(f"Total identities scanned: {len(identities)}")
 print(f"Identities with assets: {identities_with_assets}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 output_file = OUTPUT_DIR / "smart_contract_identity_scan.json"
 with output_file.open('w') as f:
 json.dump({
 "total_scanned": len(identities),
 "identities_with_assets": identities_with_assets,
 "results": results
 }, f, indent=2)
 print(f"✅ Results saved to: {output_file}")
 
 # Report
 report_file = REPORTS_DIR / "smart_contract_identity_scan_report.md"
 with report_file.open('w') as f:
 f.write("# Smart Contract Identity Scan Report\n\n")
 f.write("## Overview\n\n")
 f.write(f"Scanned {len(identities)} identities for assets and contract connections.\n\n")
 f.write("## Results\n\n")
 f.write(f"- **Total scanned**: {len(identities)}\n")
 f.write(f"- **Identities with assets**: {identities_with_assets}\n\n")
 
 if identities_with_assets > 0:
 f.write("## Identities with Assets\n\n")
 for result in results:
 if result.get("has_assets"):
 f.write(f"### {result['identity']}\n\n")
 f.write(f"- Balance: {result['balance']} QU\n")
 f.write(f"- Assets:\n")
 for asset in result['assets']:
 f.write(f" - {asset['assetCode']}: {asset['amount']}\n")
 f.write("\n")
 else:
 f.write("No identities with assets found.\n\n")
 
 print(f"✅ Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("SCAN COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

