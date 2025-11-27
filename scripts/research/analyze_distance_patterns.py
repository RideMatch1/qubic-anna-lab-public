#!/usr/bin/env python3
"""
Distanz-Analyse vertiefen - Warum bestimmte Distanzen zwischen Wörtern?
- Analyze Distanz-Verteilungen
- Finde strukturelle Distanz-Patterns
- Verstehe warum ~8-10 Zeichen Abstand
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
DICTIONARY_FILE = project_root / "outputs" / "practical" / "anna_dictionary.json"
OUTPUT_DIR = project_root / "outputs" / "derived"

def load_known_words() -> set:
 """Load bekannte Wörter aus Wörterbuch."""
 known_words = set()
 if DICTIONARY_FILE.exists():
 with DICTIONARY_FILE.open() as f:
 dictionary = json.load(f)
 all_words = dictionary.get("all_words", {})
 known_words = {word.upper() for word in all_words.keys()}
 return known_words

def analyze_distances(identities: List[str], known_words: set) -> Dict:
 """Analyze Distanzen zwischen Wörtern."""
 
 all_distances = []
 distance_by_block = defaultdict(list)
 
 for identity in identities:
 identity_upper = identity.upper()
 found_words = []
 
 for word in known_words:
 pos = identity_upper.find(word)
 if pos != -1:
 found_words.append({
 "word": word,
 "position": pos,
 "length": len(word)
 })
 
 found_words.sort(key=lambda x: x["position"])
 
 # Berechne Distanzen zwischen benachbarten Wörtern
 for i in range(len(found_words) - 1):
 word1 = found_words[i]
 word2 = found_words[i + 1]
 distance = word2["position"] - (word1["position"] + word1["length"])
 
 if 0 <= distance <= 20:
 all_distances.append(distance)
 
 # Block-Zuordnung
 mid_pos = (word1["position"] + word2["position"]) // 2
 if 0 <= mid_pos <= 13:
 distance_by_block["block_0_13"].append(distance)
 elif 14 <= mid_pos <= 27:
 distance_by_block["block_14_27"].append(distance)
 elif 28 <= mid_pos <= 41:
 distance_by_block["block_28_41"].append(distance)
 elif 42 <= mid_pos <= 55:
 distance_by_block["block_42_55"].append(distance)
 
 # Statistik
 distance_counter = Counter(all_distances)
 
 return {
 "all_distances": all_distances,
 "distance_distribution": dict(distance_counter),
 "distance_by_block": {k: list(v) for k, v in distance_by_block.items()},
 "statistics": {
 "total": len(all_distances),
 "min": min(all_distances) if all_distances else 0,
 "max": max(all_distances) if all_distances else 0,
 "avg": sum(all_distances) / len(all_distances) if all_distances else 0,
 "most_common": distance_counter.most_common(10) if distance_counter else []
 }
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("DISTANZ-ANALYSE VERTIEFEN")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Daten...")
 known_words = load_known_words()
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_identities = [e.get("layer3_identity", "") for e in layer3_data.get("results", []) if len(e.get("layer3_identity", "")) == 60]
 print(f"✅ {len(layer3_identities)} Identities geloadn")
 print()
 
 # Analyze Distanzen
 print("🔍 Analyze Distanzen...")
 distance_analysis = analyze_distances(layer3_identities, known_words)
 print("✅ Distanz-Analyse abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 stats = distance_analysis["statistics"]
 print("📊 Distanz-Statistiken:")
 print(f" Total Distanzen: {stats['total']}")
 print(f" Durchschnitt: {stats['avg']:.2f}")
 print(f" Min: {stats['min']}, Max: {stats['max']}")
 print()
 print("📊 Häufigste Distanzen:")
 for dist, count in stats["most_common"]:
 print(f" {dist} Zeichen: {count}x")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_file = OUTPUT_DIR / "distance_patterns_analysis.json"
 with output_file.open("w") as f:
 json.dump({
 "timestamp": datetime.now().isoformat(),
 "analysis": distance_analysis
 }, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

