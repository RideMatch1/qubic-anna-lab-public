#!/usr/bin/env python3
"""
Analyze Unterschiede in Layer-3 → Layer-4 Transformation for on-chain vs. off-chain
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
LAYER3_RPC_FILE = project_root / "outputs" / "derived" / "rpc_sample_results.json"
LAYER4_RPC_FILE = project_root / "outputs" / "derived" / "layer4_rpc_validation.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_data() -> List[Dict]:
 """Load alle Daten und kombiniere sie."""
 # Load Layer-3 on-chain Status
 layer3_onchain = {}
 if LAYER3_RPC_FILE.exists():
 with LAYER3_RPC_FILE.open() as f:
 rpc_data = json.load(f)
 for entry in rpc_data.get("results", []):
 identity = entry.get("layer3_identity", "")
 if identity:
 layer3_onchain[identity] = entry.get("rpc_status") == "ONCHAIN"
 
 # Load Layer-4 on-chain Status
 layer4_onchain = {}
 if LAYER4_RPC_FILE.exists():
 with LAYER4_RPC_FILE.open() as f:
 rpc_data = json.load(f)
 for entry in rpc_data.get("results", []):
 identity = entry.get("layer4_identity", "")
 if identity:
 layer4_onchain[identity] = entry.get("rpc_status") == "ONCHAIN"
 
 # Load Layer-3 Daten
 layer3_data = []
 if LAYER3_FILE.exists():
 with LAYER3_FILE.open() as f:
 data = json.load(f)
 layer3_data = data.get("results", [])
 
 # Load Layer-4 Daten
 layer4_map = {}
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 data = json.load(f)
 for entry in data.get("results", []):
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 if l3_id and l4_id:
 layer4_map[l3_id] = l4_id
 
 # Kombiniere
 combined = []
 for l3_entry in layer3_data:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 
 if l3_id and l4_id and len(l3_id) == 60 and len(l4_id) == 60:
 combined.append({
 "layer3_identity": l3_id,
 "layer4_identity": l4_id,
 "layer3_onchain": layer3_onchain.get(l3_id, None),
 "layer4_onchain": layer4_onchain.get(l4_id, None)
 })
 
 return combined

def analyze_transformation_differences(data: List[Dict]) -> Dict:
 """Analyze Unterschiede in Transformation for on-chain vs. off-chain."""
 
 # Gruppiere nach Layer-3 on-chain Status
 l3_onchain_pairs = [d for d in data if d.get("layer3_onchain") is True]
 l3_offchain_pairs = [d for d in data if d.get("layer3_onchain") is False]
 
 # Analyze Position-Änderungen for beide Gruppen
 def analyze_group(pairs: List[Dict], group_name: str) -> Dict:
 position_changes = defaultdict(lambda: {"same": 0, "different": 0})
 
 for pair in pairs:
 l3_id = pair["layer3_identity"]
 l4_id = pair["layer4_identity"]
 
 for pos in range(60):
 if l3_id[pos].upper() == l4_id[pos].upper():
 position_changes[pos]["same"] += 1
 else:
 position_changes[pos]["different"] += 1
 
 change_rates = {}
 for pos in range(60):
 if pos in position_changes:
 total = position_changes[pos]["same"] + position_changes[pos]["different"]
 if total > 0:
 change_rates[pos] = {
 "same_rate": position_changes[pos]["same"] / total,
 "different_rate": position_changes[pos]["different"] / total
 }
 
 return {
 "count": len(pairs),
 "position_changes": {str(k): dict(v) for k, v in position_changes.items()},
 "change_rates": {str(k): v for k, v in change_rates.items()}
 }
 
 l3_onchain_analysis = analyze_group(l3_onchain_pairs, "Layer-3 On-Chain")
 l3_offchain_analysis = analyze_group(l3_offchain_pairs, "Layer-3 Off-Chain")
 
 # Vergleiche Position 27, 55, 30, 4
 key_positions = [27, 55, 30, 4]
 position_comparison = {}
 
 for pos in key_positions:
 pos_str = str(pos)
 onchain_rate = l3_onchain_analysis["change_rates"].get(pos_str, {}).get("same_rate", 0)
 offchain_rate = l3_offchain_analysis["change_rates"].get(pos_str, {}).get("same_rate", 0)
 
 position_comparison[pos] = {
 "onchain_same_rate": onchain_rate,
 "offchain_same_rate": offchain_rate,
 "difference": abs(onchain_rate - offchain_rate)
 }
 
 return {
 "layer3_onchain": l3_onchain_analysis,
 "layer3_offchain": l3_offchain_analysis,
 "position_comparison": {str(k): v for k, v in position_comparison.items()},
 "total_pairs": len(data),
 "l3_onchain_count": len(l3_onchain_pairs),
 "l3_offchain_count": len(l3_offchain_pairs)
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("ON-CHAIN vs. OFF-CHAIN TRANSFORMATION ANALYSE")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Daten...")
 data = load_data()
 print(f"✅ {len(data)} Paare geloadn")
 
 l3_onchain_count = sum(1 for d in data if d.get("layer3_onchain") is True)
 l3_offchain_count = sum(1 for d in data if d.get("layer3_onchain") is False)
 print(f"✅ Layer-3 On-Chain: {l3_onchain_count}")
 print(f"✅ Layer-3 Off-Chain: {l3_offchain_count}")
 print()
 
 if l3_onchain_count == 0 or l3_offchain_count == 0:
 print("⚠️ Nicht genug Daten for Vergleich (benötige beide Gruppen)")
 return
 
 # Analyze Unterschiede
 print("🔍 Analyze Transformation-Unterschiede...")
 results = analyze_transformation_differences(data)
 print("✅ Analyse abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 print("📊 Position-Vergleich (Same Rate):")
 pos_comp = results.get("position_comparison", {})
 for pos in [27, 55, 30, 4]:
 pos_str = str(pos)
 if pos_str in pos_comp:
 onchain_rate = pos_comp[pos_str].get("onchain_same_rate", 0) * 100
 offchain_rate = pos_comp[pos_str].get("offchain_same_rate", 0) * 100
 diff = pos_comp[pos_str].get("difference", 0) * 100
 print(f" Position {pos:2d}: On-Chain {onchain_rate:5.1f}% | Off-Chain {offchain_rate:5.1f}% | Diff {diff:5.1f}%")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "results": results
 }
 
 output_file = OUTPUT_DIR / "onchain_vs_offchain_transformation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# On-Chain vs. Off-Chain Transformation Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Zusammenfassung",
 "",
 f"- **Total Paare**: {results.get('total_pairs', 0)}",
 f"- **Layer-3 On-Chain**: {results.get('l3_onchain_count', 0)}",
 f"- **Layer-3 Off-Chain**: {results.get('l3_offchain_count', 0)}",
 "",
 "## Position-Vergleich",
 ""
 ]
 
 for pos in [27, 55, 30, 4]:
 pos_str = str(pos)
 if pos_str in pos_comp:
 onchain_rate = pos_comp[pos_str].get("onchain_same_rate", 0) * 100
 offchain_rate = pos_comp[pos_str].get("offchain_same_rate", 0) * 100
 diff = pos_comp[pos_str].get("difference", 0) * 100
 report_lines.append(f"### Position {pos}:")
 report_lines.append(f"- **On-Chain Same Rate**: {onchain_rate:.1f}%")
 report_lines.append(f"- **Off-Chain Same Rate**: {offchain_rate:.1f}%")
 report_lines.append(f"- **Unterschied**: {diff:.1f}%")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "onchain_vs_offchain_transformation_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

