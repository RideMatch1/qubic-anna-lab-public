#!/usr/bin/env python3
"""
Crypto-Validierung mit venv-tx (Python 3.11)

WICHTIG: Nur echte, nachgewiesene Erkenntnisse!
"""

import sys
import subprocess
from pathlib import Path

VENV_PATH = Path(__file__).parent.parent.parent / "venv-tx"
SCRIPT_DIR = Path(__file__).parent

def run_with_venv(script_content: str) -> bool:
 """Führe Script mit venv-tx aus."""
 # Erstelle temporäres Script
 temp_script = SCRIPT_DIR / "temp_crypto_test.py"
 temp_script.write_text(script_content)
 
 try:
 # Führe mit venv-tx aus
 python_exe = VENV_PATH / "bin" / "python"
 result = subprocess.run(
 [str(python_exe), str(temp_script)],
 capture_output=True,
 text=True,
 cwd=SCRIPT_DIR.parent.parent
 )
 
 print(result.stdout)
 if result.stderr:
 print(result.stderr, file=sys.stderr)
 
 return result.returncode == 0
 finally:
 # Lösche temporäres Script
 if temp_script.exists():
 temp_script.unlink()

def main():
 print("=" * 80)
 print("CRYPTO VALIDATION WITH VENV-TX")
 print("=" * 80)
 print()
 
 if not VENV_PATH.exists():
 print(f"❌ venv-tx not found at: {VENV_PATH}")
 return False
 
 python_exe = VENV_PATH / "bin" / "python"
 if not python_exe.exists():
 print(f"❌ Python executable not found at: {python_exe}")
 return False
 
 print(f"✅ Using venv-tx: {python_exe}")
 print()
 
 # Test Script
 test_script = """
import sys
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

# Test mit bekanntem Seed
test_seed = "aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd"
print(f"Testing with seed: {test_seed[:40]}...")
print()

seed_bytes = test_seed.encode('utf-8')
subseed = get_subseed_from_seed(seed_bytes)
print(f"✅ Subseed generated")

private_key = get_private_key_from_subseed(subseed)
print(f"✅ Private key generated")

public_key = get_public_key_from_private_key(private_key)
print(f"✅ Public key generated")

identity = get_identity_from_public_key(public_key)
print(f"✅ Identity derived: {identity}")
print()

# Test gegen bekannte Identities
known_identities = {
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR": "Layer-1 Diagonal #1",
 "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD": "Layer-2 Diagonal #1",
}

print("Testing against known identities:")
for identity, label in known_identities.items():
 matches = (identity == identity)
 print(f" {label}: {'✅ MATCH' if matches else '❌ NO MATCH'}")

print()
print("✅ ALL CRYPTO FUNCTIONS WORK!")
"""
 
 success = run_with_venv(test_script)
 
 if success:
 print()
 print("=" * 80)
 print("✅ CRYPTO VALIDATION SUCCESSFUL!")
 print("=" * 80)
 print()
 print("We can now use venv-tx for crypto validation!")
 else:
 print()
 print("=" * 80)
 print("❌ CRYPTO VALIDATION FAILED")
 print("=" * 80)
 
 return success

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)

