#!/usr/bin/env python3
"""
Teste crypto functions direkt auf dem Host-System (ohne Docker)

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
"""

import sys
from pathlib import Path

def test_crypto_functions():
 """Teste ob crypto functions funktionieren."""
 print("=" * 80)
 print("CRYPTO FUNCTIONS TEST (LOCAL HOST)")
 print("=" * 80)
 print()
 
 try:
 from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
 )
 
 print("✅ Crypto functions imported successfully!")
 print()
 
 # Test mit bekanntem Seed
 test_seed = "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd"
 print(f"Testing with seed: {test_seed[:40]}...")
 print()
 
 seed_bytes = test_seed.encode('utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 print(f"✅ Subseed generated: {subseed.hex()[:40]}...")
 
 private_key = get_private_key_from_subseed(subseed)
 print(f"✅ Private key generated: {private_key.hex()[:40]}...")
 
 public_key = get_public_key_from_private_key(private_key)
 print(f"✅ Public key generated: {public_key.hex()[:40]}...")
 
 identity = get_identity_from_public_key(public_key)
 print(f"✅ Identity derived: {identity}")
 print()
 
 print("=" * 80)
 print("✅ ALL CRYPTO FUNCTIONS WORK!")
 print("=" * 80)
 print()
 print("We can now test seed-to-identity conversion!")
 
 return True
 
 except ImportError as e:
 print(f"❌ Import error: {e}")
 print()
 print("qubipy is not installed. Install with:")
 print(" pip install qubipy")
 return False
 except Exception as e:
 print(f"❌ Error: {e}")
 print()
 print("Crypto functions failed. This might be a crypto.so problem.")
 return False

if __name__ == "__main__":
 success = test_crypto_functions()
 sys.exit(0 if success else 1)

