#!/usr/bin/env python3
"""
Analyze warum neue Seeds nicht 100% funktionieren
- Vergleiche existierende vs. neue Seeds
- Finde alle beeinflussenden Faktoren
- KEINE Spekulationen - nur echte Daten!
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def derive_identity_from_seed(seed: str) -> str:
 """Leite Identity aus Seed ab."""
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

def analyze_existing_seeds_pattern(seed_char: str, target_char: str) -> Dict:
 """Analyze Pattern in existierenden Seeds."""
 
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 matching_seeds = []
 position_distributions = defaultdict(Counter)
 
 for entry in layer3_results:
 identity = entry.get("layer3_identity", "")
 if len(identity) != 60:
 continue
 
 seed = identity_to_seed(identity)
 if len(seed) >= 55:
 if seed[27].lower() == seed_char.lower():
 if identity[27].upper() == target_char.upper():
 matching_seeds.append(seed)
 
 # Analyze alle anderen Positionen
 for pos in range(55):
 if pos != 27:
 position_distributions[pos][seed[pos]] += 1
 
 # Finde häufigste Characters an jeder Position
 most_common_by_position = {}
 for pos, counter in position_distributions.items():
 if counter:
 most_common = counter.most_common(1)[0]
 total = sum(counter.values())
 most_common_by_position[pos] = {
 "char": most_common[0],
 "count": most_common[1],
 "total": total,
 "rate": most_common[1] / total if total > 0 else 0
 }
 
 return {
 "seed_char": seed_char,
 "target_char": target_char,
 "total_seeds": len(matching_seeds),
 "position_patterns": most_common_by_position
 }

def test_new_seed_with_pattern(seed_char: str, target_char: str, pattern: Dict, count: int = 20) -> Dict:
 """Teste neue Seeds mit gefundenem Pattern."""
 
 import random
 
 results = []
 
 for i in range(count):
 # Generiere Seed mit Pattern
 seed_list = ['a'] * 55 # Default
 
 # Setze Seed[27]
 seed_list[27] = seed_char.lower()
 
 # Setze andere Positionen basierend auf Pattern
 for pos, data in pattern.get("position_patterns", {}).items():
 if data["rate"] > 0.5: # Nur wenn >50% Häufigkeit
 seed_list[pos] = data["char"]
 
 # Fülle Rest zufällig
 for pos in range(55):
 if pos != 27 and pos not in pattern.get("position_patterns", {}):
 seed_list[pos] = random.choice('abcdefghijklmnopqrstuvwxyz')
 
 seed = ''.join(seed_list)
 
 # Transformiere
 identity = derive_identity_from_seed(seed)
 
 if identity:
 success = len(identity) > 27 and identity[27].upper() == target_char.upper()
 results.append({
 "seed": seed,
 "identity": identity,
 "success": success,
 "identity_27": identity[27] if len(identity) > 27 else None
 })
 
 success_count = sum(1 for r in results if r.get("success", False))
 success_rate = success_count / len(results) * 100 if results else 0
 
 return {
 "tested_count": len(results),
 "success_count": success_count,
 "success_rate": success_rate,
 "results": results[:10] # Sample
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("ANALYSE: WARUM FUNKTIONIEREN NEUE SEEDS NICHT 100%?")
 print("=" * 80)
 print()
 print("⚠️ KEINE SPEKULATIONEN - NUR ECHTE DATEN!")
 print()
 
 # Analyze existierende Seeds
 print("🔍 Analyze existierende Seeds...")
 print()
 
 test_cases = [
 ("a", "A"),
 ("b", "B"),
 ("c", "C"),
 ("d", "D")
 ]
 
 analysis_results = {}
 
 for seed_char, target_char in test_cases:
 print(f" Analyze Seed[27]='{seed_char}' → Identity[27]='{target_char}'...")
 pattern = analyze_existing_seeds_pattern(seed_char, target_char)
 analysis_results[seed_char] = pattern
 print(f" ✅ {pattern['total_seeds']} Seeds gefunden")
 print(f" ✅ {len(pattern['position_patterns'])} Positionen mit Patterns")
 print()
 
 # Zeige Top Patterns
 print("=" * 80)
 print("GEFUNDENE PATTERNS")
 print("=" * 80)
 print()
 
 for seed_char, pattern in analysis_results.items():
 print(f"📊 Seed[27]='{seed_char}' Patterns:")
 
 # Sortiere nach Rate
 sorted_positions = sorted(
 pattern["position_patterns"].items(),
 key=lambda x: x[1]["rate"],
 reverse=True
 )
 
 print(f" Top 10 Positionen (nach Häufigkeit):")
 for pos, data in sorted_positions[:10]:
 print(f" Seed[{pos:2d}]='{data['char']}': {data['rate']*100:.1f}% ({data['count']}/{data['total']})")
 print()
 
 # Teste neue Seeds mit Patterns
 print("=" * 80)
 print("TESTE NEUE SEEDS MIT PATTERNS")
 print("=" * 80)
 print()
 
 test_results = {}
 
 for seed_char, target_char in test_cases:
 print(f"🔍 Teste neue Seeds: Seed[27]='{seed_char}' → Identity[27]='{target_char}'...")
 pattern = analysis_results[seed_char]
 test_result = test_new_seed_with_pattern(seed_char, target_char, pattern, count=5) # Reduziert for Geschwindigkeit
 test_results[seed_char] = test_result
 
 success_rate = test_result["success_rate"]
 marker = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
 print(f" {marker} Erfolgsrate: {success_rate:.1f}% ({test_result['success_count']}/{test_result['tested_count']})")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "analysis_results": analysis_results,
 "test_results": test_results
 }
 
 output_file = OUTPUT_DIR / "why_new_seeds_fail_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Analyse: Warum funktionieren neue Seeds nicht 100%?",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Erkenntnisse",
 "",
 "### Existierende Seeds Patterns",
 ""
 ]
 
 for seed_char, pattern in analysis_results.items():
 report_lines.append(f"**Seed[27]='{seed_char}'**: {pattern['total_seeds']} Seeds gefunden")
 report_lines.append("")
 
 sorted_positions = sorted(
 pattern["position_patterns"].items(),
 key=lambda x: x[1]["rate"],
 reverse=True
 )
 
 report_lines.append("Top 10 Positionen:")
 for pos, data in sorted_positions[:10]:
 report_lines.append(f"- Seed[{pos}]='{data['char']}': {data['rate']*100:.1f}% ({data['count']}/{data['total']})")
 report_lines.append("")
 
 report_lines.extend([
 "### Test neue Seeds mit Patterns",
 ""
 ])
 
 for seed_char, result in test_results.items():
 success_rate = result["success_rate"]
 report_lines.append(f"**Seed[27]='{seed_char}'**: {success_rate:.1f}% Erfolgsrate ({result['success_count']}/{result['tested_count']})")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "why_new_seeds_fail_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

