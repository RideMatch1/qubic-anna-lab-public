#!/usr/bin/env python3
"""
Pattern-Analyse - Warum kommen Wörter zusammen vor?
- Analyze Wort-Kombinationen
- Finde wiederholende Muster
- Analyze Distanzen zwischen Wörtern
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
DICTIONARY_FILE = project_root / "outputs" / "practical" / "anna_dictionary.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_known_words() -> set:
 """Load bekannte Wörter aus Wörterbuch."""
 known_words = set()
 
 if DICTIONARY_FILE.exists():
 with DICTIONARY_FILE.open() as f:
 dictionary = json.load(f)
 all_words = dictionary.get("all_words", {})
 known_words = {word.upper() for word in all_words.keys()}
 
 return known_words

def find_word_pairs(identities: List[str], known_words: set) -> Dict[Tuple[str, str], List[Dict]]:
 """Finde Paare von Wörtern die zusammen vorkommen."""
 
 word_pairs = defaultdict(list)
 
 for idx, identity in enumerate(identities):
 identity_upper = identity.upper()
 
 # Finde alle Wörter in dieser Identity
 found_words = []
 for word in known_words:
 pos = identity_upper.find(word)
 if pos != -1:
 found_words.append({
 "word": word,
 "position": pos,
 "length": len(word)
 })
 
 # Sortiere nach Position
 found_words.sort(key=lambda x: x["position"])
 
 # Finde Paare (Wörter die nah beieinander sind)
 for i in range(len(found_words)):
 for j in range(i + 1, len(found_words)):
 word1 = found_words[i]
 word2 = found_words[j]
 
 # Distanz zwischen Wörtern
 distance = word2["position"] - (word1["position"] + word1["length"])
 
 if distance <= 20: # Max 20 Zeichen Abstand
 pair_key = tuple(sorted([word1["word"], word2["word"]]))
 word_pairs[pair_key].append({
 "identity_index": idx,
 "identity": identity,
 "word1": word1["word"],
 "word1_pos": word1["position"],
 "word2": word2["word"],
 "word2_pos": word2["position"],
 "distance": distance
 })
 
 return dict(word_pairs)

def analyze_patterns(word_pairs: Dict) -> Dict:
 """Analyze Patterns in Wort-Paaren."""
 
 # Häufigste Paare
 pair_counts = {pair: len(occurrences) for pair, occurrences in word_pairs.items()}
 top_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)
 
 # Durchschnittliche Distanzen
 avg_distances = {}
 for pair, occurrences in word_pairs.items():
 if occurrences:
 avg_distance = sum(occ["distance"] for occ in occurrences) / len(occurrences)
 avg_distances[pair] = avg_distance
 
 # Distanz-Verteilungen
 distance_distributions = {}
 for pair, occurrences in word_pairs.items():
 distances = [occ["distance"] for occ in occurrences]
 distance_distributions[pair] = {
 "min": min(distances),
 "max": max(distances),
 "avg": sum(distances) / len(distances),
 "count": len(distances)
 }
 
 return {
 "top_pairs": top_pairs[:100],
 "avg_distances": avg_distances,
 "distance_distributions": distance_distributions
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("PATTERN-ANALYSE")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print()
 
 # Load bekannte Wörter
 print("📂 Load bekannte Wörter...")
 known_words = load_known_words()
 print(f"✅ {len(known_words)} bekannte Wörter geloadn")
 print()
 
 # Load Identities
 print("📂 Load Identities...")
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_identities = [e.get("layer3_identity", "") for e in layer3_data.get("results", []) if len(e.get("layer3_identity", "")) == 60]
 print(f"✅ {len(layer3_identities)} Identities geloadn")
 print()
 
 # Finde Wort-Paare
 print("🔍 Finde Wort-Paare (max 20 Zeichen Abstand)...")
 word_pairs = find_word_pairs(layer3_identities, known_words)
 print(f"✅ {len(word_pairs)} verschiedene Paare gefunden")
 print()
 
 # Analyze Patterns
 print("🔍 Analyze Patterns...")
 patterns = analyze_patterns(word_pairs)
 print("✅ Pattern-Analyse abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Top Paare
 print("📊 Top 30 häufigste Wort-Paare:")
 for i, ((word1, word2), count) in enumerate(patterns["top_pairs"][:30], 1):
 avg_dist = patterns["avg_distances"].get((word1, word2), 0)
 print(f" {i}. '{word1}' + '{word2}': {count}x (Ø Distanz: {avg_dist:.1f})")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_identities": len(layer3_identities),
 "total_pairs": len(word_pairs),
 "top_pairs": [
 {
 "word1": pair[0],
 "word2": pair[1],
 "count": count,
 "avg_distance": patterns["avg_distances"].get(pair, 0),
 "distance_distribution": patterns["distance_distributions"].get(pair, {})
 }
 for pair, count in patterns["top_pairs"]
 ],
 "all_pairs": {
 f"{pair[0]}_{pair[1]}": {
 "word1": pair[0],
 "word2": pair[1],
 "occurrences": occurrences[:10] # Nur erste 10 for Platz
 }
 for pair, occurrences in list(word_pairs.items())[:100]
 }
 }
 
 output_file = OUTPUT_DIR / "word_patterns_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

