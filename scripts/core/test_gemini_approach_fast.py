#!/usr/bin/env python3
"""
Test Gemini's Raw Value Approach - Fast Version (ohne Docker for erste Tests)
"""

import json
import sys
from pathlib import Path
import numpy as np
import openpyxl

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("GEMINI RAW VALUE SEED EXTRACTION TEST (Fast - No Docker)")
print("=" * 80)
print()

# 1. Load matrix
print("1. Loading matrix...")
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
print(f" Sample at (0,0): {matrix[0, 0]}, (0,1): {matrix[0, 1]}")
print()

# 2. Load test data
print("2. Loading test data...")
seeds_file = project_root / "github_export" / "100_seeds_and_identities.json"
with seeds_file.open() as f:
 data = json.load(f)

if isinstance(data, dict) and "seeds_and_identities" in data:
 test_data = data["seeds_and_identities"]
else:
 test_data = data if isinstance(data, list) else []

print(f" ✅ Loaded {len(test_data)} items")
first_item = test_data[0]
documented_identity = first_item.get("identity", "")
documented_seed = first_item.get("seed", "")
print(f" First identity: {documented_identity[:40]}...")
print(f" Documented seed: {documented_seed[:40]}...")
print()

# 3. Get coordinates for identity 1
print("3. Getting coordinates...")
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

print(f" ✅ Got {len(coords)} coordinates")
print(f" First 5: {coords[:5]}")
print()

# 4. Extract raw values
print("4. Extracting raw values...")
raw_vals = []
for i, (r, c) in enumerate(coords[:55]):
 raw_vals.append(float(matrix[r, c]))

print(f" ✅ Extracted {len(raw_vals)} raw values")
print(f" First 10: {raw_vals[:10]}")
print()

# 5. Test transformations (ohne Docker - nur Seed-Generierung)
print("5. Testing transformations (Seed generation only, no validation)...")
print()

transformations = [
 ("Raw % 26", lambda v: int(v) % 26),
 ("Raw + 1 % 26", lambda v: (int(v) + 1) % 26),
 ("Raw - 1 % 26", lambda v: (int(v) - 1) % 26),
 ("Raw (Absolute) % 26", lambda v: abs(int(v)) % 26),
 ("Raw + 14 % 26", lambda v: (int(v) + 14) % 26),
 ("Raw + Index % 26", lambda v, i: (int(v) + i) % 26),
 ("Raw - Index % 26", lambda v, i: (int(v) - i) % 26),
 ("Raw + 26 % 26", lambda v: (int(v) + 26) % 26),
 ("Raw - 26 % 26", lambda v: (int(v) - 26) % 26),
 ("Raw mod 26 (floor)", lambda v: int(np.floor(v)) % 26),
 ("Raw mod 26 (ceil)", lambda v: int(np.ceil(v)) % 26),
 ("Raw * 2 % 26", lambda v: (int(v) * 2) % 26),
 ("Raw / 2 % 26", lambda v: int(v / 2) % 26 if v != 0 else 0),
 ("Raw XOR 13 % 26", lambda v: (int(v) ^ 13) % 26),
 ("Raw + 7 % 26", lambda v: (int(v) + 7) % 26),
 ("Raw - 7 % 26", lambda v: (int(v) - 7) % 26),
 ("Raw + 13 % 26", lambda v: (int(v) + 13) % 26),
 ("Raw - 13 % 26", lambda v: (int(v) - 13) % 26),
]

results = []

for name, func in transformations:
 try:
 import inspect
 if len(inspect.signature(func).parameters) == 2:
 indices = [func(v, i) % 26 for i, v in enumerate(raw_vals)]
 else:
 indices = [func(v) % 26 for v in raw_vals]
 
 seed_candidate = "".join(chr(ord('a') + (i % 26)) for i in indices)
 
 # Compare with documented seed
 match_with_doc_seed = (seed_candidate == documented_seed)
 
 print(f" {name:<25} -> Seed: {seed_candidate[:40]}...")
 print(f" {'✅ MATCH with documented seed!' if match_with_doc_seed else '❌ No match'}")
 
 results.append({
 "method": name,
 "seed": seed_candidate,
 "match_with_documented_seed": match_with_doc_seed,
 "documented_seed": documented_seed
 })
 
 if match_with_doc_seed:
 print(f"\n🎉 FOUND IT! Seed matches documented seed!")
 # Don't break - test all transformations
 
 print()
 
 except Exception as e:
 print(f" Error: {e}")
 print()

# 6. Save results
print("6. Saving results...")
output_file = project_root / "outputs" / "derived" / "gemini_raw_value_test_fast.json"
output_file.parent.mkdir(parents=True, exist_ok=True)

with output_file.open("w") as f:
 json.dump({
 "documented_identity": documented_identity,
 "documented_seed": documented_seed,
 "raw_values_sample": raw_vals[:20],
 "results": results
 }, f, indent=2)

print(f" ✅ Results saved to: {output_file}")
print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print()
print("Note: This test only generates seeds, it doesn't validate them with QubiPy.")
print("To validate, run the Docker version or ensure QubiPy is installed locally.")

