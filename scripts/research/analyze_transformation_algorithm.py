#!/usr/bin/env python3
"""
Analyze Transformation-Algorithmus: Warum ist Position 27 so stabil?
- Wie funktioniert Layer-3 → Layer-4 Transformation?
- Warum bleibt Position 27 stabiler?
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np

project_root = Path(__file__).parent.parent.parent
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python3"
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def derive_identity_from_seed(seed: str) -> str:
 """Leite Identity aus Seed ab."""
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{seed}"
try:
 seed_bytes = seed.encode('utf-8')
 subseed = get_subseed_from_seed(seed_bytes)
 private_key = get_private_key_from_subseed(subseed)
 public_key = get_public_key_from_private_key(private_key)
 identity = get_identity_from_public_key(public_key)
 print(identity)
except Exception:
 print("")
"""
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=5,
 cwd=project_root
 )
 identity = result.stdout.strip()
 if len(identity) == 60 and identity.isupper():
 return identity
 return ""
 except Exception:
 return ""

def analyze_seed_characteristics(pairs: List[Dict]) -> Dict:
 """Analyze Seed-Charakteristika for stabile vs. changing Positionen."""
 
 # Analyze Position 27 (stabil) vs. Position 30 (nicht stabil)
 pos27_stable_seeds = []
 pos27_changing_seeds = []
 pos30_stable_seeds = []
 pos30_changing_seeds = []
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 seed = identity_to_seed(l3_id)
 
 # Position 27
 if l3_id[27].upper() == l4_id[27].upper():
 pos27_stable_seeds.append(seed)
 else:
 pos27_changing_seeds.append(seed)
 
 # Position 30
 if l3_id[30].upper() == l4_id[30].upper():
 pos30_stable_seeds.append(seed)
 else:
 pos30_changing_seeds.append(seed)
 
 # Analyze Seed-Charakteristika
 def analyze_seed_list(seeds: List[str], name: str) -> Dict:
 if not seeds:
 return {}
 
 # Seed-Länge (sollte immer 55 sein)
 lengths = [len(s) for s in seeds]
 
 # Character Distribution an verschiedenen Positionen
 char_dist_positions = {}
 for pos in [0, 4, 13, 27, 30, 54]:
 chars = Counter()
 for seed in seeds:
 if len(seed) > pos:
 chars[seed[pos].lower()] += 1
 char_dist_positions[pos] = dict(chars.most_common(10))
 
 # Seed-Patterns (wiederholende Muster)
 patterns = Counter()
 for seed in seeds[:1000]: # Sample for Performance
 # Suche nach 3-Character-Patterns
 for i in range(len(seed) - 2):
 pattern = seed[i:i+3]
 patterns[pattern] += 1
 
 return {
 "count": len(seeds),
 "lengths": {
 "mean": np.mean(lengths) if lengths else 0,
 "unique": len(set(lengths))
 },
 "char_distributions": char_dist_positions,
 "top_patterns": dict(patterns.most_common(20))
 }
 
 return {
 "pos27_stable": analyze_seed_list(pos27_stable_seeds, "pos27_stable"),
 "pos27_changing": analyze_seed_list(pos27_changing_seeds, "pos27_changing"),
 "pos30_stable": analyze_seed_list(pos30_stable_seeds, "pos30_stable"),
 "pos30_changing": analyze_seed_list(pos30_changing_seeds, "pos30_changing")
 }

def analyze_transformation_patterns(pairs: List[Dict]) -> Dict:
 """Analyze Transformation-Patterns."""
 
 # Analyze Position 27 Transformation-Patterns
 pos27_transitions = Counter()
 pos27_context = defaultdict(lambda: {"stable": 0, "changing": 0})
 
 # Analyze Context um Position 27 (Position 25-29)
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 
 if len(l3_id) > 29 and len(l4_id) > 29:
 # Position 27 Transition
 pos27_l3 = l3_id[27].upper()
 pos27_l4 = l4_id[27].upper()
 
 if pos27_l3 == pos27_l4:
 # Stabil - analyze Context
 context = "".join([l3_id[i].upper() for i in range(25, 30)])
 pos27_context[context]["stable"] += 1
 else:
 # Changing - Transition
 transition = f"{pos27_l3}->{pos27_l4}"
 pos27_transitions[transition] += 1
 
 context = "".join([l3_id[i].upper() for i in range(25, 30)])
 pos27_context[context]["changing"] += 1
 
 # Analyze Seed-Charakteristika for stabile Position 27
 pos27_stable_seeds = []
 pos27_changing_seeds = []
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 seed = identity_to_seed(l3_id)
 
 if l3_id[27].upper() == l4_id[27].upper():
 pos27_stable_seeds.append({
 "seed": seed,
 "pos27_char": l3_id[27].upper(),
 "context": "".join([l3_id[i].upper() for i in range(25, 30)])
 })
 else:
 pos27_changing_seeds.append({
 "seed": seed,
 "pos27_char_l3": l3_id[27].upper(),
 "pos27_char_l4": l4_id[27].upper(),
 "context": "".join([l3_id[i].upper() for i in range(25, 30)])
 })
 
 return {
 "pos27_transitions": dict(pos27_transitions.most_common(20)),
 "pos27_context": {k: dict(v) for k, v in pos27_context.items() if sum(v.values()) >= 5},
 "pos27_stable_samples": pos27_stable_seeds[:100], # Sample
 "pos27_changing_samples": pos27_changing_seeds[:100] # Sample
 }

