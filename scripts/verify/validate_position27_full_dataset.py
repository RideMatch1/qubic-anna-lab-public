#!/usr/bin/env python3
"""
Vollständige Validierung Position 27 auf ALLEN 23.765 Identities
- Schnell und mit Progress Tracking
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List
from collections import Counter
from datetime import datetime
from scipy.stats import chi2_contingency
import numpy as np
import time

project_root = Path(__file__).parent.parent.parent
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python3"
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
PROGRESS_FILE = project_root / "outputs" / "derived" / "position27_full_validation_progress.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

BLOCK_END_POSITIONS = [13, 27, 41, 55]

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def derive_identity_from_seed(seed: str) -> str:
 """Leite Identity aus Seed ab."""
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{seed}"
try:
 seed_bytes = seed.encode('utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 identity = get_identity_from_public_key(public_key)
 print(identity)
except Exception:
 print("")
"""
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=5,
 cwd=project_root
 )
 identity = result.stdout.strip()
 if len(identity) == 60 and identity.isupper():
 return identity
 return ""
 except Exception:
 return ""

def derive_all_layer4_identities_fast() -> Dict:
 """Leite alle Layer-4 Identities schnell ab (mit Progress Tracking)."""
 
 print("📂 Load Layer-3 Identities...")
 if not LAYER3_FILE.exists():
 print(f"❌ Layer-3 file not found: {LAYER3_FILE}")
 return {"error": "Layer-3 file not found"}
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 
 layer3_results = layer3_data.get("results", [])
 total = len(layer3_results)
 
 print(f"✅ {total} Layer-3 Identities geloadn")
 print()
 
 # Check ob Layer-4 File bereits existiert
 if LAYER4_FILE.exists():
 print("📂 Load existierende Layer-4 Identities...")
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 existing_results = layer4_data.get("results", [])
 existing_count = len(existing_results)
 
 if existing_count == total:
 print(f"✅ Alle {total} Layer-4 Identities bereits vorhanden!")
 return {"status": "complete", "count": total}
 else:
 print(f"⚠️ Nur {existing_count}/{total} Layer-4 Identities vorhanden")
 print(" Leite fehlende ab...")
 start_idx = existing_count
 else:
 existing_results = []
 start_idx = 0
 
 # Leite fehlende ab
 print(f"🔍 Leite Layer-4 Identities ab (ab Index {start_idx})...")
 print(" ⚠️ Skipping RPC checks for speed")
 print()
 
 results = existing_results.copy()
 start_time = time.time()
 
 for i, l3_entry in enumerate(layer3_results[start_idx:], start=start_idx):
 l3_id = l3_entry.get("layer3_identity", "")
 
 if not l3_id or len(l3_id) != 60:
 results.append({
 "layer3_identity": l3_id,
 "seed": None,
 "layer4_identity": None,
 "layer4_derivable": False
 })
 continue
 
 seed = identity_to_seed(l3_id)
 l4_id = derive_identity_from_seed(seed)
 
 results.append({
 "layer3_identity": l3_id,
 "seed": seed,
 "layer4_identity": l4_id,
 "layer4_derivable": bool(l4_id and len(l4_id) == 60)
 })
 
 # Progress Update
 if (i + 1) % 1000 == 0 or (i + 1) == total:
 elapsed = time.time() - start_time
 rate = (i + 1 - start_idx) / elapsed if elapsed > 0 else 0
 remaining = (total - (i + 1)) / rate if rate > 0 else 0
 
 progress_data = {
 "current": i + 1,
 "total": total,
 "progress_percent": (i + 1) / total * 100,
 "start_time": start_time,
 "timestamp": time.time(),
 "eta_minutes": remaining / 60
 }
 
 with PROGRESS_FILE.open("w") as f:
 json.dump(progress_data, f, indent=2)
 
 print(f" Progress: {i+1}/{total} ({(i+1)/total*100:.1f}%) | Rate: {rate:.1f} ids/sec | ETA: {remaining/60:.1f} min")
 
 # Speichere Ergebnisse
 output_data = {
 "generated": datetime.now().isoformat(),
 "total": total,
 "results": results
 }
 
 with LAYER4_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print()
 print(f"✅ Alle {total} Layer-4 Identities abgeleitet")
 print(f"💾 Gespeichert: {LAYER4_FILE}")
 
 return {"status": "complete", "count": total}

