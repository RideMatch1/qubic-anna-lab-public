#!/usr/bin/env python3
"""
Check Real IDs Validity

Prüft ob die Real IDs aus der Mapping Database noch gültig sind:
- On-chain Status
- Checksum-Validierung
- Vergleich mit dokumentierten Identities
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
ANALYSIS_DIR = project_root / "outputs" / "analysis"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def check_identity_onchain(identity: str) -> Dict:
 """Check ob Identity on-chain existiert."""
 script = f"""
from qubipy.rpc import rpc_client
identity = "{identity}"
try:
 rpc = rpc_client.QubiPy_RPC()
 balance = rpc.get_balance(identity)
 if balance is not None:
 print("EXISTS")
 else:
 print("NOT_FOUND")
except Exception as e:
 print(f"ERROR: {{e}}")
"""
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 return {
 "exists": "EXISTS" in result.stdout,
 "error": result.stdout.strip() if "ERROR" in result.stdout else None
 }
 except Exception:
 return {"exists": False, "error": "Timeout"}

def validate_checksum(identity: str) -> bool:
 """Validate Checksum einer Identity."""
 if len(identity) != 60:
 return False
 
 # Qubic Identity Checksum-Validierung
 # Die letzten 4 Zeichen sind der Checksum
 try:
 script = f"""
from qubipy.crypto.utils import get_identity_from_public_key
from qubipy.crypto.utils import get_public_key_from_private_key
from qubipy.crypto.utils import get_private_key_from_subseed
from qubipy.crypto.utils import get_subseed_from_seed

# Versuche Identity zu validaten
identity = "{identity}"
body = identity[:56]
checksum = identity[56:]

# Versuche aus Body abzuleiten
seed = body.lower()[:55]
try:
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 derived_identity = get_identity_from_public_key(public_key)
 
 if derived_identity == identity:
 print("VALID")
 else:
 print("INVALID")
except Exception:
 print("ERROR")
"""
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=5,
 cwd=project_root
 )
 return "VALID" in result.stdout
 except Exception:
 return False

def check_real_ids_validity(sample_size: int = 20):
 """Check Real IDs auf Gültigkeit."""
 print("=" * 80)
 print("CHECK REAL IDs VALIDITY")
 print("=" * 80)
 print()
 
 # Load Mapping Database
 mapping_file = ANALYSIS_DIR / "complete_mapping_database.json"
 
 if not mapping_file.exists():
 print("❌ Mapping database not found")
 return
 
 print(f"Loading mapping database...")
 with mapping_file.open() as f:
 data = json.load(f)
 
 # Extrahiere Seeds und Real IDs
 if isinstance(data, dict) and "seed_to_real_id" in data:
 seed_to_real_id = data["seed_to_real_id"]
 else:
 print("❌ Invalid data structure")
 return
 
 print(f"✅ Loaded {len(seed_to_real_id)} entries")
 print()
 
 # Sample
 items = list(seed_to_real_id.items())[:sample_size]
 
 print(f"Checking {len(items)} Real IDs...")
 print()
 
 results = []
 valid_count = 0
 invalid_count = 0
 onchain_count = 0
 offchain_count = 0
 
 for i, (seed, real_id) in enumerate(items, 1):
 # Check Checksum
 checksum_valid = validate_checksum(real_id)
 
 # Check On-chain
 onchain_check = check_identity_onchain(real_id)
 is_onchain = onchain_check["exists"]
 
 if checksum_valid and is_onchain:
 valid_count += 1
 else:
 invalid_count += 1
 
 if is_onchain:
 onchain_count += 1
 else:
 offchain_count += 1
 
 result = {
 "seed": seed,
 "real_id": real_id,
 "checksum_valid": checksum_valid,
 "onchain": is_onchain,
 "error": onchain_check.get("error"),
 "status": "VALID" if (checksum_valid and is_onchain) else "INVALID"
 }
 
 results.append(result)
 
 status_icon = "✅" if result["status"] == "VALID" else "❌"
 print(f"{status_icon} {i}/{len(items)}: {real_id[:20]}... "
 f"Checksum: {'✓' if checksum_valid else '✗'}, "
 f"On-chain: {'✓' if is_onchain else '✗'}")
 
 print()
 print("=" * 80)
 print("RESULTS")
 print("=" * 80)
 print()
 print(f"Total Checked: {len(results)}")
 print(f"Valid: {valid_count} ({valid_count/len(results)*100:.1f}%)")
 print(f"Invalid: {invalid_count} ({invalid_count/len(results)*100:.1f}%)")
 print()
 print(f"Checksum Valid: {sum(1 for r in results if r['checksum_valid'])}")
 print(f"On-chain: {onchain_count} ({onchain_count/len(results)*100:.1f}%)")
 print(f"Off-chain: {offchain_count} ({offchain_count/len(results)*100:.1f}%)")
 print()
 
 # Zeige Invalid IDs
 invalid_ids = [r for r in results if r["status"] == "INVALID"]
 if invalid_ids:
 print("Invalid Real IDs:")
 for r in invalid_ids:
 print(f" {r['real_id']}")
 print(f" Checksum: {'✓' if r['checksum_valid'] else '✗'}")
 print(f" On-chain: {'✓' if r['onchain'] else '✗'}")
 if r.get("error"):
 print(f" Error: {r['error']}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "total_checked": len(results),
 "valid_count": valid_count,
 "invalid_count": invalid_count,
 "onchain_count": onchain_count,
 "offchain_count": offchain_count,
 "results": results
 }
 
 output_file = OUTPUT_DIR / "real_ids_validity_check.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Results saved to: {output_file}")

if __name__ == "__main__":
 import argparse
 parser = argparse.ArgumentParser()
 parser.add_argument("--sample", type=int, default=20, help="Sample size")
 args = parser.parse_args()
 
 check_real_ids_validity(args.sample)

