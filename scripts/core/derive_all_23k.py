#!/usr/bin/env python3
"""
Derive alle 23.765 Layer-3 Identities
Optimiert for große Datensätze mit Progress-Tracking
"""

import json
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
MAPPING_FILE = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
REPORTS_DIR = project_root / "outputs" / "reports"
PROGRESS_FILE = OUTPUT_DIR / "23k_derivation_progress.json"

# Import derivation functions
from scripts.core.derive_layer3_extended import (
 identity_to_seed,
 derive_identity_from_seed,
 load_layer2_identities
)

def save_progress(current: int, total: int, start_time: float):
 """Speichere Progress."""
 progress_data = {
 "current": current,
 "total": total,
 "progress_percent": (current / total * 100) if total > 0 else 0,
 "start_time": start_time,
 "timestamp": datetime.now().isoformat()
 }
 with PROGRESS_FILE.open("w") as f:
 json.dump(progress_data, f, indent=2)

def derive_all_23k():
 """Derive alle 23.765 Identities."""
 print("=" * 80)
 print("DERIVE ALL 23.765 LAYER-3 IDENTITIES")
 print("=" * 80)
 print()
 
 # Load alle Seeds
 if not MAPPING_FILE.exists():
 raise FileNotFoundError(f"Mapping file not found: {MAPPING_FILE}")
 
 with MAPPING_FILE.open() as f:
 data = json.load(f)
 
 seeds = list(data.get("seed_to_real_id", {}).keys())
 total_seeds = len(seeds)
 
 print(f"✅ Loaded {total_seeds} seeds from mapping database")
 print()
 
 # Load Layer-2 Identities (alle)
 print("Loading Layer-2 identities...")
 layer2_identities = []
 
 # Von Layer-1 ableiten
 layer1_identities = list(data.get("seed_to_real_id", {}).values())
 print(f"Deriving Layer-2 from {len(layer1_identities)} Layer-1 identities...")
 
 for i, layer1_id in enumerate(layer1_identities, 1):
 layer2_seed = identity_to_seed(layer1_id)
 layer2_id = derive_identity_from_seed(layer2_seed)
 if layer2_id:
 layer2_identities.append(layer2_id)
 
 if i % 1000 == 0:
 print(f" Derived {i}/{len(layer1_identities)} Layer-2 identities...")
 
 print(f"✅ Loaded {len(layer2_identities)} Layer-2 identities")
 print()
 
 # Derive Layer-3
 print("Deriving Layer-3 identities (this will take a while)...")
 print("⚠️ Skipping RPC checks - faster but no on-chain status")
 print()
 
 results = []
 start_time = datetime.now().timestamp()
 
 for i, layer2_id in enumerate(layer2_identities, 1):
 layer3_seed = identity_to_seed(layer2_id)
 layer3_id = derive_identity_from_seed(layer3_seed)
 
 if layer3_id:
 results.append({
 "layer2_identity": layer2_id,
 "seed": layer3_seed,
 "layer3_identity": layer3_id,
 "layer3_derivable": True,
 "layer3_onchain": None # No RPC check
 })
 
 # Progress update
 if i % 100 == 0:
 save_progress(i, len(layer2_identities), start_time)
 elapsed = datetime.now().timestamp() - start_time
 rate = i / elapsed if elapsed > 0 else 0
 remaining = (len(layer2_identities) - i) / rate if rate > 0 else 0
 print(f" Processed: {i}/{len(layer2_identities)} ({i/len(layer2_identities)*100:.1f}%) - "
 f"ETA: {remaining/60:.1f} min")
 
 # Final save
 save_progress(len(layer2_identities), len(layer2_identities), start_time)
 
 print()
 print(f"✅ Derived {len(results)} Layer-3 identities")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "total_derived": len(results),
 "total_layer2": len(layer2_identities),
 "timestamp": datetime.now().isoformat(),
 "results": results
 }
 
 output_file = OUTPUT_DIR / "layer3_derivation_23k_complete.json"
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Results saved to: {output_file}")
 
 # Report
 report_lines = [
 "# 23K Derivation Complete",
 "",
 f"**Total Derived**: {len(results)} Layer-3 Identities",
 f"**Total Layer-2**: {len(layer2_identities)}",
 f"**Timestamp**: {datetime.now().isoformat()}",
 "",
 "## Status",
 "- All identities derived without RPC checks",
 "- On-chain status: Unknown (not checked)",
 "",
 "## Next Steps",
 "1. Run Position 30/4 Analysis",
 "2. Run RPC Sample Validation",
 "3. Validate Position 30/4 on full dataset",
 ]
 
 report_file = REPORTS_DIR / "23K_DERIVATION_COMPLETE.md"
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 
 print(f"📄 Report saved to: {report_file}")

if __name__ == "__main__":
 derive_all_23k()

