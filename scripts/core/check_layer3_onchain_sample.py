#!/usr/bin/env python3
"""
Check Layer-3 On-Chain Status (Sample)

Prüft on-chain Status for eine Stichprobe der neuen Layer-3 Identities.
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def check_identity_onchain(identity: str) -> bool:
 """Check ob Identity on-chain existiert."""
 script = f"""
from qubipy.rpc import rpc_client
identity = "{identity}"
try:
 rpc = rpc_client.QubiPy_RPC()
 balance = rpc.get_balance(identity)
 if balance is not None:
 print("EXISTS")
 else:
 print("NOT_FOUND")
except Exception:
 print("ERROR")
"""
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=project_root
 )
 return "EXISTS" in result.stdout
 except Exception:
 return False

def main():
 """Hauptfunktion."""
 import argparse
 parser = argparse.ArgumentParser()
 parser.add_argument("--sample", type=int, default=100, help="Sample size to check")
 args = parser.parse_args()
 
 print("=" * 80)
 print("CHECK LAYER-3 ON-CHAIN STATUS (SAMPLE)")
 print("=" * 80)
 print()
 
 # Load extended data
 extended_file = OUTPUT_DIR / "layer3_derivation_extended.json"
 if not extended_file.exists():
 print("❌ Extended file not found")
 return
 
 with extended_file.open() as f:
 data = json.load(f)
 
 results = data.get("results", [])
 sample = results[:args.sample]
 
 print(f"Checking on-chain status for {len(sample)} identities...")
 print("This may take a while...")
 print()
 
 checked = 0
 onchain_count = 0
 
 for i, result in enumerate(sample, 1):
 layer3_id = result.get("layer3_identity", "")
 if not layer3_id:
 continue
 
 is_onchain = check_identity_onchain(layer3_id)
 result["layer3_onchain"] = is_onchain
 
 if is_onchain:
 onchain_count += 1
 
 checked += 1
 
 if i % 10 == 0:
 print(f" Checked: {i}/{len(sample)}, On-chain: {onchain_count}/{checked} ({onchain_count/checked*100:.1f}%)")
 
 print()
 print(f"✅ Checked {checked} identities")
 print(f"✅ On-chain: {onchain_count}/{checked} ({onchain_count/checked*100:.1f}%)")
 print()
 
 # Update extended file
 data["results"][:args.sample] = sample
 data["onchain_checked"] = checked
 data["onchain_count"] = onchain_count
 
 with extended_file.open("w") as f:
 json.dump(data, f, indent=2)
 
 print(f"💾 Updated: {extended_file}")
 print()

if __name__ == "__main__":
 main()

