#!/usr/bin/env python3
"""
KRITISCHE VALIDIERUNG: Position 27 - Check alle möglichen Fehlerquellen
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter
from datetime import datetime
from scipy.stats import chi2_contingency
import numpy as np

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

BLOCK_END_POSITIONS = [13, 27, 41, 55]

def load_all_pairs() -> Tuple[List[Dict], Dict]:
 """Load ALLE Paare und check Datenqualität."""
 
 # Load Layer-3
 layer3_data = []
 layer3_issues = {
 "missing_identity": 0,
 "wrong_length": 0,
 "invalid_chars": 0,
 "total": 0
 }
 
 if LAYER3_FILE.exists():
 with LAYER3_FILE.open() as f:
 data = json.load(f)
 layer3_data = data.get("results", [])
 
 # Load Layer-4
 layer4_map = {}
 layer4_issues = {
 "missing_identity": 0,
 "wrong_length": 0,
 "invalid_chars": 0,
 "total": 0
 }
 
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 data = json.load(f)
 for entry in data.get("results", []):
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 
 layer4_issues["total"] += 1
 
 if not l3_id:
 layer4_issues["missing_identity"] += 1
 continue
 if not l4_id:
 layer4_issues["missing_identity"] += 1
 continue
 if len(l3_id) != 60:
 layer4_issues["wrong_length"] += 1
 continue
 if len(l4_id) != 60:
 layer4_issues["wrong_length"] += 1
 continue
 
 # Check auf gültige Characters (A-Z)
 if not all(c.isalpha() and c.isupper() for c in l3_id):
 layer4_issues["invalid_chars"] += 1
 continue
 if not all(c.isalpha() and c.isupper() for c in l4_id):
 layer4_issues["invalid_chars"] += 1
 continue
 
 layer4_map[l3_id] = l4_id
 
 # Erstelle Paare
 pairs = []
 matching_issues = {
 "no_match": 0,
 "duplicate_match": 0,
 "total_checked": 0
 }
 
 seen_l4_ids = set()
 
 for l3_entry in layer3_data:
 l3_id = l3_entry.get("layer3_identity", "")
 
 matching_issues["total_checked"] += 1
 
 if not l3_id or len(l3_id) != 60:
 continue
 
 l4_id = layer4_map.get(l3_id)
 
 if not l4_id:
 matching_issues["no_match"] += 1
 continue
 
 # Check auf Duplikate
 if l4_id in seen_l4_ids:
 matching_issues["duplicate_match"] += 1
 continue
 
 seen_l4_ids.add(l4_id)
 pairs.append({"layer3": l3_id, "layer4": l4_id})
 
 issues = {
 "layer3_issues": layer3_issues,
 "layer4_issues": layer4_issues,
 "matching_issues": matching_issues,
 "total_pairs": len(pairs)
 }
 
 return pairs, issues

def calculate_stability_with_validation(pairs: List[Dict], position: int) -> Dict:
 """Berechne Stabilität mit vollständiger Validierung."""
 
 same_count = 0
 different_count = 0
 errors = {
 "length_mismatch": 0,
 "invalid_char": 0,
 "case_issues": 0
 }
 
 char_comparisons = []
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 # Validierung
 if len(l3_id) <= position or len(l4_id) <= position:
 errors["length_mismatch"] += 1
 continue
 
 l3_char = l3_id[position]
 l4_char = l4_id[position]
 
 # Check auf gültige Characters
 if not l3_char.isalpha() or not l4_char.isalpha():
 errors["invalid_char"] += 1
 continue
 
 # Normalisiere zu Uppercase
 l3_char_upper = l3_char.upper()
 l4_char_upper = l4_char.upper()
 
 # Check ob Original bereits uppercase war
 if l3_char != l3_char_upper or l4_char != l4_char_upper:
 errors["case_issues"] += 1
 
 char_comparisons.append({
 "l3": l3_char_upper,
 "l4": l4_char_upper,
 "same": l3_char_upper == l4_char_upper
 })
 
 if l3_char_upper == l4_char_upper:
 same_count += 1
 else:
 different_count += 1
 
 total = same_count + different_count
 stability_rate = same_count / total if total > 0 else 0
 
 return {
 "position": position,
 "stability_rate": stability_rate,
 "same_count": same_count,
 "different_count": different_count,
 "total": total,
 "errors": errors,
 "char_comparisons": char_comparisons[:100] # Sample for Debugging
 }

def test_statistical_significance(positions_data: Dict) -> Dict:
 """Teste statistische Signifikanz zwischen Positionen."""
 
 # Erstelle Contingency Table
 # Zeilen: Positionen (13, 27, 41, 55)
 # Spalten: Same (1) vs. Different (0)
 
 contingency = []
 position_labels = []
 
 for pos in BLOCK_END_POSITIONS:
 pos_str = str(pos)
 if pos_str in positions_data:
 data = positions_data[pos_str]
 same = data["same_count"]
 different = data["different_count"]
 contingency.append([same, different])
 position_labels.append(pos)
 
 if len(contingency) < 2:
 return {"error": "Not enough positions for chi-square test"}
 
 # Chi-Square Test
 chi2, p_value, dof, expected = chi2_contingency(contingency)
 
 # Cramér's V
 n = sum(sum(row) for row in contingency)
 min_dim = min(len(contingency), len(contingency[0]))
 cramers_v = np.sqrt(chi2 / (n * (min_dim - 1))) if n > 0 and min_dim > 1 else 0
 
 return {
 "chi2": float(chi2),
 "p_value": float(p_value),
 "dof": int(dof),
 "significant": bool(p_value < 0.05),
 "cramers_v": float(cramers_v),
 "effect_size": "large" if cramers_v > 0.5 else "medium" if cramers_v > 0.3 else "small",
 "position_labels": [int(p) for p in position_labels]
 }

def main():
 """Hauptfunktion - Kritische Validierung."""
 print("=" * 80)
 print("KRITISCHE VALIDIERUNG: Position 27")
 print("=" * 80)
 print()
 
 # 1. Load und validate Daten
 print("📂 Load und validate Daten...")
 pairs, issues = load_all_pairs()
 print(f"✅ {len(pairs)} gültige Paare gefunden")
 print()
 
 print("⚠️ Datenqualität:")
 print(f" Layer-3 Issues: {issues['layer3_issues']}")
 print(f" Layer-4 Issues: {issues['layer4_issues']}")
 print(f" Matching Issues: {issues['matching_issues']}")
 print()
 
 # 2. Berechne Stabilität for alle Block-Ende-Positionen
 print("🔍 Berechne Stabilität for alle Block-Ende-Positionen...")
 positions_data = {}
 
 for pos in BLOCK_END_POSITIONS:
 result = calculate_stability_with_validation(pairs, pos)
 positions_data[str(pos)] = result
 
 rate = result["stability_rate"] * 100
 same = result["same_count"]
 total = result["total"]
 errors = result["errors"]
 
 print(f" Position {pos:2d}: {rate:5.1f}% ({same}/{total})")
 if any(errors.values()):
 print(f" ⚠️ Errors: {errors}")
 print()
 
 # 3. Statistische Signifikanz
 print("📊 Teste statistische Signifikanz...")
 significance = test_statistical_significance(positions_data)
 
 if "error" not in significance:
 print(f" Chi-Square: {significance['chi2']:.2f}")
 print(f" p-Wert: {significance['p_value']:.6f}")
 print(f" Signifikant: {'✅ JA' if significance['significant'] else '❌ NEIN'}")
 print(f" Effect Size: {significance['effect_size']} (Cramér's V: {significance['cramers_v']:.3f})")
 else:
 print(f" ❌ {significance['error']}")
 print()
 
 # 4. Vergleich Position 27 vs. andere
 pos27_data = positions_data.get("27", {})
 if pos27_data:
 print("🔍 Vergleich Position 27 vs. andere Block-Ende:")
 pos27_rate = pos27_data["stability_rate"] * 100
 
 for pos in BLOCK_END_POSITIONS:
 if pos == 27:
 continue
 pos_str = str(pos)
 if pos_str in positions_data:
 other_rate = positions_data[pos_str]["stability_rate"] * 100
 diff = pos27_rate - other_rate
 marker = "⭐" if diff > 5 else " "
 print(f" {marker} Position 27 ({pos27_rate:.1f}%) vs. Position {pos} ({other_rate:.1f}%): {diff:+.1f}%")
 print()
 
 # 5. Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "data_quality": issues,
 "positions_data": {
 k: {
 "position": v["position"],
 "stability_rate": v["stability_rate"],
 "same_count": v["same_count"],
 "different_count": v["different_count"],
 "total": v["total"],
 "errors": v["errors"]
 }
 for k, v in positions_data.items()
 },
 "statistical_significance": significance
 }
 
 output_file = OUTPUT_DIR / "position27_critical_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # 6. Erstelle kritischen Report
 report_lines = [
 "# Kritische Validierung: Position 27",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Datenqualität",
 ""
 ]
 
 if issues:
 report_lines.append(f"- **Total Paare**: {issues['total_pairs']}")
 report_lines.append(f"- **Layer-3 Issues**: {issues['layer3_issues']}")
 report_lines.append(f"- **Layer-4 Issues**: {issues['layer4_issues']}")
 report_lines.append(f"- **Matching Issues**: {issues['matching_issues']}")
 report_lines.append("")
 
 report_lines.extend([
 "## Stabilitätsraten",
 ""
 ])
 
 for pos in BLOCK_END_POSITIONS:
 pos_str = str(pos)
 if pos_str in positions_data:
 data = positions_data[pos_str]
 rate = data["stability_rate"] * 100
 report_lines.append(f"- **Position {pos}**: {rate:.1f}% ({data['same_count']}/{data['total']})")
 report_lines.append("")
 
 if "error" not in significance:
 report_lines.extend([
 "## Statistische Signifikanz",
 "",
 f"- **Chi-Square**: {significance['chi2']:.2f}",
 f"- **p-Wert**: {significance['p_value']:.6f}",
 f"- **Signifikant**: {'✅ JA' if significance['significant'] else '❌ NEIN'}",
 f"- **Effect Size**: {significance['effect_size']} (Cramér's V: {significance['cramers_v']:.3f})",
 ""
 ])
 
 report_file = REPORTS_DIR / "position27_critical_validation_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

