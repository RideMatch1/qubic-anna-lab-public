#!/usr/bin/env python3
"""
Position-Kombinationen analyzen - Welche Positionen kommen zusammen vor?
- Analyze Kombinationen von Positionen
- Finde strukturelle Zusammenhänge
- Verstehe Block-Strukturen
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

def analyze_position_combinations(identities: List[str], known_words: set) -> Dict:
 """Analyze Position-Kombinationen."""
 
 position_combinations = defaultdict(int)
 position_pairs = defaultdict(int)
 
 for identity in identities:
 identity_upper = identity.upper()
 word_positions = []
 
 for word in known_words:
 pos = identity_upper.find(word)
 if pos != -1:
 word_positions.append(pos)
 
 word_positions.sort()
 
 # Alle Kombinationen von 2 Positionen
 for i in range(len(word_positions)):
 for j in range(i + 1, len(word_positions)):
 pos1, pos2 = word_positions[i], word_positions[j]
 pair_key = tuple(sorted([pos1, pos2]))
 position_pairs[pair_key] += 1
 
 # Block-Kombinationen
 blocks = set()
 for pos in word_positions:
 if 0 <= pos <= 13:
 blocks.add("block_0_13")
 elif 14 <= pos <= 27:
 blocks.add("block_14_27")
 elif 28 <= pos <= 41:
 blocks.add("block_28_41")
 elif 42 <= pos <= 55:
 blocks.add("block_42_55")
 
 if len(blocks) > 1:
 block_key = tuple(sorted(blocks))
 position_combinations[block_key] += 1
 
 return {
 "position_pairs": {f"{k[0]}_{k[1]}": v for k, v in position_pairs.items()},
 "block_combinations": {",".join(k): v for k, v in position_combinations.items()},
 "top_position_pairs": [{"pos1": k[0], "pos2": k[1], "count": v} for k, v in sorted(position_pairs.items(), key=lambda x: x[1], reverse=True)[:50]],
 "top_block_combinations": [{"blocks": list(k), "count": v} for k, v in sorted(position_combinations.items(), key=lambda x: x[1], reverse=True)[:20]]
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("POSITION-KOMBINATIONEN ANALYSIEREN")
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
 
 # Analyze Kombinationen
 print("🔍 Analyze Position-Kombinationen...")
 combination_analysis = analyze_position_combinations(layer3_identities, known_words)
 print("✅ Kombinations-Analyse abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 print("📊 Top 20 Position-Paare:")
 for i, pair_data in enumerate(combination_analysis["top_position_pairs"][:20], 1):
 pos1 = pair_data["pos1"]
 pos2 = pair_data["pos2"]
 count = pair_data["count"]
 print(f" {i}. Position {pos1} + {pos2}: {count}x")
 print()
 
 print("📊 Top Block-Kombinationen:")
 for i, block_data in enumerate(combination_analysis["top_block_combinations"][:10], 1):
 blocks = block_data["blocks"]
 count = block_data["count"]
 print(f" {i}. {', '.join(blocks)}: {count}x")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_file = OUTPUT_DIR / "position_combinations_analysis.json"
 with output_file.open("w") as f:
 json.dump({
 "timestamp": datetime.now().isoformat(),
 "analysis": combination_analysis
 }, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

