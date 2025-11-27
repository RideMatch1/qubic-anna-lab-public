#!/usr/bin/env python3
"""
Derive Layer-3 Identities Extended

Leitet mehr Layer-3 Identities ab (1000 statt 100) for bessere Tests:
- Load Layer-2 Identities aus verschiedenen Quellen
- Leite Layer-3 for alle ab
- Check on-chain Status
- Speichere for weitere Analyse
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def derive_identity_from_seed(seed: str) -> Optional[str]:
 """Leite Identity aus Seed ab (via venv-tx)."""
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{seed}"
try:
 seed_bytes = bytes(seed, 'utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 identity = get_identity_from_public_key(public_key)
 print(identity)
except Exception as e:
 print(f"ERROR: {{e}}")
"""
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=5,
 cwd=project_root
 )
 if result.returncode == 0 and result.stdout.strip() and not result.stdout.startswith("ERROR"):
 return result.stdout.strip()
 except Exception:
 pass
 return None

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
except Exception as e:
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

def load_layer2_identities(max_count: int = 1000) -> List[str]:
 """Load Layer-2 Identities aus verschiedenen Quellen."""
 identities = []
 
 # Quelle 1: Layer-2 Complete
 layer2_file = OUTPUT_DIR / "layer2_derivation_complete.json"
 if layer2_file.exists():
 with layer2_file.open() as f:
 data = json.load(f)
 for result in data.get("results", []):
 if result.get("layer2_onchain") and result.get("layer2_identity"):
 identities.append(result["layer2_identity"])
 
 # Quelle 2: Layer-3 Complete (hat Layer-2 als Basis)
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 if layer3_file.exists():
 with layer3_file.open() as f:
 data = json.load(f)
 for result in data.get("results", []):
 layer2 = result.get("layer2_identity")
 if layer2:
 identities.append(layer2)
 
 # Quelle 3: Complete Mapping Database (Layer-1 → Layer-2 ableiten)
 mapping_file = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
 if mapping_file.exists() and len(identities) < max_count:
 print(f"Loading from complete_mapping_database.json...")
 with mapping_file.open() as f:
 data = json.load(f)
 
 # Datenstruktur: {"seed_to_real_id": {...}}
 if isinstance(data, dict) and "seed_to_real_id" in data:
 layer1_identities = list(data["seed_to_real_id"].values())[:max_count - len(identities)]
 
 print(f"Deriving Layer-2 from {len(layer1_identities)} Layer-1 identities...")
 for i, layer1_id in enumerate(layer1_identities, 1):
 if len(identities) >= max_count:
 break
 
 layer2_seed = identity_to_seed(layer1_id)
 layer2_id = derive_identity_from_seed(layer2_seed)
 
 if layer2_id:
 identities.append(layer2_id)
 
 if i % 100 == 0:
 print(f" Derived {i}/{len(layer1_identities)} Layer-2 identities...")
 
 # Entferne Duplikate
 identities = list(dict.fromkeys(identities)) # Preserves order
 
 return identities[:max_count]

def derive_layer3_batch(layer2_identities: List[str], batch_size: int = 50) -> List[Dict]:
 """Leite Layer-3 Identities in Batches ab."""
 results = []
 
 print(f"Deriving Layer-3 for {len(layer2_identities)} Layer-2 identities...")
 print("This may take a while...")
 print()
 
 for i, layer2_id in enumerate(layer2_identities, 1):
 layer3_seed = identity_to_seed(layer2_id)
 layer3_id = derive_identity_from_seed(layer3_seed)
 
 if layer3_id:
 # Check on-chain Status
 is_onchain = check_identity_onchain(layer3_id)
 
 results.append({
 "layer2_identity": layer2_id,
 "seed": layer3_seed,
 "layer3_identity": layer3_id,
 "layer3_derivable": True,
 "layer3_onchain": is_onchain
 })
 else:
 results.append({
 "layer2_identity": layer2_id,
 "seed": layer3_seed,
 "layer3_identity": "",
 "layer3_derivable": False,
 "layer3_onchain": False
 })
 
 if i % 50 == 0:
 onchain_count = sum(1 for r in results if r.get("layer3_onchain", False))
 print(f" Processed: {i}/{len(layer2_identities)}, On-chain: {onchain_count}/{len(results)}")
 
 return results

def main():
 """Hauptfunktion."""
 import argparse
 parser = argparse.ArgumentParser()
 parser.add_argument("--count", type=int, default=1000, help="Number of Layer-3 identities to derive")
 parser.add_argument("--skip-rpc", action="store_true", help="Skip RPC checks (faster)")
 args = parser.parse_args()
 
 print("=" * 80)
 print("DERIVE LAYER-3 IDENTITIES EXTENDED")
 print("=" * 80)
 print()
 
 # Load Layer-2 Identities
 print(f"Loading Layer-2 identities (target: {args.count})...")
 layer2_identities = load_layer2_identities(max_count=args.count)
 
 print(f"✅ Loaded {len(layer2_identities)} Layer-2 identities")
 print()
 
 if len(layer2_identities) == 0:
 print("❌ No Layer-2 identities found")
 return
 
 # Leite Layer-3 ab
 if args.skip_rpc:
 print("⚠️ Skipping RPC checks - faster but no on-chain status")
 print()
 
 results = []
 for i, layer2_id in enumerate(layer2_identities, 1):
 layer3_seed = identity_to_seed(layer2_id)
 layer3_id = derive_identity_from_seed(layer3_seed)
 
 if layer3_id:
 results.append({
 "layer2_identity": layer2_id,
 "seed": layer3_seed,
 "layer3_identity": layer3_id,
 "layer3_derivable": True,
 "layer3_onchain": None # Not checked
 })
 
 if i % 100 == 0:
 print(f" Processed: {i}/{len(layer2_identities)}")
 else:
 results = derive_layer3_batch(layer2_identities)
 
 print()
 print(f"✅ Derived {len([r for r in results if r.get('layer3_derivable', False)])} Layer-3 identities")
 
 if not args.skip_rpc:
 onchain_count = sum(1 for r in results if r.get("layer3_onchain", False))
 print(f"✅ On-chain: {onchain_count}/{len(results)} ({onchain_count/len(results)*100:.1f}%)")
 
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "processed": len(results),
 "derivable": sum(1 for r in results if r.get("layer3_derivable", False)),
 "onchain": sum(1 for r in results if r.get("layer3_onchain", False)) if not args.skip_rpc else None,
 "generated": datetime.now().isoformat(),
 "results": results
 }
 
 output_file = OUTPUT_DIR / "layer3_derivation_extended.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Results saved to: {output_file}")
 print()
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report_file = REPORTS_DIR / "layer3_derivation_extended_report.md"
 
 with report_file.open("w") as f:
 f.write("# Layer-3 Derivation Extended Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write(f"Extended Layer-3 derivation for {len(results)} identities.\n\n")
 f.write(f"- **Total Processed**: {len(results)}\n")
 f.write(f"- **Derivable**: {output_data['derivable']}\n")
 if not args.skip_rpc:
 f.write(f"- **On-chain**: {output_data['onchain']} ({output_data['onchain']/len(results)*100:.1f}%)\n")
 f.write("\n")
 
 print(f"📄 Report saved to: {report_file}")
 print()

if __name__ == "__main__":
 main()

