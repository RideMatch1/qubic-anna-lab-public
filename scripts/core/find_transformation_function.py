#!/usr/bin/env python3
"""
Find Transformation Function: f(MatrixString) = Seed

Attempts to find the function that transforms the "False Seed" (Matrix String)
into the True Seed.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

# Import derive_identity from raw_value_seed_extraction
from scripts.core.raw_value_seed_extraction import derive_identity, get_qubipy_functions

QUBIPY_AVAILABLE = get_qubipy_functions() is not None

# derive_identity is imported from raw_value_seed_extraction

def load_test_data() -> List[Dict]:
 """Load test data."""
 seeds_file = project_root / "github_export" / "100_seeds_and_identities.json"
 
 if not seeds_file.exists():
 return []
 
 with seeds_file.open() as f:
 data = json.load(f)
 
 if isinstance(data, list):
 return data
 elif isinstance(data, dict) and "seeds_and_identities" in data:
 return data["seeds_and_identities"]
 else:
 return []

def test_string_transformations(false_seed: str, target_identity: str) -> List[Dict]:
 """Test string-based transformations."""
 results = []
 
 # 1. Reverse
 candidates = [("Reverse", false_seed[::-1])]
 
 # 2. Rotations
 for i in range(1, min(55, len(false_seed))):
 rot = false_seed[i:] + false_seed[:i]
 candidates.append((f"Rotate Left {i}", rot))
 rot = false_seed[-i:] + false_seed[:-i]
 candidates.append((f"Rotate Right {i}", rot))
 
 # 3. Caesar Shifts
 for i in range(1, 26):
 shifted = "".join(chr(ord('a') + (ord(c) - ord('a') + i) % 26) for c in false_seed)
 candidates.append((f"Caesar Shift +{i}", shifted))
 shifted = "".join(chr(ord('a') + (ord(c) - ord('a') - i) % 26) for c in false_seed)
 candidates.append((f"Caesar Shift -{i}", shifted))
 
 # 4. Swaps (adjacent)
 s_list = list(false_seed)
 swapped = s_list.copy()
 for i in range(0, len(swapped) - 1, 2):
 swapped[i], swapped[i+1] = swapped[i+1], swapped[i]
 candidates.append(("Swap Adjacent Pairs", "".join(swapped)))
 
 # 5. Character-wise operations
 # Add 1 to each char
 add1 = "".join(chr(ord('a') + (ord(c) - ord('a') + 1) % 26) for c in false_seed)
 candidates.append(("Add 1 to each char", add1))
 
 # Subtract 1 from each char
 sub1 = "".join(chr(ord('a') + (ord(c) - ord('a') - 1) % 26) for c in false_seed)
 candidates.append(("Subtract 1 from each char", sub1))
 
 # 6. First half + second half swapped
 mid = len(false_seed) // 2
 swapped_halves = false_seed[mid:] + false_seed[:mid]
 candidates.append(("Swap Halves", swapped_halves))
 
 # Test all candidates
 for name, seed in candidates:
 if len(seed) != 55:
 continue
 
 success, derived_id = derive_identity(seed)
 match = (derived_id == target_identity) if success else False
 
 results.append({
 "method": name,
 "seed": seed,
 "derived_identity": derived_id if success else "N/A",
 "match": match,
 "success": success
 })
 
 status = "✅ MATCH!" if match else ("✅" if success else "❌")
 print(f" {name:<30} -> {seed[:15]}... -> {derived_id[:15] if success else 'N/A'}... {status}")
 
 if match:
 print(f"\n🎉 MATCH FOUND with {name}!")
 break
 
 return results

def main():
 """Main function."""
 print("=" * 80)
 print("FIND TRANSFORMATION FUNCTION")
 print("=" * 80)
 print()
 
 # Load test data
 test_data = load_test_data()
 if not test_data:
 print("❌ No test data found!")
 return
 
 print(f"✅ Loaded {len(test_data)} test identities")
 print()
 
 all_results = []
 
 # Test first 10 identities
 for idx, item in enumerate(test_data[:10], 1):
 documented_identity = item.get("identity", "")
 false_seed = item.get("seed", "") # This is the "false seed" from identity.lower()[:55]
 
 if not documented_identity or not false_seed:
 continue
 
 print(f"Testing Identity #{idx}: {documented_identity[:30]}...")
 print(f" False Seed: {false_seed[:30]}...")
 print()
 
 print(" Testing string transformations...")
 results = test_string_transformations(false_seed, documented_identity)
 
 for result in results:
 result["identity_index"] = idx
 result["documented_identity"] = documented_identity
 result["false_seed"] = false_seed
 
 all_results.extend(results)
 
 # Check if we found a match
 if any(r.get("match") for r in results):
 print(f"\n🎉 MATCH FOUND for Identity #{idx}!")
 break
 
 print()
 
 # Save results
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_file = OUTPUT_DIR / "transformation_function_results.json"
 with output_file.open("w") as f:
 json.dump({
 "total_tested": len(test_data[:10]),
 "results": all_results
 }, f, indent=2)
 
 print(f"✅ Results saved to: {output_file}")
 print()
 print("=" * 80)
 print("ANALYSIS COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

