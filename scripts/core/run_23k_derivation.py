#!/usr/bin/env python3
"""
Batch Derivation Script for 23k Seeds
Verwendet: python3 scripts/core/derive_layer3_extended.py --count <batch_size> --skip-rpc
"""

import subprocess
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
plan_file = project_root / "outputs" / "derived" / "23k_derivation_plan.json"

with plan_file.open() as f:
 plan = json.load(f)

print("Starting batch derivation...")
print(f"Total batches: {plan['total_batches']}")

for batch_info in plan['batches']:
 batch_num = batch_info['batch']
 batch_size = batch_info['size']
 
 print(f"\nProcessing batch {batch_num}/{plan['total_batches']} ({batch_size} identities)...")
 
 cmd = [
 "python3",
 str(project_root / "scripts" / "core" / "derive_layer3_extended.py"),
 "--count", str(batch_size),
 "--skip-rpc"
 ]
 
 result = subprocess.run(cmd, cwd=project_root)
 
 if result.returncode != 0:
 print(f"❌ Batch {batch_num} failed!")
 break
 
 print(f"✅ Batch {batch_num} completed")

print("\n✅ All batches completed!")
