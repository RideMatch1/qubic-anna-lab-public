#!/usr/bin/env python3
"""
Kritische Validierung der gefundenen Wörter
- Sind die Wörter wirklich "Nachrichten" oder nur zufällige Sequenzen?
- Vergleich mit zufälligen Daten
- Statistische Signifikanz checkn
"""

import json
import sys
import random
from pathlib import Path
from typing import Dict, List
from collections import Counter
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

ANALYSIS_FILE = project_root / "outputs" / "derived" / "comprehensive_word_analysis.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def generate_random_identity() -> str:
 """Generiere zufällige Identity (60 Zeichen, A-Z)."""
 return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=60))

def find_words_in_random_data(num_identities: int, words: List[str]) -> Dict[str, int]:
 """Finde Wörter in zufälligen Daten."""
 found = Counter()
 
 for _ in range(num_identities):
 identity = generate_random_identity()
 identity_upper = identity.upper()
 
 for word in words:
 if word in identity_upper:
 found[word] += 1
 
 return dict(found)

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("KRITISCHE VALIDIERUNG DER GEFUNDENEN WÖRTER")
 print("=" * 80)
 print()
 print("⚠️ PRÜFE OB WÖRTER WIRKLICH 'NACHRICHTEN' SIND!")
 print()
 
 # Load Analyse-Ergebnisse
 if not ANALYSIS_FILE.exists():
 print(f"❌ Analyse-Datei nicht gefunden: {ANALYSIS_FILE}")
 print(" Führe zuerst comprehensive_word_analysis.py aus")
 return
 
 with ANALYSIS_FILE.open() as f:
 analysis_data = json.load(f)
 
 found_words = analysis_data.get("found_words", {})
 analysis = analysis_data.get("analysis", {})
 found_words_analysis = analysis.get("found_words", {})
 total_identities = analysis_data.get("total_identities", 0)
 
 print(f"📊 Analyze {len(found_words)} gefundene Wörter")
 print(f"📊 Total Identities: {total_identities}")
 print()
 
 # Wichtige Wörter for Vergleich
 important_words = ["ANNA", "HELLO", "HI", "HERE", "STOP", "WAS", "TEST"]
 found_important = {}
 for word in important_words:
 if word in found_words_analysis:
 # found_words_analysis[word] ist ein Dict mit "count", "expected_random", etc.
 found_important[word] = found_words_analysis[word]
 elif word in found_words:
 # found_words[word] ist eine Liste von Vorkommen
 count = len(found_words[word])
 found_important[word] = {"count": count}
 
 print("🔍 Teste gegen zufällige Daten...")
 print()
 
 # Generiere zufällige Daten und vergleiche
 random_results = find_words_in_random_data(total_identities, important_words)
 
 print("📊 Vergleich: Echte Daten vs. Zufällige Daten")
 print()
 print(f"{'Wort':<10} {'Echte Daten':<15} {'Zufällig':<15} {'Ratio':<10} {'Signifikant':<12}")
 print("-" * 70)
 
 significant_words = []
 not_significant_words = []
 
 for word in important_words:
 real_count = found_important.get(word, {}).get("count", 0)
 random_count = random_results.get(word, 0)
 
 if random_count > 0:
 ratio = real_count / random_count
 is_significant = ratio > 2.0
 else:
 ratio = float('inf') if real_count > 0 else 0
 is_significant = real_count > 0
 
 marker = "✅" if is_significant else "❌"
 print(f"{word:<10} {real_count:<15} {random_count:<15} {ratio:<10.2f} {marker}")
 
 if is_significant:
 significant_words.append(word)
 else:
 not_significant_words.append(word)
 
 print()
 
 # Analyze Positionen
 print("🔍 Analyze Positionen der Wörter...")
 print()
 
 position_analysis = {}
 
 for word, data in found_important.items():
 examples = data.get("examples", [])
 positions = [ex.get("position", -1) for ex in examples]
 
 if positions:
 position_analysis[word] = {
 "positions": positions,
 "avg_position": sum(positions) / len(positions),
 "position_range": (min(positions), max(positions))
 }
 
 print("📊 Position-Analyse:")
 for word, analysis in position_analysis.items():
 print(f" '{word}':")
 print(f" Durchschnittliche Position: {analysis['avg_position']:.1f}")
 print(f" Bereich: {analysis['position_range'][0]}-{analysis['position_range'][1]}")
 print()
 
 # Kritische Bewertung
 print("=" * 80)
 print("KRITISCHE BEWERTUNG")
 print("=" * 80)
 print()
 
 print("✅ SIGNIFIKANTE WÖRTER (mehr als 2x zufällige Erwartung):")
 for word in significant_words:
 print(f" - '{word}'")
 print()
 
 if not_significant_words:
 print("❌ NICHT SIGNIFIKANTE WÖRTER (könnten zufällig sein):")
 for word in not_significant_words:
 print(f" - '{word}'")
 print()
 
 # Fazit
 print("💡 FAZIT:")
 print()
 print(f" ✅ {len(significant_words)} Wörter sind statistisch signifikant")
 print(f" {'❌' if not_significant_words else '✅'} {'Einige Wörter könnten zufällig sein' if not_significant_words else 'Alle wichtigen Wörter sind signifikant'}")
 print()
 print(" ⚠️ WICHTIG:")
 print(" - Statistische Signifikanz bedeutet NICHT automatisch 'Nachricht'")
 print(" - Wörter könnten auch strukturelle Patterns sein")
 print(" - Weitere Validierung durch Kommunikation nötig")
 print()
 
 # Speichere Validierung
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 validation_data = {
 "timestamp": datetime.now().isoformat(),
 "total_identities": total_identities,
 "significant_words": significant_words,
 "not_significant_words": not_significant_words,
 "random_comparison": random_results,
 "position_analysis": position_analysis
 }
 
 output_file = OUTPUT_DIR / "critical_word_validation.json"
 with output_file.open("w") as f:
 json.dump(validation_data, f, indent=2)
 print(f"💾 Validierung gespeichert: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Kritische Validierung der gefundenen Wörter",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Vergleich: Echte Daten vs. Zufällige Daten",
 "",
 "| Wort | Echte Daten | Zufällig | Ratio | Signifikant |",
 "|------|-------------|----------|-------|-------------|"
 ]
 
 for word in important_words:
 real_count = found_important.get(word, {}).get("count", 0)
 random_count = random_results.get(word, 0)
 ratio = real_count / random_count if random_count > 0 else (float('inf') if real_count > 0 else 0)
 is_significant = ratio > 2.0 if random_count > 0 else real_count > 0
 marker = "✅" if is_significant else "❌"
 report_lines.append(f"| {word} | {real_count} | {random_count} | {ratio:.2f} | {marker} |")
 
 report_lines.extend([
 "",
 "## Signifikante Wörter",
 ""
 ])
 
 for word in significant_words:
 report_lines.append(f"- **'{word}'** - Statistisch signifikant (mehr als 2x zufällige Erwartung)")
 
 if not_significant_words:
 report_lines.extend([
 "",
 "## Nicht signifikante Wörter",
 ""
 ])
 for word in not_significant_words:
 report_lines.append(f"- **'{word}'** - Könnte zufällig sein")
 
 report_lines.extend([
 "",
 "## Position-Analyse",
 ""
 ])
 
 for word, analysis in position_analysis.items():
 report_lines.append(f"### '{word}'")
 report_lines.append(f"- Durchschnittliche Position: {analysis['avg_position']:.1f}")
 report_lines.append(f"- Bereich: {analysis['position_range'][0]}-{analysis['position_range'][1]}")
 report_lines.append("")
 
 report_lines.extend([
 "## Fazit",
 "",
 "⚠️ **WICHTIG:**",
 "",
 "- Statistische Signifikanz bedeutet NICHT automatisch 'Nachricht'",
 "- Wörter könnten auch strukturelle Patterns sein",
 "- Weitere Validierung durch Kommunikation nötig"
 ])
 
 report_file = REPORTS_DIR / "critical_word_validation_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 print()
 print("=" * 80)
 print("✅ VALIDIERUNG ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

