#!/usr/bin/env python3
"""
Mass Seed Derivation: Test all 221 verified identities as seeds.

This script:
1. Loads all 221 verified identities
2. Tests each as a seed (56-char body → lowercase → derive)
3. Checks derived identities on-chain
4. Maps recursively until no new identities are found
5. Saves complete structure
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

try:
 from qubipy.rpc import rpc_client
 from qubipy.crypto.utils import (
 identity_to_seed,
 derive_identity_from_seed,
 )
 HAS_QUBIPY = True
except ImportError:
 HAS_QUBIPY = False
 print("⚠️ QubiPy nicht verfügbar - verwende Docker")

OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "mass_seed_derivation.json"
OUTPUT_MD = OUTPUT_DIR / "mass_seed_derivation.md"

def load_verified_identities() -> Set[str]:
 """Load all 221 verified identities."""
 verified = set()
 
 path = Path("outputs/derived/all_identities_rpc_verification.json")
 if path.exists():
 with path.open() as f:
 data = json.load(f)
 verified = set(data.get("verified_identities", []))
 
 return verified

def identity_to_seed_candidate(identity: str) -> Optional[str]:
 """Convert identity to seed candidate (56-char body, lowercase)."""
 if len(identity) != 60:
 return None
 
 # Extract 56-char body (first 56 chars)
 body = identity[:56]
 
 # Convert to lowercase
 seed_candidate = body.lower()
 
 # Must be exactly 55 chars (seed requirement)
 if len(seed_candidate) != 55:
 return None
 
 return seed_candidate

def check_on_chain(rpc, identity: str, delay: float = 0.5) -> Tuple[bool, Optional[dict]]:
 """Check if identity exists on-chain."""
 try:
 time.sleep(delay) # Rate limiting
 balance_data = rpc.get_balance(identity)
 if balance_data:
 return True, {
 "exists": True,
 "balance": balance_data.get("balance", "0"),
 "valid_for_tick": balance_data.get("validForTick"),
 }
 else:
 return False, {"exists": False}
 except Exception as e:
 error_msg = str(e)
 if "429" in error_msg or "Too Many Requests" in error_msg:
 # Rate limiting - wait longer and retry
 time.sleep(2.0)
 try:
 balance_data = rpc.get_balance(identity)
 if balance_data:
 return True, {
 "exists": True,
 "balance": balance_data.get("balance", "0"),
 "valid_for_tick": balance_data.get("validForTick"),
 }
 except:
 pass
 return False, {"exists": False, "error": error_msg}

def derive_and_check(rpc, identity: str) -> Optional[Tuple[str, str]]:
 """
 Derive identity from seed and check on-chain.
 Returns (derived_identity, seed) if found, None otherwise.
 """
 seed = identity_to_seed_candidate(identity)
 if not seed:
 return None
 
 try:
 derived = derive_identity_from_seed(seed)
 if not derived:
 return None
 
 exists, data = check_on_chain(rpc, derived)
 if exists:
 return (derived, seed)
 except Exception:
 pass
 
 return None

def map_recursive_structure(
 rpc,
 start_identities: Set[str],
 max_depth: int = 15,
 max_identities: int = 1000,
) -> Dict:
 """
 Map complete recursive structure starting from given identities.
 """
 visited: Set[str] = set()
 layer_map: Dict[int, List[str]] = defaultdict(list)
 seed_map: Dict[str, str] = {} # identity -> seed
 parent_map: Dict[str, str] = {} # identity -> parent_identity
 
 # BFS queue: (identity, layer, parent)
 queue: List[Tuple[str, int, Optional[str]]] = [
 (id, 1, None) for id in start_identities
 ]
 
 print(f"Starting recursive mapping from {len(start_identities)} identities...")
 print(f"Max depth: {max_depth}, Max identities: {max_identities}")
 print()
 
 iteration = 0
 while queue and len(visited) < max_identities:
 current_identity, layer, parent = queue.pop(0)
 
 if current_identity in visited:
 continue
 
 visited.add(current_identity)
 layer_map[layer].append(current_identity)
 
 if parent:
 parent_map[current_identity] = parent
 
 if layer >= max_depth:
 continue
 
 iteration += 1
 if iteration % 10 == 0:
 print(f" Progress: {len(visited)} identities, Layer {layer}, Queue: {len(queue)}")
 
 # Try to derive next layer
 result = derive_and_check(rpc, current_identity)
 if result:
 derived, seed = result
 seed_map[current_identity] = seed
 queue.append((derived, layer + 1, current_identity))
 print(f" Layer {layer} → {layer+1}: {current_identity[:30]}... → {derived[:30]}... ✅")
 
 return {
 "total_identities": len(visited),
 "max_layer": max(layer_map.keys()) if layer_map else 0,
 "layer_map": {k: v for k, v in layer_map.items()},
 "seed_map": seed_map,
 "parent_map": parent_map,
 "all_identities": list(visited),
 }

def main() -> None:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("MASS SEED DERIVATION: ALLE 221 IDENTITÄTEN ALS SEEDS TESTEN")
 print("=" * 80)
 print()
 
 if not HAS_QUBIPY:
 print("❌ QubiPy nicht verfügbar")
 print(" Bitte in Docker ausführen:")
 print(" docker run --rm -v \"$PWD\":/workspace -w /workspace -e PYTHONPATH=/workspace qubic-proof python3 scripts/verify/mass_seed_derivation.py")
 return
 
 print("Load alle 221 verified Identitäten...")
 verified_identities = load_verified_identities()
 print(f"✅ {len(verified_identities)} Identitäten geloadn")
 print()
 
 print("Starte rekursive Mapping...")
 print("(Dies kann mehrere Stunden dauern wegen Rate-Limiting)")
 print()
 
 rpc = rpc_client.QubiPy_RPC()
 
 result = map_recursive_structure(
 rpc,
 verified_identities,
 max_depth=15,
 max_identities=2000, # Allow more identities
 )
 
 print()
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 print(f"Total Identitäten gefunden: {result['total_identities']}")
 print(f"Max Layer: {result['max_layer']}")
 print(f"Funktionierende Seeds: {len(result['seed_map'])}")
 print()
 
 print("Layer-Verteilung:")
 for layer in sorted(result['layer_map'].keys(), key=int):
 count = len(result['layer_map'][layer])
 print(f" Layer {layer}: {count} Identitäten")
 print()
 
 # Save results
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(result, f, indent=2)
 
 # Create markdown report
 with OUTPUT_MD.open("w", encoding="utf-8") as f:
 f.write("# Mass Seed Derivation Results\n\n")
 f.write(f"**Total Identitäten:** {result['total_identities']}\n")
 f.write(f"**Max Layer:** {result['max_layer']}\n")
 f.write(f"**Funktionierende Seeds:** {len(result['seed_map'])}\n\n")
 f.write("## Layer-Verteilung\n\n")
 for layer in sorted(result['layer_map'].keys(), key=int):
 count = len(result['layer_map'][layer])
 f.write(f"- **Layer {layer}:** {count} Identitäten\n")
 f.write("\n## Seed-Map\n\n")
 for identity, seed in list(result['seed_map'].items())[:20]:
 f.write(f"- `{identity[:50]}...` → Seed: `{seed}`\n")
 if len(result['seed_map']) > 20:
 f.write(f"\n... und {len(result['seed_map']) - 20} weitere\n")
 
 print(f"Ergebnisse gespeichert:")
 print(f" - {OUTPUT_JSON}")
 print(f" - {OUTPUT_MD}")

if __name__ == "__main__":
 main()

