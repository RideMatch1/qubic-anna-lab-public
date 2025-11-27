#!/usr/bin/env python3
"""
Identity Relationship Mapping

Mappt komplette Layer-Ketten: Layer-1 → Layer-2 → Layer-3
Findet Patterns und Beziehungen zwischen Layers.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_complete_chains() -> List[Dict]:
 """Load komplette Layer-Ketten."""
 chains = []
 
 # Load Layer-3 Daten
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 if not layer3_file.exists():
 return []
 
 with layer3_file.open() as f:
 layer3_data = json.load(f)
 
 # Load Layer-1 Identities
 db_file = project_root / "outputs" / "analysis" / "complete_mapping_database.json"
 seed_to_real_id = {}
 if db_file.exists():
 with db_file.open() as f:
 db = json.load(f)
 seed_to_real_id = db.get("seed_to_real_id", {})
 
 # Baue Chains
 for result in layer3_data.get("results", []):
 layer2_id = result.get("layer2_identity")
 layer3_id = result.get("layer3_identity")
 seed = result.get("seed", "")
 layer3_onchain = result.get("layer3_onchain", False)
 
 if not layer2_id or not layer3_id:
 continue
 
 # Finde Layer-1 (aus Seed)
 layer1_id = seed_to_real_id.get(seed)
 
 chain = {
 "layer1": layer1_id,
 "layer2": layer2_id,
 "layer3": layer3_id,
 "seed": seed,
 "layer3_onchain": layer3_onchain
 }
 
 chains.append(chain)
 
 return chains

def analyze_chain_patterns(chains: List[Dict]) -> Dict:
 """Analyze Patterns in Chains."""
 patterns = {
 "total_chains": len(chains),
 "onchain_chains": sum(1 for c in chains if c.get("layer3_onchain")),
 "offchain_chains": sum(1 for c in chains if not c.get("layer3_onchain")),
 "position_patterns": defaultdict(Counter),
 "char_transitions": defaultdict(Counter),
 "seed_patterns": Counter()
 }
 
 for chain in chains:
 layer1 = chain.get("layer1", "")
 layer2 = chain.get("layer2", "")
 layer3 = chain.get("layer3", "")
 
 if not all([layer1, layer2, layer3]):
 continue
 
 # Analyze Position 27 in allen Layers
 if len(layer1) > 27:
 patterns["position_patterns"]["layer1_pos27"][layer1[27]] += 1
 if len(layer2) > 27:
 patterns["position_patterns"]["layer2_pos27"][layer2[27]] += 1
 if len(layer3) > 27:
 patterns["position_patterns"]["layer3_pos27"][layer3[27]] += 1
 
 # Char Transitions (Layer-1 → Layer-2 → Layer-3)
 if len(layer1) > 27 and len(layer2) > 27:
 transition = f"{layer1[27]}→{layer2[27]}"
 patterns["char_transitions"]["l1_to_l2"][transition] += 1
 
 if len(layer2) > 27 and len(layer3) > 27:
 transition = f"{layer2[27]}→{layer3[27]}"
 patterns["char_transitions"]["l2_to_l3"][transition] += 1
 
 # Seed Patterns
 seed = chain.get("seed", "")
 if seed:
 patterns["seed_patterns"][seed[:10]] += 1
 
 return patterns

def analyze_onchain_vs_offchain_chains(chains: List[Dict]) -> Dict:
 """Analyze Unterschiede zwischen on-chain und off-chain Chains."""
 onchain = [c for c in chains if c.get("layer3_onchain")]
 offchain = [c for c in chains if not c.get("layer3_onchain")]
 
 analysis = {
 "onchain_count": len(onchain),
 "offchain_count": len(offchain),
 "onchain_pos27": Counter(),
 "offchain_pos27": Counter(),
 "onchain_transitions": Counter(),
 "offchain_transitions": Counter()
 }
 
 for chain in onchain:
 layer3 = chain.get("layer3", "")
 layer2 = chain.get("layer2", "")
 if len(layer3) > 27:
 analysis["onchain_pos27"][layer3[27]] += 1
 if len(layer2) > 27 and len(layer3) > 27:
 transition = f"{layer2[27]}→{layer3[27]}"
 analysis["onchain_transitions"][transition] += 1
 
 for chain in offchain:
 layer3 = chain.get("layer3", "")
 layer2 = chain.get("layer2", "")
 if len(layer3) > 27:
 analysis["offchain_pos27"][layer3[27]] += 1
 if len(layer2) > 27 and len(layer3) > 27:
 transition = f"{layer2[27]}→{layer3[27]}"
 analysis["offchain_transitions"][transition] += 1
 
 return analysis

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("IDENTITY RELATIONSHIP MAPPING")
 print("=" * 80)
 print()
 
 # Load Chains
 print("Loading complete layer chains...")
 chains = load_complete_chains()
 print(f"✅ Loaded {len(chains)} complete chains")
 print()
 
 if not chains:
 print("❌ No chains found")
 return
 
 # Analyze Patterns
 print("Analyzing chain patterns...")
 patterns = analyze_chain_patterns(chains)
 
 print("=" * 80)
 print("CHAIN PATTERN ANALYSIS")
 print("=" * 80)
 print()
 print(f"Total chains: {patterns['total_chains']}")
 print(f"On-chain chains: {patterns['onchain_chains']} ({patterns['onchain_chains']/patterns['total_chains']*100:.1f}%)")
 print(f"Off-chain chains: {patterns['offchain_chains']} ({patterns['offchain_chains']/patterns['total_chains']*100:.1f}%)")
 print()
 
 # Position 27 Patterns
 print("Position 27 Patterns by Layer:")
 for layer_name in ["layer1_pos27", "layer2_pos27", "layer3_pos27"]:
 if layer_name in patterns["position_patterns"]:
 dist = patterns["position_patterns"][layer_name]
 print(f" {layer_name}:")
 for char, count in dist.most_common(5):
 print(f" '{char}': {count}")
 print()
 
 # Transitions
 print("Top Layer-2 → Layer-3 Transitions (Position 27):")
 for transition, count in patterns["char_transitions"]["l2_to_l3"].most_common(10):
 print(f" {transition}: {count}")
 print()
 
 # On-chain vs Off-chain
 print("Analyzing on-chain vs off-chain chains...")
 onchain_analysis = analyze_onchain_vs_offchain_chains(chains)
 
 print(f"On-chain chains: {onchain_analysis['onchain_count']}")
 print(f"Off-chain chains: {onchain_analysis['offchain_count']}")
 print()
 
 print("On-chain Position 27 (Layer-3):")
 for char, count in onchain_analysis["onchain_pos27"].most_common(5):
 print(f" '{char}': {count}")
 print()
 
 print("Off-chain Position 27 (Layer-3):")
 for char, count in onchain_analysis["offchain_pos27"].most_common(5):
 print(f" '{char}': {count}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 results = {
 "chains": chains[:20], # Nur erste 20 for JSON
 "patterns": {
 "total_chains": patterns["total_chains"],
 "onchain_chains": patterns["onchain_chains"],
 "offchain_chains": patterns["offchain_chains"],
 "position_patterns": {k: dict(v) for k, v in patterns["position_patterns"].items()},
 "char_transitions": {k: dict(v.most_common(20)) for k, v in patterns["char_transitions"].items()}
 },
 "onchain_analysis": {
 "onchain_count": onchain_analysis["onchain_count"],
 "offchain_count": onchain_analysis["offchain_count"],
 "onchain_pos27": dict(onchain_analysis["onchain_pos27"].most_common(10)),
 "offchain_pos27": dict(onchain_analysis["offchain_pos27"].most_common(10)),
 "onchain_transitions": dict(onchain_analysis["onchain_transitions"].most_common(10)),
 "offchain_transitions": dict(onchain_analysis["offchain_transitions"].most_common(10))
 }
 }
 
 output_json = OUTPUT_DIR / "identity_relationship_mapping.json"
 with output_json.open("w") as f:
 json.dump(results, f, indent=2)
 
 # Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 output_md = REPORTS_DIR / "identity_relationship_mapping_report.md"
 
 with output_md.open("w") as f:
 f.write("# Identity Relationship Mapping Report\n\n")
 f.write("**Generated**: 2025-11-25\n\n")
 f.write("## Summary\n\n")
 f.write(f"- **Total chains**: {patterns['total_chains']}\n")
 f.write(f"- **On-chain chains**: {patterns['onchain_chains']} ({patterns['onchain_chains']/patterns['total_chains']*100:.1f}%)\n")
 f.write(f"- **Off-chain chains**: {patterns['offchain_chains']} ({patterns['offchain_chains']/patterns['total_chains']*100:.1f}%)\n\n")
 
 f.write("## Position 27 Patterns by Layer\n\n")
 for layer_name in ["layer1_pos27", "layer2_pos27", "layer3_pos27"]:
 if layer_name in patterns["position_patterns"]:
 f.write(f"### {layer_name}\n\n")
 dist = patterns["position_patterns"][layer_name]
 f.write("| Char | Count |\n")
 f.write("|------|-------|\n")
 for char, count in dist.most_common(10):
 f.write(f"| `{char}` | {count} |\n")
 f.write("\n")
 
 f.write("## Layer-2 → Layer-3 Transitions (Position 27)\n\n")
 f.write("| Transition | Count |\n")
 f.write("|------------|-------|\n")
 for transition, count in patterns["char_transitions"]["l2_to_l3"].most_common(20):
 f.write(f"| `{transition}` | {count} |\n")
 f.write("\n")
 
 f.write("## On-chain vs Off-chain Analysis\n\n")
 f.write("### On-chain Position 27 (Layer-3)\n\n")
 f.write("| Char | Count |\n")
 f.write("|------|-------|\n")
 for char, count in onchain_analysis["onchain_pos27"].most_common(10):
 f.write(f"| `{char}` | {count} |\n")
 f.write("\n")
 
 f.write("### Off-chain Position 27 (Layer-3)\n\n")
 f.write("| Char | Count |\n")
 f.write("|------|-------|\n")
 for char, count in onchain_analysis["offchain_pos27"].most_common(10):
 f.write(f"| `{char}` | {count} |\n")
 f.write("\n")
 
 print(f"💾 Results saved to: {output_json}")
 print(f"📄 Report saved to: {output_md}")
 print()
 
 return results

if __name__ == "__main__":
 main()

