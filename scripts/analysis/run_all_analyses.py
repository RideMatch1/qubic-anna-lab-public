#!/usr/bin/env python3
"""
Run All Analyses

Führt alle Analysen nacheinander aus:
1. Pattern Analysis
2. Seed Finding for Fake IDs
3. Complete Mapping Database
4. Pattern Discovery
"""

import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

SCRIPTS = [
 "scripts/analysis/create_complete_mapping_database.py",
 "scripts/analysis/analyze_documented_vs_real_patterns.py",
 "scripts/analysis/pattern_discovery_engine.py",
 "scripts/analysis/find_seeds_for_fake_ids.py",
]

def main():
 """Main function."""
 print("=" * 80)
 print("RUN ALL ANALYSES")
 print("=" * 80)
 print()
 
 for i, script_path in enumerate(SCRIPTS, 1):
 script = project_root / script_path
 if not script.exists():
 print(f"❌ Script not found: {script}")
 continue
 
 print(f"{i}/{len(SCRIPTS)}. Running {script.name}...")
 print()
 
 result = subprocess.run(
 [sys.executable, str(script)],
 cwd=project_root,
 capture_output=True,
 text=True
 )
 
 if result.returncode == 0:
 print(f" ✅ Completed")
 if result.stdout:
 print(result.stdout[-500:]) # Last 500 chars
 else:
 print(f" ❌ Failed: {result.stderr[:200]}")
 
 print()
 
 print("=" * 80)
 print("ALL ANALYSES COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

