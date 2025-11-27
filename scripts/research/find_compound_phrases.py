#!/usr/bin/env python3
"""
Suche nach zusammengesetzten Phrasen in Identities
- Finde bekannte Phrasen wie "ANNA WAS HERE"
- Suche nach mehreren Wörtern in einer Identity
- KEINE Spekulationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

# Bekannte Phrasen die wir suchen
KNOWN_PHRASES = [
 "ANNA WAS HERE",
 "ANNA WAS HERE STOP",
 "HELLO ANNA",
 "HI ANNA",
 "ANNA STOP",
 "ANNA HERE",
 "WAS HERE",
 "HERE STOP",
 "ANNA WAS",
 "STOP ANNA"
]

def find_phrase_in_identity(identity: str, phrase: str) -> List[int]:
 """Finde alle Positionen wo Phrase in Identity vorkommt."""
 positions = []
 identity_upper = identity.upper()
 phrase_upper = phrase.upper()
 
 # Entferne Leerzeichen for Suche
 phrase_no_spaces = phrase_upper.replace(" ", "")
 
 start = 0
 while True:
 pos = identity_upper.find(phrase_no_spaces, start)
 if pos == -1:
 break
 positions.append(pos)
 start = pos + 1
 
 return positions

def find_multiple_words_in_identity(identity: str, words: List[str], max_distance: int = 10) -> List[Dict]:
 """
 Finde mehrere Wörter in einer Identity die nah beieinander sind.
 max_distance: Maximale Distanz zwischen Wörtern (in Characters)
 """
 identity_upper = identity.upper()
 word_positions = {}
 
 # Finde Positionen aller Wörter
 for word in words:
 word_upper = word.upper()
 positions = []
 start = 0
 while True:
 pos = identity_upper.find(word_upper, start)
 if pos == -1:
 break
 positions.append(pos)
 start = pos + 1
 word_positions[word] = positions
 
 # Finde Kombinationen die nah beieinander sind
 combinations = []
 
 # For each word pair
 for i, word1 in enumerate(words):
 for word2 in words[i+1:]:
 for pos1 in word_positions[word1]:
 for pos2 in word_positions[word2]:
 distance = abs(pos2 - pos1) - len(word1)
 if distance <= max_distance and distance >= 0:
 combinations.append({
 "word1": word1,
 "word2": word2,
 "pos1": pos1,
 "pos2": pos2,
 "distance": distance,
 "identity": identity
 })
 
 return combinations

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("SUCHE NACH ZUSAMMENGESETZTEN PHRASEN")
 print("=" * 80)
 print()
 print("⚠️ KEINE SPEKULATIONEN - NUR ECHTE DATEN!")
 print()
 
 # Load Layer-3 Identities
 print("📂 Load Layer-3 Identities...")
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 layer3_identities = [e.get("layer3_identity", "") for e in layer3_results if len(e.get("layer3_identity", "")) == 60]
 print(f"✅ {len(layer3_identities)} Layer-3 Identities geloadn")
 print()
 
 # Load Layer-4 Identities
 layer4_identities = []
 if LAYER4_FILE.exists():
 print("📂 Load Layer-4 Identities...")
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 layer4_identities = [e.get("layer4_identity", "") for e in layer4_results if len(e.get("layer4_identity", "")) == 60]
 print(f"✅ {len(layer4_identities)} Layer-4 Identities geloadn")
 print()
 
 all_identities = layer3_identities + layer4_identities
 print(f"📊 Gesamt: {len(all_identities)} Identities")
 print()
 
 # Suche nach bekannten Phrasen
 print("🔍 Suche nach bekannten Phrasen...")
 found_phrases = defaultdict(list)
 
 for identity_idx, identity in enumerate(all_identities):
 for phrase in KNOWN_PHRASES:
 positions = find_phrase_in_identity(identity, phrase)
 if positions:
 found_phrases[phrase].append({
 "identity_index": identity_idx,
 "identity": identity,
 "positions": positions
 })
 
 print(f"✅ {len(found_phrases)} verschiedene Phrasen gefunden")
 print()
 
 # Suche nach mehreren Wörtern nah beieinander
 print("🔍 Suche nach mehreren Wörtern nah beieinander...")
 word_combinations = []
 
 # Wichtige Wörter
 important_words = ["ANNA", "WAS", "HERE", "STOP", "HELLO", "HI", "TEST"]
 
 for identity_idx, identity in enumerate(all_identities[:1000]): # Nur erste 1000 for Performance
 combinations = find_multiple_words_in_identity(identity, important_words, max_distance=15)
 word_combinations.extend(combinations)
 
 print(f"✅ {len(word_combinations)} Wort-Kombinationen gefunden")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 if found_phrases:
 print("📊 Gefundene bekannte Phrasen:")
 for phrase, occurrences in sorted(found_phrases.items(), key=lambda x: len(x[1]), reverse=True):
 print(f" '{phrase}': {len(occurrences)}x gefunden")
 for i, occ in enumerate(occurrences[:3], 1):
 print(f" {i}. {occ['identity']} (Positionen: {occ['positions']})")
 if len(occurrences) > 3:
 print(f" ... und {len(occurrences) - 3} weitere")
 print()
 else:
 print("❌ Keine bekannten Phrasen gefunden")
 print()
 
 # Top Wort-Kombinationen
 if word_combinations:
 print("📊 Top 10 Wort-Kombinationen (nah beieinander):")
 # Sortiere nach Distanz
 word_combinations.sort(key=lambda x: x["distance"])
 for i, combo in enumerate(word_combinations[:10], 1):
 print(f" {i}. '{combo['word1']}' + '{combo['word2']}' (Distanz: {combo['distance']})")
 print(f" Identity: {combo['identity']}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_identities": len(all_identities),
 "found_phrases": {k: len(v) for k, v in found_phrases.items()},
 "phrase_examples": {k: v[:5] for k, v in found_phrases.items()},
 "word_combinations": word_combinations[:50]
 }
 
 output_file = OUTPUT_DIR / "compound_phrases_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Suche nach zusammengesetzten Phrasen",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 f"**Total Identities**: {len(all_identities)}",
 "",
 "## Gefundene bekannte Phrasen",
 ""
 ]
 
 if found_phrases:
 for phrase, occurrences in sorted(found_phrases.items(), key=lambda x: len(x[1]), reverse=True):
 report_lines.append(f"### '{phrase}' ({len(occurrences)}x gefunden)")
 for i, occ in enumerate(occurrences[:10], 1):
 report_lines.append(f"{i}. `{occ['identity']}` (Positionen: {occ['positions']})")
 report_lines.append("")
 else:
 report_lines.append("Keine bekannten Phrasen gefunden.")
 report_lines.append("")
 
 report_lines.extend([
 "## Wort-Kombinationen (nah beieinander)",
 ""
 ])
 
 for i, combo in enumerate(word_combinations[:20], 1):
 report_lines.append(f"{i}. **'{combo['word1']}' + '{combo['word2']}'** (Distanz: {combo['distance']})")
 report_lines.append(f" - Identity: `{combo['identity']}`")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "compound_phrases_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

