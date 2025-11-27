#!/usr/bin/env python3
"""
Layer-4 Derivation (Sample-basiert - schnell for erste Analyse)
"""

import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import time

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Leite Identity aus Seed ab."""
 if not VENV_PYTHON.exists():
 return None
 
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{seed}"
seed_bytes = seed.encode('utf-8')
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
"""
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=5,
 cwd=project_root
 )
 
 if result.returncode != 0:
 return None
 
 identity = result.stdout.strip()
 if len(identity) == 60 and identity.isupper():
 return identity
 return None
 except Exception:
 return None

def load_layer3_identities(sample_size: Optional[int] = None) -> List[str]:
 """Load Layer-3 Identities (aus 23k Dataset, optional Sample)."""
 layer3_file = OUTPUT_DIR / "layer3_derivation_23k_complete.json"
 
 if not layer3_file.exists():
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 
 if not layer3_file.exists():
 print(f"❌ Layer-3 file not found")
 return []
 
 with layer3_file.open() as f:
 data = json.load(f)
 
 identities = []
 for result in data.get("results", []):
 layer3_identity = result.get("layer3_identity")
 if layer3_identity:
 identities.append(layer3_identity)
 if sample_size and len(identities) >= sample_size:
 break
 
 return identities

def derive_layer4_sample(sample_size: int = 1000):
 """Leite Layer-4 Identities ab (Sample-basiert)."""
 print("=" * 80)
 print(f"LAYER-4 DERIVATION (SAMPLE: {sample_size} Identities)")
 print("=" * 80)
 print()
 
 layer3_identities = load_layer3_identities(sample_size)
 
 if not layer3_identities:
 print("❌ No Layer-3 identities found!")
 return
 
 print(f"✅ Loaded {len(layer3_identities)} Layer-3 identities")
 print("⚠️ Skipping RPC checks for speed - will validate later")
 print()
 
 results = []
 start_time = time.time()
 
 print("Deriving Layer-4 identities...")
 print()
 
 for idx, layer3_identity in enumerate(layer3_identities, 1):
 seed = identity_to_seed(layer3_identity)
 layer4_identity = derive_identity_from_seed(seed)
 
 results.append({
 "layer3_identity": layer3_identity,
 "seed": seed,
 "layer4_identity": layer4_identity,
 "layer4_derivable": layer4_identity is not None,
 "layer4_onchain": None # Will später geprüft
 })
 
 # Progress alle 100 Identities
 if idx % 100 == 0:
 elapsed = time.time() - start_time
 rate = idx / elapsed if elapsed > 0 else 0
 remaining = (len(layer3_identities) - idx) / rate if rate > 0 else 0
 progress_pct = (idx / len(layer3_identities)) * 100
 print(f" Progress: {idx}/{len(layer3_identities)} ({progress_pct:.1f}%) | "
 f"Rate: {rate:.1f} ids/sec | "
 f"ETA: {remaining/60:.1f} min")
 
 print()
 print("=" * 80)
 print("LAYER-4 DERIVATION COMPLETE")
 print("=" * 80)
 print()
 
 derivable = sum(1 for r in results if r.get("layer4_derivable"))
 
 print(f"Layer-4 derivable: {derivable}/{len(results)} ({derivable/len(results)*100:.1f}%)")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
 "sample_size": sample_size,
 "total_layer3": len(layer3_identities),
 "layer4_derivable": derivable,
 "results": results
 }
 
 output_file = OUTPUT_DIR / f"layer4_derivation_sample_{sample_size}.json"
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Results saved to: {output_file}")
 
 # Report
 report_lines = [
 f"# Layer-4 Derivation (Sample: {sample_size})",
 "",
 f"**Sample Size**: {sample_size}",
 f"**Total Layer-3 identities**: {len(layer3_identities)}",
 f"**Layer-4 derivable**: {derivable} ({derivable/len(results)*100:.1f}%)",
 "",
 "## Next Steps",
 "",
 "1. RPC validation: Check on-chain Status for Layer-4 Sample",
 "2. Layer-4 analysis: Analyze Patterns und Operationen",
 "3. Full derivation: Leite alle 23k Layer-4 Identities ab (falls nötig)"
 ]
 
 report_file = REPORTS_DIR / f"layer4_derivation_sample_{sample_size}_report.md"
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 
 print(f"📄 Report saved to: {report_file}")

if __name__ == "__main__":
 parser = argparse.ArgumentParser(description="Derive Layer-4 identities (sample-based)")
 parser.add_argument("--sample-size", type=int, default=1000, help="Number of identities to derive (default: 1000)")
 args = parser.parse_args()
 
 derive_layer4_sample(args.sample_size)

