#!/usr/bin/env python3
"""
Position 27 Deep Dive - Warum A, B, C Transitions?
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

def analyze_position27_deep(pairs: List[Dict]) -> Dict:
 """Deep Dive in Position 27."""
 
 # 1. Character-Distribution in Layer-3 Position 27
 l3_pos27_chars = Counter()
 
 # 2. Character-Distribution in Layer-4 Position 27
 l4_pos27_chars = Counter()
 
 # 3. Transitions von Layer-3 zu Layer-4
 transitions = Counter()
 
 # 4. Stabile Characters (bleiben gleich)
 stable_chars = Counter()
 
 # 5. Context-Analyse (Position 26, 27, 28)
 context_analysis = defaultdict(lambda: {"l3": Counter(), "l4": Counter(), "transitions": Counter()})
 
 # 6. Character-Distanzen for Position 27
 distances = []
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 if len(l3_id) > 27 and len(l4_id) > 27:
 l3_char = l3_id[27].upper()
 l4_char = l4_id[27].upper()
 
 l3_pos27_chars[l3_char] += 1
 l4_pos27_chars[l4_char] += 1
 
 if l3_char == l4_char:
 stable_chars[l3_char] += 1
 else:
 transition = f"{l3_char}->{l4_char}"
 transitions[transition] += 1
 
 # Character-Distanz
 l3_val = ord(l3_char) - ord('A')
 l4_val = ord(l4_char) - ord('A')
 distance = min((l4_val - l3_val) % 26, (l3_val - l4_val) % 26)
 distances.append(distance)
 
 # Context (Position 26, 27, 28)
 if len(l3_id) > 28:
 context = f"{l3_id[26].upper()}{l3_id[27].upper()}{l3_id[28].upper()}"
 context_analysis[context]["l3"][l3_char] += 1
 context_analysis[context]["l4"][l4_char] += 1
 if l3_char != l4_char:
 context_analysis[context]["transitions"][f"{l3_char}->{l4_char}"] += 1
 
 # Analyze warum A, B, C
 abc_analysis = {
 "abc_in_l3": sum(l3_pos27_chars[c] for c in ['A', 'B', 'C']),
 "abc_in_l4": sum(l4_pos27_chars[c] for c in ['A', 'B', 'C']),
 "abc_transitions": sum(transitions[t] for t in transitions if t.startswith(('A->', 'B->', 'C->')) or '->A' in t or '->B' in t or '->C' in t),
 "abc_stable": sum(stable_chars[c] for c in ['A', 'B', 'C'])
 }
 
 return {
 "total_pairs": len(pairs),
 "l3_pos27_distribution": dict(l3_pos27_chars.most_common(26)),
 "l4_pos27_distribution": dict(l4_pos27_chars.most_common(26)),
 "transitions": dict(transitions.most_common(30)),
 "stable_chars": dict(stable_chars.most_common(26)),
 "abc_analysis": abc_analysis,
 "distance_stats": {
 "mean": sum(distances) / len(distances) if distances else 0,
 "distribution": dict(Counter(distances).most_common(10))
 },
 "context_analysis": {
 k: {
 "l3": dict(v["l3"].most_common(5)),
 "l4": dict(v["l4"].most_common(5)),
 "transitions": dict(v["transitions"].most_common(5))
 }
 for k, v in list(context_analysis.items())[:20]
 }
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("POSITION 27 DEEP DIVE")
 print("=" * 80)
 print()
 
 # Load Paare
 print("📂 Load Layer-3 → Layer-4 Paare...")
 pairs = load_pairs()
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Analyze Position 27
 print("🔍 Analyze Position 27 im Detail...")
 analysis = analyze_position27_deep(pairs)
 print("✅ Position 27 analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # A, B, C Analyse
 abc = analysis.get("abc_analysis", {})
 if abc:
 total = analysis.get("total_pairs", 0)
 print("📊 A, B, C Analyse:")
 print(f" A, B, C in Layer-3: {abc.get('abc_in_l3', 0)} ({abc.get('abc_in_l3', 0)/total*100:.1f}%)")
 print(f" A, B, C in Layer-4: {abc.get('abc_in_l4', 0)} ({abc.get('abc_in_l4', 0)/total*100:.1f}%)")
 print(f" A, B, C Transitions: {abc.get('abc_transitions', 0)}")
 print(f" A, B, C Stable: {abc.get('abc_stable', 0)}")
 print()
 
 # Top Transitions
 transitions = analysis.get("transitions", {})
 if transitions:
 print("📊 Top 15 Transitions:")
 for i, (transition, count) in enumerate(list(transitions.items())[:15], 1):
 print(f" {i:2d}. {transition}: {count} Fälle")
 print()
 
 # Stabile Characters
 stable = analysis.get("stable_chars", {})
 if stable:
 print("📊 Top 10 Stabile Characters:")
 for i, (char, count) in enumerate(list(stable.items())[:10], 1):
 print(f" {i:2d}. {char}: {count} Fälle")
 print()
 
 # Character-Distanzen
 dist_stats = analysis.get("distance_stats", {})
 if dist_stats:
 print("📊 Character-Distanzen:")
 print(f" Mean: {dist_stats.get('mean', 0):.2f}")
 dist_dist = dist_stats.get("distribution", {})
 if dist_dist:
 print(" Top Distanzen:")
 for dist, count in list(dist_dist.items())[:5]:
 print(f" {dist}: {count} Fälle")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "analysis": analysis
 }
 
 output_file = OUTPUT_DIR / "position27_deep_dive.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Position 27 Deep Dive",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## A, B, C Analyse",
 ""
 ]
 
 if abc:
 total = analysis.get("total_pairs", 0)
 report_lines.extend([
 f"- **A, B, C in Layer-3**: {abc.get('abc_in_l3', 0)} ({abc.get('abc_in_l3', 0)/total*100:.1f}%)",
 f"- **A, B, C in Layer-4**: {abc.get('abc_in_l4', 0)} ({abc.get('abc_in_l4', 0)/total*100:.1f}%)",
 f"- **A, B, C Transitions**: {abc.get('abc_transitions', 0)}",
 f"- **A, B, C Stable**: {abc.get('abc_stable', 0)}",
 ""
 ])
 
 report_file = REPORTS_DIR / "position27_deep_dive_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

