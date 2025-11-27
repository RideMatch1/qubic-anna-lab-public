#!/usr/bin/env python3
"""
Teste die ursprüngliche Derivation-Methode
"""

import json
from pathlib import Path

from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

print("=" * 80)
print("TEST: URSPRÜNGLICHE DERIVATION-METHODE")
print("=" * 80)
print()

# Load identity_deep_scan.json
deep_scan_path = Path("outputs/derived/identity_deep_scan.json")
with deep_scan_path.open() as f:
 deep_scan = json.load(f)

# Teste mit Diagonal #1
parent_identity = "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR"
expected_child = "CYTORJWZCJFCYXAHJPLPPCWPVOXTDZBWQYVWANQDYQCCIORJTVMPBIXBKIVP"

# Finde den korrekten Seed aus dem JSON
for record in deep_scan["records"]:
 if record["identity"] == parent_identity:
 # Finde das zugehörige Layer-2 Record
 label = record["label"].split(" ")[0]
 for r in deep_scan["records"]:
 if r["layer"] == "layer2" and label in r["label"]:
 expected_child = r["identity"]
 expected_seed = r["seed"]
 break
 break

print(f"Parent: {parent_identity}")
print(f"Expected Child: {expected_child}")
print(f"Expected Seed: {expected_seed}")
print()

# Teste Seed-Extraktion
seed_original = parent_identity[:56].lower()[:55]
seed_current = parent_identity[:55].lower()

print(f"Seed-Extraktion:")
print(f" Original ([:56].lower()[:55]): {seed_original}")
print(f" Aktuell ([:55].lower()): {seed_current}")
print(f" Expected: {expected_seed}")
print(f" Match Original: {seed_original == expected_seed}")
print(f" Match Aktuell: {seed_current == expected_seed}")
print()

# Teste Derivation mit qubipy.crypto.utils
try:
 seed_bytes = bytes(expected_seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 derived = get_identity_from_public_key(public_key)
 
 print(f"Derivation (qubipy.crypto.utils):")
 print(f" Derived: {derived}")
 print(f" Expected: {expected_child}")
 print(f" Match: {derived == expected_child}")
 print()
 
 if derived == expected_child:
 print("✅ URSPRÜNGLICHE METHODE FUNKTIONIERT!")
 else:
 print("❌ URSPRÜNGLICHE METHODE FUNKTIONIERT NICHT!")
 print()
 print("Vergleich (erste 20 Unterschiede):")
 count = 0
 for i, (d, e) in enumerate(zip(derived, expected_child)):
 if d != e:
 print(f" Position {i}: Derived '{d}' != Expected '{e}'")
 count += 1
 if count >= 20:
 break
 
except Exception as e:
 print(f"❌ Error: {e}")
 import traceback
 traceback.print_exc()

