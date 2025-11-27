#!/usr/bin/env python3
"""Simplified version - test first 8 identities"""

import json
import subprocess
from pathlib import Path
import numpy as np
import openpyxl
import sys

project_root = Path(__file__).parent.parent.parent
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def derive_identity(seed):
 script = f'from qubipy.crypto.utils import get_subseed_from_seed, get_private_key_from_subseed, get_public_key_from_private_key, get_identity_from_public_key; seed = "{seed}"; seed_bytes = seed.encode("utf-8"); subseed = get_subseed_from_seed(seed_bytes); private_key = get_private_key_from_subseed(subseed); public_key = get_public_key_from_private_key(private_key); identity = get_identity_from_public_key(public_key); print(identity)'
 result = subprocess.run([str(VENV_PYTHON), '-c', script], capture_output=True, text=True, timeout=30, cwd=project_root)
 if result.returncode == 0 and result.stdout.strip():
 return True, result.stdout.strip()
 return False, result.stderr.strip() or "Failed"

print("=" * 80)
print("GEMINI TEST - FIRST 8 IDENTITIES")
print("=" * 80)
print()
sys.stdout.flush()

# Load matrix
print("Loading matrix...")
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
print(f"Matrix loaded: {matrix.shape}")
print()
sys.stdout.flush()

# Load test data
print("Loading test data...")
sys.stdout.flush()
seeds_file = project_root / "github_export" / "100_seeds_and_identities.json"
with seeds_file.open() as f:
 data = json.load(f)

if isinstance(data, dict) and "seeds_and_identities" in data:
 test_data = data["seeds_and_identities"]
else:
 test_data = data if isinstance(data, list) else []

print(f"Loaded {len(test_data)} identities")
print()
sys.stdout.flush()

# Test first 8
transformations = [
 ("Raw (Absolute) % 26", lambda v: abs(int(v)) % 26),
 ("Raw % 26", lambda v: int(v) % 26),
 ("Raw + 1 % 26", lambda v: (int(v) + 1) % 26),
]

all_results = []

for identity_idx in range(min(8, len(test_data))):
 item = test_data[identity_idx]
 target_identity = item.get("identity", "")
 target_seed = item.get("seed", "")
 
 print(f"Identity #{identity_idx + 1}: {target_identity[:50]}...")
 print()
 sys.stdout.flush()
 
 # Get coordinates (diagonal pattern)
 base_row = (identity_idx) * 16
 coords = []
 for block in range(4):
 row_offset = base_row + (block // 2) * 16
 col_offset = (block % 2) * 16
 for j in range(14):
 row = row_offset + j
 col = col_offset + j
 if row < 128 and col < 128:
 coords.append((row, col))
 
 coords = coords[:55]
 
 # Extract raw values
 raw_vals = [float(matrix[r, c]) for r, c in coords]
 
 print(f" Extracted {len(raw_vals)} raw values")
 sys.stdout.flush()
 
 # Test transformations
 for name, func in transformations:
 try:
 indices = [func(v) % 26 for v in raw_vals]
 seed_candidate = "".join(chr(ord('a') + (i % 26)) for i in indices)
 
 success, derived_id = derive_identity(seed_candidate)
 
 if success:
 match = (derived_id == target_identity)
 status = "✅ MATCH!" if match else "❌"
 print(f" {name:<25} -> {status} {derived_id[:50]}...")
 sys.stdout.flush()
 
 all_results.append({
 "identity_index": identity_idx + 1,
 "target_identity": target_identity,
 "method": name,
 "seed": seed_candidate,
 "derived_identity": derived_id,
 "match": match
 })
 
 if match:
 print(f" 🎉 FOUND IT!")
 print()
 sys.stdout.flush()
 break
 else:
 print(f" {name:<25} -> ❌ Failed: {derived_id[:50]}")
 sys.stdout.flush()
 except Exception as e:
 print(f" {name:<25} -> ❌ Error: {e}")
 sys.stdout.flush()
 
 print()
 sys.stdout.flush()

# Save
output_file = project_root / "outputs" / "derived" / "gemini_all_identities_test.json"
output_file.parent.mkdir(parents=True, exist_ok=True)

with output_file.open("w") as f:
 json.dump({
 "total_identities_tested": min(8, len(test_data)),
 "matches_found": sum(1 for r in all_results if r.get("match")),
 "results": all_results
 }, f, indent=2)

print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print(f"Results saved to: {output_file}")
print()
sys.stdout.flush()

matches = [r for r in all_results if r.get("match")]
if matches:
 print(f"🎉 Found {len(matches)} match(es)!")
 for m in matches:
 print(f" Identity #{m['identity_index']}: {m['method']}")
else:
 print("❌ No matches found")

