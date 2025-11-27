#!/usr/bin/env python3
"""
Gemini Complete Test - Testet ALLE Transformationen und validiert sie
"""

import json
import sys
import subprocess
from pathlib import Path
import numpy as np
import openpyxl

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def derive_identity_venv(seed: str) -> tuple[bool, str]:
 """Derive identity from seed using venv-tx."""
 script = f'''
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)
seed = "{seed}"
seed_bytes = seed.encode("utf-8")
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
'''
 
 if not VENV_PYTHON.exists():
 return False, "venv-tx not found"
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), '-c', script],
 capture_output=True,
 text=True,
 timeout=30,
 cwd=project_root
 )
 
 if result.returncode == 0 and result.stdout.strip():
 identity = result.stdout.strip()
 if len(identity) == 60:
 return True, identity
 else:
 return False, f"Invalid identity length: {len(identity)}"
 else:
 return False, result.stderr.strip() or "Execution failed"
 except Exception as e:
 return False, str(e)

def check_identity_onchain_venv(identity: str) -> dict:
 """Check identity on-chain using venv-tx."""
 script = f'''
from qubipy.rpc import rpc_client
import json
identity = "{identity}"
try:
 rpc = rpc_client.QubiPy_RPC()
 balance_data = rpc.get_balance(identity)
 if balance_data:
 result = {{
 "exists": True,
 "balance": balance_data.get("balance", 0),
 "validForTick": balance_data.get("validForTick"),
 }}
 else:
 result = {{"exists": False}}
 print(json.dumps(result))
except Exception as e:
 print(json.dumps({{"exists": False, "error": str(e)}}))
'''
 
 if not VENV_PYTHON.exists():
 return {"exists": False, "error": "venv-tx not found"}
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), '-c', script],
 capture_output=True,
 text=True,
 timeout=30,
 cwd=project_root
 )
 
 if result.returncode == 0 and result.stdout.strip():
 return json.loads(result.stdout.strip())
 else:
 return {"exists": False, "error": result.stderr.strip() or "Execution failed"}
 except Exception as e:
 return {"exists": False, "error": str(e)}

