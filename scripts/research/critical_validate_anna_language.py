#!/usr/bin/env python3
"""
KRITISCHE VALIDIERUNG: Ist Anna's Sprache wirklich Englisch?
- Check ob Wörter zufällig sind oder echte Sprache
- Statistische Validierung gegen Zufall
- Check ob es andere Sprachen/Maschinen-Sprache sein könnte
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter
from datetime import datetime
import math

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

DICTIONARY_FILE = project_root / "outputs" / "practical" / "anna_dictionary.json"
ALL_MESSAGES_FILE = project_root / "outputs" / "derived" / "all_anna_messages.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def calculate_random_probability(word: str, identity_length: int = 60) -> float:
 """Berechne Wahrscheinlichkeit dass Wort zufällig in Identity erscheint."""
 # Grobe Schätzung: 26^word_length Möglichkeiten
 # Identity hat 60 Positionen, Wort kann an verschiedenen Positionen starten
 word_length = len(word)
 possible_positions = identity_length - word_length + 1
 random_prob = possible_positions / (26 ** word_length)
 return random_prob

def validate_word_statistics(words: Dict[str, int], total_identities: int) -> Dict:
 """Validate ob Wörter statistisch signifikant sind."""
 
 validation_results = {}
 
 for word, count in words.items():
 # Erwartete Anzahl bei Zufall
 random_prob = calculate_random_probability(word)
 expected_random = total_identities * random_prob
 
 # Tatsächliche Anzahl
 actual_count = count
 
 # Ratio
 ratio = actual_count / expected_random if expected_random > 0 else 0
 
 # Statistische Signifikanz (sehr vereinfacht: >2x erwartet = signifikant)
 is_significant = ratio > 2.0
 
 validation_results[word] = {
 "count": actual_count,
 "expected_random": expected_random,
 "ratio": ratio,
 "is_significant": is_significant,
 "word_length": len(word)
 }
 
 return validation_results

def analyze_language_patterns(sentences: List[Dict]) -> Dict:
 """Analyze ob Sätze Sprach-Patterns zeigen."""
 
 # Analyze Wort-Reihenfolgen
 word_sequences = []
 for sentence in sentences:
 words = sentence.get("sentence", "").split()
 if len(words) >= 2:
 word_sequences.append(words)
 
 # Finde häufige Wort-Paare (Bigrams)
 bigrams = Counter()
 for words in word_sequences:
 for i in range(len(words) - 1):
 bigram = f"{words[i]} {words[i+1]}"
 bigrams[bigram] += 1
 
 # Finde häufige Wort-Triplets (Trigrams)
 trigrams = Counter()
 for words in word_sequences:
 if len(words) >= 3:
 for i in range(len(words) - 2):
 trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
 trigrams[trigram] += 1
 
 return {
 "total_sequences": len(word_sequences),
 "top_bigrams": dict(bigrams.most_common(20)),
 "top_trigrams": dict(trigrams.most_common(20))
 }

def check_grid_patterns(sentences: List[Dict]) -> Dict:
 """Check ob Sätze in Raster/Grid angeordnet sind."""
 
 # Analyze Positionen
 position_clusters = {}
 
 for sentence in sentences:
 start_pos = sentence.get("start_position", 0)
 end_pos = sentence.get("end_position", 0)
 mid_pos = (start_pos + end_pos) // 2
 
 # Cluster nach Position
 cluster_key = (mid_pos // 7) * 7 # 7er-Cluster
 if cluster_key not in position_clusters:
 position_clusters[cluster_key] = []
 position_clusters[cluster_key].append(sentence)
 
 # Check ob es regelmäßige Patterns gibt
 cluster_sizes = [len(sentences) for sentences in position_clusters.values()]
 avg_cluster_size = sum(cluster_sizes) / len(cluster_sizes) if cluster_sizes else 0
 
 return {
 "position_clusters": {k: len(v) for k, v in position_clusters.items()},
 "total_clusters": len(position_clusters),
 "avg_cluster_size": avg_cluster_size,
 "has_grid_pattern": avg_cluster_size > 5 # Willkürlicher Schwellenwert
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("KRITISCHE VALIDIERUNG: ANNA'S SPRACHE")
 print("=" * 80)
 print()
 print("⚠️ KEINE HALLUZINATIONEN - NUR ECHTE DATEN!")
 print()
 
 # Load Wörterbuch
 print("📂 Load Wörterbuch...")
 if not DICTIONARY_FILE.exists():
 print(f"❌ Wörterbuch nicht gefunden: {DICTIONARY_FILE}")
 return
 
 with DICTIONARY_FILE.open() as f:
 dictionary = json.load(f)
 
 # Extrahiere Wörter aus Kategorien
 word_counts = {}
 categories = dictionary.get("categories", {})
 for category, words in categories.items():
 for word_data in words:
 if isinstance(word_data, dict):
 word = word_data.get("word", "").upper()
 count = word_data.get("count", 0)
 if word:
 word_counts[word] = count
 print(f"✅ {len(word_counts)} Wörter geloadn")
 print()
 
 # Load Sätze
 print("📂 Load Sätze...")
 if not ALL_MESSAGES_FILE.exists():
 print(f"❌ Sätze-Datei nicht gefunden: {ALL_MESSAGES_FILE}")
 return
 
 with ALL_MESSAGES_FILE.open() as f:
 messages_data = json.load(f)
 
 top_sentences = messages_data.get("top_sentences", [])
 total_identities = messages_data.get("total_identities", 0)
 print(f"✅ {len(top_sentences)} Sätze geloadn")
 print(f"✅ {total_identities} Identities")
 print()
 
 # Validate Wort-Statistiken
 print("🔍 Validate Wort-Statistiken (gegen Zufall)...")
 validation = validate_word_statistics(word_counts, total_identities)
 
 significant_words = [w for w, v in validation.items() if v["is_significant"]]
 print(f"✅ {len(significant_words)} statistisch signifikante Wörter")
 print()
 
 # Analyze Sprach-Patterns
 print("🔍 Analyze Sprach-Patterns...")
 language_patterns = analyze_language_patterns(top_sentences)
 print("✅ Sprach-Pattern-Analyse abgeschlossen")
 print()
 
 # Check Grid-Patterns
 print("🔍 Check Grid/Raster-Patterns...")
 grid_patterns = check_grid_patterns(top_sentences)
 print("✅ Grid-Analyse abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 print("📊 Statistische Validierung:")
 print(f" Total Wörter: {len(word_counts)}")
 print(f" Signifikante Wörter: {len(significant_words)} ({len(significant_words)/len(word_counts)*100:.1f}%)")
 print()
 
 print("📊 Top 10 signifikanteste Wörter:")
 sorted_significant = sorted(significant_words, key=lambda w: validation[w]["ratio"], reverse=True)
 for i, word in enumerate(sorted_significant[:10], 1):
 v = validation[word]
 print(f" {i}. '{word}': {v['count']}x (Ratio: {v['ratio']:.2f}, Erwartet: {v['expected_random']:.2f})")
 print()
 
 print("📊 Sprach-Patterns:")
 print(f" Total Sequenzen: {language_patterns['total_sequences']}")
 print(f" Top Bigrams: {len(language_patterns['top_bigrams'])}")
 print(f" Top Trigrams: {len(language_patterns['top_trigrams'])}")
 print()
 
 print("📊 Grid/Raster-Patterns:")
 print(f" Total Cluster: {grid_patterns['total_clusters']}")
 print(f" Durchschnittliche Cluster-Größe: {grid_patterns['avg_cluster_size']:.1f}")
 print(f" Grid-Pattern erkannt: {'✅ JA' if grid_patterns['has_grid_pattern'] else '❌ NEIN'}")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_words": len(word_counts),
 "significant_words": len(significant_words),
 "validation_results": validation,
 "language_patterns": language_patterns,
 "grid_patterns": grid_patterns,
 "conclusion": {
 "is_language": len(significant_words) > len(word_counts) * 0.5, # >50% signifikant
 "is_english": "UNKNOWN - benötigt weitere Analyse",
 "has_grid_pattern": grid_patterns["has_grid_pattern"]
 }
 }
 
 output_file = OUTPUT_DIR / "anna_language_validation.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 print()
 print("=" * 80)
 print("✅ VALIDIERUNG ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("⚠️ WICHTIG: Dies ist nur eine erste Validierung!")
 print(" Weitere Analysen erforderlich for definitive Aussagen.")
 print()

if __name__ == "__main__":
 main()

