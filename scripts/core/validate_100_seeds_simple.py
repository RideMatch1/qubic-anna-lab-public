#!/usr/bin/env python3
"""Simple version - validate 100 seeds to real IDs"""

import json
import subprocess
from pathlib import Path

project_root = Path('.')
venv_python = project_root / "venv-tx" / "bin" / "python"
input_file = project_root / "github_export" / "100_seeds_and_identities.json"
output_file = project_root / "outputs" / "derived" / "seeds_to_real_ids.json"

print("=" * 80)
print("VALIDATE 100 SEEDS TO REAL IDs")
print("=" * 80)
print()

# Load data
with input_file.open() as f:
 data = json.load(f)

if isinstance(data, dict) and "seeds_and_identities" in data:
 items = data["seeds_and_identities"]
else:
 items = data if isinstance(data, list) else []

print(f"Loaded {len(items)} items")
print()

results = []
matches = 0

for idx, item in enumerate(items, 1):
 seed = item.get("seed", "")
 doc_id = item.get("identity", "")
 
 if idx % 10 == 0:
 print(f"Progress: {idx}/{len(items)} (Matches: {matches})")
 
 # Derive identity
 script = f'''
from qubipy.crypto.utils import get_subseed_from_seed, get_private_key_from_subseed, get_public_key_from_private_key, get_identity_from_public_key
seed = "{seed}"
seed_bytes = seed.encode("utf-8")
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
'''
 
 result = subprocess.run(
 [str(venv_python), '-c', script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 
 if result.returncode == 0 and result.stdout.strip():
 real_id = result.stdout.strip()
 match = (real_id == doc_id)
 
 if match:
 matches += 1
 print(f"✅ #{idx}: MATCH")
 elif idx <= 5:
 print(f"❌ #{idx}: Mismatch")
 print(f" Doc: {doc_id}")
 print(f" Real: {real_id}")
 
 results.append({
 "index": idx,
 "seed": seed,
 "documented_identity": doc_id,
 "real_identity": real_id,
 "match": match
 })
 else:
 print(f"❌ #{idx}: Failed - {result.stderr[:50]}")
 results.append({
 "index": idx,
 "seed": seed,
 "documented_identity": doc_id,
 "error": result.stderr.strip() or "Failed"
 })

# Save
output_file.parent.mkdir(parents=True, exist_ok=True)
with output_file.open("w") as f:
 json.dump({
 "total": len(items),
 "matches": matches,
 "match_rate": f"{matches*100/len(items):.1f}%",
 "results": results
 }, f, indent=2)

print()
print("=" * 80)
print(f"COMPLETE: {matches}/{len(items)} matches ({matches*100/len(items):.1f}%)")
print(f"Results saved to: {output_file}")