def main():
 """Main function."""
 print("=" * 80)
 print("GEMINI COMPLETE TEST - ALL TRANSFORMATIONS")
 print("=" * 80)
 print()
 
 if not VENV_PYTHON.exists():
 print("❌ venv-tx not found!")
 print(f" Expected: {VENV_PYTHON}")
 return
 
 print(f"Using: {VENV_PYTHON}")
 print()
 
 # Load matrix
 print("1. Loading matrix...")
 matrix_path = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
 wb = openpyxl.load_workbook(matrix_path, data_only=True)
 ws = wb.active
 
 matrix = []
 for row in ws.iter_rows(min_row=1, max_row=128, min_col=1, max_col=128, values_only=True):
 row_values = []
 for cell in row:
 if cell is None:
 row_values.append(0.0)
 elif isinstance(cell, (int, float)):
 row_values.append(float(cell))
 else:
 row_values.append(0.0)
 matrix.append(row_values)
 
 matrix = np.array(matrix)
 print(f" ✅ Matrix loaded: {matrix.shape}")
 print()
 
 # Load test data
 print("2. Loading test data...")
 seeds_file = project_root / "github_export" / "100_seeds_and_identities.json"
 with seeds_file.open() as f:
 data = json.load(f)
 
 if isinstance(data, dict) and "seeds_and_identities" in data:
 test_data = data["seeds_and_identities"]
 else:
 test_data = data if isinstance(data, list) else []
 
 first_item = test_data[0]
 documented_identity = first_item.get("identity", "")
 documented_seed = first_item.get("seed", "")
 
 print(f" ✅ Target Identity: {documented_identity[:40]}...")
 print(f" ✅ Documented Seed: {documented_seed[:40]}...")
 print()
 
 # Get coordinates
 print("3. Getting coordinates...")
 base_row = 0
 coords = []
 for block in range(4):
 row_offset = base_row + (block // 2) * 16
 col_offset = (block % 2) * 16
 for j in range(14):
 row = row_offset + j
 col = col_offset + j
 if row < 128 and col < 128:
 coords.append((row, col))
 
 # Extract raw values
 raw_vals = []
 for i, (r, c) in enumerate(coords[:55]):
 raw_vals.append(float(matrix[r, c]))
 
 print(f" ✅ Extracted {len(raw_vals)} raw values")
 print()
 
 # Test ALL transformations
 print("4. Testing ALL transformations...")
 print()
 
 transformations = [
 ("Raw % 26", lambda v: int(v) % 26),
 ("Raw + 1 % 26", lambda v: (int(v) + 1) % 26),
 ("Raw - 1 % 26", lambda v: (int(v) - 1) % 26),
 ("Raw (Absolute) % 26", lambda v: abs(int(v)) % 26),
 ("Raw + 14 % 26", lambda v: (int(v) + 14) % 26),
 ("Raw + Index % 26", lambda v, i: (int(v) + i) % 26),
 ("Raw - Index % 26", lambda v, i: (int(v) - i) % 26),
 ("Raw + 26 % 26", lambda v: (int(v) + 26) % 26),
 ("Raw - 26 % 26", lambda v: (int(v) - 26) % 26),
 ("Raw mod 26 (floor)", lambda v: int(np.floor(v)) % 26),
 ("Raw mod 26 (ceil)", lambda v: int(np.ceil(v)) % 26),
 ("Raw * 2 % 26", lambda v: (int(v) * 2) % 26),
 ("Raw / 2 % 26", lambda v: int(v / 2) % 26 if v != 0 else 0),
 ("Raw XOR 13 % 26", lambda v: (int(v) ^ 13) % 26),
 ("Raw + 7 % 26", lambda v: (int(v) + 7) % 26),
 ("Raw - 7 % 26", lambda v: (int(v) - 7) % 26),
 ("Raw + 13 % 26", lambda v: (int(v) + 13) % 26),
 ("Raw - 13 % 26", lambda v: (int(v) - 13) % 26),
 ]
 
 results = []
 import inspect
 
 for i, (name, func) in enumerate(transformations, 1):
 print(f"[{i}/{len(transformations)}] {name}...")
 sys.stdout.flush()
 
 try:
 if len(inspect.signature(func).parameters) == 2:
 indices = [func(v, i) % 26 for i, v in enumerate(raw_vals)]
 else:
 indices = [func(v) % 26 for v in raw_vals]
 
 seed_candidate = "".join(chr(ord('a') + (i % 26)) for i in indices)
 
 # Derive identity
 success, identity = derive_identity_venv(seed_candidate)
 
 if not success:
 print(f" ❌ Derivation failed: {identity}")
 results.append({
 "method": name,
 "seed": seed_candidate,
 "error": identity
 })
 print()
 continue
 
 # Check match
 match = (identity == documented_identity)
 
 # Check on-chain
 onchain = check_identity_onchain_venv(identity)
 
 status = "✅ MATCH!" if match else "❌"
 onchain_status = "✅ ON-CHAIN" if onchain.get("exists") else "❌ NOT ON-CHAIN"
 
 print(f" {status} {onchain_status}")
 if match:
 print(f" 🎉 THIS IS THE ONE!")
 if onchain.get("exists"):
 print(f" Balance: {onchain.get('balance', 'N/A')} QU")
 
 results.append({
 "method": name,
 "seed": seed_candidate,
 "derived_identity": identity,
 "match": match,
 "onchain": onchain
 })
 
 if match:
 print()
 print("=" * 80)
 print("🎉 MATCH FOUND!")
 print("=" * 80)
 print(f"Method: {name}")
 print(f"Seed: {seed_candidate}")
 print(f"Identity: {identity}")
 print()
 break
 
 print()
 
 except Exception as e:
 print(f" ❌ Error: {e}")
 print()
 results.append({
 "method": name,
 "error": str(e)
 })
 
 # Save results
 output_file = project_root / "outputs" / "derived" / "gemini_complete_test.json"
 output_file.parent.mkdir(parents=True, exist_ok=True)
 
 with output_file.open("w") as f:
 json.dump({
 "target_identity": documented_identity,
 "target_seed": documented_seed,
 "total_tested": len(transformations),
 "matches_found": sum(1 for r in results if r.get("match")),
 "onchain_count": sum(1 for r in results if r.get("onchain", {}).get("exists")),
 "results": results
 }, f, indent=2)
 
 print("=" * 80)
 print("TEST COMPLETE")
 print("=" * 80)
 print(f"✅ Results saved to: {output_file}")
 print()
 
 # Summary
 matches = [r for r in results if r.get("match")]
 onchain = [r for r in results if r.get("onchain", {}).get("exists")]
 
 print(f"Summary:")
 print(f" Matches: {len(matches)}/{len(transformations)}")
 print(f" On-Chain: {len(onchain)}/{len(transformations)}")
 
 if matches:
 print()
 print("🎉 MATCHES FOUND!")
 for match in matches:
 print(f" - {match.get('method')}: {match.get('seed')[:40]}...")
 elif onchain:
 print()
 print("⚠️ No matches, but found on-chain identities:")
 for item in onchain[:5]:
 print(f" - {item.get('method')}: {item.get('derived_identity')[:40]}... (Balance: {item.get('onchain', {}).get('balance', 'N/A')} QU)")

if __name__ == "__main__":
 main()

