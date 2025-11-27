#!/usr/bin/env python3
"""
Scan Assets in Layer-2 and Layer-3

Prüft ob Layer-2 und Layer-3 Identities Assets haben (GENESIS Token, etc.).
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def check_identity_assets(identity: str) -> Optional[Dict]:
 """Check Assets einer Identity."""
 if not VENV_PYTHON.exists():
 return None
 
 script = f"""
from qubipy.rpc import QubicRPC

rpc = QubicRPC()
identity = "{identity}"
try:
 balance_data = rpc.get_balance(identity)
 if balance_data:
 assets = balance_data.get('assets', [])
 balance = balance_data.get('balance', 0)
 print(f"ASSETS:{len(assets)}:BALANCE:{balance}")
 for asset in assets:
 print(f"ASSET:{asset.get('assetCode', '')}:{asset.get('amount', 0)}")
 else:
 print("NO_DATA")
except Exception as e:
 print(f"ERROR:{str(e)}")
"""
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=15,
 cwd=project_root
 )
 
 if "ERROR" in result.stdout:
 return None
 
 if "NO_DATA" in result.stdout:
 return {"assets": [], "balance": 0, "has_assets": False}
 
 # Parse output
 lines = result.stdout.strip().split('\n')
 assets_line = lines[0]
 if "ASSETS:" in assets_line:
 parts = assets_line.split(":")
 asset_count = int(parts[1])
 balance = int(parts[3])
 
 assets = []
 for line in lines[1:]:
 if line.startswith("ASSET:"):
 asset_parts = line.split(":")
 assets.append({
 "assetCode": asset_parts[1],
 "amount": int(asset_parts[2])
 })
 
 return {
 "assets": assets,
 "balance": balance,
 "has_assets": len(assets) > 0 or balance > 0
 }
 
 return None
 except Exception:
 return None

def load_layer2_identities() -> List[str]:
 """Load Layer-2 Identities."""
 # Load aus verschiedenen Quellen
 identities = []
 
 # Aus Layer-3 Derivation (hat Layer-2 als Basis)
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 if layer3_file.exists():
 with layer3_file.open() as f:
 data = json.load(f)
 for result in data.get("results", []):
 layer2 = result.get("layer2_identity")
 if layer2:
 identities.append(layer2)
 
 return list(set(identities)) # Remove duplicates

def load_layer3_identities() -> List[str]:
 """Load Layer-3 Identities."""
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 
 if not layer3_file.exists():
 return []
 
 with layer3_file.open() as f:
 data = json.load(f)
 
 identities = []
 for result in data.get("results", []):
 layer3 = result.get("layer3_identity")
 if layer3 and result.get("layer3_derivable"):
 identities.append(layer3)
 
 return identities

def scan_assets():
 """Scanne Assets in Layer-2 und Layer-3."""
 print("=" * 80)
 print("SCAN ASSETS IN LAYER-2 AND LAYER-3")
 print("=" * 80)
 print()
 
 # Load Identities
 print("Loading identities...")
 layer2_identities = load_layer2_identities()
 layer3_identities = load_layer3_identities()
 
 print(f"✅ Loaded {len(layer2_identities)} Layer-2 identities")
 print(f"✅ Loaded {len(layer3_identities)} Layer-3 identities")
 print()
 
 # Scan Layer-2
 print("Scanning Layer-2 identities for assets...")
 layer2_results = []
 
 for idx, identity in enumerate(layer2_identities, 1):
 asset_data = check_identity_assets(identity)
 
 layer2_results.append({
 "identity": identity,
 "assets": asset_data.get("assets", []) if asset_data else [],
 "balance": asset_data.get("balance", 0) if asset_data else 0,
 "has_assets": asset_data.get("has_assets", False) if asset_data else False
 })
 
 if asset_data and asset_data.get("has_assets"):
 print(f" ✅ {identity[:40]}... has {len(asset_data['assets'])} asset(s), balance: {asset_data['balance']}")
 
 if idx % 10 == 0:
 print(f" Progress: {idx}/{len(layer2_identities)} ({idx/len(layer2_identities)*100:.1f}%)")
 
 print()
 
 # Scan Layer-3
 print("Scanning Layer-3 identities for assets...")
 layer3_results = []
 
 for idx, identity in enumerate(layer3_identities, 1):
 asset_data = check_identity_assets(identity)
 
 layer3_results.append({
 "identity": identity,
 "assets": asset_data.get("assets", []) if asset_data else [],
 "balance": asset_data.get("balance", 0) if asset_data else 0,
 "has_assets": asset_data.get("has_assets", False) if asset_data else False
 })
 
 if asset_data and asset_data.get("has_assets"):
 print(f" ✅ {identity[:40]}... has {len(asset_data['assets'])} asset(s), balance: {asset_data['balance']}")
 
 if idx % 10 == 0:
 print(f" Progress: {idx}/{len(layer3_identities)} ({idx/len(layer3_identities)*100:.1f}%)")
 
 print()
 print("=" * 80)
 print("SCAN COMPLETE")
 print("=" * 80)
 print()
 
 # Statistiken
 layer2_with_assets = sum(1 for r in layer2_results if r.get("has_assets"))
 layer3_with_assets = sum(1 for r in layer3_results if r.get("has_assets"))
 
 print(f"Layer-2 identities with assets: {layer2_with_assets}/{len(layer2_identities)}")
 print(f"Layer-3 identities with assets: {layer3_with_assets}/{len(layer3_identities)}")
 print()
 
 # Speichere Ergebnisse
 results = {
 "layer2_results": layer2_results,
 "layer3_results": layer3_results,
 "statistics": {
 "layer2_total": len(layer2_identities),
 "layer2_with_assets": layer2_with_assets,
 "layer3_total": len(layer3_identities),
 "layer3_with_assets": layer3_with_assets
 }
 }
 
 output_file = OUTPUT_DIR / "assets_layer2_layer3_scan.json"
 with output_file.open("w") as f:
 json.dump(results, f, indent=2)
 print(f"✅ Results saved to: {output_file}")
 
 # Generiere Report
 report = [
 "# Asset Scan Layer-2 and Layer-3 Report\n\n",
 f"## Layer-2 Results\n\n",
 f"- **Total scanned**: {len(layer2_identities)}\n",
 f"- **Identities with assets**: {layer2_with_assets}\n\n",
 f"## Layer-3 Results\n\n",
 f"- **Total scanned**: {len(layer3_identities)}\n",
 f"- **Identities with assets**: {layer3_with_assets}\n\n"
 ]
 
 # Liste Identities mit Assets
 if layer2_with_assets > 0:
 report.append("## Layer-2 Identities with Assets\n\n")
 for r in layer2_results:
 if r.get("has_assets"):
 report.append(f"- `{r['identity']}`\n")
 report.append(f" - Assets: {len(r['assets'])}\n")
 report.append(f" - Balance: {r['balance']}\n\n")
 
 if layer3_with_assets > 0:
 report.append("## Layer-3 Identities with Assets\n\n")
 for r in layer3_results:
 if r.get("has_assets"):
 report.append(f"- `{r['identity']}`\n")
 report.append(f" - Assets: {len(r['assets'])}\n")
 report.append(f" - Balance: {r['balance']}\n\n")
 
 report_file = REPORTS_DIR / "assets_layer2_layer3_scan_report.md"
 with report_file.open("w") as f:
 f.write("".join(report))
 print(f"✅ Report saved to: {report_file}")

if __name__ == "__main__":
 scan_assets()

