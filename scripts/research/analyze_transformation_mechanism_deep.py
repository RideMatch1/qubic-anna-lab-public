#!/usr/bin/env python3
"""
Tiefe Analyse: Transformation-Mechanismus verstehen
- Wie genau funktioniert Seed → Identity Transformation?
- Warum beeinflusst Seed-Position 27 Identity-Position 27?
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import subprocess

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def derive_identity_from_seed(seed: str) -> str:
 """Leite Identity aus Seed ab (for Tests)."""
 if not VENV_PYTHON.exists():
 return None
 
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{seed}"
seed_bytes = seed.encode('utf-8')
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
print(identity)
"""
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=5,
 cwd=project_root
 )
 
 if result.returncode != 0:
 return None
 
 identity = result.stdout.strip()
 if len(identity) == 60 and identity.isupper():
 return identity
 return None
 except Exception:
 return None

def analyze_seed_character_impact(pairs: List[Dict], seed_position: int) -> Dict:
 """Analyze wie Seed-Character an Position X Identity-Position 27 beeinflusst."""
 
 char_impact = defaultdict(lambda: {"stable": 0, "changing": 0, "identity_chars": Counter()})
 
 for pair in pairs:
 seed = identity_to_seed(pair["layer3"])
 if len(seed) > seed_position:
 seed_char = seed[seed_position].lower()
 stable = pair["layer3"][27].upper() == pair["layer4"][27].upper()
 
 if stable:
 char_impact[seed_char]["stable"] += 1
 char_impact[seed_char]["identity_chars"][pair["layer3"][27].upper()] += 1
 else:
 char_impact[seed_char]["changing"] += 1
 
 # Berechne Raten
 char_rates = {}
 for char, stats in char_impact.items():
 total = stats["stable"] + stats["changing"]
 if total >= 10:
 rate = stats["stable"] / total
 char_rates[char] = {
 "rate": rate,
 "stable": stats["stable"],
 "changing": stats["changing"],
 "total": total,
 "top_identity_chars": dict(stats["identity_chars"].most_common(5))
 }
 
 return char_rates

def analyze_seed_to_identity_mapping(pairs: List[Dict], sample_size: int = 100) -> Dict:
 """Analyze direkte Mapping zwischen Seed und Identity."""
 
 # Sample for detaillierte Analyse
 sample_pairs = pairs[:sample_size]
 
 mappings = {
 "seed_pos27_to_identity_pos27": defaultdict(Counter),
 "seed_pos54_to_identity_pos27": defaultdict(Counter),
 "seed_pos27_54_to_identity_pos27": defaultdict(Counter)
 }
 
 for pair in sample_pairs:
 seed = identity_to_seed(pair["layer3"])
 if len(seed) >= 55:
 seed27 = seed[27].lower()
 seed54 = seed[54].lower()
 identity27_l3 = pair["layer3"][27].upper()
 identity27_l4 = pair["layer4"][27].upper()
 
 # Seed[27] → Identity[27]
 mappings["seed_pos27_to_identity_pos27"][seed27][identity27_l3] += 1
 
 # Seed[54] → Identity[27]
 mappings["seed_pos54_to_identity_pos27"][seed54][identity27_l3] += 1
 
 # Kombination
 combo = f"{seed27}_{seed54}"
 mappings["seed_pos27_54_to_identity_pos27"][combo][identity27_l3] += 1
 
 # Konvertiere zu dict
 result = {}
 for key, mapping in mappings.items():
 result[key] = {
 k: dict(v.most_common(5)) for k, v in mapping.items()
 }
 
 return result

