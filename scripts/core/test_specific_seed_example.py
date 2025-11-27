#!/usr/bin/env python3
"""
Test Specific Seed Example

User provided:
- Seed: aaaaewafwvvyuuaaaaewafwvvyuuaaaaewafwvvyuuaaaaewafwvvyu
- Qubic Wallet shows Identity: CVTVPOSTYHVHCEZILWIZAFLZZKGBPNLNNTXHFIKQADVZOLKHISQCMRPEBYRJ

Let's test what our derivation produces.
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def derive_identity_from_seed(seed: str) -> tuple[str, str, str]:
 """
 Leite Identity aus Seed ab.
 Returns: (identity, private_key_hex, public_key_hex)
 """
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{seed}"
seed_bytes = seed.encode('utf-8')
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)

print(f"IDENTITY:{{identity}}")
print(f"PRIVATE_KEY:{{private_key.hex()}}")
print(f"PUBLIC_KEY:{{public_key.hex()}}")
"""
 
 if not VENV_PYTHON.exists():
 return None, None, None
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 
 if result.returncode != 0:
 print(f"Error: {result.stderr}")
 return None, None, None
 
 identity = None
 private_key = None
 public_key = None
 
 for line in result.stdout.split('\n'):
 if line.startswith('IDENTITY:'):
 identity = line.split(':', 1)[1].strip()
 elif line.startswith('PRIVATE_KEY:'):
 private_key = line.split(':', 1)[1].strip()
 elif line.startswith('PUBLIC_KEY:'):
 public_key = line.split(':', 1)[1].strip()
 
 if identity and len(identity) == 60:
 return identity, private_key, public_key
 return None, None, None
 except Exception as e:
 print(f"Exception: {e}")
 return None, None, None

def main():
 print("=" * 80)
 print("TEST SPECIFIC SEED EXAMPLE")
 print("=" * 80)
 print()
 
 # User provided example
 seed = "aaaaewafwvvyuuaaaaewafwvvyuuaaaaewafwvvyuuaaaaewafwvvyu"
 wallet_identity = "CVTVPOSTYHVHCEZILWIZAFLZZKGBPNLNNTXHFIKQADVZOLKHISQCMRPEBYRJ"
 
 print(f"Seed: {seed}")
 print(f"Expected Identity (from Qubic Wallet): {wallet_identity}")
 print()
 
 print("Deriving identity from seed...")
 derived_identity, private_key, public_key = derive_identity_from_seed(seed)
 
 if not derived_identity:
 print("❌ Could not derive identity")
 return
 
 print(f"Derived Identity: {derived_identity}")
 print()
 
 if derived_identity == wallet_identity:
 print("✅ MATCH! Derived identity matches Qubic Wallet")
 else:
 print("❌ MISMATCH!")
 print(f" Qubic Wallet: {wallet_identity}")
 print(f" Our derivation: {derived_identity}")
 print()
 print("This confirms the discrepancy!")
 
 print()
 print(f"Private Key (hex): {private_key[:32]}..." if private_key else "Private Key: None")
 print(f"Public Key (hex): {public_key[:32]}..." if public_key else "Public Key: None")
 print()
 
 # Check what the documented identity is (if any)
 print("Checking documented identity...")
 import json
 json_file = project_root / "github_export" / "100_seeds_and_identities.json"
 if json_file.exists():
 with json_file.open() as f:
 data = json.load(f)
 
 for item in data.get("seeds_and_identities", []):
 if item["seed"] == seed:
 documented_identity = item["identity"]
 print(f"Documented Identity: {documented_identity}")
 print()
 
 if documented_identity == wallet_identity:
 print("✅ Documented identity matches Qubic Wallet")
 elif documented_identity == derived_identity:
 print("✅ Documented identity matches our derivation")
 else:
 print("❌ Documented identity matches neither!")
 print(f" Qubic Wallet: {wallet_identity}")
 print(f" Our derivation: {derived_identity}")
 print(f" Documented: {documented_identity}")
 break
 else:
 print("Seed not found in documentation")
 else:
 print("Documentation file not found")
 
 print()
 print("=" * 80)
 print("TEST COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

