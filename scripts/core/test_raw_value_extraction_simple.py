#!/usr/bin/env python3
"""
Simplified Raw Value Seed Extraction Test
"""

import json
import sys
from pathlib import Path
import numpy as np
import openpyxl

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load matrix
matrix_path = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
print(f"Loading matrix from {matrix_path}...")

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
print(f"✅ Matrix loaded: {matrix.shape}")
print(f"Sample values at (0,0): {matrix[0, 0]}, (0,1): {matrix[0, 1]}")

# Load test data
seeds_file = project_root / "github_export" / "100_seeds_and_identities.json"
with seeds_file.open() as f:
 data = json.load(f)

if isinstance(data, dict) and "seeds_and_identities" in data:
 test_data = data["seeds_and_identities"]
else:
 test_data = data if isinstance(data, list) else []

print(f"✅ Loaded {len(test_data)} test identities")

# Get first identity
first_item = test_data[0]
documented_identity = first_item.get("identity", "")
documented_seed = first_item.get("seed", "")

print(f"\nFirst Identity: {documented_identity[:50]}...")
print(f"Documented Seed: {documented_seed[:50]}...")

# Get diagonal coordinates for identity 1
# Base row 0, 4 blocks of 14 chars each
coords = []
base_row = 0
for block in range(4):
 row_offset = base_row + (block // 2) * 16
 col_offset = (block % 2) * 16
 for j in range(14):
 row = row_offset + j
 col = col_offset + j
 if row < 128 and col < 128:
 coords.append((row, col))

print(f"\n✅ Got {len(coords)} coordinates")
print(f"First 5 coords: {coords[:5]}")

# Extract raw values
raw_vals = []
for i, (r, c) in enumerate(coords[:55]):
 raw_vals.append(float(matrix[r, c]))

print(f"\n✅ Extracted {len(raw_vals)} raw values")
print(f"First 10 raw values: {raw_vals[:10]}")

# Test simple transformation: Raw % 26
seed_candidate = "".join(chr(ord('a') + (int(v) % 26)) for v in raw_vals)
print(f"\nSeed candidate (Raw % 26): {seed_candidate[:50]}...")
print(f"Length: {len(seed_candidate)}")

# Compare with documented seed
print(f"\nDocumented seed: {documented_seed[:50]}...")
print(f"Match: {'✅' if seed_candidate == documented_seed else '❌'}")

# Save results
output_file = project_root / "outputs" / "derived" / "raw_value_test_results.json"
output_file.parent.mkdir(parents=True, exist_ok=True)

with output_file.open("w") as f:
 json.dump({
 "documented_identity": documented_identity,
 "documented_seed": documented_seed,
 "seed_candidate": seed_candidate,
 "match": seed_candidate == documented_seed,
 "raw_values": raw_vals[:20], # First 20 for inspection
 "coordinates": coords[:20]
 }, f, indent=2)

print(f"\n✅ Results saved to: {output_file}")

