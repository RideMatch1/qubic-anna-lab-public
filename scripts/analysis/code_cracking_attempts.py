#!/usr/bin/env python3
"""
Code Cracking Attempts

Versucht den Code zu knacken, der False Seeds in True Seeds transformiert.
Testet verschiedene mathematische Transformationen.
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List
import hashlib

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"
INPUT_FILE = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
OUTPUT_DIR = project_root / "outputs" / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def derive_identity_from_seed(seed: str) -> tuple[bool, str]:
 """Derive identity from seed."""
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

def test_transformation_functions(false_seed: str, target_doc_id: str) -> List[Dict]:
 """Teste verschiedene Transformation-Funktionen."""
 results = []
 
 # String transformations
 transformations = [
 ("Identity", lambda s: s),
 ("Reverse", lambda s: s[::-1]),
 ("Rotate +1", lambda s: "".join(chr((ord(c) - ord('a') + 1) % 26 + ord('a')) for c in s)),
 ("Rotate -1", lambda s: "".join(chr((ord(c) - ord('a') - 1) % 26 + ord('a')) for c in s)),
 ("Rotate +13", lambda s: "".join(chr((ord(c) - ord('a') + 13) % 26 + ord('a')) for c in s)),
 ("XOR with index", lambda s: "".join(chr((ord(c) ^ i) % 26 + ord('a')) for i, c in enumerate(s))),
 ("Add index", lambda s: "".join(chr((ord(c) - ord('a') + i) % 26 + ord('a')) for i, c in enumerate(s))),
 ("Subtract index", lambda s: "".join(chr((ord(c) - ord('a') - i) % 26 + ord('a')) for i, c in enumerate(s))),
 ("Hash-based", lambda s: hashlib.sha256(s.encode()).hexdigest()[:55]),
 ]
 
 for name, func in transformations:
 try:
 transformed = func(false_seed)
 if len(transformed) == 55:
 success, derived_id = derive_identity_from_seed(transformed)
 if success:
 match = (derived_id == target_doc_id)
 results.append({
 "method": name,
 "transformed_seed": transformed,
 "derived_identity": derived_id,
 "match": match
 })
 if match:
 return results # Found it!
 except:
 pass
 
 return results

def find_transformation_pattern(mismatches: List[Dict]) -> Dict:
 """Finde Transformation-Pattern durch Vergleich."""
 # Analyze first 100 for patterns
 samples = mismatches[:100]
 
 patterns = {
 "position_diffs": defaultdict(list),
 "char_diffs": defaultdict(list),
 "seed_patterns": []
 }
 
 for item in samples:
 false_seed = item.get("seed", "")
 doc_id = item.get("documented_identity", "")
 real_id = item.get("real_identity", "")
 
 if len(false_seed) == 55 and len(doc_id) == 60:
 # Compare seed with doc_id start
 seed_upper = false_seed.upper()
 doc_start = doc_id[:55]
 
 if seed_upper != doc_start:
 # Find differences
 for i in range(55):
 if seed_upper[i] != doc_start[i]:
 patterns["position_diffs"][i].append({
 "seed_char": seed_upper[i],
 "doc_char": doc_start[i],
 "seed_ord": ord(seed_upper[i]),
 "doc_ord": ord(doc_start[i])
 })
 
 return patterns

def main():
 """Main function."""
 print("=" * 80)
 print("CODE CRACKING ATTEMPTS")
 print("=" * 80)
 print()
 
 if not INPUT_FILE.exists():
 print(f"❌ Input file not found: {INPUT_FILE}")
 return
 
 print("1. Loading database...")
 with INPUT_FILE.open() as f:
 database = json.load(f)
 
 mismatches = database.get("mismatches", [])
 print(f" ✅ Loaded {len(mismatches):,} mismatches")
 print()
 
 print("2. Testing transformation functions...")
 transformation_results = []
 
 for idx, item in enumerate(mismatches[:50], 1):
 if idx % 10 == 0:
 print(f" Progress: {idx}/50")
 
 false_seed = item.get("seed", "")
 doc_id = item.get("documented_identity", "")
 
 if false_seed and doc_id:
 results = test_transformation_functions(false_seed, doc_id)
 if results:
 transformation_results.append({
 "false_seed": false_seed,
 "target_doc_id": doc_id,
 "results": results,
 "found": any(r.get("match") for r in results)
 })
 
 found_count = sum(1 for r in transformation_results if r.get("found"))
 print(f" ✅ Tested {len(transformation_results)} seeds, found {found_count} matches")
 print()
 
 print("3. Finding transformation patterns...")
 patterns = find_transformation_pattern(mismatches)
 print(f" ✅ Analyzed patterns")
 print()
 
 # Save results
 output_file = OUTPUT_DIR / "code_cracking_results.json"
 with output_file.open("w") as f:
 json.dump({
 "transformation_results": transformation_results,
 "patterns": patterns,
 "found_count": found_count
 }, f, indent=2)
 
 print("=" * 80)
 print("CODE CRACKING COMPLETE")
 print("=" * 80)
 print(f"✅ Results saved to: {output_file}")
 print()
 print(f"Summary:")
 print(f" Seeds tested: {len(transformation_results)}")
 print(f" Matches found: {found_count}")

if __name__ == "__main__":
 main()

