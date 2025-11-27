#!/usr/bin/env python3
"""
Teste Position 27+55 als Prädiktor for Layer-4 on-chain Status
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
LAYER4_RPC_FILE = project_root / "outputs" / "derived" / "layer4_rpc_validation.json"
LAYER4_DERIVATION_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_layer4_data() -> Dict:
 """Load Layer-4 Daten (RPC + Derivation)."""
 rpc_data = {}
 if LAYER4_RPC_FILE.exists():
 with LAYER4_RPC_FILE.open() as f:
 rpc_json = json.load(f)
 for entry in rpc_json.get("results", []):
 identity = entry.get("layer4_identity", "")
 if identity:
 rpc_data[identity] = entry.get("rpc_status") == "ONCHAIN"
 
 derivation_data = []
 if LAYER4_DERIVATION_FILE.exists():
 with LAYER4_DERIVATION_FILE.open() as f:
 derivation_json = json.load(f)
 derivation_data = derivation_json.get("results", [])
 
 # Kombiniere Daten
 combined = []
 for entry in derivation_data:
 identity = entry.get("layer4_identity", "")
 if identity and len(identity) == 60:
 is_onchain = rpc_data.get(identity, None)
 combined.append({
 "layer4_identity": identity,
 "layer3_identity": entry.get("layer3_identity", ""),
 "is_onchain": is_onchain
 })
 
 return combined

def test_position27_55_predictor(data: List[Dict]) -> Dict:
 """Teste Position 27+55 als Prädiktor."""
 
 # Filtere nur bekannte on-chain Status
 known_data = [d for d in data if d.get("is_onchain") is not None]
 
 if not known_data:
 return {"error": "No known on-chain status data"}
 
 # Analyze Position 27+55 Kombinationen
 combinations = defaultdict(lambda: {"onchain": 0, "offchain": 0, "total": 0})
 
 for entry in known_data:
 identity = entry.get("layer4_identity", "")
 is_onchain = entry.get("is_onchain", False)
 
 if len(identity) >= 56:
 pos27_char = identity[27].upper()
 pos55_char = identity[55].upper()
 combo = f"{pos27_char}{pos55_char}"
 
 combinations[combo]["total"] += 1
 if is_onchain:
 combinations[combo]["onchain"] += 1
 else:
 combinations[combo]["offchain"] += 1
 
 # Berechne Accuracy for jede Kombination
 combo_accuracy = {}
 for combo, stats in combinations.items():
 total = stats["total"]
 if total > 0:
 onchain_rate = stats["onchain"] / total
 # Accuracy = max(onchain_rate, 1 - onchain_rate) wenn wir vorhersagen
 accuracy = max(onchain_rate, 1 - onchain_rate)
 combo_accuracy[combo] = {
 "accuracy": accuracy,
 "onchain_rate": onchain_rate,
 "onchain": stats["onchain"],
 "offchain": stats["offchain"],
 "total": total
 }
 
 # Finde beste Prädiktoren
 sorted_combos = sorted(combo_accuracy.items(), key=lambda x: x[1]["accuracy"], reverse=True)
 
 # Analyze auch einzelne Positionen
 pos27_stats = defaultdict(lambda: {"onchain": 0, "offchain": 0, "total": 0})
 pos55_stats = defaultdict(lambda: {"onchain": 0, "offchain": 0, "total": 0})
 
 for entry in known_data:
 identity = entry.get("layer4_identity", "")
 is_onchain = entry.get("is_onchain", False)
 
 if len(identity) >= 56:
 pos27_char = identity[27].upper()
 pos55_char = identity[55].upper()
 
 pos27_stats[pos27_char]["total"] += 1
 pos55_stats[pos55_char]["total"] += 1
 
 if is_onchain:
 pos27_stats[pos27_char]["onchain"] += 1
 pos55_stats[pos55_char]["onchain"] += 1
 else:
 pos27_stats[pos27_char]["offchain"] += 1
 pos55_stats[pos55_char]["offchain"] += 1
 
 # Berechne Accuracy for einzelne Positionen
 pos27_accuracy = {}
 for char, stats in pos27_stats.items():
 total = stats["total"]
 if total > 0:
 onchain_rate = stats["onchain"] / total
 accuracy = max(onchain_rate, 1 - onchain_rate)
 pos27_accuracy[char] = {
 "accuracy": accuracy,
 "onchain_rate": onchain_rate,
 "onchain": stats["onchain"],
 "offchain": stats["offchain"],
 "total": total
 }
 
 pos55_accuracy = {}
 for char, stats in pos55_stats.items():
 total = stats["total"]
 if total > 0:
 onchain_rate = stats["onchain"] / total
 accuracy = max(onchain_rate, 1 - onchain_rate)
 pos55_accuracy[char] = {
 "accuracy": accuracy,
 "onchain_rate": onchain_rate,
 "onchain": stats["onchain"],
 "offchain": stats["offchain"],
 "total": total
 }
 
 return {
 "total_known": len(known_data),
 "onchain_count": sum(1 for d in known_data if d.get("is_onchain")),
 "offchain_count": sum(1 for d in known_data if not d.get("is_onchain")),
 "combinations": dict(combinations),
 "combo_accuracy": dict(combo_accuracy),
 "top_combos": dict(sorted_combos[:20]),
 "pos27_accuracy": pos27_accuracy,
 "pos55_accuracy": pos55_accuracy,
 "pos27_stats": {k: dict(v) for k, v in pos27_stats.items()},
 "pos55_stats": {k: dict(v) for k, v in pos55_stats.items()}
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("POSITION 27+55 PRÄDIKTOR TEST (LAYER-4)")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Layer-4 Daten...")
 data = load_layer4_data()
 print(f"✅ {len(data)} Layer-4 Identities geloadn")
 
 known_count = sum(1 for d in data if d.get("is_onchain") is not None)
 print(f"✅ {known_count} mit bekanntem on-chain Status")
 print()
 
 if known_count == 0:
 print("❌ Keine Daten mit bekanntem on-chain Status!")
 return
 
 # Teste Prädiktor
 print("🔍 Teste Position 27+55 als Prädiktor...")
 results = test_position27_55_predictor(data)
 print("✅ Prädiktor getestet")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 onchain_count = results.get("onchain_count", 0)
 total = results.get("total_known", 0)
 baseline = onchain_count / total if total > 0 else 0
 
 print(f"📊 Baseline (on-chain Rate): {baseline*100:.1f}% ({onchain_count}/{total})")
 print()
 
 # Top Kombinationen
 top_combos = results.get("top_combos", {})
 if top_combos:
 print("📊 Top 10 Position 27+55 Kombinationen (nach Accuracy):")
 for i, (combo, stats) in enumerate(list(top_combos.items())[:10], 1):
 accuracy = stats.get("accuracy", 0) * 100
 onchain_rate = stats.get("onchain_rate", 0) * 100
 total_combo = stats.get("total", 0)
 print(f" {i:2d}. {combo}: {accuracy:.1f}% Accuracy ({total_combo} Fälle, {onchain_rate:.1f}% on-chain)")
 print()
 
 # Position 27 einzeln
 pos27_acc = results.get("pos27_accuracy", {})
 if pos27_acc:
 sorted_pos27 = sorted(pos27_acc.items(), key=lambda x: x[1]["accuracy"], reverse=True)
 print("📊 Top 10 Position 27 Characters (nach Accuracy):")
 for i, (char, stats) in enumerate(sorted_pos27[:10], 1):
 accuracy = stats.get("accuracy", 0) * 100
 onchain_rate = stats.get("onchain_rate", 0) * 100
 total_char = stats.get("total", 0)
 print(f" {i:2d}. {char}: {accuracy:.1f}% Accuracy ({total_char} Fälle, {onchain_rate:.1f}% on-chain)")
 print()
 
 # Position 55 einzeln
 pos55_acc = results.get("pos55_accuracy", {})
 if pos55_acc:
 sorted_pos55 = sorted(pos55_acc.items(), key=lambda x: x[1]["accuracy"], reverse=True)
 print("📊 Top 10 Position 55 Characters (nach Accuracy):")
 for i, (char, stats) in enumerate(sorted_pos55[:10], 1):
 accuracy = stats.get("accuracy", 0) * 100
 onchain_rate = stats.get("onchain_rate", 0) * 100
 total_char = stats.get("total", 0)
 print(f" {i:2d}. {char}: {accuracy:.1f}% Accuracy ({total_char} Fälle, {onchain_rate:.1f}% on-chain)")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "baseline": baseline,
 "results": results
 }
 
 output_file = OUTPUT_DIR / "position27_55_predictor_test.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Position 27+55 Prädiktor Test (Layer-4)",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 f"**Sample Size**: {total}",
 f"**Baseline (on-chain Rate)**: {baseline*100:.1f}%",
 "",
 "## Top Position 27+55 Kombinationen",
 ""
 ]
 
 if top_combos:
 for i, (combo, stats) in enumerate(list(top_combos.items())[:15], 1):
 accuracy = stats.get("accuracy", 0) * 100
 onchain_rate = stats.get("onchain_rate", 0) * 100
 total_combo = stats.get("total", 0)
 report_lines.append(f"{i}. **{combo}**: {accuracy:.1f}% Accuracy ({total_combo} Fälle, {onchain_rate:.1f}% on-chain)")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "position27_55_predictor_test_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

