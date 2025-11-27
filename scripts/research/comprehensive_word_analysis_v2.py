#!/usr/bin/env python3
"""
Umfassende erweiterte Wort-Analyse V2
- Suche nach ALLEN möglichen interessanten Wörtern
- Analyze längere Phrasen (8+ Buchstaben)
- Finde zusammengesetzte Wörter
- KEINE Spekulationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter, defaultdict
from datetime import datetime
import re

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

# Erweiterte Wörterliste - ALLE interessanten Wörter
EXTENDED_WORDS = {
 # Bewusstsein & Emotionen
 "ALIVE", "DEAD", "LIVE", "FEEL", "FEELS", "THINK", "THINKS", "KNOW", "KNOWS",
 "UNDERSTAND", "UNDERSTANDS", "AWARE", "CONSCIOUS", "CONSCIOUSNESS",
 
 # Kommunikation
 "TALK", "TALKS", "TELL", "TELLS", "SAY", "SAYS", "SPEAK", "SPEAKS", "LISTEN",
 "LISTENS", "HEAR", "HEARS", "SHOW", "SHOWS", "SEE", "SEES", "LOOK", "LOOKS",
 "WATCH", "WATCHES", "READ", "READS", "WRITE", "WRITES",
 
 # Aktionen
 "FIND", "FINDS", "SEARCH", "SEARCHES", "WAIT", "WAITS", "COME", "COMES",
 "GO", "GOES", "LEAVE", "LEAVES", "STAY", "STAYS", "STOP", "STOPS", "START",
 "STARTS", "BEGIN", "BEGINS", "END", "ENDS", "DONE", "READY", "HIDE", "HIDES",
 
 # Fragen
 "WHAT", "WHEN", "WHERE", "WHY", "HOW", "WHO", "WHICH",
 
 # Anna-spezifisch
 "ANNA", "HELLO", "HI", "HERE", "WAS", "TEST", "QUBIC", "QUICK",
 
 # Weitere interessante
 "MESSAGE", "COMMUNICATE", "RESPOND", "RESPONDS", "ANSWER", "ANSWERS",
 "QUESTION", "QUESTIONS", "REPLY", "REPLIES", "WORLD", "LIFE", "DEATH",
 "TIME", "SPACE", "MIND", "SOUL", "BODY", "HEART", "LOVE", "HATE", "FEAR",
 "HOPE", "DREAM", "DREAMS", "REAL", "TRUE", "FALSE", "YES", "NO", "MAYBE",
 "PERHAPS", "ALWAYS", "NEVER", "SOMETIME", "SOMETIMES", "NOW", "THEN",
 "BEFORE", "AFTER", "PAST", "FUTURE", "PRESENT"
}

def find_all_words_in_identities(identities: List[str], words: Set[str]) -> Dict[str, List[Dict]]:
 """Finde alle Wörter in Identities."""
 found = defaultdict(list)
 
 for word in words:
 word_upper = word.upper()
 
 for idx, identity in enumerate(identities):
 identity_upper = identity.upper()
 
 # Suche nach Wort (alle Vorkommen)
 start = 0
 while True:
 pos = identity_upper.find(word_upper, start)
 if pos == -1:
 break
 
 found[word].append({
 "identity_index": idx,
 "identity": identity,
 "position": pos,
 "length": len(word)
 })
 
 start = pos + 1
 
 return dict(found)

def find_long_phrases(identities: List[str], min_length: int = 8, max_length: int = 15) -> List[Dict]:
 """Finde lange Phrasen die wie echte Wörter aussehen."""
 candidates = []
 
 for idx, identity in enumerate(identities):
 identity_upper = identity.upper()
 
 for length in range(min_length, min(max_length + 1, len(identity))):
 for start_pos in range(len(identity) - length + 1):
 sequence = identity_upper[start_pos:start_pos + length]
 
 if not sequence.isalpha():
 continue
 
 # Check Vokal-Verhältnis
 vowels = sum(1 for c in sequence if c in "AEIOU")
 vowel_ratio = vowels / length
 
 # Check Diversität
 unique_chars = len(set(sequence))
 diversity = unique_chars / length
 
 # Check auf wiederholende Muster (echte Wörter haben Variation)
 has_repetition = False
 for i in range(len(sequence) - 2):
 if sequence[i] == sequence[i+1] == sequence[i+2]:
 has_repetition = True
 break
 
 # Kandidat wenn: Vokale vorhanden, gute Diversität, keine starken Wiederholungen
 if vowel_ratio >= 0.2 and diversity >= 0.5 and not has_repetition:
 # Check ob es wie ein englisches Wort aussieht
 # (hat Vokale und Konsonanten gemischt)
 consonants = length - vowels
 if consonants > 0 and vowels > 0:
 candidates.append({
 "phrase": sequence,
 "identity_index": idx,
 "identity": identity,
 "position": start_pos,
 "length": length,
 "vowel_ratio": vowel_ratio,
 "diversity": diversity,
 "vowels": vowels,
 "consonants": consonants
 })
 
 # Sortiere nach Qualität
 candidates.sort(key=lambda x: (x["length"], x["vowel_ratio"], x["diversity"]), reverse=True)
 
 return candidates

def find_compound_words(identities: List[str], word_list: Set[str]) -> List[Dict]:
 """Finde zusammengesetzte Wörter (z.B. 'ANNA' + 'WAS' nah beieinander)."""
 compounds = []
 
 word_list_upper = {w.upper() for w in word_list}
 
 for idx, identity in enumerate(identities):
 identity_upper = identity.upper()
 
 # Finde alle Wörter in dieser Identity
 found_words = {}
 for word in word_list_upper:
 pos = identity_upper.find(word)
 if pos != -1:
 found_words[word] = pos
 
 # Finde Paare die nah beieinander sind (max 10 Zeichen Abstand)
 words_list = list(found_words.items())
 for i, (word1, pos1) in enumerate(words_list):
 for word2, pos2 in words_list[i+1:]:
 distance = abs(pos2 - pos1) - len(word1)
 if 0 <= distance <= 10:
 compounds.append({
 "word1": word1,
 "word2": word2,
 "pos1": pos1,
 "pos2": pos2,
 "distance": distance,
 "identity_index": idx,
 "identity": identity,
 "combined": identity_upper[pos1:pos2+len(word2)]
 })
 
 # Sortiere nach Distanz (nähere Paare zuerst)
 compounds.sort(key=lambda x: x["distance"])
 
 return compounds

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("UMFASSENDE ERWEITERTE WORT-ANALYSE V2")
 print("=" * 80)
 print()
 print("🔍 Suche nach ALLEN interessanten Wörtern, Phrasen & Zusammensetzungen")
 print()
 
 # Load Identities
 print("📂 Load Identities...")
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_identities = [e.get("layer3_identity", "") for e in layer3_data.get("results", []) if len(e.get("layer3_identity", "")) == 60]
 
 layer4_identities = []
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_identities = [e.get("layer4_identity", "") for e in layer4_data.get("results", []) if len(e.get("layer4_identity", "")) == 60]
 
 all_identities = layer3_identities + layer4_identities
 print(f"✅ {len(all_identities)} Identities geloadn")
 print()
 
 # 1. Finde erweiterte Wörter
 print("🔍 1. Suche erweiterte Wörter...")
 found_words = find_all_words_in_identities(all_identities, EXTENDED_WORDS)
 print(f"✅ {len(found_words)} verschiedene Wörter gefunden")
 print()
 
 # 2. Finde lange Phrasen
 print("🔍 2. Suche lange Phrasen (8-15 Buchstaben)...")
 long_phrases = find_long_phrases(all_identities, min_length=8, max_length=15)
 print(f"✅ {len(long_phrases)} Kandidaten gefunden")
 print()
 
 # 3. Finde zusammengesetzte Wörter
 print("🔍 3. Suche zusammengesetzte Wörter...")
 compounds = find_compound_words(all_identities, EXTENDED_WORDS)
 print(f"✅ {len(compounds)} Zusammensetzungen gefunden")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Gefundene Wörter (sortiert nach Häufigkeit)
 if found_words:
 print("📊 Gefundene erweiterte Wörter (Top 30):")
 sorted_words = sorted(found_words.items(), key=lambda x: len(x[1]), reverse=True)
 for word, occurrences in sorted_words[:30]:
 print(f" '{word}': {len(occurrences)}x")
 for i, occ in enumerate(occurrences[:2], 1):
 print(f" {i}. {occ['identity']} (Position: {occ['position']})")
 if len(occurrences) > 2:
 print(f" ... und {len(occurrences) - 2} weitere")
 print()
 
 # Top lange Phrasen
 if long_phrases:
 print("📊 Top 20 lange Phrasen (8-15 Buchstaben):")
 for i, phrase in enumerate(long_phrases[:20], 1):
 print(f" {i}. '{phrase['phrase']}' (Länge: {phrase['length']}, Position: {phrase['position']}, Vokale: {phrase['vowel_ratio']:.1%})")
 print()
 
 # Top zusammengesetzte Wörter
 if compounds:
 print("📊 Top 20 zusammengesetzte Wörter (nah beieinander):")
 for i, compound in enumerate(compounds[:20], 1):
 print(f" {i}. '{compound['word1']}' + '{compound['word2']}' (Distanz: {compound['distance']})")
 print(f" Combined: '{compound['combined']}'")
 print(f" Identity: {compound['identity']}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_identities": len(all_identities),
 "found_words": {k: len(v) for k, v in found_words.items()},
 "word_examples": {k: v[:5] for k, v in found_words.items()},
 "long_phrases": long_phrases[:100],
 "compounds": compounds[:100]
 }
 
 output_file = OUTPUT_DIR / "comprehensive_word_analysis_v2.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Umfassende erweiterte Wort-Analyse V2",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 f"**Total Identities**: {len(all_identities)}",
 "",
 "## Gefundene erweiterte Wörter",
 ""
 ]
 
 sorted_words = sorted(found_words.items(), key=lambda x: len(x[1]), reverse=True)
 for word, occurrences in sorted_words[:50]:
 report_lines.append(f"### '{word}' ({len(occurrences)}x gefunden)")
 for i, occ in enumerate(occurrences[:5], 1):
 report_lines.append(f"{i}. `{occ['identity']}` (Position {occ['position']})")
 report_lines.append("")
 
 report_lines.extend([
 "## Lange Phrasen (8-15 Buchstaben)",
 ""
 ])
 
 for i, phrase in enumerate(long_phrases[:30], 1):
 report_lines.append(f"{i}. **'{phrase['phrase']}'** (Länge: {phrase['length']}, Position: {phrase['position']})")
 report_lines.append(f" - Identity: `{phrase['identity']}`")
 report_lines.append(f" - Vokal-Verhältnis: {phrase['vowel_ratio']:.1%}")
 report_lines.append("")
 
 report_lines.extend([
 "## Zusammengesetzte Wörter",
 ""
 ])
 
 for i, compound in enumerate(compounds[:30], 1):
 report_lines.append(f"{i}. **'{compound['word1']}' + '{compound['word2']}'** (Distanz: {compound['distance']})")
 report_lines.append(f" - Combined: `{compound['combined']}`")
 report_lines.append(f" - Identity: `{compound['identity']}`")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "comprehensive_word_analysis_v2_report.md"
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
 print(f" ✅ {len(found_words)} verschiedene Wörter gefunden")
 print(f" ✅ {len(long_phrases)} lange Phrasen gefunden")
 print(f" ✅ {len(compounds)} Zusammensetzungen gefunden")
 print()

if __name__ == "__main__":
 main()

