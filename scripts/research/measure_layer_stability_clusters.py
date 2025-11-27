#!/usr/bin/env python3
"""
Layer-Stabilität for Cluster-Sequenzen messen
- Vergleicht GOT GO und NOW NO Sequenzen zwischen Layer-3 und Layer-4
- Misst Fixpunkte vs. Mutationen
- Output: JSON mit Stabilitäts-Metriken

MANUELL AUSFÜHREN:
 python3 scripts/research/measure_layer_stability_clusters.py

FORTSCHRITT:
 tail -f outputs/derived/layer_stability_clusters_status.txt
"""

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
STATUS_FILE = OUTPUT_DIR / "layer_stability_clusters_status.txt"
RESULTS_FILE = OUTPUT_DIR / "layer_stability_clusters_results.json"

# Target sequences from cluster plan
TARGET_SEQUENCES = {
 "GOT_GO": ["GOT", "GO"],
 "NOW_NO": ["NOW", "NO"],
}

def log_progress(message: str):
 """Log progress to file and console."""
 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 with STATUS_FILE.open("a") as f:
 f.write(f"[{timestamp}] {message}\n")
 print(f"[{timestamp}] {message}")

def find_sequence_positions(identity: str, sequence: List[str], max_gap: int = 10) -> List[Dict]:
 """Find all occurrences of a word sequence in an identity."""
 identity_upper = identity.upper()
 matches = []
 
 for i, word in enumerate(sequence):
 if i == 0:
 # Find first word
 pos = identity_upper.find(word)
 if pos != -1:
 matches.append({"word": word, "position": pos, "index": i})
 else:
 # Find subsequent words near previous match
 prev_match = matches[-1] if matches else None
 if prev_match:
 search_start = prev_match["position"] + len(prev_match["word"])
 search_end = search_start + max_gap
 pos = identity_upper.find(word, search_start, search_end)
 if pos != -1:
 matches.append({"word": word, "position": pos, "index": i})
 else:
 return [] # Sequence broken
 
 return matches if len(matches) == len(sequence) else []

def check_sequence_stability(l3_id: str, l4_id: str, sequence: List[str]) -> Dict:
 """Check if a sequence is stable between Layer-3 and Layer-4."""
 l3_matches = find_sequence_positions(l3_id, sequence)
 l4_matches = find_sequence_positions(l4_id, sequence)
 
 if not l3_matches:
 return {"status": "not_found_l3", "stable": False}
 
 if not l4_matches:
 return {"status": "lost_in_l4", "stable": False}
 
 # Check if positions are similar (within tolerance)
 l3_positions = [m["position"] for m in l3_matches]
 l4_positions = [m["position"] for m in l4_matches]
 
 position_diffs = [abs(l4_pos - l3_pos) for l3_pos, l4_pos in zip(l3_positions, l4_positions)]
 max_diff = max(position_diffs) if position_diffs else 0
 
 # Consider stable if positions are within 2 characters
 is_stable = max_diff <= 2 and len(l3_matches) == len(l4_matches)
 
 return {
 "status": "stable" if is_stable else "shifted",
 "stable": is_stable,
 "l3_positions": l3_positions,
 "l4_positions": l4_positions,
 "position_diffs": position_diffs,
 "max_diff": max_diff,
 }

def main():
 """Main function."""
 log_progress("=" * 80)
 log_progress("LAYER STABILITY FOR CLUSTER SEQUENCES")
 log_progress("=" * 80)
 log_progress("")
 
 # Load Layer-3 data
 log_progress("📂 Load Layer-3 Daten...")
 if not LAYER3_FILE.exists():
 log_progress(f"❌ Layer-3 Datei fehlt: {LAYER3_FILE}")
 return
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 
 layer3_map = {}
 for entry in layer3_data.get("results", []):
 l3_id = entry.get("layer3_identity", "")
 seed = entry.get("seed", "")
 if l3_id and len(l3_id) == 60 and seed:
 layer3_map[seed] = l3_id
 
 log_progress(f"✅ {len(layer3_map)} Layer-3 Identities geloadn")
 
 # Load Layer-4 data
 log_progress("📂 Load Layer-4 Daten...")
 if not LAYER4_FILE.exists():
 log_progress(f"⚠️ Layer-4 Datei fehlt: {LAYER4_FILE}")
 log_progress(" Verwende nur Layer-3 Daten for Analyse")
 layer4_map = {}
 else:
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 
 layer4_map = {}
 for entry in layer4_data.get("results", []):
 seed = entry.get("seed", "")
 l4_id = entry.get("layer4_identity", "")
 if seed and l4_id and len(l4_id) == 60:
 layer4_map[seed] = l4_id
 
 log_progress(f"✅ {len(layer4_map)} Layer-4 Identities geloadn")
 
 # Analyze sequences
 log_progress("")
 log_progress("🔍 Analyze Sequenz-Stabilität...")
 
 results = {}
 
 for seq_name, sequence in TARGET_SEQUENCES.items():
 log_progress(f" Analyze {seq_name} ({' '.join(sequence)})...")
 
 stats = {
 "total_l3_found": 0,
 "total_l4_found": 0,
 "stable_count": 0,
 "shifted_count": 0,
 "lost_count": 0,
 "not_found_l3_count": 0,
 "stability_rate": 0.0,
 "examples": [],
 }
 
 analyzed = 0
 for seed, l3_id in list(layer3_map.items())[:5000]: # Sample first 5000 for speed
 analyzed += 1
 if analyzed % 1000 == 0:
 log_progress(f" Fortschritt: {analyzed}/{min(5000, len(layer3_map))}")
 
 l3_matches = find_sequence_positions(l3_id, sequence)
 if l3_matches:
 stats["total_l3_found"] += 1
 
 if seed in layer4_map:
 l4_id = layer4_map[seed]
 stability = check_sequence_stability(l3_id, l4_id, sequence)
 
 if stability["status"] == "stable":
 stats["stable_count"] += 1
 if len(stats["examples"]) < 5:
 stats["examples"].append({
 "seed": seed[:20] + "...",
 "l3_id": l3_id,
 "l4_id": l4_id,
 "l3_positions": stability["l3_positions"],
 "l4_positions": stability["l4_positions"],
 })
 elif stability["status"] == "shifted":
 stats["shifted_count"] += 1
 elif stability["status"] == "lost_in_l4":
 stats["lost_count"] += 1
 else:
 stats["lost_count"] += 1
 else:
 stats["not_found_l3_count"] += 1
 
 total_with_l4 = stats["stable_count"] + stats["shifted_count"] + stats["lost_count"]
 if total_with_l4 > 0:
 stats["stability_rate"] = (stats["stable_count"] / total_with_l4) * 100
 
 results[seq_name] = stats
 log_progress(f" ✅ {seq_name}: {stats['stable_count']}/{total_with_l4} stabil ({stats['stability_rate']:.1f}%)")
 
 # Save results
 log_progress("")
 log_progress("💾 Speichere Ergebnisse...")
 with RESULTS_FILE.open("w") as f:
 json.dump(results, f, indent=2)
 
 log_progress(f"✅ Ergebnisse gespeichert: {RESULTS_FILE}")
 log_progress("")
 log_progress("=" * 80)
 log_progress("✅ ANALYSE ABGESCHLOSSEN")
 log_progress("=" * 80)

if __name__ == "__main__":
 main()

