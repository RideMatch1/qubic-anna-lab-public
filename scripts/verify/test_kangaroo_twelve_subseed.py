
import json
from qubipy.crypto.utils import (
 kangaroo_twelve,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

# Test-Seed
test_seed = "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd"
expected_identity = "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP"

print(f"Test-Seed: {test_seed}")
print(f"Expected Identity: {expected_identity}")
print()

# Teste: Subseed = KangarooTwelve(seed_bytes, 55, 32)
seed_bytes = test_seed.encode('utf-8')
print(f"Seed bytes length: {len(seed_bytes)}")
print()

# Variante: Subseed = KangarooTwelve(seed_bytes, 55, 32)
subseed = kangaroo_twelve(seed_bytes, len(seed_bytes), 32)
print(f"Subseed (K12(seed_bytes, 55, 32)): {subseed.hex()[:64]}...")
print()

# Private Key
private_key = get_private_key_from_subseed(subseed)
print(f"Private Key: {private_key.hex()[:64]}...")
print()

# Public Key
public_key = get_public_key_from_private_key(private_key)
print(f"Public Key: {public_key.hex()[:64]}...")
print()

# Identity
identity = get_identity_from_public_key(public_key)
print(f"Derived Identity: {identity}")
print()

if identity == expected_identity:
 print("✅✅✅ MATCH! Die korrekte Methode ist:")
 print(" subseed = kangaroo_twelve(seed_bytes, len(seed_bytes), 32)")
 result = {"match": True, "method": "kangaroo_twelve(seed_bytes, len(seed_bytes), 32)"}
else:
 print("❌ Kein Match")
 print(f" Expected: {expected_identity}")
 print(f" Got: {identity}")
 result = {"match": False, "expected": expected_identity, "got": identity}

with open("outputs/derived/kangaroo_twelve_test_result.json", "w") as f:
 json.dump(result, f, indent=2)
