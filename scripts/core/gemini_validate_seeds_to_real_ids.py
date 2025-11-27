#!/usr/bin/env python3
"""
Gemini Validate Seeds to Real IDs

Nimmt die 100 Seeds aus der JSON, leitet die echten Public IDs ab,
und vergleicht sie mit den dokumentierten Identities.

Viel effizienter als alle Transformationen zu testen!
"""

import json
import sys
import subprocess
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent.parent.parent
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"
INPUT_FILE = project_root / "github_export" / "100_seeds_and_identities.json"
OUTPUT_FILE = project_root / "outputs" / "derived" / "gemini_seeds_to_real_ids.json"

def derive_identity_from_seed(seed: str) -> tuple[bool, str]:
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
 timeout=10,
 cwd=project_root
 )
 
 if result.returncode == 0 and result.stdout.strip():
 identity = result.stdout.strip()
 if len(identity) == 60:
 return True, identity
 return False, result.stderr.strip() or "Failed"
 except Exception as e:
 return False, str(e)

def check_identity_onchain(identity: str) -> dict:
 """Check identity on-chain."""
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
 timeout=10,
 cwd=project_root
 )
 
 if result.returncode == 0 and result.stdout.strip():
 return json.loads(result.stdout.strip())
 return {"exists": False, "error": "Execution failed"}
 except Exception as e:
 return {"exists": False, "error": str(e)}

def main():
 """Main function."""
 print("=" * 80)
 print("GEMINI VALIDATE SEEDS TO REAL IDs")
 print("=" * 80)
 print()
 
 if not VENV_PYTHON.exists():
 print("❌ venv-tx not found!")
 return
 
 if not INPUT_FILE.exists():
 print(f"❌ Input file not found: {INPUT_FILE}")
 return
 
 # Load seeds and identities
 print("1. Loading seeds and identities...")
 sys.stdout.flush()
 
 with INPUT_FILE.open() as f:
 data = json.load(f)
 
 if isinstance(data, dict) and "seeds_and_identities" in data:
 items = data["seeds_and_identities"]
 else:
 items = data if isinstance(data, list) else []
 
 print(f" ✅ Loaded {len(items)} items")
 print()
 sys.stdout.flush()
 
 # Process each seed
 print("2. Deriving real identities from seeds...")
 print()
 sys.stdout.flush()
 
 results = []
 matches = []
 mismatches = []
 
 for idx, item in enumerate(items, 1):
 documented_seed = item.get("seed", "")
 documented_identity = item.get("identity", "")
 documented_balance = item.get("balance", "0")
 
 if idx % 10 == 0:
 print(f"Progress: {idx}/{len(items)} (Matches: {len(matches)})")
 sys.stdout.flush()
 
 # Derive real identity from seed
 success, real_identity = derive_identity_from_seed(documented_seed)
 
 if not success:
 print(f"❌ Identity #{idx}: Derivation failed - {real_identity[:50]}")
 results.append({
 "index": idx,
 "documented_seed": documented_seed,
 "documented_identity": documented_identity,
 "derivation_success": False,
 "error": real_identity
 })
 continue
 
 # Check if it matches
 match = (real_identity == documented_identity)
 
 # Check on-chain status
 onchain = check_identity_onchain(real_identity)
 
 result = {
 "index": idx,
 "documented_seed": documented_seed,
 "documented_identity": documented_identity,
 "documented_balance": documented_balance,
 "real_identity": real_identity,
 "match": match,
 "onchain": onchain
 }
 
 results.append(result)
 
 if match:
 matches.append(result)
 print(f"✅ MATCH! Identity #{idx}")
 print(f" Seed: {documented_seed[:50]}...")
 print(f" Identity: {real_identity}")
 if onchain.get("exists"):
 print(f" On-Chain: ✅ (Balance: {onchain.get('balance', 'N/A')} QU)")
 print()
 else:
 mismatches.append(result)
 if idx <= 10: # Show first 10 mismatches
 print(f"❌ Mismatch Identity #{idx}")
 print(f" Seed: {documented_seed[:50]}...")
 print(f" Documented: {documented_identity}")
 print(f" Real: {real_identity}")
 if onchain.get("exists"):
 print(f" On-Chain: ✅ (Balance: {onchain.get('balance', 'N/A')} QU)")
 print()
 
 sys.stdout.flush()
 
 # Save results
 OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
 
 with OUTPUT_FILE.open("w") as f:
 json.dump({
 "total_tested": len(items),
 "matches_found": len(matches),
 "mismatches": len(mismatches),
 "match_rate": f"{len(matches)*100/len(items):.1f}%",
 "matches": matches,
 "mismatches": mismatches[:20], # First 20 for analysis
 "all_results": results
 }, f, indent=2)
 
 print("=" * 80)
 print("VALIDATION COMPLETE")
 print("=" * 80)
 print(f"✅ Results saved to: {OUTPUT_FILE}")
 print()
 print(f"Summary:")
 print(f" Total tested: {len(items)}")
 print(f" Matches: {len(matches)} ({len(matches)*100/len(items):.1f}%)")
 print(f" Mismatches: {len(mismatches)} ({len(mismatches)*100/len(items):.1f}%)")
 print()
 
 # On-chain statistics
 onchain_count = sum(1 for r in results if r.get("onchain", {}).get("exists"))
 print(f"On-Chain Statistics:")
 print(f" Real identities on-chain: {onchain_count}/{len(results)} ({onchain_count*100/len(results):.1f}%)")
 print()
 
 if matches:
 print("🎉 MATCHES FOUND!")
 print(f" {len(matches)} seeds produce the documented identities")
 print()
 print("Sample matches:")
 for match in matches[:10]:
 print(f" #{match['index']}: {match['real_identity'][:50]}...")
 if match.get("onchain", {}).get("exists"):
 print(f" Balance: {match['onchain'].get('balance', 'N/A')} QU")
 
 if mismatches:
 print()
 print("⚠️ MISMATCHES:")
 print(f" {len(mismatches)} seeds produce different identities")
 print()
 print("This means:")
 print(" - The documented seeds are approximations")
 print(" - The real seeds that produce the documented identities are different")
 print(" - We need to find the transformation from documented seed → real seed")

if __name__ == "__main__":
 main()

