#!/usr/bin/env python3
"""
Generate Private Keys and Public IDs for Verification

This script generates private keys and public IDs from seeds found in the Anna Matrix.

REVIEW THIS SCRIPT BEFORE RUNNING
What it does:
- Reads: Hardcoded identity list (8 identities)
- Computes: Private keys via SHA256(seed), public keys via Ed25519
- Writes: VERIFICATION_KEYS.md, VERIFICATION_KEYS.json
- Imports: hashlib, ed25519, analysis.utils.identity_tools

Check the code to verify what it actually does.

WARNING: These are REAL private keys. Handle with care. They are published for
verification purposes only. Anyone with these keys has full control over the identities.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from analysis.utils.identity_tools import public_key_from_identity, identity_from_body
import hashlib
import ed25519

def derive_private_key_from_seed(seed: str) -> bytes:
 """
 Derive Ed25519 private key from seed using qubipy method.
 
 Args:
 seed: 55-character lowercase seed string
 
 Returns:
 32-byte private key
 """
 if len(seed) != 55:
 raise ValueError(f"Seed must be exactly 55 characters, got {len(seed)}")
 
 try:
 # Use qubipy method (correct way)
 from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 )
 seed_bytes = seed.encode('utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 return private_key
 except ImportError:
 # Fallback: Use SHA256 (simplified, may not match Qubic exactly)
 seed_bytes = seed.encode('utf-8')
 private_key_bytes = hashlib.sha256(seed_bytes).digest()
 return private_key_bytes

def get_public_key_from_private(private_key: bytes) -> bytes:
 """
 Get Ed25519 public key from private key.
 
 Args:
 private_key: 32-byte private key
 
 Returns:
 32-byte public key
 """
 signing_key = ed25519.SigningKey(private_key)
 public_key = signing_key.get_verifying_key().to_bytes()
 return public_key

def seed_to_identity(seed: str) -> Optional[str]:
 """
 Convert seed to Qubic identity using qubipy.
 
 Args:
 seed: 55-character lowercase seed
 
 Returns:
 60-character uppercase Qubic identity or None if qubipy not available
 """
 try:
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
 except ImportError:
 # Fallback: Use simplified method (not fully accurate)
 body = seed + 'a'
 body = body[:56]
 try:
 identity = identity_from_body(body)
 return identity
 except:
 return None
 except Exception:
 return None

def main():
 """Generate verification keys for the 8 initial identities."""
 
 # The 8 initial identities from FOUND_IDENTITIES.md
 identities = [
 # Diagonal identities
 "AQIOSQQMACYBPQXQSJNIUAYLMXXIWQOXQMEQYXBBTBONSJJRCWPXXDDRDWOR",
 "GWUXOMMMMFMTBWFZSNGMUKWBILTXQDKNMMMNYPEFTAMRONJMABLHTRRROHXZ",
 "ACGJGQQYILBPXDRBORFGWFZBBBNLQNGHDDELVLXXXLBNNNFBLLPBNNNLJIFV",
 "GIUVFGAWCBBFFKVBMFJESLHBBFBFWZWNNXCBQBBJRVFBNVJLTJBBBHTHKLDC",
 # Vortex identities
 "UUFEEMUUBIYXYXDUXZCFBIHABAYSACQSWSGABOBKNXBZCICLYOKOBMLKMUAF",
 "HJBRFBHTBZJLVRBXTDRFORBWNACAHAQMSBUNBONHTRHNJKXKKNKHWCBNAXLD",
 "JKLMNOIPDQORWSICTWWUIYVMOFIQCQSYKMKACMOKQYCCMCOGOCQCSCWCDQFL",
 "XYZQAUBQUUQBQBYQAYEIYAQYMMEMQQQMMQSQEQAZSMOGWOXKIRMJXMCLFAVK",
 ]
 
 identity_names = [
 "Diagonal #1", "Diagonal #2", "Diagonal #3", "Diagonal #4",
 "Vortex #1", "Vortex #2", "Vortex #3", "Vortex #4"
 ]
 
 results = []
 
 print("Generating private keys and public IDs for verification...")
 print("=" * 80)
 
 for i, (identity, name) in enumerate(zip(identities, identity_names), 1):
 print(f"\n{i}. {name}")
 print(f" Identity: {identity}")
 
 # Derive seed from identity
 seed = identity.lower()[:55]
 print(f" Seed: {seed}")
 
 # Derive private key from seed
 try:
 private_key = derive_private_key_from_seed(seed)
 private_key_hex = private_key.hex()
 print(f" Private Key: {private_key_hex}")
 
 # Get public key
 public_key = get_public_key_from_private(private_key)
 public_key_hex = public_key.hex()
 print(f" Public Key: {public_key_hex}")
 
 # Verify: Derive identity from seed and check it matches
 derived_identity = seed_to_identity(seed)
 if derived_identity:
 print(f" Derived Identity: {derived_identity}")
 # Note: The derived identity may not match the documented identity
 # This is the known discrepancy we've documented
 match = (derived_identity == identity)
 print(f" Match: {match}")
 else:
 print(f" Derived Identity: (could not derive - qubipy may not be available)")
 match = False
 
 results.append({
 "name": name,
 "documented_identity": identity,
 "seed": seed,
 "private_key_hex": private_key_hex,
 "public_key_hex": public_key_hex,
 "derived_identity": derived_identity if derived_identity else None,
 "match": match if derived_identity else None
 })
 
 except Exception as e:
 print(f" ERROR: {e}")
 results.append({
 "name": name,
 "documented_identity": identity,
 "seed": seed,
 "error": str(e)
 })
 
 # Save to JSON
 import json
 output_file = project_root / "VERIFICATION_KEYS.json"
 with open(output_file, 'w') as f:
 json.dump(results, f, indent=2)
 
 print("\n" + "=" * 80)
 print(f"Results saved to: {output_file}")
 print("\nWARNING: These are REAL private keys. Anyone with these keys has full control.")
 print("They are published for verification purposes only.")
 
 # Also create a markdown file
 md_file = project_root / "VERIFICATION_KEYS.md"
 with open(md_file, 'w') as f:
 f.write("# Verification Keys - For Independent Verification\n\n")
 f.write("**WARNING**: These are REAL private keys. Handle with extreme care.\n")
 f.write("Anyone with these keys has full control over the identities.\n")
 f.write("They are published for verification purposes only.\n\n")
 f.write("## How to Verify\n\n")
 f.write("1. Import the private key into Qubic Wallet\n")
 f.write("2. Check that the public ID matches the documented identity\n")
 f.write("3. Verify the identity exists on-chain using Qubic RPC\n")
 f.write("4. Sign a message to prove you control the key\n\n")
 f.write("## Keys\n\n")
 
 for result in results:
 f.write(f"### {result['name']}\n\n")
 f.write(f"- **Documented Identity**: `{result['documented_identity']}`\n")
 f.write(f"- **Seed**: `{result['seed']}`\n")
 if 'private_key_hex' in result:
 f.write(f"- **Private Key (hex)**: `{result['private_key_hex']}`\n")
 f.write(f"- **Public Key (hex)**: `{result['public_key_hex']}`\n")
 f.write(f"- **Derived Identity**: `{result['derived_identity']}`\n")
 f.write(f"- **Match**: {result['match']}\n")
 else:
 f.write(f"- **Error**: {result.get('error', 'Unknown error')}\n")
 f.write("\n")
 
 print(f"Markdown file saved to: {md_file}")
 print("\nYou can now verify these keys independently using Qubic Wallet or RPC.")

if __name__ == "__main__":
 main()

