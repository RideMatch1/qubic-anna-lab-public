#!/usr/bin/env python3
"""
Master Seed Fusion: Layer-1 Seeds (directly from Matrix)

CRITICAL: Uses Layer-1 seeds, not Layer-2 seeds!
Layer-1 seeds are the raw, unencrypted fragments directly extracted from the Anna Matrix.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "master_seed_fusion_layer1.json"
OUTPUT_MD = OUTPUT_DIR / "master_seed_fusion_layer1.md"

SEED_LENGTH = 55
ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def load_layer1_seeds() -> List[str]:
 """Load the 8 Layer-1 seeds directly from Layer-1 identities (Matrix extraction)."""
 layer1_identities = [
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR", # Diagonal #1
 "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ", # Diagonal #2
 "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV", # Diagonal #3
 "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC", # Diagonal #4
 "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF", # Vortex #1
 "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD", # Vortex #2
 "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL", # Vortex #3
 "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK", # Vortex #4
 ]
 
 seeds = []
 for identity in layer1_identities:
 seed = identity[:56].lower()[:55]
 if len(seed) == SEED_LENGTH and seed.isalpha() and seed.islower():
 seeds.append(seed)
 
 return seeds

def normalize_seed(seed: str) -> str:
 """Normalize seed to 55 lowercase letters."""
 seed = ''.join(c for c in seed.lower() if c in ALPHABET)
 if len(seed) < SEED_LENGTH:
 seed = (seed * ((SEED_LENGTH // len(seed)) + 1))[:SEED_LENGTH]
 elif len(seed) > SEED_LENGTH:
 seed = seed[:SEED_LENGTH]
 return seed

def fusion_xor(seeds: List[str]) -> str:
 """XORs all seeds character by character (mod 26)."""
 if not seeds:
 return ""
 
 result = []
 for i in range(SEED_LENGTH):
 xor_val = 0
 for seed in seeds:
 if i < len(seed):
 char_val = ord(seed[i]) - ord('a')
 xor_val ^= char_val
 result.append(chr((xor_val % 26) + ord('a')))
 
 return ''.join(result)

def fusion_concat_k12(seeds: List[str]) -> str:
 """Concatenates all seeds and hashes with K12, maps to a-z."""
 mega_string = ''.join(seeds)
 
 try:
 import sys
 sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")
 from qubipy.crypto.utils import kangaroo_twelve
 hashed = kangaroo_twelve(mega_string.encode(), len(mega_string.encode()), SEED_LENGTH)
 except:
 import hashlib
 hashed = hashlib.sha256(mega_string.encode()).digest()
 # Pad or truncate to SEED_LENGTH
 while len(hashed) < SEED_LENGTH:
 hashed += hashlib.sha256(hashed).digest()
 hashed = hashed[:SEED_LENGTH]
 
 # Map bytes to a-z (0-25)
 result = ''.join(chr((b % 26) + ord('a')) for b in hashed[:SEED_LENGTH])
 return result

def fusion_modular_sum(seeds: List[str]) -> str:
 """Sum of character values mod 26."""
 if not seeds:
 return ""
 
 result = []
 for i in range(SEED_LENGTH):
 total = 0
 for seed in seeds:
 if i < len(seed):
 total += (ord(seed[i]) - ord('a'))
 result.append(chr((total % 26) + ord('a')))
 
 return ''.join(result)

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Derive identity from seed using native crypto functions."""
 try:
 import sys
 sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")
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
 return identity
 except Exception as e:
 print(f" ⚠️ Derivation failed: {e}")
 return None

def check_identity_rpc(rpc, identity: str) -> dict:
 """Check identity on-chain via RPC."""
 result = {
 "balance": None,
 "assets": None,
 "history": None,
 "status": "unknown",
 "error": None,
 }
 
 try:
 time.sleep(1.0) # Rate limiting
 balance_data = rpc.get_balance(identity)
 if balance_data:
 result["balance"] = str(balance_data.get("balance", 0))
 
 try:
 assets = rpc.get_owned_assets(identity)
 result["assets"] = assets if assets else []
 except:
 result["assets"] = []
 
 try:
 history = rpc.get_transaction_history(identity, limit=10)
 result["history"] = history if history else []
 except:
 result["history"] = []
 
 balance_int = int(result["balance"])
 has_assets = result["assets"] and len(result["assets"]) > 0
 has_history = result["history"] and len(result["history"]) > 0
 
 if balance_int > 0 or has_assets or has_history:
 result["status"] = "HIT"
 else:
 result["status"] = "empty"
 else:
 result["status"] = "not_found"
 except Exception as e:
 result["error"] = str(e)
 result["status"] = "rpc_error"
 
 return result

