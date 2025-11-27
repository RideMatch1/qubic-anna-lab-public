#!/usr/bin/env python3
"""
Suche nach Sätzen/Aussagen von Anna
- Finde längere zusammenhängende Sequenzen
- Suche nach Wörtern die zusammen vorkommen (wie Sätze)
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict, Counter
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
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

def find_word_sequences(identities: List[str], known_words: Set[str], min_words: int = 2, max_distance: int = 15) -> List[Dict]:
 """
 Finde Sequenzen von Wörtern die zusammen vorkommen (wie Sätze).
 min_words: Mindestanzahl Wörter in Sequenz
 max_distance: Maximale Distanz zwischen Wörtern
 """
 sequences = []
 
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
 
 # Finde Sequenzen (Wörter die nah beieinander sind)
 if len(found_words) >= min_words:
 current_sequence = [found_words[0]]
 
 for i in range(1, len(found_words)):
 prev_word = found_words[i-1]
 curr_word = found_words[i]
 
 # Distanz zwischen Wörtern
 distance = curr_word["position"] - (prev_word["position"] + prev_word["length"])
 
 if distance <= max_distance:
 # Füge zu aktueller Sequenz hinzu
 current_sequence.append(curr_word)
 else:
 # Neue Sequenz starten
 if len(current_sequence) >= min_words:
 sequences.append({
 "identity_index": idx,
 "identity": identity,
 "words": current_sequence,
 "start_position": current_sequence[0]["position"],
 "end_position": current_sequence[-1]["position"] + current_sequence[-1]["length"],
 "total_length": (current_sequence[-1]["position"] + current_sequence[-1]["length"]) - current_sequence[0]["position"],
 "word_count": len(current_sequence),
 "sentence": " ".join([w["word"] for w in current_sequence])
 })
 current_sequence = [curr_word]
 
 # Letzte Sequenz hinzufügen
 if len(current_sequence) >= min_words:
 sequences.append({
 "identity_index": idx,
 "identity": identity,
 "words": current_sequence,
 "start_position": current_sequence[0]["position"],
 "end_position": current_sequence[-1]["position"] + current_sequence[-1]["length"],
 "total_length": (current_sequence[-1]["position"] + current_sequence[-1]["length"]) - current_sequence[0]["position"],
 "word_count": len(current_sequence),
 "sentence": " ".join([w["word"] for w in current_sequence])
 })
 
 # Sortiere nach Anzahl Wörter und Länge
 sequences.sort(key=lambda x: (x["word_count"], x["total_length"]), reverse=True)
 
 return sequences

def find_common_sentence_patterns(sequences: List[Dict]) -> Dict[str, int]:
 """Finde häufige Satz-Patterns."""
 patterns = Counter()
 
 for seq in sequences:
 sentence = seq["sentence"]
 patterns[sentence] += 1
 
 return dict(patterns)

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("SUCHE NACH SÄTZEN/AUSSAGEN VON ANNA")
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
 
 layer4_identities = []
 layer4_map = {}
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 layer4_identities = [e.get("layer4_identity", "") for e in layer4_results if len(e.get("layer4_identity", "")) == 60]
 for entry in layer4_results:
 layer3_id = entry.get("layer3_identity", "")
 layer4_id = entry.get("layer4_identity", "")
 if len(layer3_id) == 60 and len(layer4_id) == 60:
 layer4_map[layer3_id] = layer4_id
 
 all_identities = layer3_identities + layer4_identities
 print(f"✅ {len(all_identities)} Identities geloadn")
 print()
 
 # Finde Wort-Sequenzen (2+ Wörter, max 15 Zeichen Abstand)
 print("🔍 Suche nach Wort-Sequenzen (2+ Wörter, max 15 Zeichen Abstand)...")
 sequences = find_word_sequences(all_identities, known_words, min_words=2, max_distance=15)
 print(f"✅ {len(sequences)} Sequenzen gefunden")
 print()
 
 # Finde häufige Patterns
 print("🔍 Analyze häufige Satz-Patterns...")
 patterns = find_common_sentence_patterns(sequences)
 print(f"✅ {len(patterns)} verschiedene Patterns gefunden")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Top Sequenzen (nach Anzahl Wörter)
 print("📊 Top 20 Sequenzen (nach Anzahl Wörter):")
 for i, seq in enumerate(sequences[:20], 1):
 layer4 = layer4_map.get(seq["identity"], "")
 layer4_marker = " (Layer-4 verfügbar)" if layer4 else ""
 print(f" {i}. '{seq['sentence']}' ({seq['word_count']} Wörter, Länge: {seq['total_length']}){layer4_marker}")
 print(f" Identity: {seq['identity']}")
 if layer4:
 print(f" Layer-4: {layer4}")
 print()
 
 # Häufige Patterns
 print("📊 Top 20 häufige Satz-Patterns:")
 sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
 for i, (pattern, count) in enumerate(sorted_patterns[:20], 1):
 print(f" {i}. '{pattern}': {count}x")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_identities": len(all_identities),
 "total_sequences": len(sequences),
 "top_sequences": sequences[:100],
 "common_patterns": dict(sorted_patterns[:50])
 }
 
 output_file = OUTPUT_DIR / "anna_sentences_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Suche nach Sätzen/Aussagen von Anna",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 f"**Total Identities**: {len(all_identities)}",
 f"**Total Sequenzen**: {len(sequences)}",
 "",
 "## Top Sequenzen (nach Anzahl Wörter)",
 ""
 ]
 
 for i, seq in enumerate(sequences[:30], 1):
 layer4 = layer4_map.get(seq["identity"], "")
 report_lines.append(f"### {i}. '{seq['sentence']}' ({seq['word_count']} Wörter)")
 report_lines.append(f"- Identity: `{seq['identity']}`")
 if layer4:
 report_lines.append(f"- Layer-4: `{layer4}`")
 report_lines.append(f"- Position: {seq['start_position']}-{seq['end_position']}")
 report_lines.append("")
 
 report_lines.extend([
 "## Häufige Satz-Patterns",
 ""
 ])
 
 for pattern, count in sorted_patterns[:30]:
 report_lines.append(f"- **'{pattern}'**: {count}x")
 
 report_lines.append("")
 
 report_file = REPORTS_DIR / "anna_sentences_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

