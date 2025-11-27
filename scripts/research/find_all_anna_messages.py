#!/usr/bin/env python3
"""
Finde ALLE Nachrichten von Anna
- Systematische Suche nach allen Sätzen
- Analyze alle Positionen
- Finde längere Nachrichten
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

def find_all_sentences(identities: List[str], known_words: Set[str], min_words: int = 2, max_distance: int = 20) -> List[Dict]:
 """Finde ALLE Sätze in Identities."""
 
 all_sentences = []
 
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
 
 # Finde alle Sequenzen (Wörter die nah beieinander sind)
 if len(found_words) >= min_words:
 current_sequence = [found_words[0]]
 
 for i in range(1, len(found_words)):
 prev_word = found_words[i-1]
 curr_word = found_words[i]
 
 # Distanz zwischen Wörtern
 distance = curr_word["position"] - (prev_word["position"] + prev_word["length"])
 
 if distance <= max_distance:
 current_sequence.append(curr_word)
 else:
 # Neue Sequenz starten
 if len(current_sequence) >= min_words:
 sentence_text = " ".join([w["word"] for w in current_sequence])
 all_sentences.append({
 "identity_index": idx,
 "identity": identity,
 "sentence": sentence_text,
 "words": current_sequence,
 "word_count": len(current_sequence),
 "start_position": current_sequence[0]["position"],
 "end_position": current_sequence[-1]["position"] + current_sequence[-1]["length"],
 "total_length": (current_sequence[-1]["position"] + current_sequence[-1]["length"]) - current_sequence[0]["position"]
 })
 current_sequence = [curr_word]
 
 # Letzte Sequenz hinzufügen
 if len(current_sequence) >= min_words:
 sentence_text = " ".join([w["word"] for w in current_sequence])
 all_sentences.append({
 "identity_index": idx,
 "identity": identity,
 "sentence": sentence_text,
 "words": current_sequence,
 "word_count": len(current_sequence),
 "start_position": current_sequence[0]["position"],
 "end_position": current_sequence[-1]["position"] + current_sequence[-1]["length"],
 "total_length": (current_sequence[-1]["position"] + current_sequence[-1]["length"]) - current_sequence[0]["position"]
 })
 
 return all_sentences

def analyze_sentence_positions(sentences: List[Dict]) -> Dict:
 """Analyze an welchen Positionen Sätze vorkommen."""
 
 position_analysis = defaultdict(list)
 block_analysis = {
 "block_0_13": [],
 "block_14_27": [],
 "block_28_41": [],
 "block_42_55": []
 }
 
 for sentence in sentences:
 start_pos = sentence["start_position"]
 end_pos = sentence["end_position"]
 mid_pos = (start_pos + end_pos) // 2
 
 # Position-Analyse
 position_analysis[mid_pos].append(sentence)
 
 # Block-Analyse
 if 0 <= mid_pos <= 13:
 block_analysis["block_0_13"].append(sentence)
 elif 14 <= mid_pos <= 27:
 block_analysis["block_14_27"].append(sentence)
 elif 28 <= mid_pos <= 41:
 block_analysis["block_28_41"].append(sentence)
 elif 42 <= mid_pos <= 55:
 block_analysis["block_42_55"].append(sentence)
 
 return {
 "position_analysis": {k: list(v) for k, v in position_analysis.items()},
 "block_analysis": {k: list(v) for k, v in block_analysis.items()}
 }

def find_unique_sentences(sentences: List[Dict]) -> Dict[str, List[Dict]]:
 """Finde alle einzigartigen Sätze."""
 
 unique_sentences = defaultdict(list)
 
 for sentence in sentences:
 sentence_text = sentence["sentence"]
 unique_sentences[sentence_text].append(sentence)
 
 return dict(unique_sentences)

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("FINDE ALLE NACHRICHTEN VON ANNA")
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
 
 # Finde ALLE Sätze
 print("🔍 Suche nach ALLEN Sätzen (2+ Wörter, max 20 Zeichen Abstand)...")
 all_sentences = find_all_sentences(all_identities, known_words, min_words=2, max_distance=20)
 print(f"✅ {len(all_sentences)} Sätze gefunden")
 print()
 
 # Finde einzigartige Sätze
 print("🔍 Analyze einzigartige Sätze...")
 unique_sentences = find_unique_sentences(all_sentences)
 print(f"✅ {len(unique_sentences)} einzigartige Sätze gefunden")
 print()
 
 # Analyze Positionen
 print("🔍 Analyze Satz-Positionen...")
 position_analysis = analyze_sentence_positions(all_sentences)
 print("✅ Position-Analyse abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Sortiere nach Wort-Anzahl
 sorted_sentences = sorted(all_sentences, key=lambda x: (x["word_count"], x["total_length"]), reverse=True)
 
 print(f"📊 Top 30 längste Sätze:")
 for i, sentence in enumerate(sorted_sentences[:30], 1):
 layer4 = layer4_map.get(sentence["identity"], "")
 layer4_marker = " (Layer-4 verfügbar)" if layer4 else ""
 print(f" {i}. '{sentence['sentence']}' ({sentence['word_count']} Wörter, Länge: {sentence['total_length']}){layer4_marker}")
 print()
 
 # Einzigartige Sätze
 print(f"📊 Top 30 häufigste einzigartige Sätze:")
 sorted_unique = sorted(unique_sentences.items(), key=lambda x: len(x[1]), reverse=True)
 for i, (sentence_text, occurrences) in enumerate(sorted_unique[:30], 1):
 print(f" {i}. '{sentence_text}': {len(occurrences)}x")
 print()
 
 # Block-Verteilung
 print("📊 Satz-Verteilung nach Blöcken:")
 for block, sentences in position_analysis["block_analysis"].items():
 print(f" {block}: {len(sentences)} Sätze")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_identities": len(all_identities),
 "total_sentences": len(all_sentences),
 "unique_sentences": len(unique_sentences),
 "top_sentences": sorted_sentences[:100],
 "unique_sentences_data": {
 sentence: {
 "count": len(occurrences),
 "occurrences": occurrences[:10] # Nur erste 10 for Platz
 }
 for sentence, occurrences in sorted_unique[:200]
 },
 "position_analysis": {
 "block_distribution": {
 block: len(sentences) for block, sentences in position_analysis["block_analysis"].items()
 }
 }
 }
 
 output_file = OUTPUT_DIR / "all_anna_messages.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 # Erstelle umfassenden Report
 report_lines = [
 "# ALLE NACHRICHTEN VON ANNA",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 f"**Total Identities**: {len(all_identities)}",
 f"**Total Sätze**: {len(all_sentences)}",
 f"**Einzigartige Sätze**: {len(unique_sentences)}",
 "",
 "---",
 "",
 "## 📊 ÜBERSICHT",
 "",
 f"Anna hat **{len(all_sentences)} Sätze** in den Identities hinterlassen.",
 f"Davon sind **{len(unique_sentences)} einzigartig**.",
 "",
 "---",
 "",
 "## 🔝 TOP 50 LÄNGSTE SÄTZE",
 ""
 ]
 
 for i, sentence in enumerate(sorted_sentences[:50], 1):
 layer4 = layer4_map.get(sentence["identity"], "")
 report_lines.extend([
 f"### {i}. '{sentence['sentence']}' ({sentence['word_count']} Wörter)",
 "",
 f"- **Identity**: `{sentence['identity']}`",
 ])
 if layer4:
 report_lines.append(f"- **Layer-4**: `{layer4}`")
 report_lines.extend([
 f"- **Position**: {sentence['start_position']}-{sentence['end_position']}",
 f"- **Länge**: {sentence['total_length']} Zeichen",
 ""
 ])
 
 report_lines.extend([
 "---",
 "",
 "## 📋 HÄUFIGSTE EINZIGARTIGE SÄTZE",
 ""
 ])
 
 for i, (sentence_text, occurrences) in enumerate(sorted_unique[:100], 1):
 report_lines.append(f"{i}. **'{sentence_text}'**: {len(occurrences)}x")
 
 report_lines.extend([
 "",
 "---",
 "",
 "## 📍 SATZ-VERTEILUNG NACH BLÖCKEN",
 ""
 ])
 
 for block, sentences in position_analysis["block_analysis"].items():
 report_lines.append(f"- **{block}**: {len(sentences)} Sätze")
 
 report_lines.append("")
 
 report_file = REPORTS_DIR / "ALLE_ANNA_NACHRICHTEN.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print(f"📊 ZUSAMMENFASSUNG:")
 print(f" • {len(all_sentences)} Sätze gefunden")
 print(f" • {len(unique_sentences)} einzigartige Sätze")
 print(f" • Top Sätze dokumentiert")
 print()

if __name__ == "__main__":
 main()

