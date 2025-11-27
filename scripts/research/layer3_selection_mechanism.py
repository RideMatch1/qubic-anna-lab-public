#!/usr/bin/env python3
"""
Layer-3 Selection Mechanism Research

Forscht nach dem Mechanismus der Layer-3 On-chain Auswahl.
Baut Prediction Model basierend auf Position 27 und anderen Faktoren.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
import numpy as np

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_layer3_data() -> Dict:
 """Load Layer-3 Daten."""
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 
 if not layer3_file.exists():
 return {}
 
 with layer3_file.open() as f:
 return json.load(f)

def build_prediction_model(layer3_data: Dict) -> Dict:
 """Baue Prediction Model for On-chain Status."""
 results_data = layer3_data.get("results", [])
 
 if not results_data:
 return {}
 
 # Features sammeln
 features = {
 "position27": Counter(),
 "position26": Counter(),
 "position28": Counter(),
 "seed_patterns": Counter(),
 "layer2_pos27": Counter()
 }
 
 onchain_features = defaultdict(Counter)
 offchain_features = defaultdict(Counter)
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 layer2_id = result.get("layer2_identity", "")
 seed = result.get("seed", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) < 28:
 continue
 
 # Features extrahieren
 pos27 = layer3_id[27]
 pos26 = layer3_id[26] if len(layer3_id) > 26 else None
 pos28 = layer3_id[28] if len(layer3_id) > 28 else None
 layer2_pos27 = layer2_id[27] if layer2_id and len(layer2_id) > 27 else None
 
 # Seed pattern (erste 5 chars)
 seed_prefix = seed[:5] if seed else None
 
 # Features speichern
 if is_onchain:
 onchain_features["pos27"][pos27] += 1
 if pos26:
 onchain_features["pos26"][pos26] += 1
 if pos28:
 onchain_features["pos28"][pos28] += 1
 if layer2_pos27:
 onchain_features["layer2_pos27"][layer2_pos27] += 1
 if seed_prefix:
 onchain_features["seed_prefix"][seed_prefix] += 1
 else:
 offchain_features["pos27"][pos27] += 1
 if pos26:
 offchain_features["pos26"][pos26] += 1
 if pos28:
 offchain_features["pos28"][pos28] += 1
 if layer2_pos27:
 offchain_features["layer2_pos27"][layer2_pos27] += 1
 if seed_prefix:
 offchain_features["seed_prefix"][seed_prefix] += 1
 
 # Berechne Wahrscheinlichkeiten
 total_onchain = sum(onchain_features["pos27"].values())
 total_offchain = sum(offchain_features["pos27"].values())
 
 probabilities = {}
 
 # Position 27 Wahrscheinlichkeiten
 for char in set(list(onchain_features["pos27"].keys()) + list(offchain_features["pos27"].keys())):
 onchain_count = onchain_features["pos27"].get(char, 0)
 offchain_count = offchain_features["pos27"].get(char, 0)
 total = onchain_count + offchain_count
 
 if total > 0:
 prob_onchain = (onchain_count / total) * 100
 probabilities[char] = {
 "char": char,
 "onchain_count": onchain_count,
 "offchain_count": offchain_count,
 "total": total,
 "prob_onchain": prob_onchain,
 "prob_offchain": 100 - prob_onchain
 }
 
 return {
 "total_onchain": total_onchain,
 "total_offchain": total_offchain,
 "onchain_rate": (total_onchain / (total_onchain + total_offchain)) * 100 if (total_onchain + total_offchain) > 0 else 0,
 "position27_probabilities": probabilities,
 "onchain_features": {k: dict(v.most_common(10)) for k, v in onchain_features.items()},
 "offchain_features": {k: dict(v.most_common(10)) for k, v in offchain_features.items()}
 }

def test_prediction_model(model: Dict, layer3_data: Dict) -> Dict:
 """Teste das Prediction Model."""
 results_data = layer3_data.get("results", [])
 
 if not results_data or not model.get("position27_probabilities"):
 return {}
 
 predictions = {
 "correct": 0,
 "incorrect": 0,
 "total": 0,
 "by_char": defaultdict(lambda: {"correct": 0, "incorrect": 0})
 }
 
 for result in results_data:
 layer3_id = result.get("layer3_identity", "")
 is_onchain = result.get("layer3_onchain", False)
 
 if not layer3_id or len(layer3_id) < 28:
 continue
 
 pos27 = layer3_id[27]
 prob_data = model["position27_probabilities"].get(pos27)
 
 if not prob_data:
 continue
 
 # Prediction: Wenn prob_onchain > 50%, dann on-chain
 predicted_onchain = prob_data["prob_onchain"] > 50
 
 predictions["total"] += 1
 
 if predicted_onchain == is_onchain:
 predictions["correct"] += 1
 predictions["by_char"][pos27]["correct"] += 1
 else:
 predictions["incorrect"] += 1
 predictions["by_char"][pos27]["incorrect"] += 1
 
 accuracy = (predictions["correct"] / predictions["total"] * 100) if predictions["total"] > 0 else 0
 
 return {
 "accuracy": accuracy,
 "correct": predictions["correct"],
 "incorrect": predictions["incorrect"],
 "total": predictions["total"],
 "by_char": dict(predictions["by_char"])
 }

def analyze_selection_rules(model: Dict) -> List[Dict]:
 """Analyze mögliche Selection Rules."""
 rules = []
 
 if not model.get("position27_probabilities"):
 return rules
 
 # Rule 1: Position 27 = 'A' → On-chain
 prob_a = model["position27_probabilities"].get('A', {})
 if prob_a.get("prob_onchain", 0) > 50:
 rules.append({
 "rule": "Position 27 = 'A' → On-chain",
 "confidence": prob_a.get("prob_onchain", 0),
 "support": prob_a.get("onchain_count", 0),
 "description": "If position 27 is 'A', identity is likely on-chain"
 })
 
 # Rule 2: Position 27 = 'C' → Off-chain
 prob_c = model["position27_probabilities"].get('C', {})
 if prob_c.get("prob_offchain", 0) > 50:
 rules.append({
 "rule": "Position 27 = 'C' → Off-chain",
 "confidence": prob_c.get("prob_offchain", 0),
 "support": prob_c.get("offchain_count", 0),
 "description": "If position 27 is 'C', identity is likely off-chain"
 })
 
 # Rule 3: Position 27 = 'B' → Neutral/Uncertain
 prob_b = model["position27_probabilities"].get('B', {})
 if prob_b:
 rules.append({
 "rule": "Position 27 = 'B' → Neutral",
 "confidence": 50, # Neutral
 "support": prob_b.get("total", 0),
 "description": "If position 27 is 'B', prediction is uncertain"
 })
 
 return rules

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("LAYER-3 SELECTION MECHANISM RESEARCH")
 print("=" * 80)
 print()
 
 # Load Daten
 print("Loading Layer-3 data...")
 layer3_data = load_layer3_data()
 
 if not layer3_data:
 print("❌ Layer-3 data not found")
 return
 
 print(f"✅ Loaded {len(layer3_data.get('results', []))} entries")
 print()
 
 # Baue Model
 print("Building prediction model...")
 model = build_prediction_model(layer3_data)
 
 print("=" * 80)
 print("PREDICTION MODEL RESULTS")
 print("=" * 80)
 print()
 print(f"Total on-chain: {model['total_onchain']}")
 print(f"Total off-chain: {model['total_offchain']}")
 print(f"On-chain rate: {model['onchain_rate']:.1f}%")
 print()
 
 print("Position 27 Probabilities (On-chain):")
 for char, prob_data in sorted(model["position27_probabilities"].items(), 
 key=lambda x: x[1]["prob_onchain"], reverse=True)[:10]:
 print(f" '{char}': {prob_data['prob_onchain']:.1f}% "
 f"({prob_data['onchain_count']}/{prob_data['total']})")
 print()
 
 # Teste Model
 print("Testing prediction model...")
 test_results = test_prediction_model(model, layer3_data)
 
 if test_results:
 print(f"Model Accuracy: {test_results['accuracy']:.1f}%")
 print(f"Correct: {test_results['correct']}/{test_results['total']}")
 print(f"Incorrect: {test_results['incorrect']}/{test_results['total']}")
 print()
 
 # Selection Rules
 print("Analyzing selection rules...")
 rules = analyze_selection_rules(model)
 
 print("Selection Rules:")
 for rule in rules:
 print(f" {rule['rule']}:")
 print(f" Confidence: {rule['confidence']:.1f}%")
 print(f" Support: {rule['support']} occurrences")
 print(f" Description: {rule['description']}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 results = {
 "model": model,
 "test_results": test_results,
 "selection_rules": rules
 }
 
 output_json = OUTPUT_DIR / "layer3_selection_mechanism.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "layer3_selection_mechanism_report.md"
 
 with output_md.open("w") as f:
 f.write("# Layer-3 Selection Mechanism Research Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write(f"- **Total on-chain**: {model['total_onchain']}\n")
 f.write(f"- **Total off-chain**: {model['total_offchain']}\n")
 f.write(f"- **On-chain rate**: {model['onchain_rate']:.1f}%\n")
 if test_results:
 f.write(f"- **Model Accuracy**: {test_results['accuracy']:.1f}%\n")
 f.write("\n")
 
 f.write("## Position 27 Probabilities\n\n")
 f.write("| Char | On-chain Count | Off-chain Count | Total | Prob On-chain | Prob Off-chain |\n")
 f.write("|------|----------------|-----------------|-------|---------------|----------------|\n")
 for char, prob_data in sorted(model["position27_probabilities"].items(), 
 key=lambda x: x[1]["prob_onchain"], reverse=True):
 f.write(f"| `{char}` | {prob_data['onchain_count']} | {prob_data['offchain_count']} | "
 f"{prob_data['total']} | {prob_data['prob_onchain']:.1f}% | "
 f"{prob_data['prob_offchain']:.1f}% |\n")
 f.write("\n")
 
 f.write("## Selection Rules\n\n")
 for rule in rules:
 f.write(f"### {rule['rule']}\n\n")
 f.write(f"- **Confidence**: {rule['confidence']:.1f}%\n")
 f.write(f"- **Support**: {rule['support']} occurrences\n")
 f.write(f"- **Description**: {rule['description']}\n\n")
 
 if test_results:
 f.write("## Model Test Results\n\n")
 f.write(f"- **Accuracy**: {test_results['accuracy']:.1f}%\n")
 f.write(f"- **Correct**: {test_results['correct']}/{test_results['total']}\n")
 f.write(f"- **Incorrect**: {test_results['incorrect']}/{test_results['total']}\n\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

