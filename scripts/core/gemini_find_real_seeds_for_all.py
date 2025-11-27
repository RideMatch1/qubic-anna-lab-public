#!/usr/bin/env python3
"""
Gemini Find Real Seeds for All Identities

Für ALLE 100 Identities finden, welche Transformationen die richtige Identity produzieren.
Ziel: Pattern/Muster erkennen durch Verknüpfung vieler echter Seeds mit echten IDs.
"""

import json
import sys
import subprocess
from pathlib import Path
import numpy as np
import openpyxl
from collections import defaultdict

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

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
 timeout=30,
 cwd=project_root
 )
 
 if result.returncode == 0 and result.stdout.strip():
 identity = result.stdout.strip()
 if len(identity) == 60:
 return True, identity
 else:
 return False, f"Invalid identity length: {len(identity)}"
 else:
 return False, result.stderr.strip() or "Execution failed"
 except Exception as e:
 return False, str(e)

def get_diagonal_coordinates(identity_index: int) -> list:
 """Get coordinates for diagonal extraction pattern (same as original extraction)."""
 # Original pattern: 4 blocks, each 14x14 diagonal
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

def get_vortex_coordinates(vortex_num: int) -> list:
 """Get coordinates for vortex pattern."""
 # Vortex patterns start at different positions
 # This is a placeholder - need to find actual vortex coordinates
 base_row = 0
 base_col = 0
 
 coords = []
 # Vortex pattern (spiral)
 # TODO: Implement actual vortex extraction
 return coords[:55]

def main():
 """Main function."""
 print("=" * 80)
 print("GEMINI FIND REAL SEEDS FOR ALL IDENTITIES")
 print("=" * 80)
 print()
 
 if not VENV_PYTHON.exists():
 print("❌ venv-tx not found!")
 return
 
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
 
 # All transformations to test
 transformations = [
 ("Raw (Absolute) % 26", lambda v: abs(int(v)) % 26),
 ("Raw % 26", lambda v: int(v) % 26),
 ("Raw + 1 % 26", lambda v: (int(v) + 1) % 26),
 ("Raw - 1 % 26", lambda v: (int(v) - 1) % 26),
 ("Raw + 14 % 26", lambda v: (int(v) + 14) % 26),
 ("Raw - 14 % 26", lambda v: (int(v) - 14) % 26),
 ("Raw + 7 % 26", lambda v: (int(v) + 7) % 26),
 ("Raw - 7 % 26", lambda v: (int(v) - 7) % 26),
 ("Raw + 13 % 26", lambda v: (int(v) + 13) % 26),
 ("Raw - 13 % 26", lambda v: (int(v) - 13) % 26),
 ("Raw + Index % 26", lambda v, i: (int(v) + i) % 26),
 ("Raw - Index % 26", lambda v, i: (int(v) - i) % 26),
 ("Raw * 2 % 26", lambda v: (int(v) * 2) % 26),
 ("Raw / 2 % 26", lambda v: int(v / 2) % 26 if v != 0 else 0),
 ("Raw XOR 13 % 26", lambda v: (int(v) ^ 13) % 26),
 ]
 
 # Try different coordinate patterns (based on original extraction methods)
 # Original: 4 diagonal blocks starting at (0,0), (0,16), (16,0), (16,16)
 def get_original_diagonal_pattern(identity_idx):
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
 
 coordinate_patterns = [
 ("Original_Diagonal", get_original_diagonal_pattern),
 ("Diagonal_0_0", lambda idx: [(i, i) for i in range(55)]),
 ("Diagonal_0_32", lambda idx: [(i, (i + 32) % 128) for i in range(55)]),
 ("Diagonal_0_64", lambda idx: [(i, (i + 64) % 128) for i in range(55)]),
 ("Block_0_0", lambda idx: [(r, c) for r in range(8) for c in range(7)][:55]),
 ("Block_0_16", lambda idx: [(r, c + 16) for r in range(8) for c in range(7)][:55]),
 ("Block_16_0", lambda idx: [(r + 16, c) for r in range(8) for c in range(7)][:55]),
 ("Block_16_16", lambda idx: [(r + 16, c + 16) for r in range(8) for c in range(7)][:55]),
 ]
 
 all_results = []
 matches_found = []
 pattern_stats = defaultdict(int)
 
 print("3. Testing all identities...")
 print()
 sys.stdout.flush()
 
 for identity_idx, item in enumerate(all_identities, 1):
 target_identity = item.get("identity", "")
 target_seed = item.get("seed", "")
 
 if identity_idx % 10 == 0:
 print(f"Progress: {identity_idx}/{len(all_identities)}")
 sys.stdout.flush()
 
 found_match = False
 
 # Try each coordinate pattern
 for pattern_name, pattern_func in coordinate_patterns:
 if found_match:
 break
 
 coords = pattern_func(identity_idx)
 if len(coords) < 55:
 continue
 
 # Extract raw values
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
 print(f" Pattern: {pattern_name}")
 print(f" Method: {name}")
 print(f" Seed: {seed_candidate}")
 print(f" Identity: {derived_id}")
 print()
 sys.stdout.flush()
 
 matches_found.append({
 "identity_index": identity_idx,
 "target_identity": target_identity,
 "target_seed": target_seed,
 "pattern": pattern_name,
 "method": name,
 "real_seed": seed_candidate,
 "derived_identity": derived_id,
 "coordinates": coords[:55]
 })
 
 pattern_stats[f"{pattern_name}_{name}"] += 1
 found_match = True
 break
 
 # Store all results for analysis
 all_results.append({
 "identity_index": identity_idx,
 "target_identity": target_identity,
 "pattern": pattern_name,
 "method": name,
 "seed": seed_candidate,
 "derived_identity": derived_id,
 "match": match
 })
 
 except Exception as e:
 pass # Skip errors
 
 # Save results
 output_file = project_root / "outputs" / "derived" / "gemini_all_real_seeds.json"
 output_file.parent.mkdir(parents=True, exist_ok=True)
 
 with output_file.open("w") as f:
 json.dump({
 "total_identities_tested": len(all_identities),
 "matches_found": len(matches_found),
 "pattern_statistics": dict(pattern_stats),
 "matches": matches_found,
 "all_results_sample": all_results[:100] # Sample for analysis
 }, f, indent=2)
 
 print("=" * 80)
 print("TEST COMPLETE")
 print("=" * 80)
 print(f"✅ Results saved to: {output_file}")
 print()
 print(f"Summary:")
 print(f" Total identities tested: {len(all_identities)}")
 print(f" Matches found: {len(matches_found)}")
 print()
 
 if pattern_stats:
 print("Pattern Statistics:")
 for pattern_method, count in sorted(pattern_stats.items(), key=lambda x: -x[1]):
 print(f" {pattern_method}: {count}")
 
 if matches_found:
 print()
 print("🎉 MATCHES FOUND!")
 print(f" {len(matches_found)} identities matched with real seeds")
 print()
 print("Sample matches:")
 for match in matches_found[:10]:
 print(f" Identity #{match['identity_index']}: {match['pattern']} + {match['method']}")
 else:
 print("❌ No matches found")

if __name__ == "__main__":
 main()

