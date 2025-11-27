#!/usr/bin/env python3
"""
Raw Value Seed Extraction - Docker Version
Uses Docker to run QubiPy for identity derivation.
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
import openpyxl

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_matrix() -> Optional[np.ndarray]:
 """Load the Anna Matrix from Excel."""
 matrix_path = project_root / "data" / "anna-matrix" / "Anna_Matrix.xlsx"
 
 if not matrix_path.exists():
 print(f"❌ Matrix file not found: {matrix_path}")
 return None
 
 print(f"Loading matrix from {matrix_path}...")
 try:
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
 
 return np.array(matrix)
 except Exception as e:
 print(f"Error loading matrix: {e}")
 return None

def get_diagonal_coordinates(identity_index: int = 1) -> List[Tuple[int, int]]:
 """Get coordinates for diagonal extraction pattern."""
 base_row = (identity_index - 1) * 32
 
 coords = []
 for block in range(4):
 row_offset = base_row + (block // 2) * 16
 col_offset = (block % 2) * 16
 
 for j in range(14):
 row = row_offset + j
 col = col_offset + j
 if row < 128 and col < 128:
 coords.append((row, col))
 
 return coords

def extract_raw_sequence(matrix: np.ndarray, coords: List[Tuple[int, int]], length: int = 55) -> List[float]:
 """Extract raw values sequence from coordinates."""
 raw_values = []
 for i, (r, c) in enumerate(coords[:length]):
 if 0 <= r < 128 and 0 <= c < 128:
 raw_values.append(float(matrix[r, c]))
 return raw_values

def derive_identity_docker(seed_candidate: str) -> Tuple[bool, str]:
 """Derive identity from seed using Docker."""
 try:
 script = f'''
import sys
sys.path.insert(0, "/workspace")
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)
seed = "{seed_candidate}"
seed_bytes = seed.encode("utf-8")
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
'''
 
 result = subprocess.run(
 ['docker', 'run', '--rm', '-v', f'{project_root}:/workspace', '-w', '/workspace',
 'python:3.11', 'bash', '-c', f'pip install -q qubipy && python3 -c """{script}"""'],
 capture_output=True,
 text=True,
 timeout=30
 )
 
 if result.returncode == 0 and result.stdout.strip():
 identity = result.stdout.strip()
 if len(identity) == 60:
 return True, identity
 else:
 return False, f"Invalid identity length: {len(identity)}"
 else:
 return False, result.stderr.strip() or "Docker execution failed"
 except subprocess.TimeoutExpired:
 return False, "Docker timeout"
 except Exception as e:
 return False, f"Docker error: {str(e)}"

def test_transformations(raw_vals: List[float], target_identity: str) -> List[Dict]:
 """Test various transformations on raw values."""
 results = []
 
 transformations = [
 ("Raw % 26 (Baseline)", lambda v: int(v) % 26),
 ("Raw + 1 % 26", lambda v: (int(v) + 1) % 26),
 ("Raw - 1 % 26", lambda v: (int(v) - 1) % 26),
 ("Raw + 14 % 26", lambda v: (int(v) + 14) % 26),
 ("Raw (Absolute) % 26", lambda v: abs(int(v)) % 26),
 ("Raw / 2 % 26", lambda v: int(v / 2) % 26 if v != 0 else 0),
 ("Raw * 2 % 26", lambda v: int(v * 2) % 26),
 ("Raw + Index % 26", lambda v, i: (int(v) + i) % 26),
 ("Raw - Index % 26", lambda v, i: (int(v) - i) % 26),
 ("Raw + 26 % 26", lambda v: (int(v) + 26) % 26),
 ("Raw - 26 % 26", lambda v: (int(v) - 26) % 26),
 ("Raw mod 26 (floor)", lambda v: int(np.floor(v)) % 26),
 ("Raw mod 26 (ceil)", lambda v: int(np.ceil(v)) % 26),
 ]
 
 for name, func in transformations:
 try:
 import inspect
 if len(inspect.signature(func).parameters) == 2:
 indices = [func(v, i) % 26 for i, v in enumerate(raw_vals)]
 else:
 indices = [func(v) % 26 for v in raw_vals]
 
 seed_candidate = "".join(chr(ord('a') + (i % 26)) for i in indices)
 
 # Check with Docker
 success, derived_id = derive_identity_docker(seed_candidate)
 match = (derived_id == target_identity) if success else False
 
 results.append({
 "method": name,
 "seed": seed_candidate,
 "derived_identity": derived_id if success else "N/A",
 "match": match,
 "success": success
 })
 
 status = "✅ MATCH!" if match else ("✅" if success else "❌")
 print(f" {name:<25} -> {seed_candidate[:20]}... -> {derived_id[:20] if success else 'N/A'}... {status}")
 
 if match:
 print(f"\n🎉 FOUND IT! The True Seed is: {seed_candidate}")
 break
 
 except Exception as e:
 print(f" Error testing {name}: {e}")
 results.append({
 "method": name,
 "seed": "ERROR",
 "derived_identity": str(e),
 "match": False,
 "success": False
 })
 
 return results

def load_test_data() -> List[Dict]:
 """Load test data."""
 seeds_file = project_root / "github_export" / "100_seeds_and_identities.json"
 
 if not seeds_file.exists():
 return []
 
 with seeds_file.open() as f:
 data = json.load(f)
 
 if isinstance(data, dict) and "seeds_and_identities" in data:
 return data["seeds_and_identities"]
 elif isinstance(data, list):
 return data
 return []

def main():
 """Main function."""
 print("=" * 80)
 print("RAW VALUE SEED EXTRACTION (Docker)")
 print("=" * 80)
 print()
 
 # Check Docker
 try:
 result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
 if result.returncode != 0:
 print("❌ Docker not available!")
 return
 print(f"✅ Docker available: {result.stdout.strip()}")
 except FileNotFoundError:
 print("❌ Docker not found!")
 return
 
 print()
 
 # Load matrix
 matrix = load_matrix()
 if matrix is None:
 return
 
 print(f"✅ Matrix loaded: {matrix.shape}")
 print()
 
 # Load test data
 test_data = load_test_data()
 if not test_data:
 print("❌ No test data found!")
 return
 
 print(f"✅ Loaded {len(test_data)} test identities")
 print()
 
 # Test first 3 identities (Docker is slow)
 all_results = []
 
 for idx, item in enumerate(test_data[:3], 1):
 documented_identity = item.get("identity", "")
 seed = item.get("seed", "")
 
 if not documented_identity or not seed:
 continue
 
 print(f"Testing Identity #{idx}: {documented_identity[:30]}...")
 print(f" Documented Seed: {seed[:30]}...")
 
 # Get coordinates
 coords = get_diagonal_coordinates(idx)
 
 if not coords:
 print(" ⚠️ No coordinates found")
 continue
 
 # Extract raw values
 raw_vals = extract_raw_sequence(matrix, coords, length=55)
 
 if len(raw_vals) < 55:
 print(f" ⚠️ Only {len(raw_vals)} raw values extracted")
 continue
 
 print(f" ✅ Extracted {len(raw_vals)} raw values")
 print(f" Sample: {raw_vals[:5]}")
 print()
 
 # Test transformations
 print(" Testing transformations (using Docker)...")
 results = test_transformations(raw_vals, documented_identity)
 
 for result in results:
 result["identity_index"] = idx
 result["documented_identity"] = documented_identity
 result["documented_seed"] = seed
 
 all_results.extend(results)
 
 # Check if we found a match
 if any(r.get("match") for r in results):
 print(f"\n🎉 MATCH FOUND for Identity #{idx}!")
 break
 
 print()
 
 # Save results
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_file = OUTPUT_DIR / "raw_value_seed_extraction_results.json"
 with output_file.open("w") as f:
 json.dump({
 "total_tested": len(test_data[:3]),
 "results": all_results
 }, f, indent=2)
 
 print(f"✅ Results saved to: {output_file}")
 print()
 print("=" * 80)
 print("ANALYSIS COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