def analyze_cryptographic_properties(pairs: List[Dict]) -> Dict:
 """Analyze kryptographische Eigenschaften der Transformation."""
 
 # Analyze ob bestimmte Seed-Patterns zu stabilen Position 27 führen
 # Teste verschiedene Hypothesen
 
 # Hypothese 1: Seed-Position 27 Character beeinflusst Identity-Position 27
 seed_pos27_to_identity_pos27 = defaultdict(lambda: Counter())
 
 # Hypothese 2: Seed-Position 0-4 beeinflusst Identity-Position 27
 seed_early_to_identity_pos27 = defaultdict(lambda: Counter())
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 seed = identity_to_seed(l3_id)
 
 if len(seed) >= 28 and len(l3_id) > 27 and len(l4_id) > 27:
 # Hypothese 1: Seed Position 27
 seed_char_27 = seed[27].lower() if len(seed) > 27 else None
 identity_pos27_l3 = l3_id[27].upper()
 identity_pos27_l4 = l4_id[27].upper()
 
 if seed_char_27:
 if identity_pos27_l3 == identity_pos27_l4:
 seed_pos27_to_identity_pos27[seed_char_27]["stable"] += 1
 else:
 seed_pos27_to_identity_pos27[seed_char_27]["changing"] += 1
 
 # Hypothese 2: Seed Position 0-4
 seed_early = seed[:5].lower()
 if identity_pos27_l3 == identity_pos27_l4:
 seed_early_to_identity_pos27[seed_early]["stable"] += 1
 else:
 seed_early_to_identity_pos27[seed_early]["changing"] += 1
 
 return {
 "seed_pos27_correlation": {
 k: dict(v) for k, v in seed_pos27_to_identity_pos27.items()
 },
 "seed_early_correlation": {
 k: dict(v) for k, v in seed_early_to_identity_pos27.items() if sum(v.values()) >= 10
 }
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("TRANSFORMATION-ALGORITHMUS ANALYSE")
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
 
 # Analyze Seed-Charakteristika
 print("🔍 Analyze Seed-Charakteristika...")
 seed_analysis = analyze_seed_characteristics(pairs)
 print("✅ Seed-Charakteristika analysiert")
 print()
 
 # Analyze Transformation-Patterns
 print("🔍 Analyze Transformation-Patterns...")
 transformation_patterns = analyze_transformation_patterns(pairs)
 print("✅ Transformation-Patterns analysiert")
 print()
 
 # Analyze kryptographische Eigenschaften
 print("🔍 Analyze kryptographische Eigenschaften...")
 crypto_properties = analyze_cryptographic_properties(pairs)
 print("✅ Kryptographische Eigenschaften analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Position 27 vs. 30 Seed-Charakteristika
 pos27_stable = seed_analysis.get("pos27_stable", {})
 pos27_changing = seed_analysis.get("pos27_changing", {})
 
 if pos27_stable and pos27_changing:
 print("📊 Position 27 Seed-Charakteristika:")
 print(f" Stabile Fälle: {pos27_stable.get('count', 0)}")
 print(f" Changing Fälle: {pos27_changing.get('count', 0)}")
 print()
 
 # Transformation-Patterns
 pos27_transitions = transformation_patterns.get("pos27_transitions", {})
 if pos27_transitions:
 print("📊 Top Position 27 Transitions:")
 for transition, count in list(pos27_transitions.items())[:10]:
 print(f" {transition}: {count} Fälle")
 print()
 
 # Kryptographische Eigenschaften
 seed_pos27_corr = crypto_properties.get("seed_pos27_correlation", {})
 if seed_pos27_corr:
 print("📊 Seed Position 27 → Identity Position 27 Korrelation:")
 for seed_char, stats in list(seed_pos27_corr.items())[:10]:
 stable = stats.get("stable", 0)
 changing = stats.get("changing", 0)
 total = stable + changing
 if total > 0:
 stable_rate = stable / total * 100
 print(f" Seed '{seed_char}': {stable_rate:.1f}% stabil ({stable}/{total})")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "seed_analysis": seed_analysis,
 "transformation_patterns": transformation_patterns,
 "crypto_properties": crypto_properties
 }
 
 output_file = OUTPUT_DIR / "transformation_algorithm_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Transformation-Algorithmus Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Position 27 vs. Position 30 Seed-Charakteristika",
 ""
 ]
 
 if pos27_stable and pos27_changing:
 report_lines.extend([
 f"- **Position 27 stabile Fälle**: {pos27_stable.get('count', 0)}",
 f"- **Position 27 changing Fälle**: {pos27_changing.get('count', 0)}",
 ""
 ])
 
 if pos27_transitions:
 report_lines.extend([
 "## Top Position 27 Transitions",
 ""
 ])
 for transition, count in list(pos27_transitions.items())[:10]:
 report_lines.append(f"- **{transition}**: {count} Fälle")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "transformation_algorithm_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

