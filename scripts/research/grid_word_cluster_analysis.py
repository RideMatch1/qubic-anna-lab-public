#!/usr/bin/env python3
"""
Grid-/Wort-Cluster-Analyse
- verbindet die 7x7-Grid-Struktur mit allen bekannten Anna-Sätzen
- misst Wortdichten je Grid-Zelle/Spalte/Zeile
- findet Cluster (z. B. komplette Sätze in einer Spalte, v. a. Spalte 6)
- kategorisiert Wörter nach Wörterbuch (Themenfelder)
- liefert vollständig reproduzierbare JSON-Daten (keine Halluzinationen)
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

MESSAGES_FILE = project_root / "outputs" / "derived" / "all_anna_messages.json"
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
DICTIONARY_FILE = project_root / "outputs" / "practical" / "anna_dictionary.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

GRID_SIZE = 7
GRID_CELLS = GRID_SIZE * GRID_SIZE
BLOCK_END_POSITIONS = {13, 27, 41, 55}

def load_layer_identities() -> List[str]:
 """Load alle Layer-3 (+ optionale Layer-4) Identities."""
 identities = []

 if not LAYER3_FILE.exists():
 raise FileNotFoundError(f"Layer-3 Datei fehlt: {LAYER3_FILE}")

 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_entries = [
 e.get("layer3_identity", "")
 for e in layer3_data.get("results", [])
 if len(e.get("layer3_identity", "")) == 60
 ]
 identities.extend(layer3_entries)

 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_entries = [
 e.get("layer4_identity", "")
 for e in layer4_data.get("results", [])
 if len(e.get("layer4_identity", "")) == 60
 ]
 identities.extend(layer4_entries)

 return identities

def find_all_sentences(identities: List[str], known_words: Set[str], min_words: int = 2, max_distance: int = 20) -> List[Dict]:
 """Rekonstruiere Sätze direkt aus Identities."""
 sentences: List[Dict] = []

 sorted_words = sorted(known_words, key=lambda w: (-len(w), w))

 for idx, identity in enumerate(identities):
 identity_upper = identity.upper()
 found_words = []

 for word in sorted_words:
 start = 0
 while True:
 pos = identity_upper.find(word, start)
 if pos == -1:
 break
 found_words.append(
 {
 "word": word,
 "position": pos,
 "length": len(word),
 }
 )
 start = pos + 1

 found_words.sort(key=lambda x: (x["position"], -x["length"]))
 if len(found_words) < min_words:
 continue

 current_sequence = [found_words[0]]
 for entry in found_words[1:]:
 prev = current_sequence[-1]
 distance = entry["position"] - (prev["position"] + prev["length"])

 if distance <= max_distance:
 current_sequence.append(entry)
 else:
 if len(current_sequence) >= min_words:
 sentences.append(
 {
 "identity_index": idx,
 "identity": identity,
 "sentence": " ".join(w["word"] for w in current_sequence),
 "words": current_sequence.copy(),
 "word_count": len(current_sequence),
 "start_position": current_sequence[0]["position"],
 "end_position": current_sequence[-1]["position"] + current_sequence[-1]["length"],
 "total_length": (current_sequence[-1]["position"] + current_sequence[-1]["length"]) - current_sequence[0]["position"],
 }
 )
 current_sequence = [entry]

 if len(current_sequence) >= min_words:
 sentences.append(
 {
 "identity_index": idx,
 "identity": identity,
 "sentence": " ".join(w["word"] for w in current_sequence),
 "words": current_sequence.copy(),
 "word_count": len(current_sequence),
 "start_position": current_sequence[0]["position"],
 "end_position": current_sequence[-1]["position"] + current_sequence[-1]["length"],
 "total_length": (current_sequence[-1]["position"] + current_sequence[-1]["length"]) - current_sequence[0]["position"],
 }
 )

 return sentences

def load_sentences(known_words: Set[str]) -> List[Dict]:
 """Load Sätze aus Datei; falls nur Top-100 vorhanden → vollständige Rekonstruktion."""
 if MESSAGES_FILE.exists():
 with MESSAGES_FILE.open() as f:
 data = json.load(f)

 expected = data.get("total_sentences", 0)
 for key in ("all_sentences", "sentences", "top_sentences"):
 sentences = data.get(key)
 if sentences:
 if expected and len(sentences) < expected and key == "top_sentences":
 # Nur Top-Liste -> später fallback
 continue
 return sentences

 print("⚠️ Nur Top-Sätze vorhanden – rekonstruiere komplette Liste aus Identities...")

 print("🔄 Rekonstruiere Sätze direkt aus Layer-Identities...")
 identities = load_layer_identities()
 return find_all_sentences(identities, known_words)

def load_dictionary_categories() -> Tuple[Dict[str, str], Dict[str, int], Set[str]]:
 """
 Load Wörterbuch und mappe jedes Wort auf seine Kategorie.
 Rückgabe:
 - word_to_category: WORD -> Kategorie
 - word_counts: WORD -> Häufigkeit (aus Wörterbuch)
 - known_words: Menge aller verfügbaren Wörter
 """
 if not DICTIONARY_FILE.exists():
 return {}, {}, set()

 with DICTIONARY_FILE.open() as f:
 dictionary = json.load(f)

 word_to_category: Dict[str, str] = {}

 for category, entries in dictionary.get("categories", {}).items():
 for entry in entries:
 word = entry.get("word", "").upper()
 if word:
 word_to_category[word] = category

 all_words = dictionary.get("all_words", {})
 word_counts = {word.upper(): count for word, count in all_words.items()}
 known_words = set(word_counts.keys())
 return word_to_category, word_counts, known_words

def get_grid_coord(position: int) -> Tuple[int, int]:
 """Map Identity-Position (0-59) in 7x7-Grid."""
 if position < 0:
 raise ValueError(f"Ungültige Position: {position}")
 grid_index = position % GRID_CELLS
 row = grid_index // GRID_SIZE
 col = grid_index % GRID_SIZE
 return row, col

def analyze_grid_word_clusters(
 sentences: List[Dict], word_to_category: Dict[str, str], word_counts_dict: Dict[str, int]
) -> Dict:
 """Kernanalyse: verteilt Wörter auf Grid und bildet Cluster."""

 # Strukturen
 grid_cells: Dict[Tuple[int, int], Dict] = defaultdict(
 lambda: {
 "word_counter": Counter(),
 "category_counter": Counter(),
 "identities": set(),
 "sentence_examples": [],
 "positions": [],
 }
 )
 column_word_counter: Dict[int, Counter] = defaultdict(Counter)
 column_category_counter: Dict[int, Counter] = defaultdict(Counter)
 column_identity_counter: Dict[int, Counter] = defaultdict(Counter)
 row_word_counter: Dict[int, Counter] = defaultdict(Counter)
 row_category_counter: Dict[int, Counter] = defaultdict(Counter)
 column_active_rows: Dict[int, Set[int]] = defaultdict(set)
 row_active_cols: Dict[int, Set[int]] = defaultdict(set)

 column_single_sentence_clusters: Dict[int, Counter] = defaultdict(Counter)
 column6_neighbors: Counter = Counter()

 block_end_stats: Dict[int, Dict] = {
 pos: {"word_counter": Counter(), "category_counter": Counter(), "identities": set()}
 for pos in BLOCK_END_POSITIONS
 }

 total_words = 0
 processed_sentences = 0

 for sentence_entry in sentences:
 word_entries = sentence_entry.get("words", [])
 if not word_entries:
 continue

 identity = sentence_entry.get("identity", "")
 sentence_text = sentence_entry.get("sentence", "")

 processed_sentences += 1
 columns_in_sentence: List[int] = []

 for word_info in word_entries:
 word = word_info.get("word", "")
 pos = word_info.get("position")

 if not word or pos is None:
 continue

 word_upper = word.upper()
 row, col = get_grid_coord(int(pos))

 cell = grid_cells[(row, col)]
 cell["word_counter"][word_upper] += 1
 cell["category_counter"][word_to_category.get(word_upper, "Unk")] += 1
 cell["identities"].add(identity)
 cell["positions"].append(int(pos))

 if len(cell["sentence_examples"]) < 3:
 cell["sentence_examples"].append(
 {
 "sentence": sentence_text,
 "identity": identity,
 "word": word_upper,
 "position": int(pos),
 }
 )

 column_word_counter[col][word_upper] += 1
 column_category_counter[col][word_to_category.get(word_upper, "Unk")] += 1
 column_identity_counter[col][identity] += 1
 column_active_rows[col].add(row)

 row_word_counter[row][word_upper] += 1
 row_category_counter[row][word_to_category.get(word_upper, "Unk")] += 1
 row_active_cols[row].add(col)

 if int(pos) in block_end_stats:
 block_end_stats[int(pos)]["word_counter"][word_upper] += 1
 block_end_stats[int(pos)]["category_counter"][
 word_to_category.get(word_upper, "Unk")
 ] += 1
 block_end_stats[int(pos)]["identities"].add(identity)

 columns_in_sentence.append(col)
 total_words += 1

 unique_columns = sorted(set(columns_in_sentence))
 if unique_columns:
 if len(unique_columns) == 1:
 seq = tuple(word_info.get("word", "").upper() for word_info in word_entries if word_info.get("word"))
 if seq:
 column_single_sentence_clusters[unique_columns[0]][seq] += 1
 if 6 in unique_columns:
 for other_col in unique_columns:
 if other_col != 6:
 column6_neighbors[other_col] += 1

 # Grid-Zusammenfassung
 grid_summary = []
 for row in range(GRID_SIZE):
 for col in range(GRID_SIZE):
 cell = grid_cells.get((row, col))
 word_count = sum(cell["word_counter"].values()) if cell else 0
 unique_words = len(cell["word_counter"]) if cell else 0
 top_words = cell["word_counter"].most_common(5) if cell else []
 top_categories = cell["category_counter"].most_common(3) if cell else []
 identity_count = len(cell["identities"]) if cell else 0
 example_sentences = cell["sentence_examples"] if cell else []

 grid_summary.append(
 {
 "grid_coord": [row, col],
 "word_count": word_count,
 "unique_words": unique_words,
 "top_words": [
 {"word": w, "count": c} for w, c in top_words
 ],
 "top_categories": [
 {"category": cat, "count": c} for cat, c in top_categories
 ],
 "identity_count": identity_count,
 "sentence_examples": example_sentences,
 }
 )

 # Spalten-/Zeilen-Summary
 column_summary = {}
 for col in range(GRID_SIZE):
 total = sum(
 entry["word_count"] for entry in grid_summary if entry["grid_coord"][1] == col
 )
 active_rows = len(column_active_rows[col])
 column_summary[col] = {
 "total_words": total,
 "unique_words": len(column_word_counter[col]),
 "top_words": [
 {"word": w, "count": c} for w, c in column_word_counter[col].most_common(10)
 ],
 "top_categories": [
 {"category": cat, "count": c}
 for cat, c in column_category_counter[col].most_common(5)
 ],
 "active_rows": active_rows,
 "row_density_pct": active_rows / GRID_SIZE * 100,
 "top_identities": [
 {"identity": ident, "count": cnt}
 for ident, cnt in column_identity_counter[col].most_common(200)
 ],
 }

 row_summary = {}
 for row in range(GRID_SIZE):
 total = sum(
 entry["word_count"] for entry in grid_summary if entry["grid_coord"][0] == row
 )
 active_cols = len(row_active_cols[row])
 row_summary[row] = {
 "total_words": total,
 "unique_words": len(row_word_counter[row]),
 "top_words": [
 {"word": w, "count": c} for w, c in row_word_counter[row].most_common(10)
 ],
 "top_categories": [
 {"category": cat, "count": c}
 for cat, c in row_category_counter[row].most_common(5)
 ],
 "active_cols": active_cols,
 "col_density_pct": active_cols / GRID_SIZE * 100,
 }

 # Block-Ende
 block_end_summary = []
 for pos in sorted(BLOCK_END_POSITIONS):
 stats = block_end_stats[pos]
 block_end_summary.append(
 {
 "position": pos,
 "top_words": [
 {"word": w, "count": c} for w, c in stats["word_counter"].most_common(8)
 ],
 "top_categories": [
 {"category": cat, "count": c}
 for cat, c in stats["category_counter"].most_common(5)
 ],
 "identity_count": len(stats["identities"]),
 }
 )

 # Cluster-Patterns
 cluster_patterns = []
 for col, counter in column_single_sentence_clusters.items():
 for (words_tuple, count) in counter.most_common(10):
 cluster_patterns.append(
 {
 "column": col,
 "words": list(words_tuple),
 "count": count,
 }
 )

 # Sort Cluster global
 cluster_patterns.sort(key=lambda x: x["count"], reverse=True)

 result = {
 "timestamp": datetime.now().isoformat(),
 "source_file": str(MESSAGES_FILE),
 "total_sentences": processed_sentences,
 "total_words": total_words,
 "grid_summary": grid_summary,
 "column_summary": column_summary,
 "row_summary": row_summary,
 "column6_neighboring_columns": [
 {"column": col, "shared_sentences": count}
 for col, count in column6_neighbors.most_common()
 ],
 "block_end_summary": block_end_summary,
 "cluster_patterns_single_column": cluster_patterns[:25],
 "word_dictionary_size": len(word_counts_dict),
 }
 return result

def main():
 print("=" * 80)
 print("GRID / WORT-CLUSTER ANALYSE (7x7)")
 print("=" * 80)
 print("⚠️ 100% datenbasiert, keine Halluzinationen.\n")

 word_to_category, word_counts_dict, known_words = load_dictionary_categories()
 sentences = load_sentences(known_words)
 print(f"📚 Geloadne Sätze: {len(sentences)}")

 result = analyze_grid_word_clusters(sentences, word_to_category, word_counts_dict)

 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 output_file = OUTPUT_DIR / "grid_word_cluster_analysis.json"
 with output_file.open("w") as f:
 json.dump(result, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")

 print("\nTop 5 Cluster (einzelne Spalte):")
 for entry in result["cluster_patterns_single_column"][:5]:
 print(f" ▸ Spalte {entry['column']}: {' '.join(entry['words'])} ({entry['count']}×)")

 print("\n✅ Analyse abgeschlossen.")

if __name__ == "__main__":
 main()