def validate_position27_full() -> Dict:
 """Validate Position 27 auf vollständigem Datensatz."""
 
 print("=" * 80)
 print("VOLLSTÄNDIGE VALIDIERUNG: Position 27")
 print("=" * 80)
 print()
 
 # 1. Stelle sicher, dass alle Layer-4 Identities vorhanden sind
 print("📂 Check Layer-4 Identities...")
 derive_result = derive_all_layer4_identities_fast()
 
 if "error" in derive_result:
 return {"error": derive_result["error"]}
 
 print()
 
 # 2. Load alle Paare
 print("📂 Load alle Layer-3 → Layer-4 Paare...")
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 
 # Erstelle Mapping
 layer4_map = {}
 for entry in layer4_results:
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 if l3_id and l4_id and len(l3_id) == 60 and len(l4_id) == 60:
 layer4_map[l3_id] = l4_id
 
 # Erstelle Paare
 pairs = []
 for l3_entry in layer3_results:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 if l3_id and l4_id and len(l3_id) == 60 and len(l4_id) == 60:
 pairs.append({"layer3": l3_id, "layer4": l4_id})
 
 total_pairs = len(pairs)
 print(f"✅ {total_pairs} gültige Paare gefunden")
 print()
 
 # 3. Berechne Stabilität for alle Block-Ende-Positionen
 print("🔍 Berechne Stabilität for alle Block-Ende-Positionen...")
 positions_data = {}
 
 for pos in BLOCK_END_POSITIONS:
 same_count = 0
 different_count = 0
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 if len(l3_id) > pos and len(l4_id) > pos:
 if l3_id[pos].upper() == l4_id[pos].upper():
 same_count += 1
 else:
 different_count += 1
 
 total = same_count + different_count
 stability_rate = same_count / total if total > 0 else 0
 
 positions_data[pos] = {
 "stability_rate": stability_rate,
 "same_count": same_count,
 "different_count": different_count,
 "total": total
 }
 
 rate = stability_rate * 100
 print(f" Position {pos:2d}: {rate:5.1f}% ({same_count}/{total})")
 
 print()
 
 # 4. Statistische Signifikanz
 print("📊 Teste statistische Signifikanz...")
 contingency = []
 position_labels = []
 
 for pos in BLOCK_END_POSITIONS:
 data = positions_data[pos]
 same = data["same_count"]
 different = data["different_count"]
 contingency.append([same, different])
 position_labels.append(pos)
 
 chi2, p_value, dof, expected = chi2_contingency(contingency)
 n = sum(sum(row) for row in contingency)
 min_dim = min(len(contingency), len(contingency[0]))
 cramers_v = np.sqrt(chi2 / (n * (min_dim - 1))) if n > 0 and min_dim > 1 else 0
 
 print(f" Chi-Square: {chi2:.2f}")
 print(f" p-Wert: {p_value:.6f}")
 print(f" Signifikant: {'✅ JA' if p_value < 0.05 else '❌ NEIN'}")
 print(f" Effect Size: {'large' if cramers_v > 0.5 else 'medium' if cramers_v > 0.3 else 'small'} (Cramér's V: {cramers_v:.3f})")
 print()
 
 # 5. Vergleich Position 27 vs. andere
 pos27_data = positions_data[27]
 pos27_rate = pos27_data["stability_rate"] * 100
 
 print("🔍 Vergleich Position 27 vs. andere Block-Ende:")
 for pos in BLOCK_END_POSITIONS:
 if pos == 27:
 continue
 other_rate = positions_data[pos]["stability_rate"] * 100
 diff = pos27_rate - other_rate
 marker = "⭐" if diff > 5 else " "
 print(f" {marker} Position 27 ({pos27_rate:.1f}%) vs. Position {pos} ({other_rate:.1f}%): {diff:+.1f}%")
 print()
 
 # 6. Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_pairs": total_pairs,
 "positions_data": {
 str(k): {
 "stability_rate": v["stability_rate"],
 "same_count": v["same_count"],
 "different_count": v["different_count"],
 "total": v["total"]
 }
 for k, v in positions_data.items()
 },
 "statistical_significance": {
 "chi2": float(chi2),
 "p_value": float(p_value),
 "dof": int(dof),
 "significant": bool(p_value < 0.05),
 "cramers_v": float(cramers_v),
 "effect_size": "large" if cramers_v > 0.5 else "medium" if cramers_v > 0.3 else "small"
 }
 }
 
 output_file = OUTPUT_DIR / "position27_full_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # 7. Erstelle Report
 report_lines = [
 "# Vollständige Validierung: Position 27 (Alle 23.765 Identities)",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Ergebnisse",
 "",
 f"- **Total Paare**: {total_pairs}",
 "",
 "### Stabilitätsraten",
 ""
 ]
 
 for pos in BLOCK_END_POSITIONS:
 data = positions_data[pos]
 rate = data["stability_rate"] * 100
 report_lines.append(f"- **Position {pos}**: {rate:.1f}% ({data['same_count']}/{data['total']})")
 
 report_lines.extend([
 "",
 "### Statistische Signifikanz",
 "",
 f"- **Chi-Square**: {chi2:.2f}",
 f"- **p-Wert**: {p_value:.6f}",
 f"- **Signifikant**: {'✅ JA' if p_value < 0.05 else '❌ NEIN'}",
 f"- **Effect Size**: {'large' if cramers_v > 0.5 else 'medium' if cramers_v > 0.3 else 'small'} (Cramér's V: {cramers_v:.3f})",
 "",
 "### Vergleich Position 27",
 ""
 ])
 
 for pos in BLOCK_END_POSITIONS:
 if pos == 27:
 continue
 other_rate = positions_data[pos]["stability_rate"] * 100
 diff = pos27_rate - other_rate
 report_lines.append(f"- **Position 27 ({pos27_rate:.1f}%) vs. Position {pos} ({other_rate:.1f}%)**: {diff:+.1f}%")
 
 report_file = REPORTS_DIR / "position27_full_validation_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 return output_data

if __name__ == "__main__":
 validate_position27_full()

