#!/usr/bin/env python3
"""
Validate Seeds with Docker - Batch Version
Validiert mehrere Seeds in einem Docker-Call (schneller)
"""

import json
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def validate_seeds_batch(seeds: list, target_identity: str) -> dict:
 """Validate multiple seeds in one Docker call."""
 # Create Python script that tests all seeds
 script = f'''
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

target = "{target_identity}"
results = {{}}

seeds = {json.dumps(seeds)}

for i, seed in enumerate(seeds):
 try:
 seed_bytes = seed.encode("utf-8")
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 identity = get_identity_from_public_key(public_key)
 match = (identity == target)
 results[i] = {{"seed": seed, "identity": identity, "match": match}}
 except Exception as e:
 results[i] = {{"seed": seed, "error": str(e)}}

import json
print(json.dumps(results))
'''
 
 try:
 result = subprocess.run(
 ['docker', 'run', '--rm', '-v', f'{project_root}:/workspace', '-w', '/workspace',
 'python:3.11', 'bash', '-c', f'pip install -q qubipy && python3 -c """{script}"""'],
 capture_output=True,
 text=True,
 timeout=180
 )
 
 if result.returncode == 0 and result.stdout.strip():
 return json.loads(result.stdout.strip())
 else:
 return {"error": result.stderr.strip() or "Docker execution failed"}
 except subprocess.TimeoutExpired:
 return {"error": "Docker timeout"}
 except Exception as e:
 return {"error": str(e)}

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
 print("VALIDATING SEEDS WITH DOCKER (Batch)")
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
 
 # Validate in batch
 validation_results = validate_seeds_batch(seeds_to_test, documented_identity)
 
 if "error" in validation_results:
 print(f"❌ Error: {validation_results['error']}")
 return
 
 # Process results
 print("Results:")
 print()
 
 found_match = False
 final_results = []
 
 for i, (seed, method) in enumerate(zip(seeds_to_test, method_names)):
 if str(i) in validation_results:
 result = validation_results[str(i)]
 if "error" in result:
 print(f" {method:<25} -> ERROR: {result['error'][:50]}")
 else:
 identity = result.get("identity", "")
 match = result.get("match", False)
 status = "✅ MATCH!" if match else "❌"
 print(f" {method:<25} -> {identity[:40]}... {status}")
 
 final_results.append({
 "method": method,
 "seed": seed,
 "derived_identity": identity,
 "match": match
 })
 
 if match:
 found_match = True
 print(f"\n🎉 FOUND IT! Method: {method}")
 print(f" Seed: {seed}")
 print(f" Identity: {identity}")
 
 # Save results
 output_file = project_root / "outputs" / "derived" / "gemini_seed_validation_results.json"
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

