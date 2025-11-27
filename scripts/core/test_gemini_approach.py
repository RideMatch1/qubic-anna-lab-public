#!/usr/bin/env python3
"""
Test Gemini's Raw Value Approach
Vereinfachte Version die direkt funktioniert
"""

import json
import subprocess
import sys
from pathlib import Path
import numpy as np
import openpyxl

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("GEMINI RAW VALUE SEED EXTRACTION TEST")
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

# 5. Test transformations
print("5. Testing transformations...")
print()

transformations = [
 ("Raw % 26", lambda v: int(v) % 26),
 ("Raw + 1 % 26", lambda v: (int(v) + 1) % 26),
 ("Raw - 1 % 26", lambda v: (int(v) - 1) % 26),
 ("Raw (Absolute) % 26", lambda v: abs(int(v)) % 26),
]

results = []

for name, func in transformations:
 try:
 indices = [func(v) % 26 for v in raw_vals]
 seed_candidate = "".join(chr(ord('a') + (i % 26)) for i in indices)
 
 print(f" Testing: {name}")
 print(f" Seed: {seed_candidate[:40]}...")
 
 # Test with Docker
 script = f'''
from qubipy.crypto.utils import get_subseed_from_seed, get_private_key_from_subseed, get_public_key_from_private_key, get_identity_from_public_key
seed = "{seed_candidate}"
seed_bytes = seed.encode("utf-8")
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
'''
 
 print(f" Calling Docker (this may take a while)...")
 sys.stdout.flush()
 
 result = subprocess.run(
 ['docker', 'run', '--rm', '-v', f'{project_root}:/workspace', '-w', '/workspace',
 'python:3.11', 'bash', '-c', f'pip install -q qubipy && python3 -c """{script}"""'],
 capture_output=True,
 text=True,
 timeout=120 # Increased timeout
 )
 
 print(f" Docker returned (code: {result.returncode})")
 sys.stdout.flush()
 
 if result.returncode == 0 and result.stdout.strip():
 derived_identity = result.stdout.strip()
 match = (derived_identity == documented_identity)
 status = "✅ MATCH!" if match else "❌"
 print(f" Derived: {derived_identity[:40]}...")
 print(f" Status: {status}")
 
 results.append({
 "method": name,
 "seed": seed_candidate,
 "derived_identity": derived_identity,
 "match": match
 })
 
 if match:
 print(f"\n🎉 FOUND IT! Seed: {seed_candidate}")
 break
 else:
 print(f" Error: {result.stderr[:100]}")
 results.append({
 "method": name,
 "seed": seed_candidate,
 "error": result.stderr[:200]
 })
 
 print()
 
 except Exception as e:
 print(f" Error: {e}")
 print()

# 6. Save results
print("6. Saving results...")
output_file = project_root / "outputs" / "derived" / "gemini_raw_value_test.json"
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

