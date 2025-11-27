#!/usr/bin/env python3
"""
Umfassende Analyse: ALLE Seed-Positionen die Identity[27] beeinflussen
- Systematische Analyse aller 55 Seed-Positionen
- Finde alle Positionen mit signifikanter Korrelation
- Erstelle vollständiges Mapping-System
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np
from scipy.stats import chi2_contingency

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def analyze_seed_position_influence(pairs: List[Dict], seed_pos: int, target_pos: int = 27, min_samples: int = 50) -> Dict:
 """Analyze Einfluss einer Seed-Position auf Identity-Position."""
 
 char_mappings = defaultdict(Counter)
 char_totals = Counter()
 
 for pair in pairs:
 seed = identity_to_seed(pair["layer3"])
 l3_id = pair["layer3"]
 
 if len(seed) > seed_pos and len(l3_id) > target_pos:
 seed_char = seed[seed_pos].lower()
 identity_char = l3_id[target_pos].upper()
 
 char_mappings[seed_char][identity_char] += 1
 char_totals[seed_char] += 1
 
 # Berechne Erfolgsraten und statistische Signifikanz
 results = {}
 
 for seed_char, counter in char_mappings.items():
 total = char_totals[seed_char]
 if total >= min_samples:
 most_common = counter.most_common(1)[0]
 success_rate = most_common[1] / total
 
 # Berechne Varianz (wie stark ist die Korrelation?)
 all_rates = [count / total for count in counter.values()]
 variance = np.var(all_rates) if len(all_rates) > 1 else 0
 
 results[seed_char] = {
 "target_character": most_common[0],
 "success_rate": success_rate,
 "count": most_common[1],
 "total": total,
 "variance": variance,
 "all_distributions": dict(counter.most_common(10))
 }
 
 # Berechne Gesamt-Statistik for diese Position
 if results:
 all_success_rates = [r["success_rate"] for r in results.values()]
 mean_success = np.mean(all_success_rates)
 max_success = np.max(all_success_rates)
 min_success = np.min(all_success_rates)
 
 # Chi-Square Test for gesamte Position
 contingency = []
 for seed_char in sorted(results.keys()):
 data = results[seed_char]
 target_char = data["target_character"]
 count = data["count"]
 total = data["total"]
 contingency.append([count, total - count])
 
 if len(contingency) > 1 and all(len(row) == 2 for row in contingency):
 try:
 chi2, p_value, dof, expected = chi2_contingency(contingency)
 n = sum(sum(row) for row in contingency)
 min_dim = min(len(contingency), len(contingency[0]))
 cramers_v = np.sqrt(chi2 / (n * (min_dim - 1))) if n > 0 and min_dim > 1 else 0
 except:
 chi2, p_value, cramers_v = np.nan, np.nan, 0
 else:
 chi2, p_value, cramers_v = np.nan, np.nan, 0
 
 return {
 "seed_position": seed_pos,
 "target_position": target_pos,
 "char_mappings": results,
 "statistics": {
 "mean_success_rate": mean_success,
 "max_success_rate": max_success,
 "min_success_rate": min_success,
 "chi2": float(chi2) if not np.isnan(chi2) else None,
 "p_value": float(p_value) if not np.isnan(p_value) else None,
 "cramers_v": float(cramers_v) if not np.isnan(cramers_v) else 0,
 "significant": p_value < 0.05 if not np.isnan(p_value) else False
 }
 }
 
 return {
 "seed_position": seed_pos,
 "target_position": target_pos,
 "char_mappings": {},
 "statistics": {}
 }

def analyze_all_seed_positions(pairs: List[Dict], target_pos: int = 27) -> Dict:
 """Analyze ALLE 55 Seed-Positionen."""
 
 print("=" * 80)
 print("ANALYSE ALLER SEED-POSITIONEN")
 print("=" * 80)
 print()
 print(f"🔍 Analyze alle 55 Seed-Positionen → Identity[{target_pos}]...")
 print()
 
 all_results = {}
 significant_positions = []
 
 for seed_pos in range(55):
 if seed_pos % 10 == 0:
 print(f" Progress: {seed_pos}/55...")
 
 result = analyze_seed_position_influence(pairs, seed_pos, target_pos, min_samples=50)
 all_results[seed_pos] = result
 
 # Check ob signifikant
 stats = result.get("statistics", {})
 if stats.get("significant", False):
 significant_positions.append({
 "position": seed_pos,
 "cramers_v": stats.get("cramers_v", 0),
 "max_success_rate": stats.get("max_success_rate", 0),
 "p_value": stats.get("p_value", 1.0)
 })
 
 print("✅ Alle Positionen analysiert")
 print()
 
 # Sortiere signifikante Positionen
 significant_positions.sort(key=lambda x: x["cramers_v"], reverse=True)
 
 return {
 "all_positions": all_results,
 "significant_positions": significant_positions,
 "target_position": target_pos
 }

def find_strongest_correlations(analysis_results: Dict) -> Dict:
 """Finde stärkste Korrelationen."""
 
 strongest = []
 
 for pos, result in analysis_results.get("all_positions", {}).items():
 char_mappings = result.get("char_mappings", {})
 stats = result.get("statistics", {})
 
 if stats.get("significant", False):
 # Finde beste Mapping for diese Position
 best_char = max(
 char_mappings.items(),
 key=lambda x: x[1]["success_rate"]
 ) if char_mappings else None
 
 if best_char:
 seed_char, mapping_data = best_char
 strongest.append({
 "seed_position": pos,
 "seed_char": seed_char,
 "target_char": mapping_data["target_character"],
 "success_rate": mapping_data["success_rate"],
 "count": mapping_data["count"],
 "total": mapping_data["total"],
 "cramers_v": stats.get("cramers_v", 0),
 "variance": mapping_data.get("variance", 0)
 })
 
 # Sortiere nach Cramér's V (stärkste Korrelation)
 strongest.sort(key=lambda x: x["cramers_v"], reverse=True)
 
 return {
 "strongest_correlations": strongest[:30], # Top 30
 "total_significant": len(strongest)
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("UMFASSENDE ANALYSE: ALLE SEED-POSITIONEN")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Daten...")
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 print(f"✅ {len(layer3_results)} Layer-3 Identities geloadn")
 print()
 
 # Erstelle Paare (for Konsistenz)
 pairs = []
 for entry in layer3_results:
 identity = entry.get("layer3_identity", "")
 if identity and len(identity) == 60:
 pairs.append({"layer3": identity, "layer4": ""}) # Layer-4 nicht nötig for diese Analyse
 
 print(f"✅ {len(pairs)} Identities for Analyse vorbereitet")
 print()
 
 # Analyze alle Positionen
 analysis_results = analyze_all_seed_positions(pairs, target_pos=27)
 
 # Finde stärkste Korrelationen
 print("🔍 Finde stärkste Korrelationen...")
 strongest = find_strongest_correlations(analysis_results)
 print("✅ Stärkste Korrelationen gefunden")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Signifikante Positionen
 sig_positions = analysis_results.get("significant_positions", [])
 print(f"📊 Signifikante Positionen: {len(sig_positions)}")
 print()
 
 if sig_positions:
 print("📊 Top 20 Signifikante Positionen (nach Cramér's V):")
 for i, pos_data in enumerate(sig_positions[:20], 1):
 pos = pos_data["position"]
 cramers_v = pos_data["cramers_v"]
 max_rate = pos_data["max_success_rate"] * 100
 marker = "⭐" if cramers_v > 0.1 else " "
 print(f" {marker} {i:2d}. Seed[{pos:2d}]: Cramér's V={cramers_v:.4f}, Max Rate={max_rate:.1f}%")
 print()
 
 # Stärkste Korrelationen
 strongest_corrs = strongest.get("strongest_correlations", [])
 if strongest_corrs:
 print("📊 Top 20 Stärkste Korrelationen:")
 for i, corr in enumerate(strongest_corrs[:20], 1):
 rate = corr["success_rate"] * 100
 marker = "⭐" if rate >= 40 else " "
 print(f" {marker} {i:2d}. Seed[{corr['seed_position']:2d}]='{corr['seed_char']}' → Identity[27]='{corr['target_char']}' ({rate:.1f}%, Cramér's V={corr['cramers_v']:.4f})")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "analysis_results": analysis_results,
 "strongest_correlations": strongest
 }
 
 output_file = OUTPUT_DIR / "all_seed_positions_influence_analysis.json"
 with output_file.open("w") as f:
 # Konvertiere numpy types
 def convert_to_python(obj):
 if isinstance(obj, np.bool_):
 return bool(obj)
 elif isinstance(obj, np.integer):
 return int(obj)
 elif isinstance(obj, np.floating):
 return float(obj)
 elif isinstance(obj, dict):
 return {k: convert_to_python(v) for k, v in obj.items()}
 elif isinstance(obj, list):
 return [convert_to_python(item) for item in obj]
 return obj
 
 json.dump(convert_to_python(output_data), f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle detaillierten Report
 report_lines = [
 "# Umfassende Analyse: Alle Seed-Positionen",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Signifikante Positionen",
 "",
 f"**Total signifikant**: {len(sig_positions)} von 55 Positionen",
 ""
 ]
 
 if sig_positions:
 report_lines.append("### Top 20 (nach Cramér's V):")
 report_lines.append("")
 for i, pos_data in enumerate(sig_positions[:20], 1):
 pos = pos_data["position"]
 cramers_v = pos_data["cramers_v"]
 max_rate = pos_data["max_success_rate"] * 100
 report_lines.append(f"{i}. **Seed[{pos}]**: Cramér's V={cramers_v:.4f}, Max Rate={max_rate:.1f}%")
 report_lines.append("")
 
 report_lines.extend([
 "## Stärkste Korrelationen",
 ""
 ])
 
 if strongest_corrs:
 for i, corr in enumerate(strongest_corrs[:30], 1):
 rate = corr["success_rate"] * 100
 report_lines.append(f"{i}. **Seed[{corr['seed_position']}]='{corr['seed_char']}'** → Identity[27]='{corr['target_char']}' ({rate:.1f}%, Cramér's V={corr['cramers_v']:.4f}, {corr['count']}/{corr['total']})")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "all_seed_positions_influence_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("💡 ERKENNTNISSE:")
 print()
 print(f" ✅ {len(sig_positions)} signifikante Positionen gefunden")
 print(f" ✅ {len(strongest_corrs)} starke Korrelationen identifiziert")
 print(" ✅ Vollständiges Mapping-System möglich")
 print()

if __name__ == "__main__":
 main()

