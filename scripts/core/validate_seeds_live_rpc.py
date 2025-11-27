#!/usr/bin/env python3
"""
Validate Seeds with Live RPC (Multiple Methods)
1. Try local QubiPy
2. Try direct TCP RPC (like 72_live_node_check.py)
3. Fallback to Docker
"""

import json
import socket
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Known Qubic RPC Nodes (from analysis/72_live_node_check.py)
RPC_NODES = [
 {"host": "167.99.139.198", "port": 21841, "label": "nyc-01"},
 {"host": "167.99.253.63", "port": 21841, "label": "nyc-02"},
 {"host": "134.122.69.166", "port": 21841, "label": "ams-01"},
 {"host": "64.226.122.206", "port": 21841, "label": "ams-02"},
 {"host": "45.152.160.217", "port": 21841, "label": "sgp-01"},
]

def send_tcp_rpc(host: str, port: int, payload: dict, timeout: float = 5.0) -> dict:
 """Send JSON-RPC over raw TCP (like 72_live_node_check.py)."""
 data = json.dumps(payload).encode("utf-8") + b"\n"
 try:
 with socket.create_connection((host, port), timeout=timeout) as sock:
 sock.sendall(data)
 raw = sock.makefile().readline()
 return json.loads(raw)
 except Exception as e:
 raise RuntimeError(f"TCP RPC error: {e}")

def get_identity_from_seed_method1_qubipy(seed: str) -> Tuple[bool, str]:
 """Method 1: Try local QubiPy."""
 try:
 from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
 )
 
 seed_bytes = seed.encode('utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 identity = get_identity_from_public_key(public_key)
 return True, identity
 except ImportError:
 return False, "QubiPy not available locally"
 except Exception as e:
 return False, f"QubiPy error: {e}"

def get_identity_from_seed_method2_docker(seed: str) -> Tuple[bool, str]:
 """Method 2: Use Docker."""
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
 
 try:
 result = subprocess.run(
 ['docker', 'run', '--rm', '-v', f'{project_root}:/workspace', '-w', '/workspace',
 'python:3.11', 'bash', '-c', f'pip install -q qubipy && python3 -c """{script}"""'],
 capture_output=True,
 text=True,
 timeout=60
 )
 
 if result.returncode == 0 and result.stdout.strip():
 identity = result.stdout.strip()
 if len(identity) == 60:
 return True, identity
 return False, result.stderr.strip() or "Docker execution failed"
 except subprocess.TimeoutExpired:
 return False, "Docker timeout"
 except Exception as e:
 return False, f"Docker error: {e}"

def get_identity_from_seed(seed: str) -> Tuple[bool, str, str]:
 """Get identity from seed using best available method."""
 # Method 1: Local QubiPy (fastest)
 success, identity = get_identity_from_seed_method1_qubipy(seed)
 if success:
 return True, identity, "local_qubipy"
 
 # Method 2: Docker (slower but reliable)
 success, identity = get_identity_from_seed_method2_docker(seed)
 if success:
 return True, identity, "docker"
 
 return False, identity, "failed" # identity contains error message

def check_identity_onchain_tcp(identity: str) -> Dict:
 """Check identity on-chain using direct TCP RPC."""
 payload = {
 "jsonrpc": "2.0",
 "id": 1,
 "method": "getIdentity",
 "params": {"identity": identity},
 }
 
 for node in RPC_NODES:
 try:
 resp = send_tcp_rpc(node["host"], node["port"], payload, timeout=5.0)
 if "result" in resp:
 return {
 "exists": True,
 "node": node["label"],
 "response": resp.get("result", {})
 }
 except Exception:
 continue
 
 return {"exists": False, "error": "No working node"}

def check_identity_onchain_qubipy(identity: str) -> Dict:
 """Check identity on-chain using QubiPy RPC."""
 try:
 from qubipy.rpc import rpc_client
 rpc = rpc_client.QubiPy_RPC()
 balance_data = rpc.get_balance(identity)
 
 if balance_data:
 return {
 "exists": True,
 "method": "qubipy_rpc",
 "balance": balance_data.get("balance", 0),
 "validForTick": balance_data.get("validForTick"),
 }
 else:
 return {"exists": False, "method": "qubipy_rpc"}
 except ImportError:
 return {"exists": False, "error": "QubiPy not available"}
 except Exception as e:
 return {"exists": False, "error": str(e)}

def check_identity_onchain(identity: str) -> Dict:
 """Check identity on-chain using best available method."""
 # Try QubiPy RPC first (if available)
 result = check_identity_onchain_qubipy(identity)
 if result.get("exists") or "error" not in result:
 return result
 
 # Fallback to direct TCP RPC
 return check_identity_onchain_tcp(identity)

def main():
 """Main function."""
 # Load fast test results
 fast_file = project_root / "outputs" / "derived" / "gemini_raw_value_test_fast.json"
 
 if not fast_file.exists():
 print("❌ Fast test results not found. Run test_gemini_approach_fast.py first.")
 print(" Running it now...")
 import subprocess
 result = subprocess.run(
 [sys.executable, str(project_root / "scripts" / "core" / "test_gemini_approach_fast.py")],
 cwd=project_root,
 capture_output=True,
 text=True
 )
 if result.returncode != 0:
 print(f"❌ Failed to generate test data: {result.stderr}")
 return
 
 if not fast_file.exists():
 print("❌ Test data file still not found after running script")
 return
 
 with fast_file.open() as f:
 data = json.load(f)
 
 documented_identity = data.get("documented_identity", "")
 results = data.get("results", [])
 
 if not documented_identity:
 print("❌ No documented identity found")
 return
 
 print("=" * 80)
 print("VALIDATING SEEDS WITH LIVE RPC (Multiple Methods)")
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
 
 print(f"Testing {len(seeds_to_test)} seeds...")
 print()
 
 # Validate
 final_results = []
 
 for i, (seed, method) in enumerate(zip(seeds_to_test, method_names), 1):
 print(f"[{i}/{len(seeds_to_test)}] Testing: {method}")
 print(f" Seed: {seed[:40]}...")
 
 # Derive identity
 success, identity, derivation_method = get_identity_from_seed(seed)
 
 if not success:
 print(f" ❌ Derivation failed: {identity}")
 final_results.append({
 "method": method,
 "seed": seed,
 "error": identity,
 "derivation_method": derivation_method
 })
 print()
 continue
 
 print(f" ✅ Derived: {identity[:40]}... (via {derivation_method})")
 
 # Check match
 match = (identity == documented_identity)
 print(f" {'✅ MATCH!' if match else '❌ No match'}")
 
 # Check on-chain
 print(f" Checking on-chain...")
 onchain = check_identity_onchain(identity)
 onchain_status = "✅ ON-CHAIN" if onchain.get("exists") else "❌ NOT ON-CHAIN"
 print(f" {onchain_status}")
 
 final_results.append({
 "method": method,
 "seed": seed,
 "derived_identity": identity,
 "match": match,
 "derivation_method": derivation_method,
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
 output_file = project_root / "outputs" / "derived" / "gemini_seed_validation_live_rpc.json"
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

