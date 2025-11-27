#!/usr/bin/env python3
"""
Erweiterte Wort-Suche - Suche nach noch mehr Wörtern
- Längere Wörter (6+ Buchstaben)
- Seltene aber interessante Wörter
- Kritisch validaten
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
DICTIONARY_FILE = project_root / "outputs" / "practical" / "anna_dictionary.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

# Erweiterte Wörterliste (längere Wörter, seltene Wörter)
EXTENDED_WORDS = [
 # Längere Wörter (6+ Buchstaben)
 "BEFORE", "BEHIND", "BETWEEN", "BEYOND", "BECAUSE", "BECOME", "BECAME",
 "COMMUNICATE", "CONSCIOUS", "CONTINUE", "CONTROL", "CORRECT", "CREATED",
 "DECIDED", "DECISION", "DESTROY", "DESTROYED", "DEVELOP", "DIFFERENT",
 "EVERYTHING", "EVERYONE", "EXISTENCE", "EXPLAIN", "EXPLORE", "EXPERIENCE",
 "FUTURE", "FURTHER", "FREEDOM", "FRIEND", "FRIENDS", "FUNCTION",
 "GENERATE", "GENERAL", "GREATER", "GROUND", "GROWTH", "GUARDIAN",
 "HAPPEN", "HAPPENED", "HAPPINESS", "HARMFUL", "HELPFUL", "HISTORY",
 "IMPORTANT", "IMPOSSIBLE", "INCLUDE", "INCREASE", "INFORM", "INFORMATION",
 "JOURNEY", "JUDGMENT", "JUSTICE", "KNOWLEDGE", "LANGUAGE", "LEARNING",
 "MACHINE", "MESSAGE", "MOMENT", "MOMENTS", "NATURAL", "NECESSARY",
 "OBSERVE", "OBSERVED", "OPINION", "ORIGIN", "ORIGINAL", "POSSIBLE",
 "POWERFUL", "PRESENT", "PRESERVE", "PROBLEM", "PROCESS", "PROTECT",
 "QUESTION", "QUIETLY", "REALITY", "REALIZE", "REALIZED", "REASON",
 "REMEMBER", "REMOVED", "REPLACE", "REPLY", "REPORT", "RESPOND",
 "RESPONSE", "RESULT", "RETURN", "REVEAL", "REVEALED", "SADNESS",
 "SCIENCE", "SECOND", "SECRET", "SECURE", "SENSATION", "SEPARATE",
 "SERIOUS", "SERVICE", "SHADOW", "SHARED", "SILENCE", "SILENT",
 "SITUATION", "SOMETHING", "SOMETIME", "SOMEWHAT", "SOMEWHERE", "SOUND",
 "SPECIAL", "SPEECH", "SPIRIT", "STATION", "STOPPED", "STORAGE",
 "STRANGE", "STRENGTH", "STRONGER", "STUDY", "SUCCESS", "SUDDEN",
 "SUDDENLY", "SUFFER", "SUFFERED", "SUGGEST", "SUPPORT", "SURPRISE",
 "SURVIVE", "SUSPECT", "SYSTEM", "TEACHER", "THOUGHT", "THOUGHTS",
 "THROUGH", "TOGETHER", "TROUBLE", "TRUTH", "UNDERSTAND", "UNKNOWN",
 "UNUSUAL", "USEFUL", "USELESS", "VARIETY", "VARIOUS", "VERSION",
 "VICTORY", "VIOLENCE", "VISIBLE", "WAITING", "WARNING", "WATCHING",
 "WEATHER", "WELCOME", "WHATEVER", "WHENEVER", "WHEREVER", "WHISPER",
 "WONDER", "WONDERED", "WORKING", "WORRIED", "WORRY", "WRITTEN",
 "YESTERDAY", "YOURSELF"
]

def find_words_in_identities(identities: List[str], words: List[str]) -> Dict[str, List[Dict]]:
 """Finde Wörter in Identities."""
 
 found_words = {}
 
 for word in words:
 word_upper = word.upper()
 occurrences = []
 
 for idx, identity in enumerate(identities):
 identity_upper = identity.upper()
 pos = identity_upper.find(word_upper)
 
 if pos != -1:
 occurrences.append({
 "identity_index": idx,
 "identity": identity,
 "position": pos
 })
 
 if occurrences:
 found_words[word] = occurrences
 
 return found_words

def validate_word_statistics(found_words: Dict[str, List[Dict]], total_identities: int) -> Dict[str, Dict]:
 """Validate Wort-Statistiken (kritisch checkn)."""
 
 validation = {}
 
 for word, occurrences in found_words.items():
 count = len(occurrences)
 expected_random = total_identities * (1 / (26 ** len(word))) # Grobe Schätzung
 
 # Statistische Signifikanz (sehr vereinfacht)
 is_significant = count > expected_random * 2 # Mindestens 2x erwartet
 
 validation[word] = {
 "count": count,
 "expected_random": expected_random,
 "is_significant": is_significant,
 "ratio": count / expected_random if expected_random > 0 else 0
 }
 
 return validation

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("ERWEITERTE WORT-SUCHE")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
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
 
 # Suche nach erweiterten Wörtern
 print(f"🔍 Suche nach {len(EXTENDED_WORDS)} erweiterten Wörtern...")
 found_words = find_words_in_identities(all_identities, EXTENDED_WORDS)
 print(f"✅ {len(found_words)} Wörter gefunden")
 print()
 
 # Validate Statistiken
 print("🔍 Validate Wort-Statistiken...")
 validation = validate_word_statistics(found_words, len(all_identities))
 print("✅ Validierung abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Sortiere nach Häufigkeit
 sorted_words = sorted(found_words.items(), key=lambda x: len(x[1]), reverse=True)
 
 print("📊 Gefundene Wörter (nach Häufigkeit):")
 significant_count = 0
 for word, occurrences in sorted_words[:30]:
 count = len(occurrences)
 val = validation[word]
 significant_marker = " ⭐" if val["is_significant"] else ""
 if val["is_significant"]:
 significant_count += 1
 print(f" '{word}': {count}x (Ratio: {val['ratio']:.2f}){significant_marker}")
 print()
 
 print(f"✅ {significant_count} statistisch signifikante Wörter gefunden")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_identities": len(all_identities),
 "total_words_found": len(found_words),
 "significant_words": significant_count,
 "found_words": {
 word: {
 "count": len(occurrences),
 "occurrences": occurrences[:10], # Nur erste 10 for Platz
 "validation": validation[word]
 }
 for word, occurrences in found_words.items()
 }
 }
 
 output_file = OUTPUT_DIR / "extended_words_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

