#!/usr/bin/env python3
"""
Umfassende Layer-3 → Layer-4 Analyse aus verschiedenen Blickwinkeln
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import statistics

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_sample_5000.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_layer_data(file_path: Path) -> List[Dict]:
 """Load Layer-Daten."""
 if not file_path.exists():
 return []
 
 with file_path.open() as f:
 data = json.load(f)
 
 return data.get("results", [])

def analyze_character_changes(pairs: List[Dict]) -> Dict:
 """Analyze Character-Änderungen von verschiedenen Blickwinkeln."""
 
 # 1. Position-spezifische Änderungen
 position_changes = defaultdict(lambda: {"same": 0, "different": 0, "changes": []})
 
 # 2. Character-spezifische Änderungen (welche Characters ändern sich am meisten)
 char_change_frequency = Counter()
 char_stability = defaultdict(lambda: {"stays": 0, "changes": 0})
 
 # 3. Pattern-Änderungen (z.B. AA -> BB, AB -> CD)
 pattern_changes = Counter()
 
 # 4. Position-Paare (z.B. Position 27+30, 27+4)
 position_pair_stability = defaultdict(int)
 
 # 5. Checksum-Bereich Analyse
 checksum_analysis = {"positions_56_59": defaultdict(lambda: {"same": 0, "different": 0})}
 
 # 6. Body-Bereich Analyse (0-55)
 body_analysis = {"positions_0_55": defaultdict(lambda: {"same": 0, "different": 0})}
 
 # 7. Symmetrie-Analyse (Position i vs. Position 59-i)
 symmetry_analysis = defaultdict(lambda: {"both_same": 0, "both_different": 0, "one_same": 0})
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 if len(l3_id) != 60 or len(l4_id) != 60:
 continue
 
 # Position-spezifische Änderungen
 for pos in range(60):
 l3_char = l3_id[pos].upper()
 l4_char = l4_id[pos].upper()
 
 if l3_char == l4_char:
 position_changes[pos]["same"] += 1
 char_stability[l3_char]["stays"] += 1
 else:
 position_changes[pos]["different"] += 1
 char_change_frequency[l3_char] += 1
 char_stability[l3_char]["changes"] += 1
 position_changes[pos]["changes"].append((l3_char, l4_char))
 
 # Pattern-Änderungen (2-Character Patterns)
 for pos in range(59):
 l3_pattern = l3_id[pos:pos+2].upper()
 l4_pattern = l4_id[pos:pos+2].upper()
 if l3_pattern != l4_pattern:
 pattern_changes[f"{l3_pattern}->{l4_pattern}"] += 1
 
 # Position-Paare Stabilität
 for pos1 in [27, 30, 4, 55]:
 for pos2 in [27, 30, 4, 55]:
 if pos1 < pos2:
 if l3_id[pos1] == l4_id[pos1] and l3_id[pos2] == l4_id[pos2]:
 position_pair_stability[f"{pos1}+{pos2}"] += 1
 
 # Checksum-Bereich
 for pos in range(56, 60):
 if l3_id[pos] == l4_id[pos]:
 checksum_analysis["positions_56_59"][pos]["same"] += 1
 else:
 checksum_analysis["positions_56_59"][pos]["different"] += 1
 
 # Body-Bereich
 for pos in range(56):
 if l3_id[pos] == l4_id[pos]:
 body_analysis["positions_0_55"][pos]["same"] += 1
 else:
 body_analysis["positions_0_55"][pos]["different"] += 1
 
 # Symmetrie-Analyse
 for pos in range(30):
 mirror_pos = 59 - pos
 l3_same = l3_id[pos] == l4_id[pos]
 l3_mirror_same = l3_id[mirror_pos] == l4_id[mirror_pos]
 
 if l3_same and l3_mirror_same:
 symmetry_analysis[pos]["both_same"] += 1
 elif not l3_same and not l3_mirror_same:
 symmetry_analysis[pos]["both_different"] += 1
 else:
 symmetry_analysis[pos]["one_same"] += 1
 
 # Berechne Änderungsraten
 change_rates = {}
 for pos in range(60):
 if pos in position_changes:
 total = position_changes[pos]["same"] + position_changes[pos]["different"]
 if total > 0:
 change_rates[pos] = {
 "same_rate": position_changes[pos]["same"] / total,
 "different_rate": position_changes[pos]["different"] / total,
 "total": total,
 "most_common_changes": Counter(position_changes[pos]["changes"]).most_common(5)
 }
 
 return {
 "position_changes": {str(k): v for k, v in position_changes.items()},
 "change_rates": {str(k): v for k, v in change_rates.items()},
 "char_change_frequency": dict(char_change_frequency.most_common(20)),
 "char_stability": {k: dict(v) for k, v in char_stability.items()},
 "pattern_changes": dict(pattern_changes.most_common(20)),
 "position_pair_stability": dict(position_pair_stability),
 "checksum_analysis": {k: {str(p): dict(v) for p, v in d.items()} for k, d in checksum_analysis.items()},
 "body_analysis": {k: {str(p): dict(v) for p, v in d.items()} for k, d in body_analysis.items()},
 "symmetry_analysis": {str(k): dict(v) for k, v in symmetry_analysis.items()}
 }

def analyze_clusters(pairs: List[Dict]) -> Dict:
 """Analyze Clusters von ähnlichen Änderungen."""
 
 # Gruppiere nach Änderungsmustern
 change_patterns = defaultdict(list)
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 if len(l3_id) != 60 or len(l4_id) != 60:
 continue
 
 # Erstelle Pattern-String (S=same, D=different)
 pattern = "".join(["S" if l3_id[i] == l4_id[i] else "D" for i in range(60)])
 change_patterns[pattern].append(pair)
 
 # Finde häufigste Patterns
 pattern_frequency = {pattern: len(pairs_list) for pattern, pairs_list in change_patterns.items()}
 
 return {
 "unique_patterns": len(change_patterns),
 "pattern_frequency": dict(sorted(pattern_frequency.items(), key=lambda x: x[1], reverse=True)[:20]),
 "most_common_pattern": max(pattern_frequency.items(), key=lambda x: x[1]) if pattern_frequency else None
 }

def analyze_numeric_patterns(pairs: List[Dict]) -> Dict:
 """Analyze numerische Patterns (Character-Distanzen, etc.)."""
 
 char_distances = []
 position_stability_scores = []
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 if len(l3_id) != 60 or len(l4_id) != 60:
 continue
 
 # Character-Distanzen (A=0, B=1, ..., Z=25)
 same_count = sum(1 for i in range(60) if l3_id[i].upper() == l4_id[i].upper())
 position_stability_scores.append(same_count)
 
 # Distanz zwischen Characters an gleicher Position
 for pos in range(60):
 l3_char = ord(l3_id[pos].upper()) - ord('A')
 l4_char = ord(l4_id[pos].upper()) - ord('A')
 distance = abs(l3_char - l4_char)
 char_distances.append(distance)
 
 return {
 "char_distances": {
 "mean": statistics.mean(char_distances) if char_distances else 0,
 "median": statistics.median(char_distances) if char_distances else 0,
 "stdev": statistics.stdev(char_distances) if len(char_distances) > 1 else 0,
 "distribution": dict(Counter(char_distances))
 },
 "position_stability": {
 "mean": statistics.mean(position_stability_scores) if position_stability_scores else 0,
 "median": statistics.median(position_stability_scores) if position_stability_scores else 0,
 "stdev": statistics.stdev(position_stability_scores) if len(position_stability_scores) > 1 else 0,
 "min": min(position_stability_scores) if position_stability_scores else 0,
 "max": max(position_stability_scores) if position_stability_scores else 0
 }
 }

def analyze_special_positions(pairs: List[Dict]) -> Dict:
 """Analyze spezielle Positionen (27, 30, 4, 55, etc.) im Detail."""
 
 special_positions = [27, 30, 4, 55, 0, 1, 28, 29, 56, 57, 58, 59]
 
 analysis = {}
 
 for pos in special_positions:
 char_transitions = Counter()
 char_stability = Counter()
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 if len(l3_id) > pos and len(l4_id) > pos:
 l3_char = l3_id[pos].upper()
 l4_char = l4_id[pos].upper()
 
 if l3_char == l4_char:
 char_stability[l3_char] += 1
 else:
 char_transitions[f"{l3_char}->{l4_char}"] += 1
 
 analysis[pos] = {
 "stable_chars": dict(char_stability.most_common(10)),
 "transitions": dict(char_transitions.most_common(10)),
 "stability_rate": sum(char_stability.values()) / len(pairs) if pairs else 0
 }
 
 return analysis

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("UMFASSENDE LAYER-3 → LAYER-4 ANALYSE")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Daten...")
 layer3_data = load_layer_data(LAYER3_FILE)
 layer4_data = load_layer_data(LAYER4_FILE)
 
 print(f"✅ Layer-3: {len(layer3_data)} Identities")
 print(f"✅ Layer-4: {len(layer4_data)} Identities")
 print()
 
 if not layer3_data or not layer4_data:
 print("❌ Nicht genug Daten for Analyse!")
 return
 
 # Erstelle Paare
 print("🔗 Erstelle Layer-3 → Layer-4 Paare...")
 pairs = []
 layer4_map = {r.get("layer3_identity"): r.get("layer4_identity") 
 for r in layer4_data 
 if r.get("layer3_identity") and r.get("layer4_identity")}
 
 for l3_entry in layer3_data:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 if l3_id and l4_id:
 pairs.append({"layer3": l3_id, "layer4": l4_id})
 
 print(f"✅ {len(pairs)} Paare erstellt")
 print()
 
 # Verschiedene Analysen
 print("🔍 Analyze Character-Änderungen...")
 change_analysis = analyze_character_changes(pairs)
 print("✅ Character-Änderungen analysiert")
 print()
 
 print("🔍 Analyze Clusters...")
 cluster_analysis = analyze_clusters(pairs)
 print(f"✅ Clusters analysiert ({cluster_analysis['unique_patterns']} unique patterns)")
 print()
 
 print("🔍 Analyze numerische Patterns...")
 numeric_analysis = analyze_numeric_patterns(pairs)
 print("✅ Numerische Patterns analysiert")
 print()
 
 print("🔍 Analyze spezielle Positionen...")
 special_analysis = analyze_special_positions(pairs)
 print("✅ Spezielle Positionen analysiert")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_pairs": len(pairs),
 "change_analysis": change_analysis,
 "cluster_analysis": cluster_analysis,
 "numeric_analysis": numeric_analysis,
 "special_analysis": special_analysis
 }
 
 output_file = OUTPUT_DIR / "comprehensive_layer3_layer4_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle umfassenden Report
 report_lines = [
 "# Umfassende Layer-3 → Layer-4 Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 f"**Analysierte Paare**: {len(pairs)}",
 "",
 "## 1. Position-spezifische Änderungen",
 ""
 ]
 
 # Top Positionen nach Stabilität
 change_rates = change_analysis.get("change_rates", {})
 if change_rates:
 sorted_by_stability = sorted(
 change_rates.items(),
 key=lambda x: x[1].get("same_rate", 0),
 reverse=True
 )[:15]
 
 report_lines.append("### Top 15 Positionen nach Stabilität:")
 for pos, rates in sorted_by_stability:
 same_rate = rates.get("same_rate", 0) * 100
 report_lines.append(f"- **Position {pos}**: {same_rate:.1f}% bleiben gleich")
 report_lines.append("")
 
 # Character-Stabilität
 report_lines.extend([
 "## 2. Character-Stabilität",
 "",
 "### Characters die am häufigsten gleich bleiben:"
 ])
 
 char_stability = change_analysis.get("char_stability", {})
 if char_stability:
 stability_scores = []
 for char, stats in char_stability.items():
 total = stats.get("stays", 0) + stats.get("changes", 0)
 if total > 0:
 stability_rate = stats.get("stays", 0) / total
 stability_scores.append((char, stability_rate, stats.get("stays", 0)))
 
 stability_scores.sort(key=lambda x: x[1], reverse=True)
 for char, rate, count in stability_scores[:15]:
 report_lines.append(f"- **{char}**: {rate*100:.1f}% bleiben gleich ({count} Fälle)")
 report_lines.append("")
 
 # Position-Paare
 report_lines.extend([
 "## 3. Position-Paare Stabilität",
 ""
 ])
 
 pair_stability = change_analysis.get("position_pair_stability", {})
 if pair_stability:
 for pair, count in sorted(pair_stability.items(), key=lambda x: x[1], reverse=True):
 rate = count / len(pairs) * 100
 report_lines.append(f"- **Position {pair}**: {rate:.1f}% beide gleich ({count} Fälle)")
 report_lines.append("")
 
 # Numerische Patterns
 report_lines.extend([
 "## 4. Numerische Patterns",
 ""
 ])
 
 numeric = numeric_analysis.get("char_distances", {})
 if numeric:
 report_lines.append(f"- **Durchschnittliche Character-Distanz**: {numeric.get('mean', 0):.2f}")
 report_lines.append(f"- **Median Character-Distanz**: {numeric.get('median', 0):.2f}")
 report_lines.append("")
 
 stability = numeric_analysis.get("position_stability", {})
 if stability:
 report_lines.append(f"- **Durchschnittliche gleiche Positionen pro Paar**: {stability.get('mean', 0):.2f}")
 report_lines.append(f"- **Min**: {stability.get('min', 0)}, **Max**: {stability.get('max', 0)}")
 report_lines.append("")
 
 # Spezielle Positionen
 report_lines.extend([
 "## 5. Spezielle Positionen Detail-Analyse",
 ""
 ])
 
 special = special_analysis
 for pos in [27, 30, 4, 55]:
 if pos in special:
 data = special[pos]
 report_lines.append(f"### Position {pos}:")
 report_lines.append(f"- **Stabilitätsrate**: {data.get('stability_rate', 0)*100:.1f}%")
 if data.get("stable_chars"):
 report_lines.append("- **Stabile Characters (Top 5):**")
 for char, count in list(data["stable_chars"].items())[:5]:
 report_lines.append(f" - {char}: {count} Fälle")
 report_lines.append("")
 
 # Clusters
 report_lines.extend([
 "## 6. Change Pattern Clusters",
 ""
 ])
 
 clusters = cluster_analysis
 report_lines.append(f"- **Unique Patterns**: {clusters.get('unique_patterns', 0)}")
 if clusters.get("most_common_pattern"):
 pattern, count = clusters["most_common_pattern"]
 rate = count / len(pairs) * 100
 report_lines.append(f"- **Häufigstes Pattern**: {rate:.2f}% ({count} Fälle)")
 report_lines.append(f" - Pattern: {pattern[:30]}... (S=same, D=different)")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "comprehensive_layer3_layer4_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

