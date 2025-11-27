#!/usr/bin/env python3
"""
Validate Seeds with Docker - Final Version
Nutzt Docker for Identity-Derivation (da QubiPy lokal nicht verfügbar)
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def derive_identity_docker(seed: str) -> Tuple[bool, str]:
 """Derive identity from seed using Docker."""
 # Use inline script to avoid f-string issues
 script = "from qubipy.crypto.utils import get_subseed_from_seed, get_private_key_from_subseed, get_public_key_from_private_key, get_identity_from_public_key; seed = '" + seed + "'; seed_bytes = seed.encode('utf-8'); subseed = get_subseed_from_seed(seed_bytes); private_key = get_private_key_from_subseed(subseed); public_key = get_public_key_from_private_key(private_key); identity = get_identity_from_public_key(public_key); print(identity)"
 
 try:
 result = subprocess.run(
 ['docker', 'run', '--rm', '-v', f'{project_root}:/workspace', '-w', '/workspace',
 'qubic-proof', 'python3', '-c', script],
 capture_output=True,
 text=True,
 timeout=120
 )
 
 if result.returncode == 0 and result.stdout.strip():
 identity = result.stdout.strip()
 if len(identity) == 60:
 return True, identity
 else:
 return False, f"Invalid identity length: {len(identity)}"
 else:
 return False, result.stderr.strip() or "Docker execution failed"
 except subprocess.TimeoutExpired:
 return False, "Docker timeout"
 except Exception as e:
 return False, f"Docker error: {e}"

def check_identity_onchain_docker(identity: str) -> Dict:
 """Check identity on-chain using Docker."""
 # Use inline script to avoid f-string issues
 script = "from qubipy.rpc import rpc_client; import json; identity = '" + identity + "'; rpc = rpc_client.QubiPy_RPC(); balance_data = rpc.get_balance(identity); result = {'exists': True, 'balance': balance_data.get('balance', 0), 'validForTick': balance_data.get('validForTick')} if balance_data else {'exists': False}; print(json.dumps(result))"
 
 try:
 result = subprocess.run(
 ['docker', 'run', '--rm', '-v', f'{project_root}:/workspace', '-w', '/workspace',
 'qubic-proof', 'python3', '-c', script],
 capture_output=True,
 text=True,
 timeout=60
 )
 
 if result.returncode == 0 and result.stdout.strip():
 return json.loads(result.stdout.strip())
 else:
 return {"exists": False, "error": result.stderr.strip() or "Docker execution failed"}
 except subprocess.TimeoutExpired:
 return {"exists": False, "error": "Docker timeout"}
 except Exception as e:
 return {"exists": False, "error": str(e)}

def main():
 """Main function."""
 # Load fast test results
 fast_file = project_root / "outputs" / "derived" / "gemini_raw_value_test_fast.json"
 
 if not fast_file.exists():
 print("❌ Fast test results not found. Run test_gemini_approach_fast.py first.")
 return
 
 with fast_file.open() as f:
 data = json.load(f)
 
 documented_identity = data.get("documented_identity", "")
 results = data.get("results", [])
 
 if not documented_identity:
 print("❌ No documented identity found")
 return
 
 print("=" * 80)
 print("VALIDATING SEEDS WITH DOCKER")
 print("=" * 80)
 print()
 print(f"Target Identity: {documented_identity[:40]}...")
 print()
 
 # Collect all seeds
 seeds_to_test = []
 method_names = []
 for result in results:
 seed = result.get("seed", "")
 if seed and len(seed) == 55:
 seeds_to_test.append(seed)
 method_names.append(result.get("method", ""))
 
 if not seeds_to_test:
 print("❌ No seeds to test!")
 return
 
 print(f"Testing {len(seeds_to_test)} seeds...")
 print()
 
 # Validate
 final_results = []
 
 for i, (seed, method) in enumerate(zip(seeds_to_test, method_names), 1):
 print(f"[{i}/{len(seeds_to_test)}] Testing: {method}")
 print(f" Seed: {seed[:40]}...")
 sys.stdout.flush()
 
 # Derive identity
 print(f" Deriving identity (Docker)...")
 sys.stdout.flush()
 success, identity = derive_identity_docker(seed)
 
 if not success:
 print(f" ❌ Derivation failed: {identity}")
 final_results.append({
 "method": method,
 "seed": seed,
 "error": identity,
 "derivation_method": "docker"
 })
 print()
 continue
 
 print(f" ✅ Derived: {identity[:40]}...")
 
 # Check match
 match = (identity == documented_identity)
 print(f" {'✅ MATCH!' if match else '❌ No match'}")
 
 # Check on-chain
 print(f" Checking on-chain (Docker)...")
 sys.stdout.flush()
 onchain = check_identity_onchain_docker(identity)
 onchain_status = "✅ ON-CHAIN" if onchain.get("exists") else "❌ NOT ON-CHAIN"
 print(f" {onchain_status}")
 
 final_results.append({
 "method": method,
 "seed": seed,
 "derived_identity": identity,
 "match": match,
 "derivation_method": "docker",
 "onchain": onchain
 })
 
 if match:
 print(f"\n🎉 FOUND IT! Method: {method}")
 print(f" Seed: {seed}")
 print(f" Identity: {identity}")
 print()
 break
 
 print()
 
 # Save results
 output_file = project_root / "outputs" / "derived" / "gemini_seed_validation_docker.json"
 output_file.parent.mkdir(parents=True, exist_ok=True)
 
 with output_file.open("w") as f:
 json.dump({
 "target_identity": documented_identity,
 "total_tested": len(seeds_to_test),
 "matches_found": sum(1 for r in final_results if r.get("match")),
 "results": final_results
 }, f, indent=2)
 
 print("=" * 80)
 print("VALIDATION COMPLETE")
 print("=" * 80)
 print(f"✅ Results saved to: {output_file}")
 print()
 
 # Summary
 matches = [r for r in final_results if r.get("match")]
 if matches:
 print(f"🎉 Found {len(matches)} matching seed(s)!")
 else:
 print("❌ No matches found")

if __name__ == "__main__":
 main()

