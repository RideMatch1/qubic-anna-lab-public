#!/usr/bin/env python3
"""
Analyze Unterschied: On-Chain Prädiktor (Position 30) vs. Transformation-Stabilität (Position 27)
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def analyze_onchain_vs_transformation() -> Dict:
 """Analyze Unterschied zwischen On-Chain Prädiktor und Transformation-Stabilität."""
 
 print("📂 Load Layer-3 und Layer-4 Daten...")
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 
 # Erstelle Mapping
 layer4_map = {}
 for entry in layer4_results:
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 if l3_id and l4_id:
 layer4_map[l3_id] = l4_id
 
 pairs = []
 for l3_entry in layer3_results:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 if l3_id and l4_id and len(l3_id) == 60 and len(l4_id) == 60:
 pairs.append({
 "layer3": l3_id,
 "layer4": l4_id,
 "layer3_onchain": l3_entry.get("layer3_onchain", None)
 })
 
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Analyze Position 30 (On-Chain Prädiktor) vs. Position 27 (Transformation-Stabilität)
 analysis = {
 "pos30_onchain": defaultdict(lambda: {"onchain": 0, "offchain": 0}),
 "pos27_transformation": defaultdict(lambda: {"stable": 0, "changing": 0}),
 "combined": defaultdict(lambda: {
 "onchain_stable": 0,
 "onchain_changing": 0,
 "offchain_stable": 0,
 "offchain_changing": 0
 })
 }
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 is_onchain = pair.get("layer3_onchain")
 
 # Position 30 (On-Chain Prädiktor)
 if len(l3_id) > 30:
 pos30_char = l3_id[30].upper()
 if is_onchain is not None:
 if is_onchain:
 analysis["pos30_onchain"][pos30_char]["onchain"] += 1
 else:
 analysis["pos30_onchain"][pos30_char]["offchain"] += 1
 
 # Position 27 (Transformation-Stabilität)
 if len(l3_id) > 27 and len(l4_id) > 27:
 pos27_char = l3_id[27].upper()
 if l3_id[27].upper() == l4_id[27].upper():
 analysis["pos27_transformation"][pos27_char]["stable"] += 1
 else:
 analysis["pos27_transformation"][pos27_char]["changing"] += 1
 
 # Kombiniert: Position 30 + Position 27
 if len(l3_id) > 30 and len(l3_id) > 27 and len(l4_id) > 27 and is_onchain is not None:
 pos30_char = l3_id[30].upper()
 pos27_stable = l3_id[27].upper() == l4_id[27].upper()
 
 key = f"{pos30_char}_{pos27_stable}"
 if is_onchain:
 if pos27_stable:
 analysis["combined"][key]["onchain_stable"] += 1
 else:
 analysis["combined"][key]["onchain_changing"] += 1
 else:
 if pos27_stable:
 analysis["combined"][key]["offchain_stable"] += 1
 else:
 analysis["combined"][key]["offchain_changing"] += 1
 
 # Berechne Raten
 pos30_rates = {}
 for char, stats in analysis["pos30_onchain"].items():
 total = stats["onchain"] + stats["offchain"]
 if total > 0:
 onchain_rate = stats["onchain"] / total * 100
 pos30_rates[char] = {
 "onchain_rate": onchain_rate,
 "onchain": stats["onchain"],
 "offchain": stats["offchain"],
 "total": total
 }
 
 pos27_rates = {}
 for char, stats in analysis["pos27_transformation"].items():
 total = stats["stable"] + stats["changing"]
 if total > 0:
 stable_rate = stats["stable"] / total * 100
 pos27_rates[char] = {
 "stable_rate": stable_rate,
 "stable": stats["stable"],
 "changing": stats["changing"],
 "total": total
 }
 
 return {
 "pos30_onchain_rates": pos30_rates,
 "pos27_transformation_rates": pos27_rates,
 "combined_analysis": dict(analysis["combined"])
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("ON-CHAIN vs. TRANSFORMATION ANALYSE")
 print("=" * 80)
 print()
 
 # Analyze
 analysis = analyze_onchain_vs_transformation()
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Position 30 (On-Chain Prädiktor)
 pos30_rates = analysis.get("pos30_onchain_rates", {})
 if pos30_rates:
 print("📊 Position 30 (On-Chain Prädiktor) - Top Characters:")
 sorted_pos30 = sorted(
 pos30_rates.items(),
 key=lambda x: x[1]["onchain_rate"],
 reverse=True
 )
 for char, stats in sorted_pos30[:10]:
 rate = stats["onchain_rate"]
 total = stats["total"]
 print(f" {char}: {rate:.1f}% on-chain ({stats['onchain']}/{total})")
 print()
 
 # Position 27 (Transformation-Stabilität)
 pos27_rates = analysis.get("pos27_transformation_rates", {})
 if pos27_rates:
 print("📊 Position 27 (Transformation-Stabilität) - Top Characters:")
 sorted_pos27 = sorted(
 pos27_rates.items(),
 key=lambda x: x[1]["stable_rate"],
 reverse=True
 )
 for char, stats in sorted_pos27[:10]:
 rate = stats["stable_rate"]
 total = stats["total"]
 print(f" {char}: {rate:.1f}% stabil ({stats['stable']}/{total})")
 print()
 
 # Vergleich
 print("📊 Vergleich Position 30 vs. Position 27:")
 print()
 print(" Position 30: Prädiziert ON-CHAIN Status (welche Identities existieren)")
 print(" Position 27: Prädiziert TRANSFORMATION-STABILITÄT (welche Characters bleiben gleich)")
 print()
 print(" → Verschiedene Mechanismen!")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "analysis": analysis
 }
 
 output_file = OUTPUT_DIR / "onchain_vs_transformation_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# On-Chain vs. Transformation Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Position 30 (On-Chain Prädiktor)",
 ""
 ]
 
 if pos30_rates:
 sorted_pos30 = sorted(
 pos30_rates.items(),
 key=lambda x: x[1]["onchain_rate"],
 reverse=True
 )
 for char, stats in sorted_pos30[:10]:
 rate = stats["onchain_rate"]
 report_lines.append(f"- **{char}**: {rate:.1f}% on-chain ({stats['onchain']}/{stats['total']})")
 report_lines.append("")
 
 report_lines.extend([
 "## Position 27 (Transformation-Stabilität)",
 ""
 ])
 
 if pos27_rates:
 sorted_pos27 = sorted(
 pos27_rates.items(),
 key=lambda x: x[1]["stable_rate"],
 reverse=True
 )
 for char, stats in sorted_pos27[:10]:
 rate = stats["stable_rate"]
 report_lines.append(f"- **{char}**: {rate:.1f}% stabil ({stats['stable']}/{stats['total']})")
 report_lines.append("")
 
 report_lines.extend([
 "## Vergleich",
 "",
 "- **Position 30**: Prädiziert ON-CHAIN Status (welche Identities existieren)",
 "- **Position 27**: Prädiziert TRANSFORMATION-STABILITÄT (welche Characters bleiben gleich)",
 "",
 "→ **Verschiedene Mechanismen!**"
 ])
 
 report_file = REPORTS_DIR / "onchain_vs_transformation_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

