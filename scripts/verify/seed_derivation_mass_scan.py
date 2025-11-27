#!/usr/bin/env python3
"""
Mass Seed Derivation Scan: Test if ALL 179 new identities can function as seeds
and derive additional layers of identities.

This could reveal a MASSIVE hidden structure!
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Set

from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)
from qubipy.rpc import rpc_client

OUTPUT_DIR = Path("outputs/derived")
SCAN_FILE = OUTPUT_DIR / "comprehensive_matrix_scan.json"
ANALYSIS_FILE = OUTPUT_DIR / "new_identities_analysis.json"
OUTPUT_JSON = OUTPUT_DIR / "seed_derivation_mass_scan.json"

KNOWN_8 = [
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
]

def identity_to_seed_candidate(identity: str) -> str | None:
 """Convert identity to seed candidate (56 chars, lowercase, first 55)."""
 body = identity[:56].lower()[:55]
 if len(body) == 55 and body.isalpha():
 return body
 return None

def derive_identity_from_seed(seed: str) -> str | None:
 """Derive Qubic identity from seed."""
 try:
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 return get_identity_from_public_key(public_key)
 except:
 return None

def check_on_chain(rpc: rpc_client.QubiPy_RPC, identity: str) -> bool:
 """Quick on-chain check."""
 try:
 time.sleep(0.3)
 balance = rpc.get_balance(identity)
 return balance is not None
 except:
 return False

def scan_identity_as_seed(rpc: rpc_client.QubiPy_RPC, identity: str) -> Dict:
 """Test if an identity can function as a seed and derive on-chain identities."""
 result = {
 "source_identity": identity,
 "seed_candidate": None,
 "derived_identity": None,
 "derived_on_chain": False,
 "error": None,
 }
 
 seed_candidate = identity_to_seed_candidate(identity)
 if not seed_candidate:
 result["error"] = "Not seed-like"
 return result
 
 result["seed_candidate"] = seed_candidate
 
 derived = derive_identity_from_seed(seed_candidate)
 if not derived:
 result["error"] = "Derivation failed"
 return result
 
 result["derived_identity"] = derived
 result["derived_on_chain"] = check_on_chain(rpc, derived)
 
 return result

def main() -> None:
 rpc = rpc_client.QubiPy_RPC()
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=== Mass Seed Derivation Scan ===\n")
 print("Testing if ALL 179 new identities can function as seeds...\n")
 
 # Load all new identities
 with SCAN_FILE.open("r", encoding="utf-8") as f:
 scan_data = json.load(f)
 
 all_identities = set()
 for result in scan_data.get("results", []):
 for identity in result.get("on_chain_identities", []):
 all_identities.add(identity)
 
 new_identities = list(all_identities - set(KNOWN_8))
 
 print(f"Total new identities to test: {len(new_identities)}")
 print(f"Testing first 100 (to avoid rate limiting)...\n")
 
 results: List[Dict] = []
 successful_seeds: List[Dict] = []
 derived_on_chain: Set[str] = set()
 
 for i, identity in enumerate(new_identities[:100], 1):
 print(f"[{i}/100] Testing {identity[:30]}...", end=" ", flush=True)
 
 result = scan_identity_as_seed(rpc, identity)
 results.append(result)
 
 if result.get("derived_identity"):
 print(f"✓ Derived: {result['derived_identity'][:30]}...", end=" ", flush=True)
 
 if result.get("derived_on_chain"):
 print("✅ ON-CHAIN!")
 successful_seeds.append(result)
 derived_on_chain.add(result["derived_identity"])
 else:
 print("(not on-chain)")
 else:
 print(f"✗ {result.get('error', 'failed')}")
 
 print(f"\n=== Summary ===")
 print(f"Total tested: {len(results)}")
 print(f"Valid seed candidates: {len([r for r in results if r.get('seed_candidate')])}")
 print(f"Successful derivations: {len([r for r in results if r.get('derived_identity')])}")
 print(f"Derived identities on-chain: {len(successful_seeds)}")
 
 if successful_seeds:
 print(f"\n🎉 FOUND {len(successful_seeds)} IDENTITIES THAT FUNCTION AS SEEDS!")
 print(f"\nThese identities can derive on-chain identities:")
 for i, seed_result in enumerate(successful_seeds[:20], 1):
 print(f" {i}. {seed_result['source_identity'][:40]}...")
 print(f" → {seed_result['derived_identity']}")
 
 if len(successful_seeds) > 20:
 print(f" ... and {len(successful_seeds) - 20} more!")
 
 print(f"\n⚠️ THIS COULD BE A MASSIVE HIDDEN STRUCTURE!")
 print(f" If we recursively derive from these, we could find HUNDREDS or THOUSANDS of identities!")
 
 # Save results
 output = {
 "total_tested": len(results),
 "valid_seed_candidates": len([r for r in results if r.get("seed_candidate")]),
 "successful_derivations": len([r for r in results if r.get("derived_identity")]),
 "derived_on_chain_count": len(successful_seeds),
 "results": results,
 "successful_seeds": successful_seeds,
 "all_derived_on_chain": list(derived_on_chain),
 }
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(output, f, indent=2)
 
 print(f"\nReport saved to: {OUTPUT_JSON}")
 
 if successful_seeds:
 print(f"\n💡 NEXT STEP: Recursively derive from these {len(successful_seeds)} seeds")
 print(f" to find Layer 3, Layer 4, Layer 5... potentially INFINITE layers!")

if __name__ == "__main__":
 main()

