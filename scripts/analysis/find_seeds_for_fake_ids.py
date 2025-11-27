#!/usr/bin/env python3
"""
Find Seeds for Fake IDs

Versucht die echten Seeds zu finden, die die dokumentierten ("Fake") IDs produzieren.
Testet verschiedene Transformationen und Methoden.
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import openpyxl

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"
INPUT_FILE = project_root / "outputs" / "derived" / "complete_24846_seeds_to_real_ids_mapping.json"
OUTPUT_DIR = project_root / "outputs" / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def derive_identity_from_seed(seed: str) -> tuple[bool, str]:
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

def test_seed_transformations(false_seed: str, target_identity: str) -> List[Dict]:
 """Teste verschiedene Transformationen des False Seeds."""
 results = []
 
 transformations = [
 ("Original", lambda s: s),
 ("Reverse", lambda s: s[::-1]),
 ("Uppercase", lambda s: s.upper()),
 ("Rotate +1", lambda s: "".join(chr((ord(c) - ord('a') + 1) % 26 + ord('a')) for c in s)),
 ("Rotate -1", lambda s: "".join(chr((ord(c) - ord('a') - 1) % 26 + ord('a')) for c in s)),
 ("Rotate +13", lambda s: "".join(chr((ord(c) - ord('a') + 13) % 26 + ord('a')) for c in s)),
 ("XOR with index", lambda s: "".join(chr((ord(c) ^ i) % 26 + ord('a')) for i, c in enumerate(s))),
 ("Add index", lambda s: "".join(chr((ord(c) - ord('a') + i) % 26 + ord('a')) for i, c in enumerate(s))),
 ("Subtract index", lambda s: "".join(chr((ord(c) - ord('a') - i) % 26 + ord('a')) for i, c in enumerate(s))),
 ]
 
 for name, func in transformations:
 try:
 transformed_seed = func(false_seed)
 if len(transformed_seed) == 55:
 success, derived_id = derive_identity_from_seed(transformed_seed)
 if success:
 match = (derived_id == target_identity)
 results.append({
 "method": name,
 "seed": transformed_seed,
 "derived_identity": derived_id,
 "match": match
 })
 if match:
 return results # Found it!
 except:
 pass
 
 return results

def find_seed_in_matrix(target_identity: str, matrix: np.ndarray) -> List[Dict]:
 """Versuche den Seed in der Matrix zu finden."""
 results = []
 
 # Try different extraction patterns
 patterns = [
 ("Diagonal_0_0", [(i, i) for i in range(55)]),
 ("Diagonal_0_32", [(i, (i + 32) % 128) for i in range(55)]),
 ("Diagonal_0_64", [(i, (i + 64) % 128) for i in range(55)]),
 ("Block_0_0", [(r, c) for r in range(8) for c in range(7)][:55]),
 ]
 
 for pattern_name, coords in patterns:
 # Extract raw values
 raw_vals = []
 for r, c in coords:
 if r < 128 and c < 128:
 raw_vals.append(float(matrix[r, c]))
 
 if len(raw_vals) < 55:
 continue
 
 # Test transformations
 transformations = [
 ("Raw % 26", lambda v: int(v) % 26),
 ("Raw (Absolute) % 26", lambda v: abs(int(v)) % 26),
 ("Raw + 1 % 26", lambda v: (int(v) + 1) % 26),
 ]
 
 for name, func in transformations:
 try:
 indices = [func(v) % 26 for v in raw_vals]
 seed_candidate = "".join(chr(ord('a') + (i % 26)) for i in indices)
 
 success, derived_id = derive_identity_from_seed(seed_candidate)
 if success:
 match = (derived_id == target_identity)
 results.append({
 "pattern": pattern_name,
 "method": name,
 "seed": seed_candidate,
 "derived_identity": derived_id,
 "match": match
 })
 if match:
 return results # Found it!
 except:
 pass
 
 return results

def main():
 """Main function."""
 print("=" * 80)
 print("FIND SEEDS FOR FAKE IDs")
 print("=" * 80)
 print()
 
 if not INPUT_FILE.exists():
 print(f"❌ Input file not found: {INPUT_FILE}")
 return
 
 print("1. Loading mapping data...")
 with INPUT_FILE.open() as f:
 data = json.load(f)
 
 mismatches = data.get("mismatches_list", [])
 if not mismatches:
 results = data.get("results", [])
 mismatches = [r for r in results if r.get("real_identity") and not r.get("match")]
 
 print(f" ✅ Loaded {len(mismatches):,} mismatches")
 print()
 
 # Load matrix
 print("2. Loading matrix...")
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
 
 # Test first 100 fake IDs
 print("3. Testing seed transformations for fake IDs...")
 print()
 
 found_seeds = []
 test_results = []
 
 for idx, item in enumerate(mismatches[:100], 1):
 if idx % 10 == 0:
 print(f" Progress: {idx}/100")
 
 doc_id = item.get("documented_identity", "")
 false_seed = item.get("seed", "")
 
 if not doc_id or not false_seed:
 continue
 
 # Test seed transformations
 transformation_results = test_seed_transformations(false_seed, doc_id)
 
 # Test matrix extraction
 matrix_results = find_seed_in_matrix(doc_id, matrix)
 
 test_result = {
 "documented_identity": doc_id,
 "false_seed": false_seed,
 "transformation_results": transformation_results,
 "matrix_results": matrix_results,
 "found": any(r.get("match") for r in transformation_results + matrix_results)
 }
 
 test_results.append(test_result)
 
 if test_result["found"]:
 found_seeds.append(test_result)
 print(f" ✅ Found seed for: {doc_id[:40]}...")
 
 # Save results
 output_file = OUTPUT_DIR / "seeds_for_fake_ids_analysis.json"
 with output_file.open("w") as f:
 json.dump({
 "total_tested": len(test_results),
 "found_seeds": len(found_seeds),
 "results": test_results,
 "found_seeds_list": found_seeds
 }, f, indent=2)
 
 print()
 print("=" * 80)
 print("ANALYSIS COMPLETE")
 print("=" * 80)
 print(f"✅ Results saved to: {output_file}")
 print()
 print(f"Summary:")
 print(f" Total tested: {len(test_results)}")
 print(f" Seeds found: {len(found_seeds)}")

if __name__ == "__main__":
 main()