def test_seed_character_variations(pairs: List[Dict]) -> Dict:
 """Teste wie Variationen in Seed-Characters Identity beeinflussen."""
 
 # Finde Paare mit Seed[27]='a' + Seed[54]='o'
 matching_pairs = []
 for pair in pairs:
 seed = identity_to_seed(pair["layer3"])
 if len(seed) >= 55 and seed[27].lower() == 'a' and seed[54].lower() == 'o':
 matching_pairs.append(pair)
 
 if len(matching_pairs) < 10:
 return {"error": "Not enough matching pairs"}
 
 # Analyze Variationen
 variations = {
 "seed_positions": defaultdict(Counter),
 "identity_positions": defaultdict(Counter),
 "transitions": []
 }
 
 for pair in matching_pairs[:50]: # Sample
 seed = identity_to_seed(pair["layer3"])
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 # Seed-Positionen
 for pos in [0, 4, 13, 27, 30, 54]:
 if len(seed) > pos:
 variations["seed_positions"][pos][seed[pos].lower()] += 1
 
 # Identity-Positionen
 for pos in [13, 27, 41, 55]:
 if len(l3_id) > pos:
 variations["identity_positions"][pos][l3_id[pos].upper()] += 1
 
 # Transitions Position 27
 if len(l3_id) > 27 and len(l4_id) > 27:
 transition = f"{l3_id[27].upper()}→{l4_id[27].upper()}"
 variations["transitions"].append(transition)
 
 # Zusammenfassung
 result = {
 "matching_pairs_count": len(matching_pairs),
 "seed_positions": {str(k): dict(v.most_common(5)) for k, v in variations["seed_positions"].items()},
 "identity_positions": {str(k): dict(v.most_common(5)) for k, v in variations["identity_positions"].items()},
 "top_transitions": dict(Counter(variations["transitions"]).most_common(10))
 }
 
 return result

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("TIEFE ANALYSE: TRANSFORMATION-MECHANISMUS")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Layer-3 und Layer-4 Daten...")
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
 for l3_entry in layer3_results:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 if l3_id and l4_id and len(l3_id) == 60 and len(l4_id) == 60:
 pairs.append({"layer3": l3_id, "layer4": l4_id})
 
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Analysen
 print("🔍 Analyze Seed-Character Impact (Position 27)...")
 seed27_impact = analyze_seed_character_impact(pairs, 27)
 print("✅ Seed-Position 27 Impact analysiert")
 print()
 
 print("🔍 Analyze Seed-Character Impact (Position 54)...")
 seed54_impact = analyze_seed_character_impact(pairs, 54)
 print("✅ Seed-Position 54 Impact analysiert")
 print()
 
 print("🔍 Analyze Seed → Identity Mapping...")
 mapping_analysis = analyze_seed_to_identity_mapping(pairs, sample_size=200)
 print("✅ Mapping analysiert")
 print()
 
 print("🔍 Teste Seed Character Variations...")
 variations = test_seed_character_variations(pairs)
 print("✅ Variations getestet")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Seed-Position 27 Impact
 if seed27_impact:
 print("📊 Seed-Position 27 Impact auf Identity-Position 27:")
 sorted_impact = sorted(seed27_impact.items(), key=lambda x: x[1]["rate"], reverse=True)
 for char, stats in sorted_impact[:10]:
 rate = stats["rate"] * 100
 print(f" Seed[27]='{char}': {rate:.1f}% ({stats['stable']}/{stats['total']})")
 print()
 
 # Seed-Position 54 Impact
 if seed54_impact:
 print("📊 Seed-Position 54 Impact auf Identity-Position 27:")
 sorted_impact = sorted(seed54_impact.items(), key=lambda x: x[1]["rate"], reverse=True)
 for char, stats in sorted_impact[:10]:
 rate = stats["rate"] * 100
 print(f" Seed[54]='{char}': {rate:.1f}% ({stats['stable']}/{stats['total']})")
 print()
 
 # Variations
 if "error" not in variations:
 print("📊 Seed Character Variations (Seed[27]='a' + Seed[54]='o'):")
 print(f" Matching Pairs: {variations['matching_pairs_count']}")
 print(f" Top Transitions: {list(variations['top_transitions'].keys())[:5]}")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "seed27_impact": seed27_impact,
 "seed54_impact": seed54_impact,
 "mapping_analysis": mapping_analysis,
 "variations": variations
 }
 
 output_file = OUTPUT_DIR / "transformation_mechanism_deep_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Transformation-Mechanismus Tiefe Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Seed-Position 27 Impact",
 ""
 ]
 
 if seed27_impact:
 sorted_impact = sorted(seed27_impact.items(), key=lambda x: x[1]["rate"], reverse=True)
 for char, stats in sorted_impact[:10]:
 rate = stats["rate"] * 100
 report_lines.append(f"- **Seed[27]='{char}'**: {rate:.1f}% ({stats['stable']}/{stats['total']})")
 report_lines.append("")
 
 report_lines.extend([
 "## Seed-Position 54 Impact",
 ""
 ])
 
 if seed54_impact:
 sorted_impact = sorted(seed54_impact.items(), key=lambda x: x[1]["rate"], reverse=True)
 for char, stats in sorted_impact[:10]:
 rate = stats["rate"] * 100
 report_lines.append(f"- **Seed[54]='{char}'**: {rate:.1f}% ({stats['stable']}/{stats['total']})")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "transformation_mechanism_deep_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

