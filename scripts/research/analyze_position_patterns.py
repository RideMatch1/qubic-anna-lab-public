#!/usr/bin/env python3
"""
Position-Analyse - Warum sind Wörter an bestimmten Positionen?
- Analyze Position-Verteilungen
- Finde strukturelle Patterns
- Verstehe Matrix-Beziehungen
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter, defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
DICTIONARY_FILE = project_root / "outputs" / "practical" / "anna_dictionary.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_known_words() -> Set[str]:
 """Load bekannte Wörter aus Wörterbuch."""
 known_words = set()
 
 if DICTIONARY_FILE.exists():
 with DICTIONARY_FILE.open() as f:
 dictionary = json.load(f)
 all_words = dictionary.get("all_words", {})
 known_words = {word.upper() for word in all_words.keys()}
 
 return known_words

def analyze_word_positions(identities: List[str], known_words: Set[str]) -> Dict:
 """Analyze Position-Verteilungen for alle Wörter."""
 
 position_data = defaultdict(lambda: defaultdict(int)) # word -> position -> count
 
 for identity in identities:
 identity_upper = identity.upper()
 
 for word in known_words:
 pos = identity_upper.find(word)
 if pos != -1:
 position_data[word][pos] += 1
 
 # Analyze for jedes Wort
 analysis = {}
 
 for word, positions in position_data.items():
 total = sum(positions.values())
 if total == 0:
 continue
 
 # Häufigste Positionen
 sorted_positions = sorted(positions.items(), key=lambda x: x[1], reverse=True)
 top_positions = sorted_positions[:10]
 
 # Durchschnittliche Position
 avg_position = sum(pos * count for pos, count in positions.items()) / total
 
 # Position-Verteilung (0-13, 14-27, 28-41, 42-55, 56-59)
 block_distribution = {
 "0-13": sum(count for pos, count in positions.items() if 0 <= pos <= 13),
 "14-27": sum(count for pos, count in positions.items() if 14 <= pos <= 27),
 "28-41": sum(count for pos, count in positions.items() if 28 <= pos <= 41),
 "42-55": sum(count for pos, count in positions.items() if 42 <= pos <= 55),
 "56-59": sum(count for pos, count in positions.items() if 56 <= pos <= 59)
 }
 
 analysis[word] = {
 "total_count": total,
 "avg_position": avg_position,
 "top_positions": top_positions,
 "block_distribution": block_distribution,
 "position_range": (min(positions.keys()), max(positions.keys()))
 }
 
 return analysis

def analyze_structural_patterns(position_analysis: Dict) -> Dict:
 """Analyze strukturelle Patterns in Positionen."""
 
 patterns = {
 "block_end_positions": defaultdict(list), # Position 13, 27, 41, 55
 "block_start_positions": defaultdict(list), # Position 0, 14, 28, 42
 "middle_positions": defaultdict(list), # Position 30 (Mitte)
 "checksum_area": defaultdict(list) # Position 56-59
 }
 
 for word, data in position_analysis.items():
 top_positions = [pos for pos, _ in data["top_positions"][:3]]
 
 # Block-Ende-Positionen (13, 27, 41, 55)
 for pos in top_positions:
 if pos in [13, 27, 41, 55]:
 patterns["block_end_positions"][pos].append(word)
 
 # Block-Start-Positionen (0, 14, 28, 42)
 for pos in top_positions:
 if pos in [0, 14, 28, 42]:
 patterns["block_start_positions"][pos].append(word)
 
 # Mitte (Position 30)
 for pos in top_positions:
 if 28 <= pos <= 32: # Um Position 30
 patterns["middle_positions"][pos].append(word)
 
 # Checksum-Bereich (56-59)
 for pos in top_positions:
 if 56 <= pos <= 59:
 patterns["checksum_area"][pos].append(word)
 
 return patterns

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("POSITION-ANALYSE")
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
 
 # Analyze Positionen
 print("🔍 Analyze Position-Verteilungen...")
 position_analysis = analyze_word_positions(layer3_identities, known_words)
 print(f"✅ {len(position_analysis)} Wörter analysiert")
 print()
 
 # Analyze strukturelle Patterns
 print("🔍 Analyze strukturelle Patterns...")
 structural_patterns = analyze_structural_patterns(position_analysis)
 print("✅ Struktur-Analyse abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Top Wörter nach durchschnittlicher Position
 print("📊 Top 20 Wörter (nach durchschnittlicher Position):")
 sorted_by_avg = sorted(position_analysis.items(), key=lambda x: x[1]["avg_position"])
 for i, (word, data) in enumerate(sorted_by_avg[:20], 1):
 print(f" {i}. '{word}': Durchschnitt {data['avg_position']:.1f} (Range: {data['position_range'][0]}-{data['position_range'][1]})")
 print()
 
 # Block-Ende-Positionen
 print("📊 Wörter an Block-Ende-Positionen (13, 27, 41, 55):")
 for pos in [13, 27, 41, 55]:
 words = structural_patterns["block_end_positions"].get(pos, [])
 if words:
 print(f" Position {pos}: {len(words)} Wörter")
 for word in words[:5]:
 count = position_analysis[word]["total_count"]
 print(f" - '{word}' ({count}x)")
 if len(words) > 5:
 print(f" ... und {len(words) - 5} weitere")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_identities": len(layer3_identities),
 "position_analysis": position_analysis,
 "structural_patterns": {
 "block_end_positions": {k: list(v) for k, v in structural_patterns["block_end_positions"].items()},
 "block_start_positions": {k: list(v) for k, v in structural_patterns["block_start_positions"].items()},
 "middle_positions": {k: list(v) for k, v in structural_patterns["middle_positions"].items()},
 "checksum_area": {k: list(v) for k, v in structural_patterns["checksum_area"].items()}
 }
 }
 
 output_file = OUTPUT_DIR / "position_patterns_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

