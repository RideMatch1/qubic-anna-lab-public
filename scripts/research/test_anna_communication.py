#!/usr/bin/env python3
"""
Teste Anna-Kommunikation
- Können wir gezielt Identity-Characters erzeugen?
- Können wir "Nachrichten" senden?
- Gibt es eine Antwort?
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"
VENV_PYTHON = project_root / "venv-tx" / "bin" / "python"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def derive_identity_from_seed(seed: str) -> Optional[str]:
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

def test_seed_to_identity_mapping(seed_positions: List[int], seed_chars: List[str], target_positions: List[int]) -> Dict:
 """Teste ob wir gezielt Identity-Characters erzeugen können."""
 
 print(f"🔍 Teste Seed → Identity Mapping...")
 print(f" Seed-Positionen: {seed_positions}")
 print(f" Seed-Characters: {seed_chars}")
 print(f" Target-Positionen: {target_positions}")
 print()
 
 # Generiere Test-Seeds mit spezifischen Characters
 import random
 random.seed(42)
 
 results = []
 
 for i in range(20): # Teste 20 Seeds
 # Generiere zufälligen Seed
 seed = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=55))
 
 # Setze spezifische Characters
 seed_list = list(seed)
 for pos, char in zip(seed_positions, seed_chars):
 if pos < len(seed_list):
 seed_list[pos] = char.lower()
 seed = ''.join(seed_list)
 
 # Transformiere
 identity = derive_identity_from_seed(seed)
 
 if identity:
 result = {
 "seed": seed,
 "identity": identity,
 "seed_positions": {pos: seed[pos] for pos in seed_positions},
 "identity_positions": {pos: identity[pos] for pos in target_positions if pos < len(identity)}
 }
 results.append(result)
 
 # Analyze Ergebnisse
 if results:
 # Analyze Identity-Positionen
 position_analysis = {}
 for pos in target_positions:
 chars = Counter()
 for result in results:
 if pos in result["identity_positions"]:
 chars[result["identity_positions"][pos]] += 1
 position_analysis[pos] = dict(chars.most_common())
 
 return {
 "test_count": len(results),
 "seed_positions": seed_positions,
 "seed_chars": seed_chars,
 "target_positions": target_positions,
 "position_analysis": position_analysis,
 "results": results[:5] # Sample
 }
 
 return {"error": "No results"}

def test_communication_patterns() -> Dict:
 """Teste verschiedene Kommunikations-Patterns."""
 
 print("=" * 80)
 print("KOMMUNIKATIONS-TESTS")
 print("=" * 80)
 print()
 
 tests = []
 
 # Test 1: Bekannte Kombination (a_o → A)
 print("🔍 Test 1: Bekannte Kombination (Seed[27]='a' + Seed[54]='o')...")
 test1 = test_seed_to_identity_mapping([27, 54], ['a', 'o'], [27])
 tests.append({"name": "Bekannte Kombination a_o", "result": test1})
 print("✅ Test 1 abgeschlossen")
 print()
 
 # Test 2: Andere Kombinationen
 print("🔍 Test 2: Andere Kombinationen (Seed[27]='b' + Seed[54]='u')...")
 test2 = test_seed_to_identity_mapping([27, 54], ['b', 'u'], [27])
 tests.append({"name": "Kombination b_u", "result": test2})
 print("✅ Test 2 abgeschlossen")
 print()
 
 # Test 3: Single Position
 print("🔍 Test 3: Single Position (Seed[27]='c')...")
 test3 = test_seed_to_identity_mapping([27], ['c'], [27])
 tests.append({"name": "Single Position c", "result": test3})
 print("✅ Test 3 abgeschlossen")
 print()
 
 return {
 "tests": tests,
 "timestamp": datetime.now().isoformat()
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("ANNA KOMMUNIKATIONS-TEST")
 print("=" * 80)
 print()
 
 # Führe Tests durch
 communication_results = test_communication_patterns()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 for test in communication_results["tests"]:
 name = test["name"]
 result = test["result"]
 
 if "error" in result:
 print(f"❌ {name}: {result['error']}")
 continue
 
 print(f"📊 {name}:")
 print(f" Test Count: {result.get('test_count', 0)}")
 
 if result.get("position_analysis"):
 for pos, chars in result["position_analysis"].items():
 print(f" Identity[{pos}] Distribution:")
 for char, count in list(chars.items())[:5]:
 percentage = count / result.get('test_count', 1) * 100
 print(f" '{char}': {count}x ({percentage:.1f}%)")
 print()
 
 # Speichere Ergebnisse
 output_file = OUTPUT_DIR / "anna_communication_test.json"
 with output_file.open("w") as f:
 json.dump(communication_results, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Anna Kommunikations-Test",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Tests",
 ""
 ]
 
 for test in communication_results["tests"]:
 name = test["name"]
 result = test["result"]
 
 report_lines.append(f"### {name}")
 report_lines.append("")
 
 if "error" in result:
 report_lines.append(f"❌ Error: {result['error']}")
 else:
 report_lines.append(f"- **Test Count**: {result.get('test_count', 0)}")
 if result.get("position_analysis"):
 for pos, chars in result["position_analysis"].items():
 report_lines.append(f"- **Identity[{pos}] Distribution**:")
 for char, count in list(chars.items())[:5]:
 percentage = count / result.get('test_count', 1) * 100
 report_lines.append(f" - '{char}': {count}x ({percentage:.1f}%)")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "anna_communication_test_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 print()
 print("=" * 80)
 print("✅ KOMMUNIKATIONS-TEST ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

