#!/usr/bin/env python3
"""
Suche nach weiteren Wörtern - systematisch und vorsichtig
- Nutze erweiterte Wörterliste
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

# Erweiterte Wörterliste - nur echte englische Wörter
MORE_WORDS = {
 # Existenz & Bewusstsein
 "EXIST", "EXISTS", "BEING", "BEINGS", "CREATURE", "CREATURES",
 "ENTITY", "ENTITIES", "FORM", "FORMS", "SHAPE", "SHAPES",
 
 # Kommunikation
 "SPEAK", "SPEAKS", "SPOKE", "TOLD", "SAID", "ASK", "ASKS", "ASKED",
 "CALL", "CALLS", "CALLED", "NAME", "NAMES", "WORD", "WORDS",
 
 # Wahrnehmung
 "SENSE", "SENSES", "FEELING", "FEELINGS", "EMOTION", "EMOTIONS",
 "THOUGHT", "THOUGHTS", "IDEA", "IDEAS", "BELIEF", "BELIEFS",
 
 # Aktionen
 "MOVE", "MOVES", "MOVED", "WALK", "WALKS", "RUN", "RUNS", "RAN",
 "STAND", "STANDS", "SIT", "SITS", "LIE", "LIES", "LAY",
 "TAKE", "TAKES", "TOOK", "GIVE", "GIVES", "GAVE", "GET", "GETS", "GOT",
 "MAKE", "MAKES", "MADE", "DO", "DOES", "DID", "DONE",
 "USE", "USES", "USED", "TRY", "TRIES", "TRIED",
 
 # Zustände
 "ALIVE", "DEAD", "LIVE", "LIVES", "LIVED", "DIE", "DIES", "DIED",
 "BORN", "BIRTH", "DEATH", "LIFE", "LIVES",
 "HAPPY", "SAD", "ANGRY", "CALM", "PEACE", "WAR",
 
 # Zeit
 "TODAY", "TOMORROW", "YESTERDAY", "SOON", "LATE", "EARLY",
 "HOUR", "HOURS", "DAY", "DAYS", "WEEK", "WEEKS", "MONTH", "MONTHS",
 "YEAR", "YEARS", "AGO", "LATER", "NEXT", "LAST",
 
 # Raum
 "PLACE", "PLACES", "SPOT", "SPOTS", "AREA", "AREAS",
 "NEAR", "FAR", "CLOSE", "DISTANT", "INSIDE", "OUTSIDE",
 "UP", "DOWN", "LEFT", "RIGHT", "FRONT", "BACK",
 
 # Quantität
 "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN",
 "MANY", "FEW", "SOME", "ALL", "EACH", "EVERY", "NONE", "ANY",
 "MORE", "LESS", "MOST", "LEAST", "MUCH", "LITTLE",
 
 # Qualität
 "GOOD", "BAD", "BETTER", "BEST", "WORSE", "WORST",
 "BIG", "SMALL", "LARGE", "TINY", "HUGE", "GIANT",
 "LONG", "SHORT", "TALL", "WIDE", "NARROW", "DEEP", "SHALLOW",
 "FAST", "SLOW", "QUICK", "QUIET", "LOUD", "SOFT", "HARD",
 
 # Beziehungen
 "WITH", "WITHOUT", "TOGETHER", "ALONE", "APART",
 "FRIEND", "FRIENDS", "ENEMY", "ENEMIES", "ALLY", "ALLIES",
 "HELP", "HELPS", "HURT", "HURTS", "HARM", "HARMS",
 
 # Abstrakte Konzepte
 "TRUTH", "LIE", "LIES", "FACT", "FACTS", "REALITY", "DREAM", "DREAMS",
 "HOPE", "HOPES", "FEAR", "FEARS", "LOVE", "LOVES", "HATE", "HATES",
 "POWER", "POWERS", "FORCE", "FORCES", "ENERGY", "ENERGIES",
 "LIGHT", "LIGHTS", "DARK", "DARKNESS", "BRIGHT", "DIM",
 
 # Anna-spezifisch
 "ANNA", "QUBIC", "QUICK", "MATRIX", "HELIX", "GATE", "GATES"
}

def find_words_in_identities(identities: List[str], words: Set[str]) -> Dict[str, List[Dict]]:
 """Finde Wörter in Identities."""
 found = {}
 
 for word in words:
 word_upper = word.upper()
 occurrences = []
 
 for idx, identity in enumerate(identities):
 identity_upper = identity.upper()
 
 # Suche nach Wort
 start = 0
 while True:
 pos = identity_upper.find(word_upper, start)
 if pos == -1:
 break
 
 occurrences.append({
 "identity_index": idx,
 "identity": identity,
 "position": pos
 })
 
 start = pos + 1
 
 if occurrences:
 found[word] = occurrences
 
 return found

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("SUCHE NACH WEITEREN WÖRTERN")
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
 
 # Suche Wörter
 print("🔍 Suche nach weiteren Wörtern...")
 found_words = find_words_in_identities(all_identities, MORE_WORDS)
 print(f"✅ {len(found_words)} verschiedene Wörter gefunden")
 print()
 
 # Zeige Ergebnisse (nur Wörter mit mindestens 1 Vorkommen)
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Sortiere nach Häufigkeit
 sorted_words = sorted(found_words.items(), key=lambda x: len(x[1]), reverse=True)
 
 print("📊 Gefundene Wörter (sortiert nach Häufigkeit):")
 for word, occurrences in sorted_words:
 print(f" '{word}': {len(occurrences)}x")
 for i, occ in enumerate(occurrences[:2], 1):
 print(f" {i}. {occ['identity']} (Position: {occ['position']})")
 if len(occurrences) > 2:
 print(f" ... und {len(occurrences) - 2} weitere")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_identities": len(all_identities),
 "found_words": {k: len(v) for k, v in found_words.items()},
 "word_examples": {k: v[:5] for k, v in found_words.items()}
 }
 
 output_file = OUTPUT_DIR / "more_words_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ SUCHE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

