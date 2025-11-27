#!/usr/bin/env python3
"""
Gemini Find Real Seeds - Optimized Version

Für ALLE 100 Identities finden, welche Transformationen die richtige Identity produzieren.
Optimiert mit Checkpoints und schnelleren Tests.
"""

import json
import sys
import subprocess
from pathlib import Path
import numpy as np
import openpyxl
from collections import defaultdict

project_root = Path(__file__).parent.parent.parent
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"
CHECKPOINT_FILE = project_root / "outputs" / "derived" / "gemini_find_seeds_checkpoint.json"
OUTPUT_FILE = project_root / "outputs" / "derived" / "gemini_all_real_seeds.json"

def derive_identity(seed: str) -> tuple[bool, str]:
 """Derive identity from seed using venv-tx."""
 script = f'''
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)
seed = "{seed}"
seed_bytes = seed.encode("utf-8")
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
'''
 
 if not VENV_PYTHON.exists():
 return False, "venv-tx not found"
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), '-c', script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 
 if result.returncode == 0 and result.stdout.strip():
 identity = result.stdout.strip()
 if len(identity) == 60:
 return True, identity
 return False, result.stderr.strip() or "Failed"
 except Exception as e:
 return False, str(e)

def get_original_diagonal_pattern():
 """Original diagonal pattern: 4 blocks of 14x14 diagonals."""
 base_row = 0
 coords = []
 for block in range(4):
 row_offset = base_row + (block // 2) * 16
 col_offset = (block % 2) * 16
 for j in range(14):
 row = row_offset + j
 col = col_offset + j
 if row < 128 and col < 128:
 coords.append((row, col))
 return coords[:55]

def main():
 """Main function."""
 print("=" * 80)
 print("GEMINI FIND REAL SEEDS - OPTIMIZED")
 print("=" * 80)
 print()
 
 if not VENV_PYTHON.exists():
 print("❌ venv-tx not found!")
 return
 
 # Load checkpoint if exists
 checkpoint = {}
 if CHECKPOINT_FILE.exists():
 with CHECKPOINT_FILE.open() as f:
 checkpoint = json.load(f)
 print(f"📂 Loaded checkpoint: {checkpoint.get('last_identity_index', 0)}/{checkpoint.get('total', 0)}")
 print()
 
 # Load matrix
 print("1. Loading matrix...")
 sys.stdout.flush()
 matrix_path = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
 wb = openpyxl.load_workbook(matrix_path, data_only=True)
 ws = wb.active
 
 matrix = []
 for row in ws.iter_rows(min_row=1, max_row=128, min_col=1, max_col=128, values_only=True):
 row_values = []
 for cell in row:
 if cell is None:
 row_values.append(0.0)
 elif isinstance(cell, (int, float)):
 row_values.append(float(cell))
 else:
 row_values.append(0.0)
 matrix.append(row_values)
 
 matrix = np.array(matrix)
 print(f" ✅ Matrix loaded: {matrix.shape}")
 print()
 sys.stdout.flush()
 
 # Load ALL 100 identities
 print("2. Loading all 100 identities...")
 sys.stdout.flush()
 seeds_file = project_root / "github_export" / "100_seeds_and_identities.json"
 with seeds_file.open() as f:
 data = json.load(f)
 
 if isinstance(data, dict) and "seeds_and_identities" in data:
 all_identities = data["seeds_and_identities"]
 else:
 all_identities = data if isinstance(data, list) else []
 
 print(f" ✅ Loaded {len(all_identities)} identities")
 print()
 sys.stdout.flush()
 
 # Key transformations (most promising based on previous tests)
 transformations = [
 ("Raw (Absolute) % 26", lambda v: abs(int(v)) % 26),
 ("Raw % 26", lambda v: int(v) % 26),
 ("Raw + 1 % 26", lambda v: (int(v) + 1) % 26),
 ("Raw - 1 % 26", lambda v: (int(v) - 1) % 26),
 ("Raw + 14 % 26", lambda v: (int(v) + 14) % 26),
 ("Raw + Index % 26", lambda v, i: (int(v) + i) % 26),
 ("Raw - Index % 26", lambda v, i: (int(v) - i) % 26),
 ]
 
 # Use original diagonal pattern (most likely to work)
 coords = get_original_diagonal_pattern()
 
 # Load existing results
 matches_found = checkpoint.get("matches", [])
 pattern_stats = defaultdict(int, checkpoint.get("pattern_stats", {}))
 start_idx = checkpoint.get("last_identity_index", 0)
 
 print("3. Testing identities...")
 print(f" Starting from identity #{start_idx + 1}")
 print()
 sys.stdout.flush()
 
 for identity_idx, item in enumerate(all_identities[start_idx:], start=start_idx + 1):
 target_identity = item.get("identity", "")
 target_seed = item.get("seed", "")
 
 if identity_idx % 5 == 0:
 print(f"Progress: {identity_idx}/{len(all_identities)} (Matches: {len(matches_found)})")
 sys.stdout.flush()
 
 # Save checkpoint
 CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
 with CHECKPOINT_FILE.open("w") as f:
 json.dump({
 "last_identity_index": identity_idx - 1,
 "total": len(all_identities),
 "matches": matches_found,
 "pattern_stats": dict(pattern_stats)
 }, f, indent=2)
 
 # Extract raw values (same pattern for all)
 raw_vals = []
 for r, c in coords[:55]:
 if r < 128 and c < 128:
 raw_vals.append(float(matrix[r, c]))
 else:
 raw_vals.append(0.0)
 
 if len(raw_vals) < 55:
 continue
 
 # Test each transformation
 for name, func in transformations:
 try:
 import inspect
 if len(inspect.signature(func).parameters) == 2:
 indices = [func(v, i) % 26 for i, v in enumerate(raw_vals)]
 else:
 indices = [func(v) % 26 for v in raw_vals]
 
 seed_candidate = "".join(chr(ord('a') + (i % 26)) for i in indices)
 
 # Derive identity
 success, derived_id = derive_identity(seed_candidate)
 
 if success:
 match = (derived_id == target_identity)
 
 if match:
 print(f"✅ MATCH! Identity #{identity_idx}")
 print(f" Method: {name}")
 print(f" Seed: {seed_candidate}")
 print(f" Identity: {derived_id}")
 print()
 sys.stdout.flush()
 
 matches_found.append({
 "identity_index": identity_idx,
 "target_identity": target_identity,
 "target_seed": target_seed,
 "method": name,
 "real_seed": seed_candidate,
 "derived_identity": derived_id
 })
 
 pattern_stats[name] += 1
 break # Found match, move to next identity
 
 except Exception as e:
 pass # Skip errors
 
 # Save final results
 OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
 
 with OUTPUT_FILE.open("w") as f:
 json.dump({
 "total_identities_tested": len(all_identities),
 "matches_found": len(matches_found),
 "pattern_statistics": dict(pattern_stats),
 "matches": matches_found
 }, f, indent=2)
 
 print("=" * 80)
 print("TEST COMPLETE")
 print("=" * 80)
 print(f"✅ Results saved to: {OUTPUT_FILE}")
 print()
 print(f"Summary:")
 print(f" Total identities tested: {len(all_identities)}")
 print(f" Matches found: {len(matches_found)}")
 print()
 
 if pattern_stats:
 print("Pattern Statistics:")
 for method, count in sorted(pattern_stats.items(), key=lambda x: -x[1]):
 print(f" {method}: {count}")
 
 if matches_found:
 print()
 print("🎉 MATCHES FOUND!")
 print(f" {len(matches_found)} identities matched with real seeds")
 print()
 print("Sample matches:")
 for match in matches_found[:10]:
 print(f" Identity #{match['identity_index']}: {match['method']}")

if __name__ == "__main__":
 main()

