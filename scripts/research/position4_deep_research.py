#!/usr/bin/env python3
"""
Position 4 Deep Research

Warum ist Position 4 der beste Prädiktor?
Tiefe Analyse der Patterns, Beziehungen und Bedeutung.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
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
 
 # Layer-1
 db_file = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
 if db_file.exists():
 with db_file.open() as f:
 db = json.load(f)
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

def analyze_position4_evolution(data: Dict) -> Dict:
 """Analyze Evolution von Position 4 durch die Layers."""
 evolution = {}
 
 for layer_name in ["layer1", "layer2", "layer3"]:
 identities = data.get(layer_name, [])
 
 pos4_dist = Counter()
 pos4_onchain = Counter()
 pos4_offchain = Counter()
 
 # For Layer-3: Distinguish on-chain vs off-chain
 if layer_name == "layer3":
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 if layer3_file.exists():
 with layer3_file.open() as f:
 layer3_data = json.load(f)
 
 layer3_dict = {r.get("layer3_identity"): r.get("layer3_onchain", False) 
 for r in layer3_data.get("results", [])}
 
 for identity in identities:
 if len(identity) > 4:
 char = identity[4]
 pos4_dist[char] += 1
 is_onchain = layer3_dict.get(identity, False)
 if is_onchain:
 pos4_onchain[char] += 1
 else:
 pos4_offchain[char] += 1
 else:
 for identity in identities:
 if len(identity) > 4:
 char = identity[4]
 pos4_dist[char] += 1
 
 evolution[layer_name] = {
 "total": len(identities),
 "pos4_distribution": dict(pos4_dist.most_common(26)),
 "pos4_onchain": dict(pos4_onchain),
 "pos4_offchain": dict(pos4_offchain)
 }
 
 return evolution

def analyze_position4_context_patterns(data: Dict) -> Dict:
 """Analyze context-Patterns um Position 4."""
 layer3_identities = data.get("layer3", [])
 
 if not layer3_identities:
 return {}
 
 # Load on-chain Status
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 layer3_dict = {}
 if layer3_file.exists():
 with layer3_file.open() as f:
 layer3_data = json.load(f)
 layer3_dict = {r.get("layer3_identity"): r.get("layer3_onchain", False) 
 for r in layer3_data.get("results", [])}
 
 # Analyze Patterns
 patterns = {
 "before_pos4": defaultdict(Counter), # Position 0-3
 "at_pos4": defaultdict(Counter), # Position 4
 "after_pos4": defaultdict(Counter), # Position 5-9
 "bigrams": defaultdict(Counter), # 2-char patterns
 "trigrams": defaultdict(Counter) # 3-char patterns
 }
 
 for identity in layer3_identities:
 if len(identity) < 10:
 continue
 
 is_onchain = layer3_dict.get(identity, False)
 status = "onchain" if is_onchain else "offchain"
 
 # Before Position 4 (0-3)
 before = identity[0:4]
 patterns["before_pos4"][status][before] += 1
 
 # At Position 4
 at_pos4 = identity[4]
 patterns["at_pos4"][status][at_pos4] += 1
 
 # After Position 4 (5-9)
 after = identity[5:10]
 patterns["after_pos4"][status][after] += 1
 
 # Bigrams (3-5, 4-6)
 bigram_35 = identity[3:5]
 bigram_46 = identity[4:6]
 patterns["bigrams"][status][bigram_35] += 1
 patterns["bigrams"][status][bigram_46] += 1
 
 # Trigrams (2-5, 3-6, 4-7)
 trigram_25 = identity[2:5]
 trigram_36 = identity[3:6]
 trigram_47 = identity[4:7]
 patterns["trigrams"][status][trigram_25] += 1
 patterns["trigrams"][status][trigram_36] += 1
 patterns["trigrams"][status][trigram_47] += 1
 
 return patterns

def analyze_position4_matrix_relationship() -> Dict:
 """Analyze Beziehung zwischen Position 4 und Matrix-Extraktion."""
 # Position 4 in 60-char identity
 # Identity will aus Matrix extrahiert
 # Welche Matrix-Koordinaten beeinflussen Position 4?
 
 # For diagonal extraction:
 # - Position 0-13: Erste 14 Werte
 # - Position 4: 5. Wert in der Extraktion
 
 # For vortex extraction:
 # - Komplexer, aber Position 4 ist auch 5. Wert
 
 analysis = {
 "position_in_extraction": 4, # 5. Wert (0-indexed)
 "matrix_coordinate_estimate": "Row 4, Col 4 (diagonal) or equivalent",
 "possible_meanings": [
 "Early extraction value - 5th value from matrix",
 "Selection marker - early position suggests importance",
 "Functional role - position 4 may encode function",
 "Evolutionary fitness - early position = important"
 ]
 }
 
 return analysis

def analyze_position4_combinations(data: Dict) -> Dict:
 """Analyze Kombinationen von Position 4 mit anderen Positionen."""
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 if not layer3_file.exists():
 return {}
 
 with layer3_file.open() as f:
 layer3_data = json.load(f)
 
 results_data = layer3_data.get("results", [])
 
 # Teste Position 4 + andere Positionen
 combinations = {}
 
 # Wichtige Positionen zum Testen
 test_positions = [0, 1, 2, 3, 5, 6, 7, 27, 30, 55]
 
 for other_pos in test_positions:
 if other_pos == 4:
 continue
 
 # Baue kombinierte Model
 combo_onchain = defaultdict(int)
 combo_offchain = defaultdict(int)
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= max(4, other_pos):
 continue
 
 pos4_char = layer3_id[4]
 other_char = layer3_id[other_pos]
 combo = f"{pos4_char}{other_char}"
 
 if is_onchain:
 combo_onchain[combo] += 1
 else:
 combo_offchain[combo] += 1
 
 # Teste Accuracy
 correct = 0
 total = 0
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) <= max(4, other_pos):
 continue
 
 pos4_char = layer3_id[4]
 other_char = layer3_id[other_pos]
 combo = f"{pos4_char}{other_char}"
 
 on_count = combo_onchain.get(combo, 0)
 off_count = combo_offchain.get(combo, 0)
 total_count = on_count + off_count
 
 if total_count > 0:
 prob_onchain = (on_count / total_count) * 100
 predicted_onchain = prob_onchain > 50
 
 total += 1
 if predicted_onchain == is_onchain:
 correct += 1
 
 accuracy = (correct / total * 100) if total > 0 else 0
 
 combinations[f"pos4_pos{other_pos}"] = {
 "accuracy": accuracy,
 "correct": correct,
 "total": total,
 "improvement": accuracy - 80.0 # vs Position 4 alone
 }
 
 return combinations

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("POSITION 4 DEEP RESEARCH")
 print("=" * 80)
 print()
 print("Position 4 is the BEST validated predictor - researching why...")
 print()
 
 # Load Daten
 print("Loading all layer data...")
 data = load_all_layer_data()
 print(f"✅ Layer-1: {len(data['layer1'])} identities")
 print(f"✅ Layer-2: {len(data['layer2'])} identities")
 print(f"✅ Layer-3: {len(data['layer3'])} identities")
 print()
 
 # Evolution Analysis
 print("Analyzing Position 4 evolution through layers...")
 evolution = analyze_position4_evolution(data)
 
 print("Position 4 Evolution:")
 for layer_name, analysis in evolution.items():
 print(f" {layer_name}: {analysis['total']} identities")
 if "pos4_onchain" in analysis and analysis["pos4_onchain"]:
 print(f" On-chain top: {max(analysis['pos4_onchain'].items(), key=lambda x: x[1])}")
 print(f" Off-chain top: {max(analysis['pos4_offchain'].items(), key=lambda x: x[1])}")
 print()
 
 # Context Patterns
 print("Analyzing context patterns around Position 4...")
 context_patterns = analyze_position4_context_patterns(data)
 
 if context_patterns:
 print("Top Context Patterns:")
 for pattern_type, patterns in context_patterns.items():
 if patterns.get("onchain"):
 top_onchain = max(patterns["onchain"].items(), key=lambda x: x[1])
 print(f" {pattern_type} (on-chain): {top_onchain}")
 if patterns.get("offchain"):
 top_offchain = max(patterns["offchain"].items(), key=lambda x: x[1])
 print(f" {pattern_type} (off-chain): {top_offchain}")
 print()
 
 # Matrix Relationship
 print("Analyzing Position 4 relationship to matrix extraction...")
 matrix_relationship = analyze_position4_matrix_relationship()
 print(f"Position in extraction: {matrix_relationship['position_in_extraction']}")
 print(f"Matrix coordinate estimate: {matrix_relationship['matrix_coordinate_estimate']}")
 print()
 
 # Combinations
 print("Analyzing Position 4 combinations with other positions...")
 combinations = analyze_position4_combinations(data)
 
 print("Position 4 Combinations:")
 sorted_combos = sorted(combinations.items(), key=lambda x: x[1]["accuracy"], reverse=True)
 for combo_name, combo_data in sorted_combos[:5]:
 improvement = combo_data["improvement"]
 improvement_str = f"+{improvement:.1f}%" if improvement > 0 else f"{improvement:.1f}%"
 print(f" {combo_name}: {combo_data['accuracy']:.1f}% ({improvement_str} vs Position 4 alone)")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 results = {
 "evolution": evolution,
 "context_patterns": {k: {sk: dict(sv.most_common(10)) for sk, sv in v.items()} 
 for k, v in context_patterns.items()},
 "matrix_relationship": matrix_relationship,
 "combinations": combinations
 }
 
 output_json = OUTPUT_DIR / "position4_deep_research.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "position4_deep_research_report.md"
 
 with output_md.open("w") as f:
 f.write("# Position 4 Deep Research Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write("Deep research into why Position 4 is the best validated predictor.\n\n")
 
 f.write("## Position 4 Evolution Through Layers\n\n")
 for layer_name, analysis in evolution.items():
 f.write(f"### {layer_name}\n\n")
 f.write(f"- **Total**: {analysis['total']}\n")
 f.write(f"- **Top 5 chars at Position 4:**\n")
 for char, count in list(analysis['pos4_distribution'].items())[:5]:
 pct = (count / analysis['total']) * 100
 f.write(f" - `{char}`: {count} ({pct:.1f}%)\n")
 f.write("\n")
 
 f.write("## Context Patterns\n\n")
 if context_patterns:
 for pattern_type, patterns in context_patterns.items():
 f.write(f"### {pattern_type}\n\n")
 if patterns.get("onchain"):
 f.write("**Top On-Chain Patterns:**\n")
 for pattern, count in list(patterns["onchain"].most_common(5)):
 f.write(f"- `{pattern}`: {count}\n")
 if patterns.get("offchain"):
 f.write("**Top Off-Chain Patterns:**\n")
 for pattern, count in list(patterns["offchain"].most_common(5)):
 f.write(f"- `{pattern}`: {count}\n")
 f.write("\n")
 
 f.write("## Matrix Relationship\n\n")
 f.write(f"- **Position in extraction**: {matrix_relationship['position_in_extraction']}\n")
 f.write(f"- **Matrix coordinate estimate**: {matrix_relationship['matrix_coordinate_estimate']}\n")
 f.write(f"\n**Possible Meanings:**\n")
 for meaning in matrix_relationship['possible_meanings']:
 f.write(f"- {meaning}\n")
 f.write("\n")
 
 f.write("## Position 4 Combinations\n\n")
 f.write("| Combination | Accuracy | Improvement vs Position 4 |\n")
 f.write("|-------------|----------|----------------------------|\n")
 sorted_combos = sorted(combinations.items(), key=lambda x: x[1]["accuracy"], reverse=True)
 for combo_name, combo_data in sorted_combos:
 improvement = combo_data["improvement"]
 improvement_str = f"+{improvement:.1f}%" if improvement > 0 else f"{improvement:.1f}%"
 f.write(f"| {combo_name} | {combo_data['accuracy']:.1f}% | {improvement_str} |\n")
 f.write("\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

