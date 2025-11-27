#!/usr/bin/env python3
"""
Validate Seeds with Direct RPC Calls
Nutzt direkte HTTP-RPC-Calls statt Docker/QubiPy
"""

import json
import requests
import sys
from pathlib import Path
from typing import Dict, List, Tuple

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Qubic RPC Endpoints (bekannte Nodes)
RPC_ENDPOINTS = [
 "https://rpc.qubic.li",
 "https://rpc.qubic.network",
 "http://95.217.207.59:21841", # Public node
 "http://88.99.104.28:21841", # Public node
]

def get_identity_from_seed_direct(seed: str) -> Tuple[bool, str]:
 """
 Derive identity from seed using direct cryptographic operations.
 Falls QubiPy lokal verfügbar ist, nutze es. Sonst versuche RPC.
 """
 # Method 1: Try local QubiPy
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
 pass
 
 # Method 2: Try RPC call (if Qubic RPC supports seed derivation)
 # Note: Most RPCs only support balance checks, not derivation
 # So we'll need to use a different approach
 
 return False, "QubiPy not available and RPC doesn't support derivation"

def check_identity_onchain(identity: str) -> Dict:
 """Check if identity exists on-chain using RPC."""
 for endpoint in RPC_ENDPOINTS:
 try:
 # Qubic RPC typically uses JSON-RPC
 payload = {
 "jsonrpc": "2.0",
 "method": "getBalance",
 "params": [identity],
 "id": 1
 }
 
 response = requests.post(
 endpoint,
 json=payload,
 timeout=10,
 headers={"Content-Type": "application/json"}
 )
 
 if response.status_code == 200:
 data = response.json()
 if "result" in data:
 return {
 "exists": True,
 "balance": data.get("result", {}).get("balance", 0),
 "endpoint": endpoint
 }
 except Exception as e:
 continue
 
 return {"exists": False, "error": "No working endpoint"}

def validate_seeds_with_rpc(seeds: List[str], target_identity: str) -> Dict:
 """Validate seeds by deriving identities and checking on-chain."""
 results = {}
 
 # First, try to derive identities
 derived_identities = {}
 
 for i, seed in enumerate(seeds):
 success, identity = get_identity_from_seed_direct(seed)
 if success:
 derived_identities[i] = {
 "seed": seed,
 "derived_identity": identity,
 "match": (identity == target_identity)
 }
 else:
 derived_identities[i] = {
 "seed": seed,
 "error": identity # error message
 }
 
 # Check on-chain status for derived identities
 for i, data in derived_identities.items():
 if "derived_identity" in data:
 identity = data["derived_identity"]
 onchain = check_identity_onchain(identity)
 data["onchain"] = onchain
 
 return derived_identities

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
 print("VALIDATING SEEDS WITH DIRECT RPC")
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
 validation_results = validate_seeds_with_rpc(seeds_to_test, documented_identity)
 
 # Process results
 print("Results:")
 print()
 
 found_match = False
 final_results = []
 
 for i, (seed, method) in enumerate(zip(seeds_to_test, method_names)):
 if i in validation_results:
 result = validation_results[i]
 if "error" in result:
 print(f" {method:<25} -> ERROR: {result['error'][:50]}")
 else:
 identity = result.get("derived_identity", "")
 match = result.get("match", False)
 onchain = result.get("onchain", {})
 status = "✅ MATCH!" if match else "❌"
 onchain_status = "✅ ON-CHAIN" if onchain.get("exists") else "❌ NOT ON-CHAIN"
 
 print(f" {method:<25} -> {identity[:40]}... {status} {onchain_status}")
 
 final_results.append({
 "method": method,
 "seed": seed,
 "derived_identity": identity,
 "match": match,
 "onchain": onchain
 })
 
 if match:
 found_match = True
 print(f"\n🎉 FOUND IT! Method: {method}")
 print(f" Seed: {seed}")
 print(f" Identity: {identity}")
 
 # Save results
 output_file = project_root / "outputs" / "derived" / "gemini_seed_validation_rpc_results.json"
 output_file.parent.mkdir(parents=True, exist_ok=True)
 
 with output_file.open("w") as f:
 json.dump({
 "target_identity": documented_identity,
 "total_tested": len(seeds_to_test),
 "matches_found": sum(1 for r in final_results if r.get("match")),
 "results": final_results
 }, f, indent=2)
 
 print()
 print(f"✅ Results saved to: {output_file}")
 print()
 print("=" * 80)
 print("VALIDATION COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

