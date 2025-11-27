#!/usr/bin/env python3
"""
Analyze Character-Transition Patterns in Layer-3 → Layer-4 Transformation
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_pairs() -> List[Dict]:
 """Load Layer-3 → Layer-4 Paare."""
 layer3_data = []
 if LAYER3_FILE.exists():
 with LAYER3_FILE.open() as f:
 data = json.load(f)
 layer3_data = data.get("results", [])
 
 layer4_map = {}
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 data = json.load(f)
 for entry in data.get("results", []):
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 if l3_id and l4_id:
 layer4_map[l3_id] = l4_id
 
 pairs = []
 for l3_entry in layer3_data:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 if l3_id and l4_id and len(l3_id) == 60 and len(l4_id) == 60:
 pairs.append({"layer3": l3_id, "layer4": l4_id})
 
 return pairs

def analyze_character_transitions(pairs: List[Dict]) -> Dict:
 """Analyze Character-Transition Patterns."""
 
 # 1. Direkte Transitions (A->B, C->D, etc.)
 direct_transitions = Counter()
 
 # 2. Position-spezifische Transitions
 position_transitions = defaultdict(lambda: Counter())
 
 # 3. Character-Distanzen (A=0, B=1, ..., Z=25)
 char_distances = defaultdict(list)
 
 # 4. Häufigste Transition-Patterns pro Position
 position_transition_patterns = defaultdict(lambda: Counter())
 
 # 5. Stabile Characters pro Position (bleiben gleich)
 stable_chars_per_position = defaultdict(Counter)
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 for pos in range(60):
 l3_char = l3_id[pos].upper()
 l4_char = l4_id[pos].upper()
 
 if l3_char == l4_char:
 stable_chars_per_position[pos][l3_char] += 1
 else:
 transition = f"{l3_char}->{l4_char}"
 direct_transitions[transition] += 1
 position_transitions[pos][transition] += 1
 
 # Character-Distanz
 l3_val = ord(l3_char) - ord('A')
 l4_val = ord(l4_char) - ord('A')
 distance = (l4_val - l3_val) % 26 # Circular distance
 char_distances[pos].append(distance)
 
 # Analyze Distanzen
 distance_stats = {}
 for pos in range(60):
 if pos in char_distances and char_distances[pos]:
 distances = char_distances[pos]
 distance_stats[pos] = {
 "mean": sum(distances) / len(distances),
 "most_common": Counter(distances).most_common(5)
 }
 
 return {
 "total_pairs": len(pairs),
 "direct_transitions": dict(direct_transitions.most_common(30)),
 "position_transitions": {str(k): dict(v.most_common(10)) for k, v in position_transitions.items()},
 "stable_chars_per_position": {str(k): dict(v.most_common(10)) for k, v in stable_chars_per_position.items()},
 "distance_stats": {str(k): v for k, v in distance_stats.items()},
 "top_transitions_by_position": {
 str(pos): list(position_transitions[pos].most_common(5))
 for pos in [27, 55, 30, 4]
 if pos in position_transitions
 }
 }

def analyze_seed_transformations(pairs: List[Dict]) -> Dict:
 """Analyze Seed-Transformationen."""
 
 # Seeds sind identity.lower()[:55]
 seed_changes = []
 seed_stability = {"same": 0, "different": 0}
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 l3_seed = l3_id.lower()[:55]
 l4_seed = l4_id.lower()[:55]
 
 if l3_seed == l4_seed:
 seed_stability["same"] += 1
 else:
 seed_stability["different"] += 1
 # Analyze Seed-Änderungen
 changes = sum(1 for i in range(55) if l3_seed[i] != l4_seed[i])
 seed_changes.append(changes)
 
 return {
 "seed_stability": seed_stability,
 "seed_change_stats": {
 "mean": sum(seed_changes) / len(seed_changes) if seed_changes else 0,
 "min": min(seed_changes) if seed_changes else 0,
 "max": max(seed_changes) if seed_changes else 0,
 "distribution": dict(Counter(seed_changes))
 }
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("CHARACTER-TRANSITION PATTERNS ANALYSE")
 print("=" * 80)
 print()
 
 # Load Paare
 print("📂 Load Layer-3 → Layer-4 Paare...")
 pairs = load_pairs()
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Analyze Transitions
 print("🔍 Analyze Character-Transitions...")
 transition_analysis = analyze_character_transitions(pairs)
 print("✅ Character-Transitions analysiert")
 print()
 
 # Analyze Seed-Transformationen
 print("🔍 Analyze Seed-Transformationen...")
 seed_analysis = analyze_seed_transformations(pairs)
 print("✅ Seed-Transformationen analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Top Transitions
 top_transitions = transition_analysis.get("direct_transitions", {})
 if top_transitions:
 print("📊 Top 15 Character-Transitions:")
 for i, (transition, count) in enumerate(list(top_transitions.items())[:15], 1):
 print(f" {i:2d}. {transition}: {count} Fälle")
 print()
 
 # Position-spezifische Transitions (27, 55, 30, 4)
 top_by_pos = transition_analysis.get("top_transitions_by_position", {})
 if top_by_pos:
 print("📊 Top Transitions for wichtige Positionen:")
 for pos in [27, 55, 30, 4]:
 pos_str = str(pos)
 if pos_str in top_by_pos:
 print(f" Position {pos}:")
 for transition, count in top_by_pos[pos_str][:5]:
 print(f" {transition}: {count} Fälle")
 print()
 
 # Seed-Analyse
 seed_stab = seed_analysis.get("seed_stability", {})
 if seed_stab:
 total = seed_stab.get("same", 0) + seed_stab.get("different", 0)
 if total > 0:
 same_rate = seed_stab.get("same", 0) / total * 100
 print(f"📊 Seed-Stabilität: {same_rate:.1f}% bleiben gleich ({seed_stab.get('same', 0)}/{total})")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "transition_analysis": transition_analysis,
 "seed_analysis": seed_analysis
 }
 
 output_file = OUTPUT_DIR / "character_transitions_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Character-Transition Patterns Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 f"**Analysierte Paare**: {len(pairs)}",
 "",
 "## Top Character-Transitions",
 ""
 ]
 
 if top_transitions:
 for i, (transition, count) in enumerate(list(top_transitions.items())[:20], 1):
 report_lines.append(f"{i}. **{transition}**: {count} Fälle")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "character_transitions_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

