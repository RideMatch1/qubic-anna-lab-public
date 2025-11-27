#!/usr/bin/env python3
"""
Tiefe Analyse von Position 27
- Warum ist Position 27 so stabil (25.7%)?
- Welche Charaktere sind am stabilsten?
- Gibt es Patterns bei Position 27?
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def analyze_position27_stability() -> Dict:
 """Analyze Position 27 Stabilität im Detail."""
 
 # Load Layer-3 und Layer-4 Daten
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_identities = [e.get("layer3_identity", "") for e in layer3_data.get("results", []) if len(e.get("layer3_identity", "")) == 60]
 
 layer4_map = {}
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 for entry in layer4_data.get("results", []):
 layer3_id = entry.get("layer3_identity", "")
 layer4_id = entry.get("layer4_identity", "")
 if len(layer3_id) == 60 and len(layer4_id) == 60:
 layer4_map[layer3_id] = layer4_id
 
 # Analyze Position 27
 position27_analysis = {
 "total_pairs": 0,
 "stable_count": 0,
 "stable_rate": 0.0,
 "character_stability": defaultdict(lambda: {"total": 0, "stable": 0}),
 "character_transitions": defaultdict(lambda: defaultdict(int)),
 "stable_characters": [],
 "unstable_characters": []
 }
 
 for layer3_id in layer3_identities:
 if layer3_id not in layer4_map:
 continue
 
 layer4_id = layer4_map[layer3_id]
 position27_analysis["total_pairs"] += 1
 
 char3 = layer3_id[27]
 char4 = layer4_id[27]
 
 # Charakter-Statistik
 position27_analysis["character_stability"][char3]["total"] += 1
 if char3 == char4:
 position27_analysis["stable_count"] += 1
 position27_analysis["character_stability"][char3]["stable"] += 1
 else:
 # Transition
 position27_analysis["character_transitions"][char3][char4] += 1
 
 # Berechne Stabilitäts-Rate
 if position27_analysis["total_pairs"] > 0:
 position27_analysis["stable_rate"] = position27_analysis["stable_count"] / position27_analysis["total_pairs"]
 
 # Finde stabilste Charaktere
 for char, stats in position27_analysis["character_stability"].items():
 if stats["total"] > 0:
 stability_rate = stats["stable"] / stats["total"]
 if stats["total"] >= 10: # Mindestens 10 Vorkommen
 position27_analysis["stable_characters"].append({
 "character": char,
 "total": stats["total"],
 "stable": stats["stable"],
 "stability_rate": stability_rate
 })
 
 position27_analysis["stable_characters"].sort(key=lambda x: (x["stability_rate"], x["total"]), reverse=True)
 
 # Finde unstabilste Charaktere
 for char, stats in position27_analysis["character_stability"].items():
 if stats["total"] > 0:
 stability_rate = stats["stable"] / stats["total"]
 if stats["total"] >= 10 and stability_rate < 0.5: # Weniger als 50% stabil
 position27_analysis["unstable_characters"].append({
 "character": char,
 "total": stats["total"],
 "stable": stats["stable"],
 "stability_rate": stability_rate
 })
 
 position27_analysis["unstable_characters"].sort(key=lambda x: x["stability_rate"])
 
 return position27_analysis

def analyze_position27_context() -> Dict:
 """Analyze context um Position 27."""
 
 # Load Daten
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_identities = [e.get("layer3_identity", "") for e in layer3_data.get("results", []) if len(e.get("layer3_identity", "")) == 60]
 
 layer4_map = {}
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 for entry in layer4_data.get("results", []):
 layer3_id = entry.get("layer3_identity", "")
 layer4_id = entry.get("layer4_identity", "")
 if len(layer3_id) == 60 and len(layer4_id) == 60:
 layer4_map[layer3_id] = layer4_id
 
 # Analyze context (Positionen 25-29)
 context_analysis = {
 "position_stability": {},
 "block_stability": {}
 }
 
 for pos in range(25, 30): # Positionen 25-29
 stable_count = 0
 total_count = 0
 
 for layer3_id in layer3_identities:
 if layer3_id not in layer4_map:
 continue
 
 layer4_id = layer4_map[layer3_id]
 total_count += 1
 
 if layer3_id[pos] == layer4_id[pos]:
 stable_count += 1
 
 if total_count > 0:
 context_analysis["position_stability"][pos] = {
 "total": total_count,
 "stable": stable_count,
 "rate": stable_count / total_count
 }
 
 # Block-Stabilität (Block 14-27)
 block_stable = 0
 block_total = 0
 
 for layer3_id in layer3_identities:
 if layer3_id not in layer4_map:
 continue
 
 layer4_id = layer4_map[layer3_id]
 block_total += 1
 
 # Check ob Block 14-27 identisch ist
 if layer3_id[14:28] == layer4_id[14:28]:
 block_stable += 1
 
 if block_total > 0:
 context_analysis["block_stability"] = {
 "total": block_total,
 "stable": block_stable,
 "rate": block_stable / block_total
 }
 
 return context_analysis

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("TIEFE ANALYSE VON POSITION 27")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print()
 
 # Analyze Position 27 Stabilität
 print("🔍 Analyze Position 27 Stabilität...")
 position27_analysis = analyze_position27_stability()
 print(f"✅ {position27_analysis['total_pairs']} Paare analysiert")
 print(f" Stabilität: {position27_analysis['stable_rate']*100:.1f}%")
 print()
 
 # Analyze context
 print("🔍 Analyze context um Position 27...")
 context_analysis = analyze_position27_context()
 print("✅ context-Analyse abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 print(f"📊 Position 27 Stabilität:")
 print(f" Total Paare: {position27_analysis['total_pairs']}")
 print(f" Stabile: {position27_analysis['stable_count']}")
 print(f" Stabilitäts-Rate: {position27_analysis['stable_rate']*100:.1f}%")
 print()
 
 print("📊 Top 20 stabilste Charaktere an Position 27:")
 for i, char_data in enumerate(position27_analysis["stable_characters"][:20], 1):
 print(f" {i}. '{char_data['character']}': {char_data['stability_rate']*100:.1f}% ({char_data['stable']}/{char_data['total']})")
 print()
 
 if position27_analysis["unstable_characters"]:
 print("📊 Unstabilste Charaktere an Position 27:")
 for i, char_data in enumerate(position27_analysis["unstable_characters"][:10], 1):
 print(f" {i}. '{char_data['character']}': {char_data['stability_rate']*100:.1f}% ({char_data['stable']}/{char_data['total']})")
 print()
 
 print("📊 context-Stabilität (Positionen 25-29):")
 for pos in sorted(context_analysis["position_stability"].keys()):
 data = context_analysis["position_stability"][pos]
 marker = " ⭐" if pos == 27 else ""
 print(f" Position {pos}: {data['rate']*100:.1f}% ({data['stable']}/{data['total']}){marker}")
 print()
 
 if context_analysis["block_stability"]:
 block_data = context_analysis["block_stability"]
 print(f"📊 Block 14-27 Stabilität:")
 print(f" {block_data['rate']*100:.1f}% ({block_data['stable']}/{block_data['total']})")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "position27_analysis": {
 "total_pairs": position27_analysis["total_pairs"],
 "stable_count": position27_analysis["stable_count"],
 "stable_rate": position27_analysis["stable_rate"],
 "stable_characters": position27_analysis["stable_characters"],
 "unstable_characters": position27_analysis["unstable_characters"],
 "character_transitions": {
 char: dict(transitions) for char, transitions in position27_analysis["character_transitions"].items()
 }
 },
 "context_analysis": context_analysis
 }
 
 output_file = OUTPUT_DIR / "position27_deep_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

