#!/usr/bin/env python3
"""
Quick layer check: Just verify how deep each chain goes without full asset checks.
"""

from __future__ import annotations

from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)
from qubipy.rpc import rpc_client
import time

LAYER2_IDENTITIES = [
 ("Diagonal #1", "OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD"),
 ("Diagonal #2", "OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE"),
 ("Diagonal #3", "WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG"),
 ("Diagonal #4", "BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI"),
 ("Vortex #1", "FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL"),
 ("Vortex #2", "PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI"),
 ("Vortex #3", "RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN"),
 ("Vortex #4", "DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB"),
]

def derive_next(identity: str):
 """Derive next layer identity."""
 body = identity[:56].lower()[:55]
 if len(body) != 55 or not body.isalpha():
 return None
 try:
 seed_bytes = bytes(body, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 return get_identity_from_public_key(public_key)
 except:
 return None

def check_exists_quick(rpc, identity: str) -> bool:
 """Quick existence check."""
 try:
 time.sleep(0.8) # Reduced delay
 balance = rpc.get_balance(identity)
 return balance is not None
 except:
 return False

def main():
 rpc = rpc_client.QubiPy_RPC()
 
 print("=== Quick Layer Depth Check ===\n")
 
 results = []
 
 for label, identity in LAYER2_IDENTITIES:
 print(f"{label}:", end=" ", flush=True)
 current = identity
 depth = 1 # Start counting from Layer 2
 
 for layer in range(2, 20): # Check up to Layer 19
 next_identity = derive_next(current)
 if not next_identity:
 break
 
 exists = check_exists_quick(rpc, next_identity)
 if not exists:
 break
 
 depth += 1
 current = next_identity
 print(f"L{layer}", end=" ", flush=True)
 
 results.append((label, depth))
 print(f"→ {depth} layers total")
 
 print("\n=== Summary ===")
 max_depth = max(d for _, d in results)
 min_depth = min(d for _, d in results)
 
 print(f"Max depth: {max_depth} layers")
 print(f"Min depth: {min_depth} layers")
 print(f"Average: {sum(d for _, d in results) / len(results):.1f} layers")
 
 print("\nPer chain:")
 for label, depth in results:
 print(f" {label}: {depth} layers")

if __name__ == "__main__":
 main()

