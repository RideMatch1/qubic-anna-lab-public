#!/usr/bin/env python3
"""
Position 27 Deep Dive Research

Warum ist Position 27 der Marker for Layer-3 On-chain Status?
Analysiert Position 27 in allen Layers und findet Patterns.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_all_layer_data() -> Dict:
 """Load Daten aus allen Layers."""
 data = {
 "layer1": [],
 "layer2": [],
 "layer3": []
 }
 
 # Layer-1 aus Mapping Database
 db_file = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
 if db_file.exists():
 with db_file.open() as f:
 db = json.load(f)
 # Sample von Layer-1
 seed_to_real_id = db.get("seed_to_real_id", {})
 data["layer1"] = list(seed_to_real_id.values())[:100]
 
 # Layer-2 und Layer-3
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 if layer3_file.exists():
 with layer3_file.open() as f:
 layer3_data = json.load(f)
 
 for result in layer3_data.get("results", []):
 layer2 = result.get("layer2_identity")
 layer3 = result.get("layer3_identity")
 if layer2:
 data["layer2"].append(layer2)
 if layer3:
 data["layer3"].append(layer3)
 
 return data

def analyze_position27_all_layers(data: Dict) -> Dict:
 """Analyze Position 27 in allen Layers."""
 results = {}
 
 for layer_name, identities in data.items():
 if not identities:
 continue
 
 pos27_chars = []
 pos27_dist = Counter()
 
 for identity in identities:
 if len(identity) > 27:
 char = identity[27]
 pos27_chars.append(char)
 pos27_dist[char] += 1
 
 # On-chain vs Off-chain for Layer-3
 if layer_name == "layer3":
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 if layer3_file.exists():
 with layer3_file.open() as f:
 layer3_data = json.load(f)
 
 onchain_pos27 = []
 offchain_pos27 = []
 
 for result in layer3_data.get("results", []):
 layer3_id = result.get("layer3_identity")
 is_onchain = result.get("layer3_onchain", False)
 
 if layer3_id and len(layer3_id) > 27:
 char = layer3_id[27]
 if is_onchain:
 onchain_pos27.append(char)
 else:
 offchain_pos27.append(char)
 
 results[layer_name] = {
 "total": len(identities),
 "position27_distribution": dict(pos27_dist.most_common(26)),
 "onchain_pos27": Counter(onchain_pos27),
 "offchain_pos27": Counter(offchain_pos27),
 "onchain_top_char": Counter(onchain_pos27).most_common(1)[0] if onchain_pos27 else None,
 "offchain_top_char": Counter(offchain_pos27).most_common(1)[0] if offchain_pos27 else None
 }
 else:
 results[layer_name] = {
 "total": len(identities),
 "position27_distribution": dict(pos27_dist.most_common(26))
 }
 else:
 results[layer_name] = {
 "total": len(identities),
 "position27_distribution": dict(pos27_dist.most_common(26))
 }
 
 return results

def analyze_position27_context(data: Dict) -> Dict:
 """Analyze context um Position 27."""
 context_analysis = {}
 
 for layer_name, identities in data.items():
 if not identities or layer_name != "layer3":
 continue
 
 # Analyze Position 26, 27, 28 (context)
 context_patterns = defaultdict(Counter)
 
 for identity in identities:
 if len(identity) > 28:
 # 3-char Pattern um Position 27
 pattern = identity[26:29]
 context_patterns["pattern_26_28"][pattern] += 1
 
 # Einzelne Positionen
 context_patterns["pos26"][identity[26]] += 1
 context_patterns["pos27"][identity[27]] += 1
 context_patterns["pos28"][identity[28]] += 1
 
 context_analysis[layer_name] = {
 "pattern_26_28": dict(context_patterns["pattern_26_28"].most_common(20)),
 "pos26_dist": dict(context_patterns["pos26"].most_common(10)),
 "pos27_dist": dict(context_patterns["pos27"].most_common(10)),
 "pos28_dist": dict(context_patterns["pos28"].most_common(10))
 }
 
 return context_analysis

def analyze_position27_meaning() -> Dict:
 """Forscht nach der Bedeutung von Position 27."""
 # Position 27 in 60-char identity = Position 27/60 = 45% durch
 # Das ist nahe der Mitte (30 wäre genau Mitte)
 
 # In Qubic Identity:
 # - Positions 0-55: Body (56 chars)
 # - Positions 56-59: Checksum (4 chars)
 # Position 27 ist in der ersten Hälfte des Bodies
 
 # Mögliche Bedeutungen:
 meanings = {
 "position_in_identity": 27,
 "position_percentage": 27/60 * 100,
 "in_body": True,
 "body_position": 27,
 "distance_to_checksum": 60 - 27,
 "possible_meanings": [
 "Part of public key encoding",
 "Selection marker for on-chain status",
 "Layer indicator",
 "Functional role marker",
 "Evolutionary fitness marker"
 ]
 }
 
 return meanings

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("POSITION 27 DEEP DIVE RESEARCH")
 print("=" * 80)
 print()
 
 # Load Daten
 print("Loading all layer data...")
 data = load_all_layer_data()
 print(f"✅ Layer-1: {len(data['layer1'])} identities")
 print(f"✅ Layer-2: {len(data['layer2'])} identities")
 print(f"✅ Layer-3: {len(data['layer3'])} identities")
 print()
 
 # Analyze Position 27
 print("Analyzing Position 27 in all layers...")
 pos27_analysis = analyze_position27_all_layers(data)
 
 print("=" * 80)
 print("POSITION 27 ANALYSIS RESULTS")
 print("=" * 80)
 print()
 
 for layer_name, analysis in pos27_analysis.items():
 print(f"Layer {layer_name}:")
 print(f" Total: {analysis['total']}")
 
 if "onchain_top_char" in analysis and analysis["onchain_top_char"]:
 onchain_char, onchain_count = analysis["onchain_top_char"]
 offchain_char, offchain_count = analysis["offchain_top_char"]
 print(f" On-chain top char at pos27: '{onchain_char}' ({onchain_count} occurrences)")
 print(f" Off-chain top char at pos27: '{offchain_char}' ({offchain_count} occurrences)")
 
 print(f" Top 5 chars at pos27:")
 for char, count in list(analysis["position27_distribution"].items())[:5]:
 pct = (count / analysis["total"]) * 100
 print(f" '{char}': {count} ({pct:.1f}%)")
 print()
 
 # context-Analyse
 print("Analyzing context around Position 27...")
 context_analysis = analyze_position27_context(data)
 
 if "layer3" in context_analysis:
 print("\nLayer-3 Context (Positions 26-28):")
 ctx = context_analysis["layer3"]
 print(f" Top patterns (26-28):")
 for pattern, count in list(ctx["pattern_26_28"].items())[:5]:
 print(f" '{pattern}': {count}")
 print()
 
 # Bedeutung
 meanings = analyze_position27_meaning()
 print("Position 27 Meaning Analysis:")
 print(f" Position: {meanings['position_in_identity']}/60 ({meanings['position_percentage']:.1f}%)")
 print(f" In body: {meanings['in_body']}")
 print(f" Distance to checksum: {meanings['distance_to_checksum']} positions")
 print(f" Possible meanings:")
 for meaning in meanings["possible_meanings"]:
 print(f" - {meaning}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 results = {
 "position27_analysis": pos27_analysis,
 "context_analysis": context_analysis,
 "meaning_analysis": meanings
 }
 
 output_json = OUTPUT_DIR / "position27_deep_dive.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "position27_deep_dive_report.md"
 
 with output_md.open("w") as f:
 f.write("# Position 27 Deep Dive Research Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write("Deep analysis of Position 27 as the Layer-3 on-chain marker.\n\n")
 
 f.write("## Position 27 Analysis by Layer\n\n")
 for layer_name, analysis in pos27_analysis.items():
 f.write(f"### Layer {layer_name}\n\n")
 f.write(f"- **Total**: {analysis['total']}\n")
 
 if "onchain_top_char" in analysis and analysis["onchain_top_char"]:
 onchain_char, onchain_count = analysis["onchain_top_char"]
 offchain_char, offchain_count = analysis["offchain_top_char"]
 f.write(f"- **On-chain top char**: `{onchain_char}` ({onchain_count} occurrences)\n")
 f.write(f"- **Off-chain top char**: `{offchain_char}` ({offchain_count} occurrences)\n")
 
 f.write(f"\n**Top 10 Characters at Position 27:**\n\n")
 f.write("| Char | Count | Percentage |\n")
 f.write("|------|-------|------------|\n")
 for char, count in list(analysis["position27_distribution"].items())[:10]:
 pct = (count / analysis["total"]) * 100
 f.write(f"| `{char}` | {count} | {pct:.1f}% |\n")
 f.write("\n")
 
 f.write("## Context Analysis\n\n")
 if "layer3" in context_analysis:
 ctx = context_analysis["layer3"]
 f.write("### Layer-3 Context (Positions 26-28)\n\n")
 f.write("**Top Patterns (26-28):**\n\n")
 for pattern, count in list(ctx["pattern_26_28"].items())[:10]:
 f.write(f"- `{pattern}`: {count} occurrences\n")
 f.write("\n")
 
 f.write("## Meaning Analysis\n\n")
 f.write(f"- **Position**: {meanings['position_in_identity']}/60 ({meanings['position_percentage']:.1f}%)\n")
 f.write(f"- **In body**: {meanings['in_body']}\n")
 f.write(f"- **Distance to checksum**: {meanings['distance_to_checksum']} positions\n")
 f.write(f"\n**Possible Meanings:**\n\n")
 for meaning in meanings["possible_meanings"]:
 f.write(f"- {meaning}\n")
 f.write("\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

