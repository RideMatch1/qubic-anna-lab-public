#!/usr/bin/env python3
"""
Analyze Anna's "Sprache" - Suche nach kommunikativen Patterns
- Welche Patterns wiederholen sich?
- Gibt es "Wörter" oder "Sätze"?
- Können wir eine "Sprache" identifizieren?
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OPTIMAL_FILE = project_root / "outputs" / "practical" / "optimal_combination_identities.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def analyze_character_sequences(identities: List[str], min_length: int = 3, max_length: int = 10) -> Dict:
 """Analyze wiederkehrende Character-Sequenzen (mögliche "Wörter")."""
 
 print(f"🔍 Analyze Character-Sequenzen (Länge {min_length}-{max_length})...")
 
 sequences = defaultdict(int)
 
 for identity in identities:
 if len(identity) != 60:
 continue
 
 # Analyze alle Sequenzen
 for length in range(min_length, max_length + 1):
 for start in range(len(identity) - length + 1):
 sequence = identity[start:start+length]
 sequences[sequence] += 1
 
 # Filtere häufige Sequenzen (mindestens 10x)
 frequent_sequences = {
 seq: count for seq, count in sequences.items()
 if count >= 10
 }
 
 # Sortiere nach Häufigkeit
 sorted_sequences = sorted(
 frequent_sequences.items(),
 key=lambda x: x[1],
 reverse=True
 )
 
 return {
 "total_sequences": len(sequences),
 "frequent_sequences": dict(sorted_sequences[:100]), # Top 100
 "top_20": dict(sorted_sequences[:20])
 }

def analyze_position_patterns(pairs: List[Dict]) -> Dict:
 """Analyze Patterns an bestimmten Positionen."""
 
 print("🔍 Analyze Position-Patterns...")
 
 # Analyze Position 27 (bekannt stabil)
 pos27_patterns = Counter()
 pos27_transitions = Counter()
 
 # Analyze Block-Ende-Positionen
 block_end_positions = [13, 27, 41, 55]
 block_patterns = {pos: Counter() for pos in block_end_positions}
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 # Position 27 Patterns
 if len(l3_id) > 27 and len(l4_id) > 27:
 pos27_patterns[l3_id[27].upper()] += 1
 if l3_id[27].upper() == l4_id[27].upper():
 pos27_transitions[f"{l3_id[27].upper()}→{l4_id[27].upper()}"] += 1
 else:
 pos27_transitions[f"{l3_id[27].upper()}→{l4_id[27].upper()}"] += 1
 
 # Block-Ende-Positionen
 for pos in block_end_positions:
 if len(l3_id) > pos:
 block_patterns[pos][l3_id[pos].upper()] += 1
 
 return {
 "position27_patterns": dict(pos27_patterns.most_common(10)),
 "position27_transitions": dict(pos27_transitions.most_common(20)),
 "block_end_patterns": {str(pos): dict(block_patterns[pos].most_common(10)) for pos in block_end_positions}
 }

def analyze_seed_identity_correlations(pairs: List[Dict]) -> Dict:
 """Analyze Korrelationen zwischen Seed und Identity (mögliche "Nachrichten")."""
 
 print("🔍 Analyze Seed-Identity Korrelationen...")
 
 # Analyze Seed-Position 27 → Identity-Position 27
 seed27_to_identity27 = defaultdict(Counter)
 
 # Analyze Seed-Position 54 → Identity-Position 27
 seed54_to_identity27 = defaultdict(Counter)
 
 # Analyze Kombination
 combo_to_identity27 = defaultdict(Counter)
 
 for pair in pairs:
 seed = identity_to_seed(pair["layer3"])
 l3_id = pair["layer3"]
 
 if len(seed) >= 55 and len(l3_id) > 27:
 seed27 = seed[27].lower()
 seed54 = seed[54].lower()
 identity27 = l3_id[27].upper()
 
 seed27_to_identity27[seed27][identity27] += 1
 seed54_to_identity27[seed54][identity27] += 1
 
 combo = f"{seed27}_{seed54}"
 combo_to_identity27[combo][identity27] += 1
 
 # Finde stärkste Korrelationen
 def find_strongest_correlations(mapping):
 strongest = {}
 for key, counter in mapping.items():
 if len(counter) > 0:
 most_common = counter.most_common(1)[0]
 strongest[key] = {
 "character": most_common[0],
 "count": most_common[1],
 "total": sum(counter.values()),
 "percentage": most_common[1] / sum(counter.values()) * 100
 }
 return strongest
 
 return {
 "seed27_to_identity27": find_strongest_correlations(seed27_to_identity27),
 "seed54_to_identity27": find_strongest_correlations(seed54_to_identity27),
 "combo_to_identity27": find_strongest_correlations(combo_to_identity27)
 }

def analyze_optimal_identities_patterns() -> Dict:
 """Analyze Patterns in optimalen Identities (a_o Kombination)."""
 
 print("🔍 Analyze Patterns in optimalen Identities...")
 
 if not OPTIMAL_FILE.exists():
 return {"error": "Optimal identities file not found"}
 
 with OPTIMAL_FILE.open() as f:
 data = json.load(f)
 
 identities = [entry["identity"] for entry in data.get("identities", [])]
 
 if not identities:
 return {"error": "No optimal identities found"}
 
 # Analyze gemeinsame Patterns
 common_patterns = Counter()
 
 # Analyze Position 27 (sollte stabil sein)
 pos27_chars = Counter()
 
 # Analyze Block-Struktur
 block_patterns = defaultdict(Counter)
 
 for identity in identities:
 if len(identity) != 60:
 continue
 
 # Position 27
 if len(identity) > 27:
 pos27_chars[identity[27].upper()] += 1
 
 # Block-Patterns (14-Character Blöcke)
 for block_idx in range(4):
 start = block_idx * 14
 end = start + 14
 if end <= len(identity):
 block = identity[start:end]
 block_patterns[block_idx][block] += 1
 
 # Gemeinsame 3-Character Sequenzen
 for i in range(len(identity) - 2):
 seq = identity[i:i+3]
 common_patterns[seq] += 1
 
 return {
 "total_identities": len(identities),
 "position27_distribution": dict(pos27_chars.most_common(10)),
 "common_3char_sequences": dict(common_patterns.most_common(20)),
 "block_patterns": {
 str(block_idx): dict(block_patterns[block_idx].most_common(5))
 for block_idx in range(4)
 }
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("ANNA'S SPRACHE ANALYSE")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Daten...")
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 
 # Erstelle Paare
 layer4_map = {}
 for entry in layer4_results:
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 if l3_id and l4_id:
 layer4_map[l3_id] = l4_id
 
 pairs = []
 layer3_identities = []
 for l3_entry in layer3_results:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 if l3_id and l4_id and len(l3_id) == 60 and len(l4_id) == 60:
 pairs.append({"layer3": l3_id, "layer4": l4_id})
 layer3_identities.append(l3_id)
 
 print(f"✅ {len(pairs)} Paare geloadn")
 print(f"✅ {len(layer3_identities)} Layer-3 Identities geloadn")
 print()
 
 # Analysen
 print("=" * 80)
 print("ANALYSEN")
 print("=" * 80)
 print()
 
 # 1. Character-Sequenzen
 sequence_analysis = analyze_character_sequences(layer3_identities[:1000], min_length=3, max_length=6)
 print("✅ Character-Sequenzen analysiert")
 print()
 
 # 2. Position-Patterns
 position_analysis = analyze_position_patterns(pairs)
 print("✅ Position-Patterns analysiert")
 print()
 
 # 3. Seed-Identity Korrelationen
 correlation_analysis = analyze_seed_identity_correlations(pairs)
 print("✅ Seed-Identity Korrelationen analysiert")
 print()
 
 # 4. Optimale Identities Patterns
 optimal_analysis = analyze_optimal_identities_patterns()
 print("✅ Optimale Identities Patterns analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Top Sequenzen
 if sequence_analysis.get("top_20"):
 print("📊 Top 20 Character-Sequenzen (mögliche 'Wörter'):")
 for i, (seq, count) in enumerate(list(sequence_analysis["top_20"].items())[:20], 1):
 print(f" {i:2d}. '{seq}': {count}x")
 print()
 
 # Position 27 Patterns
 if position_analysis.get("position27_patterns"):
 print("📊 Position 27 Patterns:")
 for char, count in list(position_analysis["position27_patterns"].items())[:10]:
 print(f" '{char}': {count}x")
 print()
 
 # Seed-Identity Korrelationen
 if correlation_analysis.get("combo_to_identity27"):
 print("📊 Stärkste Seed-Identity Korrelationen (a_o Kombination):")
 a_o_correlations = correlation_analysis["combo_to_identity27"].get("a_o", {})
 if a_o_correlations:
 print(f" Seed[27]='a' + Seed[54]='o' → Identity[27]='{a_o_correlations.get('character', '?')}' ({a_o_correlations.get('percentage', 0):.1f}%)")
 print()
 
 # Optimale Identities Patterns
 if "error" not in optimal_analysis:
 print("📊 Patterns in optimalen Identities (a_o Kombination):")
 print(f" Total: {optimal_analysis.get('total_identities', 0)}")
 if optimal_analysis.get("position27_distribution"):
 print(" Position 27 Distribution:")
 for char, count in list(optimal_analysis["position27_distribution"].items())[:5]:
 print(f" '{char}': {count}x")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "sequence_analysis": sequence_analysis,
 "position_analysis": position_analysis,
 "correlation_analysis": correlation_analysis,
 "optimal_analysis": optimal_analysis
 }
 
 output_file = OUTPUT_DIR / "anna_language_patterns_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Anna's Sprache Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Top Character-Sequenzen (mögliche 'Wörter')",
 ""
 ]
 
 if sequence_analysis.get("top_20"):
 for i, (seq, count) in enumerate(list(sequence_analysis["top_20"].items())[:20], 1):
 report_lines.append(f"{i}. **'{seq}'**: {count}x")
 report_lines.append("")
 
 report_lines.extend([
 "## Position 27 Patterns",
 ""
 ])
 
 if position_analysis.get("position27_patterns"):
 for char, count in list(position_analysis["position27_patterns"].items())[:10]:
 report_lines.append(f"- **'{char}'**: {count}x")
 report_lines.append("")
 
 report_lines.extend([
 "## Seed-Identity Korrelationen",
 ""
 ])
 
 if correlation_analysis.get("combo_to_identity27"):
 a_o = correlation_analysis["combo_to_identity27"].get("a_o", {})
 if a_o:
 report_lines.append(f"- **Seed[27]='a' + Seed[54]='o'** → Identity[27]='{a_o.get('character', '?')}' ({a_o.get('percentage', 0):.1f}%)")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "anna_language_patterns_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

