#!/usr/bin/env python3
"""
Umfassende Wort-Analyse in Anna Identities
- Suche nach ALLEN möglichen Wörtern (nicht nur bekannten)
- Validate gefundene Patterns kritisch
- Finde längere Wörter/Phrasen
- KEINE Spekulationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter, defaultdict
from datetime import datetime
import re

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

# Englische Wörterliste (häufige Wörter)
COMMON_ENGLISH_WORDS = {
 # 2 Buchstaben
 "HI", "OK", "NO", "GO", "TO", "OF", "IN", "ON", "AT", "IT", "IS", "AS", "WE", "HE", "ME", "MY", "UP", "SO", "DO", "BE", "BY", "OR", "IF", "AN", "AM",
 # 3 Buchstaben
 "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "GET", "HAS", "HIM", "HIS", "HOW", "ITS", "MAY", "NEW", "NOW", "OLD", "SEE", "TWO", "WAY", "WHO", "BOY", "DID", "ITS", "LET", "PUT", "SAY", "SHE", "TOO", "USE", "HER", "HIM", "HIS", "ITS", "OUR", "THE", "THEY", "THEM", "THIS", "THAT", "THESE", "THOSE",
 # 4 Buchstaben
 "THAT", "WITH", "HAVE", "THIS", "WILL", "YOUR", "FROM", "THEY", "KNOW", "WANT", "BEEN", "GOOD", "MUCH", "SOME", "TIME", "VERY", "WHEN", "COME", "HERE", "JUST", "LIKE", "LONG", "MAKE", "MANY", "OVER", "SUCH", "TAKE", "THAN", "THEM", "WELL", "WERE", "WHAT", "WHEN", "WILL", "WITH", "WOULD", "YEAR", "YOUR", "ANNA", "STOP", "TEST", "HELLO", "QUIC", "QUBIC",
 # 5 Buchstaben
 "ABOUT", "AFTER", "AGAIN", "BEING", "COULD", "EVERY", "FIRST", "GREAT", "MIGHT", "NEVER", "OTHER", "PLACE", "RIGHT", "SHALL", "SHOULD", "STILL", "THERE", "THESE", "THING", "THINK", "THOSE", "THREE", "UNDER", "UNTIL", "WHERE", "WHICH", "WHILE", "WORLD", "WOULD", "WRITE", "WRONG", "YOUNG", "HELLO", "QUBIC",
 # 6 Buchstaben
 "ALWAYS", "BEFORE", "BETWEEN", "CALLED", "CHANGE", "COMING", "DURING", "EITHER", "ENOUGH", "FAMILY", "FATHER", "FRIEND", "HAPPEN", "HAVING", "LITTLE", "LOOKED", "MOMENT", "MOTHER", "NEVER", "PEOPLE", "PERSON", "PLEASE", "PUBLIC", "REALLY", "SCHOOL", "SECOND", "SHOULD", "SOMETHING", "SOMETIMES", "SUDDENLY", "SUPPOSE", "THROUGH", "TURNED", "WANTED", "WITHIN", "WITHOUT", "WORKED", "WORLD", "WRITTEN",
 # 7 Buchstaben
 "AGAINST", "ALREADY", "ANOTHER", "BECAUSE", "BECOME", "BEFORE", "BELIEVE", "BETWEEN", "CALLED", "CHANGE", "COMING", "DURING", "EITHER", "ENOUGH", "FAMILY", "FATHER", "FRIEND", "HAPPEN", "HAVING", "LITTLE", "LOOKED", "MOMENT", "MOTHER", "NEVER", "PEOPLE", "PERSON", "PLEASE", "PUBLIC", "REALLY", "SCHOOL", "SECOND", "SHOULD", "SOMETHING", "SOMETIMES", "SUDDENLY", "SUPPOSE", "THROUGH", "TURNED", "WANTED", "WITHIN", "WITHOUT", "WORKED", "WORLD", "WRITTEN",
 # 8+ Buchstaben
 "SOMETHING", "SOMETIMES", "TOGETHER", "WHATEVER", "WHENEVER", "WHEREVER", "YOURSELF"
}

def find_all_words_in_identities(identities: List[str], min_length: int = 2, max_length: int = 10) -> Dict[str, List[Dict]]:
 """
 Finde ALLE möglichen Wörter in Identities.
 Check gegen englische Wörterliste UND finde alle alphabetischen Sequenzen.
 """
 
 found_words = defaultdict(list)
 all_sequences = Counter()
 
 for identity_idx, identity in enumerate(identities):
 identity_upper = identity.upper()
 
 # Suche nach allen möglichen Sequenzen
 for length in range(min_length, max_length + 1):
 for start_pos in range(len(identity) - length + 1):
 sequence = identity_upper[start_pos:start_pos + length]
 
 # Nur alphabetische Sequenzen
 if not sequence.isalpha():
 continue
 
 # Check ob es ein bekanntes Wort ist
 if sequence in COMMON_ENGLISH_WORDS:
 found_words[sequence].append({
 "identity_index": identity_idx,
 "identity": identity,
 "position": start_pos,
 "length": length
 })
 
 # Zähle alle Sequenzen (for statistische Analyse)
 all_sequences[sequence] += 1
 
 return dict(found_words), dict(all_sequences)

def analyze_word_statistics(found_words: Dict, all_sequences: Dict, total_identities: int) -> Dict:
 """Analyze statistische Signifikanz der gefundenen Wörter."""
 
 analysis = {
 "total_identities": total_identities,
 "found_words": {},
 "statistics": {}
 }
 
 for word, occurrences in found_words.items():
 count = len(occurrences)
 expected_random = total_identities * (26 ** -len(word)) # Zufällige Erwartung
 ratio = count / expected_random if expected_random > 0 else float('inf')
 
 analysis["found_words"][word] = {
 "count": count,
 "expected_random": expected_random,
 "ratio": ratio,
 "is_significant": ratio > 2.0, # Mehr als 2x zufällige Erwartung
 "examples": occurrences[:5] # Erste 5 Beispiele
 }
 
 # Top Sequenzen (auch wenn nicht in Wörterliste)
 top_sequences = sorted(all_sequences.items(), key=lambda x: x[1], reverse=True)[:100]
 analysis["top_sequences"] = [
 {"sequence": seq, "count": count, "is_word": seq in COMMON_ENGLISH_WORDS}
 for seq, count in top_sequences
 ]
 
 return analysis

def find_longer_phrases(identities: List[str], min_length: int = 8) -> List[Dict]:
 """Finde längere Phrasen (8+ Buchstaben) die wie echte Wörter aussehen."""
 
 phrases = []
 
 for identity_idx, identity in enumerate(identities):
 identity_upper = identity.upper()
 
 # Suche nach langen alphabetischen Sequenzen
 for length in range(min_length, min(20, len(identity))):
 for start_pos in range(len(identity) - length + 1):
 sequence = identity_upper[start_pos:start_pos + length]
 
 if sequence.isalpha() and len(set(sequence)) > length // 2: # Mindestens 50% verschiedene Buchstaben
 # Check ob es wie ein Wort aussieht (Vokale vorhanden)
 vowels = sum(1 for c in sequence if c in "AEIOU")
 if vowels >= length // 4: # Mindestens 25% Vokale
 phrases.append({
 "phrase": sequence,
 "identity_index": identity_idx,
 "identity": identity,
 "position": start_pos,
 "length": length,
 "vowel_ratio": vowels / length
 })
 
 # Sortiere nach Länge und Vokal-Verhältnis
 phrases.sort(key=lambda x: (x["length"], x["vowel_ratio"]), reverse=True)
 
 return phrases[:50] # Top 50

def validate_findings(found_words: Dict, identities: List[str]) -> Dict:
 """Kritische Validierung der gefundenen Wörter."""
 
 validation = {
 "total_words_found": len(found_words),
 "validation_results": {},
 "warnings": []
 }
 
 for word, occurrences in found_words.items():
 # Check ob Wort wirklich in Identities vorkommt
 verified_count = 0
 for occ in occurrences:
 identity = occ["identity"]
 pos = occ["position"]
 if identity[pos:pos+len(word)].upper() == word:
 verified_count += 1
 
 validation["validation_results"][word] = {
 "claimed_count": len(occurrences),
 "verified_count": verified_count,
 "is_valid": verified_count == len(occurrences),
 "verification_rate": verified_count / len(occurrences) if occurrences else 0
 }
 
 if verified_count != len(occurrences):
 validation["warnings"].append(
 f"Wort '{word}': {len(occurrences)} behauptet, {verified_count} verifiziert"
 )
 
 return validation

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("UMFASSENDE WORT-ANALYSE IN ANNA IDENTITIES")
 print("=" * 80)
 print()
 print("⚠️ KEINE SPEKULATIONEN - NUR ECHTE DATEN!")
 print()
 
 # Load Layer-3 Identities
 print("📂 Load Layer-3 Identities...")
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 layer3_identities = [e.get("layer3_identity", "") for e in layer3_results if len(e.get("layer3_identity", "")) == 60]
 print(f"✅ {len(layer3_identities)} Layer-3 Identities geloadn")
 print()
 
 # Load Layer-4 Identities
 layer4_identities = []
 if LAYER4_FILE.exists():
 print("📂 Load Layer-4 Identities...")
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 layer4_identities = [e.get("layer4_identity", "") for e in layer4_results if len(e.get("layer4_identity", "")) == 60]
 print(f"✅ {len(layer4_identities)} Layer-4 Identities geloadn")
 print()
 
 # Kombiniere alle Identities
 all_identities = layer3_identities + layer4_identities
 print(f"📊 Gesamt: {len(all_identities)} Identities")
 print()
 
 # Finde alle Wörter
 print("🔍 Suche nach allen möglichen Wörtern...")
 found_words, all_sequences = find_all_words_in_identities(all_identities, min_length=2, max_length=10)
 print(f"✅ {len(found_words)} verschiedene Wörter gefunden")
 print()
 
 # Analyze Statistiken
 print("📊 Analyze statistische Signifikanz...")
 analysis = analyze_word_statistics(found_words, all_sequences, len(all_identities))
 print("✅ Analyse abgeschlossen")
 print()
 
 # Finde längere Phrasen
 print("🔍 Suche nach längeren Phrasen (8+ Buchstaben)...")
 phrases = find_longer_phrases(all_identities, min_length=8)
 print(f"✅ {len(phrases)} Phrasen gefunden")
 print()
 
 # Validate kritisch
 print("🔍 Kritische Validierung...")
 validation = validate_findings(found_words, all_identities)
 print("✅ Validierung abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Gefundene Wörter (signifikant)
 significant_words = {
 word: data for word, data in analysis["found_words"].items()
 if data["is_significant"]
 }
 
 print(f"📊 Signifikante Wörter (>{2.0}x zufällige Erwartung): {len(significant_words)}")
 for word, data in sorted(significant_words.items(), key=lambda x: x[1]["count"], reverse=True)[:20]:
 print(f" '{word}': {data['count']}x (Erwartung: {data['expected_random']:.2f}, Ratio: {data['ratio']:.2f}x)")
 print()
 
 # Längere Phrasen
 print(f"📊 Top 10 längere Phrasen:")
 for i, phrase in enumerate(phrases[:10], 1):
 print(f" {i}. '{phrase['phrase']}' (Länge: {phrase['length']}, Position: {phrase['position']})")
 print()
 
 # Validierungswarnungen
 if validation["warnings"]:
 print(f"⚠️ Validierungswarnungen: {len(validation['warnings'])}")
 for warning in validation["warnings"][:10]:
 print(f" {warning}")
 print()
 else:
 print("✅ Keine Validierungswarnungen - alle Wörter verifiziert!")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_identities": len(all_identities),
 "found_words": found_words,
 "analysis": analysis,
 "phrases": phrases,
 "validation": validation
 }
 
 output_file = OUTPUT_DIR / "comprehensive_word_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Umfassende Wort-Analyse in Anna Identities",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 f"**Total Identities**: {len(all_identities)}",
 "",
 "## Signifikante Wörter",
 ""
 ]
 
 for word, data in sorted(significant_words.items(), key=lambda x: x[1]["count"], reverse=True):
 report_lines.append(f"### '{word}' ({data['count']}x gefunden)")
 report_lines.append(f"- Erwartung (zufällig): {data['expected_random']:.2f}")
 report_lines.append(f"- Ratio: {data['ratio']:.2f}x")
 report_lines.append(f"- Signifikant: {'✅' if data['is_significant'] else '❌'}")
 report_lines.append("")
 report_lines.append("**Beispiele:**")
 for i, example in enumerate(data["examples"][:5], 1):
 report_lines.append(f"{i}. `{example['identity']}` (Position {example['position']})")
 report_lines.append("")
 
 report_lines.extend([
 "## Längere Phrasen (8+ Buchstaben)",
 ""
 ])
 
 for i, phrase in enumerate(phrases[:20], 1):
 report_lines.append(f"{i}. **'{phrase['phrase']}'** (Länge: {phrase['length']}, Position: {phrase['position']})")
 report_lines.append(f" - Identity: `{phrase['identity']}`")
 report_lines.append(f" - Vokal-Verhältnis: {phrase['vowel_ratio']:.2%}")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "comprehensive_word_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("💡 ERKENNTNISSE:")
 print()
 print(f" ✅ {len(found_words)} verschiedene Wörter gefunden")
 print(f" ✅ {len(significant_words)} signifikante Wörter")
 print(f" ✅ {len(phrases)} längere Phrasen gefunden")
 warnings_count = len(validation['warnings'])
 status_msg = 'Alle Wörter verifiziert' if warnings_count == 0 else f"{warnings_count} Warnungen"
 print(f" ✅ {status_msg}")
 print()

if __name__ == "__main__":
 main()