def main() -> int:
 """Main function."""
 print("=" * 80)
 print("🧬 MASTER SEED FUSION PROTOCOL - LAYER 1 SEEDS")
 print("=" * 80)
 print()
 
 # Load Layer-1 seeds
 seeds = load_layer1_seeds()
 
 if not seeds or len(seeds) != 8:
 print(f"❌ Expected 8 Layer-1 seeds, found {len(seeds)}")
 return 1
 
 print(f"📦 Loaded {len(seeds)} Layer-1 seeds (directly from Matrix):")
 for i, seed in enumerate(seeds, 1):
 print(f" {i}. {seed}")
 print()
 
 # Normalize seeds
 normalized_seeds = [normalize_seed(s) for s in seeds]
 
 # Initialize RPC
 rpc = None
 try:
 import sys
 sys.path.insert(0, "venv-tx/lib/python3.11/site-packages")
 from qubipy.rpc import rpc_client
 rpc = rpc_client.QubiPy_RPC()
 print("✅ RPC connection established")
 except Exception as e:
 print(f"⚠️ RPC connection failed: {e}")
 print(" Continuing without RPC checks")
 
 print()
 print("=" * 80)
 print("🔬 FUSION METHODS")
 print("=" * 80)
 print()
 
 # Fusion methods
 methods = [
 ("XOR Sum (Binary Fusion)", fusion_xor),
 ("Concatenation + K12 Hash", fusion_concat_k12),
 ("Modular Sum (Character Addition)", fusion_modular_sum),
 ]
 
 results = []
 
 for method_name, fusion_func in methods:
 print(f"🔍 Method: {method_name}")
 print(f" Combining {len(normalized_seeds)} seeds...")
 
 fused_seed = fusion_func(normalized_seeds)
 print(f" Fused seed: {fused_seed}")
 
 # Derive identity
 identity = derive_identity_from_seed(fused_seed)
 
 result = {
 "method": method_name,
 "seed": fused_seed,
 "identity": identity,
 "balance": None,
 "assets": None,
 "history": None,
 "status": "unknown",
 "error": None,
 }
 
 if identity:
 print(f" Identity: {identity}")
 
 if rpc:
 rpc_result = check_identity_rpc(rpc, identity)
 result.update(rpc_result)
 
 if result["status"] == "HIT":
 print(f" 🎉🎉🎉 HIT! Balance: {result['balance']}, Assets: {len(result.get('assets', []))}, History: {len(result.get('history', []))}")
 elif result["balance"] is not None:
 print(f" Balance: {result['balance']} QU")
 if result["assets"]:
 print(f" Assets: {len(result['assets'])}")
 if result.get("history"):
 print(f" History: {len(result['history'])} transactions")
 print(f" Status: {result['status']}")
 else:
 print(f" Status: {result['status']}")
 if result["error"]:
 print(f" Error: {result['error']}")
 else:
 print(f" Status: identity derived (no RPC check)")
 result["status"] = "derived_no_rpc"
 else:
 print(f" ❌ Failed to derive identity")
 result["status"] = "derivation_failed"
 
 results.append(result)
 print()
 
 # Save results
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump({
 "layer1_seeds": seeds,
 "normalized_seeds": normalized_seeds,
 "fusion_results": results,
 }, f, indent=2, ensure_ascii=False)
 
 # Create markdown report
 with OUTPUT_MD.open("w", encoding="utf-8") as f:
 f.write("# Master Seed Fusion Results (Layer-1 Seeds)\n\n")
 f.write(f"**Layer-1 Seeds:** {len(seeds)} (directly from Matrix)\n\n")
 f.write("## Fusion Methods\n\n")
 
 for result in results:
 f.write(f"### {result['method']}\n\n")
 f.write(f"- **Seed:** `{result['seed']}`\n")
 if result["identity"]:
 f.write(f"- **Identity:** `{result['identity']}`\n")
 if result["balance"] is not None:
 f.write(f"- **Balance:** {result['balance']} QU\n")
 if result["assets"]:
 f.write(f"- **Assets:** {len(result['assets'])}\n")
 if result.get("history"):
 f.write(f"- **History:** {len(result['history'])} transactions\n")
 f.write(f"- **Status:** {result['status']}\n")
 if result["error"]:
 f.write(f"- **Error:** {result['error']}\n")
 f.write("\n")
 
 print("=" * 80)
 print("✅ FUSION COMPLETE")
 print("=" * 80)
 print()
 print(f"💾 Results saved to:")
 print(f" {OUTPUT_JSON}")
 print(f" {OUTPUT_MD}")
 print()
 
 # Summary
 hits = [r for r in results if r["status"] == "HIT"]
 if hits:
 print(f"🎉 {len(hits)} HIT(S) FOUND!")
 for hit in hits:
 print(f" - {hit['method']}: {hit['identity']}")
 print(f" Balance: {hit['balance']}, Assets: {len(hit.get('assets', []))}, History: {len(hit.get('history', []))}")
 else:
 print("❌ No hits found - Master Seed not in fused wallets")
 print()
 print("💡 Next steps:")
 print(" - Try other fusion methods")
 print(" - Check if Master Seed is in a different layer")
 print(" - Verify Layer-1 seed extraction")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

