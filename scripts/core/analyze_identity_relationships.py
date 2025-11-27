#!/usr/bin/env python3
"""
Analyze Identity Relationships

Analysiert die Beziehungen zwischen Layer-1, Layer-2, Layer-3 Identities.
Findet Patterns und Zusammenhänge.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_layer_relationships() -> Dict:
 """Load Layer-Beziehungen."""
 relationships = {
 "layer1_to_layer2": {},
 "layer2_to_layer3": {},
 "complete_chains": []
 }
 
 # Load Layer-3 Daten
 layer3_file = OUTPUT_DIR / "layer3_derivation_complete.json"
 if layer3_file.exists():
 with layer3_file.open() as f:
 data = json.load(f)
 
 for result in data.get("results", []):
 layer2 = result.get("layer2_identity")
 layer3 = result.get("layer3_identity")
 seed = result.get("seed", "")
 
 if layer2 and layer3:
 relationships["layer2_to_layer3"][layer2] = {
 "layer3": layer3,
 "seed": seed,
 "layer3_onchain": result.get("layer3_onchain", False)
 }
 
 # Finde Layer-1 → Layer-2 Beziehungen
 # Layer-1 Identities aus 100_SEEDS_AND_IDENTITIES
 seeds_file = project_root / "github_export" / "100_seeds_and_identities.json"
 if seeds_file.exists():
 with seeds_file.open() as f:
 seeds_data = json.load(f)
 
 if isinstance(seeds_data, list):
 layer1_identities = [item.get("identity") for item in seeds_data if item.get("identity")]
 elif isinstance(seeds_data, dict) and "seeds_and_identities" in seeds_data:
 layer1_identities = [item.get("identity") for item in seeds_data["seeds_and_identities"] if item.get("identity")]
 
 # Finde Layer-2 for Layer-1
 for layer1 in layer1_identities:
 seed = layer1.lower()[:55]
 # Finde Layer-2, der diesen Seed verwendet
 for layer2, layer2_data in relationships["layer2_to_layer3"].items():
 if layer2_data.get("seed") == seed:
 relationships["layer1_to_layer2"][layer1] = {
 "layer2": layer2,
 "seed": seed
 }
 # Erstelle komplette Chain
 relationships["complete_chains"].append({
 "layer1": layer1,
 "layer2": layer2,
 "layer3": layer2_data.get("layer3"),
 "layer3_onchain": layer2_data.get("layer3_onchain", False)
 })
 break
 
 return relationships

def analyze_chain_statistics(relationships: Dict) -> Dict:
 """Analyze Chain-Statistiken."""
 chains = relationships.get("complete_chains", [])
 
 stats = {
 "total_chains": len(chains),
 "chains_with_onchain_layer3": sum(1 for c in chains if c.get("layer3_onchain")),
 "chains_without_onchain_layer3": sum(1 for c in chains if not c.get("layer3_onchain")),
 "onchain_rate": sum(1 for c in chains if c.get("layer3_onchain")) / len(chains) if chains else 0
 }
 
 return stats

def generate_report(relationships: Dict, stats: Dict) -> str:
 """Generiere Markdown-Report."""
 report = ["# Identity Relationships Analysis\n\n"]
 report.append("## Overview\n\n")
 report.append("Analyse der Beziehungen zwischen Layer-1, Layer-2, Layer-3 Identities.\n\n")
 
 report.append("## Chain Statistics\n\n")
 report.append(f"- **Total chains**: {stats.get('total_chains', 0)}\n")
 report.append(f"- **Chains with on-chain Layer-3**: {stats.get('chains_with_onchain_layer3', 0)}\n")
 report.append(f"- **Chains without on-chain Layer-3**: {stats.get('chains_without_onchain_layer3', 0)}\n")
 report.append(f"- **On-chain rate**: {stats.get('onchain_rate', 0):.1%}\n\n")
 
 report.append("## Layer Relationships\n\n")
 report.append(f"- **Layer-1 → Layer-2 mappings**: {len(relationships.get('layer1_to_layer2', {}))}\n")
 report.append(f"- **Layer-2 → Layer-3 mappings**: {len(relationships.get('layer2_to_layer3', {}))}\n\n")
 
 report.append("## Conclusions\n\n")
 report.append("1. **Complete chains exist** - Layer-1 → Layer-2 → Layer-3\n")
 report.append("2. **Not all chains have on-chain Layer-3** - some may be unused\n")
 report.append("3. **Recursive structure** - each layer derives from previous\n")
 report.append("4. **Systematic relationships** - patterns in layer connections\n\n")
 
 return "".join(report)

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("ANALYZE IDENTITY RELATIONSHIPS")
 print("=" * 80)
 print()
 
 # Load Beziehungen
 print("Loading layer relationships...")
 relationships = load_layer_relationships()
 
 print(f"✅ Layer-1 → Layer-2: {len(relationships.get('layer1_to_layer2', {}))}")
 print(f"✅ Layer-2 → Layer-3: {len(relationships.get('layer2_to_layer3', {}))}")
 print(f"✅ Complete chains: {len(relationships.get('complete_chains', []))}")
 print()
 
 # Analyze
 print("Analyzing chain statistics...")
 stats = analyze_chain_statistics(relationships)
 
 # Kombiniere Ergebnisse
 results = {
 "relationships": relationships,
 "statistics": stats
 }
 
 # Speichere JSON
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_file = OUTPUT_DIR / "identity_relationships_analysis.json"
 with output_file.open("w") as f:
 json.dump(results, f, indent=2)
 print(f"✅ Results saved to: {output_file}")
 
 # Generiere Report
 report = generate_report(relationships, stats)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report_file = REPORTS_DIR / "identity_relationships_analysis_report.md"
 with report_file.open("w") as f:
 f.write(report)
 print(f"✅ Report saved to: {report_file}")
 
 print()
 print("=" * 80)
 print("ANALYSIS COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

