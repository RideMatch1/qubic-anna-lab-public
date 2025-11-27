#!/usr/bin/env python3
"""
Master Seed Fusion: Combines the 8 Layer-1 seeds (directly from Matrix) into a single 'Master Seed'.

CRITICAL: We use Layer-1 seeds, not Layer-2 seeds!
Layer-1 seeds are the raw, unencrypted fragments directly extracted from the Anna Matrix.
Layer-2 seeds are cryptographically derived and complex - mixing them is like mixing encrypted files.

Methods:
1. XOR Fusion: Binary XOR of all seed bytes (classic secret reconstruction)
2. Concatenation + K12: Hash(Seed1 + Seed2 + ... + Seed8)
3. Modular Addition: Sum of bytes mod 26
4. Interleaved: Alternating characters from each seed

If the 'Treasure' is not in the 8 wallets, it might be in the wallet formed by their union.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

try:
 from qubipy.rpc import rpc_client
 HAS_RPC = True
except ImportError:
 HAS_RPC = False

try:
 from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
 kangaroo_twelve,
 )
 HAS_CRYPTO = True
except (ImportError, OSError) as e:
 HAS_CRYPTO = False
 print(f"⚠️ QubiPy crypto not available ({e}) - will use fallback")

QUBIPY_AVAILABLE = HAS_RPC and HAS_CRYPTO

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "master_seed_fusion.json"
OUTPUT_MD = OUTPUT_DIR / "master_seed_fusion.md"

# Standard Qubic seed length
SEED_LENGTH = 55
ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def load_layer1_seeds() -> List[str]:
 """Load the 8 Layer-1 seeds directly from Layer-1 identities (Matrix extraction)."""
 # Layer 1 Identities (directly from Matrix)
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
 
 # Extract seeds from Layer-1 identities: identity[:56].lower()[:55]
 seeds = []
 for identity in layer1_identities:
 seed = identity[:56].lower()[:55]
 if len(seed) == SEED_LENGTH and seed.isalpha() and seed.islower():
 seeds.append(seed)
 else:
 print(f"⚠️ Invalid seed extracted from {identity[:30]}...")
 
 if len(seeds) != 8:
 print(f"⚠️ Expected 8 seeds, found {len(seeds)}")
 
 return seeds

def normalize_seed(seed: str) -> str:
 """Normalize seed to 55 lowercase letters."""
 seed = ''.join(c for c in seed.lower() if c in ALPHABET)
 if len(seed) < SEED_LENGTH:
 # Pad by repeating
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
 
 if QUBIPY_AVAILABLE:
 hashed = kangaroo_twelve(mega_string.encode())
 else:
 import hashlib
 hashed = hashlib.sha256(mega_string.encode()).digest()
 
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

def fusion_interleaved(seeds: List[str]) -> str:
 """Interleaves characters from all seeds (round-robin)."""
 if not seeds:
 return ""
 
 result = []
 max_len = max(len(s) for s in seeds)
 
 for i in range(SEED_LENGTH):
 seed_idx = i % len(seeds)
 char_idx = i // len(seeds)
 if char_idx < len(seeds[seed_idx]):
 result.append(seeds[seed_idx][char_idx])
 else:
 result.append('a') # Padding
 
 return ''.join(result)[:SEED_LENGTH]

def fusion_reverse_concat_k12(seeds: List[str]) -> str:
 """Reverse order concatenation + K12."""
 return fusion_concat_k12(seeds[::-1])

def check_identity(rpc, seed: str, method_name: str) -> dict:
 """Derives ID from fused seed and checks RPC."""
 result = {
 "method": method_name,
 "seed": seed,
 "identity": None,
 "balance": None,
 "assets": None,
 "history": None,
 "status": "unknown",
 "error": None,
 }
 
 try:
 seed = normalize_seed(seed)
 
 if HAS_CRYPTO:
 # Derive identity from seed using the correct method
 try:
 seed_bytes = seed.encode('utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 identity = get_identity_from_public_key(public_key)
 result["identity"] = identity
 except Exception as e:
 result["error"] = f"Crypto derivation failed: {e}"
 result["identity"] = None
 elif HAS_RPC:
 # Fallback: Try to use RPC to derive (if available)
 result["identity"] = None
 result["error"] = "Crypto functions not available"
 
 if rpc:
 try:
 balance_data = rpc.get_balance(identity)
 balance = balance_data.get("balance", 0)
 result["balance"] = str(balance)
 
 assets = rpc.get_owned_assets(identity)
 result["assets"] = assets if assets else []
 
 # Check transaction history
 try:
 history = rpc.get_transaction_history(identity, limit=10)
 result["history"] = history if history else []
 except:
 result["history"] = []
 
 if int(balance) > 0 or (assets and len(assets) > 0) or (result["history"] and len(result["history"]) > 0):
 result["status"] = "HIT"
 else:
 result["status"] = "empty"
 except Exception as e:
 result["error"] = str(e)
 result["status"] = "rpc_error"
 else:
 result["identity"] = f"SIMULATED_ID_{seed[:10]}"
 result["status"] = "simulated"
 
 except Exception as e:
 result["error"] = str(e)
 result["status"] = "error"
 
 return result

def main() -> int:
 """Main function."""
 print("=" * 80)
 print("🧬 MASTER SEED FUSION PROTOCOL")
 print("=" * 80)
 print()
 
 # Load Layer-1 seeds (directly from Matrix)
 seeds = load_layer1_seeds()
 
 if not seeds:
 print("❌ No Layer-1 seeds found!")
 return 1
 
 if len(seeds) != 8:
 print(f"⚠️ Expected 8 seeds, found {len(seeds)}")
 
 print(f"📦 Loaded {len(seeds)} Layer-1 seeds (directly from Matrix):")
 for i, seed in enumerate(seeds, 1):
 print(f" {i}. {seed}")
 print()
 
 # Normalize seeds
 normalized_seeds = [normalize_seed(s) for s in seeds]
 
 # Initialize RPC
 rpc = None
 if QUBIPY_AVAILABLE:
 try:
 rpc = rpc_client.QubiPy_RPC()
 print("✅ RPC connection established")
 except Exception as e:
 print(f"⚠️ RPC connection failed: {e}")
 print(" Continuing with simulation only")
 else:
 print("⚠️ QubiPy not available - simulating only")
 
 print()
 print("=" * 80)
 print("🔬 FUSION METHODS")
 print("=" * 80)
 print()
 
 # Fusion methods
 methods = [
 ("XOR Sum (Binary Fusion)", fusion_xor),
 ("Concatenation + K12 Hash", fusion_concat_k12),
 ("Reverse Order + K12 Hash", fusion_reverse_concat_k12),
 ("Modular Sum (Character Addition)", fusion_modular_sum),
 ("Interleaved (Round-Robin)", fusion_interleaved),
 ]
 
 results = []
 
 for method_name, fusion_func in methods:
 print(f"🔍 Method: {method_name}")
 print(f" Combining {len(normalized_seeds)} seeds...")
 
 fused_seed = fusion_func(normalized_seeds)
 print(f" Fused seed: {fused_seed}")
 
 result = check_identity(rpc, fused_seed, method_name)
 results.append(result)
 
 if result["status"] == "HIT":
 print(f" 🎉🎉🎉 HIT! Balance: {result['balance']}, Assets: {len(result.get('assets', []))}, History: {len(result.get('history', []))}")
 elif result["identity"]:
 print(f" Identity: {result['identity']}")
 if result["balance"] is not None:
 print(f" Balance: {result['balance']} QU")
 if result["assets"]:
 print(f" Assets: {len(result['assets'])}")
 if result.get("history"):
 print(f" History: {len(result['history'])} transactions")
 else:
 print(f" Status: {result['status']}")
 else:
 print(f" Status: {result['status']}")
 if result["error"]:
 print(f" Error: {result['error']}")
 
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
 else:
 print("❌ No hits found - Master Seed not in fused wallets")
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

