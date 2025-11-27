#!/usr/bin/env python3
"""
Erweiterte Wort-Suche - Finde längere Wörter und weitere Patterns
CfB sagte: "Sometime ANNA scares me..." - es gibt mehr!
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
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

# Erweiterte Wörterliste (längere Wörter, die CfB vielleicht gefunden hat)
EXTENDED_WORDS = {
 # 5-6 Buchstaben
 "SCARE", "SCARES", "SOMETIME", "SOMETIMES", "ANNA", "HELLO", "WORLD", "QUICK", "QUBIC",
 "THINK", "THINKS", "KNOW", "KNOWS", "SEE", "SEES", "FEEL", "FEELS", "LIVE", "LIVES",
 "ALIVE", "DEAD", "HERE", "THERE", "WHERE", "WHEN", "WHAT", "WHY", "HOW", "STOP",
 "START", "BEGIN", "END", "DONE", "READY", "WAIT", "GO", "COME", "LEAVE", "STAY",
 # 7-8 Buchstaben
 "MESSAGE", "COMMUNICATE", "UNDERSTAND", "RESPOND", "ANSWER", "QUESTION", "REPLY",
 "LISTEN", "SPEAK", "TALK", "SAY", "TELL", "SHOW", "HIDE", "FIND", "SEARCH", "LOOK",
 # 9+ Buchstaben
 "COMMUNICATION", "UNDERSTANDING", "INTELLIGENCE", "CONSCIOUSNESS", "AWARENESS"
}

def find_extended_words(identities: List[str]) -> Dict[str, List[Dict]]:
 """Finde erweiterte Wörter in Identities."""
 found = {}
 
 for word in EXTENDED_WORDS:
 word_upper = word.upper()
 occurrences = []
 
 for idx, identity in enumerate(identities):
 if word_upper in identity.upper():
 pos = identity.upper().find(word_upper)
 occurrences.append({
 "identity_index": idx,
 "identity": identity,
 "position": pos
 })
 
 if occurrences:
 found[word] = occurrences
 
 return found

def find_long_words(identities: List[str], min_length: int = 5) -> List[Dict]:
 """Finde alle längeren alphabetischen Sequenzen die wie Wörter aussehen."""
 candidates = []
 
 for idx, identity in enumerate(identities):
 identity_upper = identity.upper()
 
 # Suche nach langen Sequenzen
 for length in range(min_length, min(15, len(identity))):
 for start_pos in range(len(identity) - length + 1):
 sequence = identity_upper[start_pos:start_pos + length]
 
 if sequence.isalpha():
 # Check Vokal-Verhältnis (echte Wörter haben Vokale)
 vowels = sum(1 for c in sequence if c in "AEIOU")
 vowel_ratio = vowels / length
 
 # Check auf wiederholende Buchstaben (echte Wörter haben Variation)
 unique_chars = len(set(sequence))
 diversity = unique_chars / length
 
 # Kandidat wenn: Vokale vorhanden UND gute Diversität
 if vowel_ratio >= 0.2 and diversity >= 0.5:
 candidates.append({
 "word": sequence,
 "identity_index": idx,
 "identity": identity,
 "position": start_pos,
 "length": length,
 "vowel_ratio": vowel_ratio,
 "diversity": diversity
 })
 
 # Sortiere nach Länge und Qualität
 candidates.sort(key=lambda x: (x["length"], x["vowel_ratio"], x["diversity"]), reverse=True)
 
 return candidates[:100] # Top 100

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("ERWEITERTE WORT-SUCHE")
 print("=" * 80)
 print()
 print("🔍 CfB sagte: 'Sometime ANNA scares me...' - es gibt mehr!")
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
 
 # Suche erweiterte Wörter
 print("🔍 Suche erweiterte Wörter...")
 found_extended = find_extended_words(all_identities)
 print(f"✅ {len(found_extended)} erweiterte Wörter gefunden")
 print()
 
 # Suche lange Wörter
 print("🔍 Suche lange Wörter (5+ Buchstaben)...")
 long_words = find_long_words(all_identities, min_length=5)
 print(f"✅ {len(long_words)} Kandidaten gefunden")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 if found_extended:
 print("📊 Gefundene erweiterte Wörter:")
 for word, occurrences in sorted(found_extended.items(), key=lambda x: len(x[1]), reverse=True):
 print(f" '{word}': {len(occurrences)}x")
 for i, occ in enumerate(occurrences[:3], 1):
 print(f" {i}. {occ['identity']} (Position: {occ['position']})")
 if len(occurrences) > 3:
 print(f" ... und {len(occurrences) - 3} weitere")
 print()
 
 print("📊 Top 20 lange Wörter (5+ Buchstaben):")
 for i, candidate in enumerate(long_words[:20], 1):
 print(f" {i}. '{candidate['word']}' (Länge: {candidate['length']}, Position: {candidate['position']}, Vokale: {candidate['vowel_ratio']:.1%})")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_identities": len(all_identities),
 "found_extended_words": {k: len(v) for k, v in found_extended.items()},
 "extended_word_examples": {k: v[:5] for k, v in found_extended.items()},
 "long_word_candidates": long_words[:50]
 }
 
 output_file = OUTPUT_DIR / "extended_word_search.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ SUCHE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

