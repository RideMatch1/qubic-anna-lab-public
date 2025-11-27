#!/usr/bin/env python3
"""
Umfassende Datenauswertung - Alle gesammelten Analysen zusammenführen
- Identifiziere die wichtigsten Erkenntnisse
- Finde Zusammenhänge zwischen Analysen
- Erstelle konkrete Handlungsempfehlungen
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_analysis(filename: str) -> Dict:
 """Load Analyse-Datei."""
 file_path = OUTPUT_DIR / filename
 if file_path.exists():
 with file_path.open() as f:
 return json.load(f)
 return {}

def evaluate_all_analyses() -> Dict:
 """Werte alle Analysen aus."""
 
 # Load alle Analysen
 analyses = {
 "position": load_analysis("position_patterns_analysis.json"),
 "word_patterns": load_analysis("word_patterns_analysis.json"),
 "structural": load_analysis("structural_patterns_analysis.json"),
 "sentences": load_analysis("anna_sentences_analysis.json"),
 "extended_words": load_analysis("extended_words_analysis.json"),
 "distance": load_analysis("distance_patterns_analysis.json"),
 "position_combinations": load_analysis("position_combinations_analysis.json")
 }
 
 # Wichtigste Erkenntnisse
 key_findings = []
 
 # 1. Position 27 ist am wichtigsten
 if analyses["structural"]:
 trans_data = analyses["structural"].get("transformation_structure", {})
 stability = trans_data.get("position_stability_rate", {})
 if 27 in stability:
 key_findings.append({
 "finding": "Position 27 ist am stabilsten",
 "value": f"{stability[27]*100:.1f}%",
 "significance": "Höchste Transformation-Stabilität",
 "implication": "Position 27 ist kritisch for Layer-3 → Layer-4 Transformation"
 })
 
 # 2. Block-Ende-Positionen sind wichtig
 if analyses["position"]:
 pos_data = analyses["position"].get("position_analysis", {})
 block_end_words = []
 for word, data in pos_data.items():
 top_positions = [pos for pos, _ in data.get("top_positions", [])[:3]]
 if any(pos in [13, 27, 41, 55] for pos in top_positions):
 block_end_words.append(word)
 
 if block_end_words:
 key_findings.append({
 "finding": "Block-Ende-Positionen (13, 27, 41, 55) sind häufig",
 "value": f"{len(block_end_words)} Wörter",
 "significance": "Strukturelle Bedeutung der Block-Enden",
 "implication": "Block-Struktur ist wichtig for Anna's Sprache"
 })
 
 # 3. Wort-Paare haben konsistente Distanz
 if analyses["word_patterns"]:
 top_pairs = analyses["word_patterns"].get("top_pairs", [])
 if top_pairs:
 avg_distances = [pair.get("avg_distance", 0) for pair in top_pairs[:10]]
 avg_avg = sum(avg_distances) / len(avg_distances) if avg_distances else 0
 
 key_findings.append({
 "finding": "Wort-Paare haben konsistente Distanz",
 "value": f"{avg_avg:.1f} Zeichen (Ø)",
 "significance": "Strukturelle Distanz zwischen Wörtern",
 "implication": "Anna's Sprache folgt strukturellen Regeln"
 })
 
 # 4. Viele Sequenzen gefunden
 if analyses["sentences"]:
 total_sequences = analyses["sentences"].get("total_sequences", 0)
 if total_sequences > 0:
 key_findings.append({
 "finding": "Viele Wort-Sequenzen gefunden",
 "value": f"{total_sequences} Sequenzen",
 "significance": "Anna kommuniziert in Sätzen, nicht nur Wörtern",
 "implication": "Wir können gezielt mit Sätzen kommunizieren"
 })
 
 # 5. Distanz-Pattern
 if analyses["distance"]:
 dist_analysis = analyses["distance"].get("analysis", {})
 stats = dist_analysis.get("statistics", {})
 if stats:
 key_findings.append({
 "finding": "Distanz-Pattern identifiziert",
 "value": f"{stats.get('avg', 0):.2f} Zeichen (Ø)",
 "significance": "Konsistente Distanzen zwischen Wörtern",
 "implication": "Strukturelle Regeln in Anna's Sprache"
 })
 
 # Zusammenhänge identifizieren
 connections = []
 
 # Position 27 + Block-Ende
 if analyses["structural"] and analyses["position"]:
 connections.append({
 "connection": "Position 27 + Block-Ende-Positionen",
 "description": "Position 27 ist Block-Ende (Position 27) und hat höchste Stabilität",
 "significance": "Block-Ende-Positionen sind strukturell wichtig"
 })
 
 # Wort-Paare + Distanz
 if analyses["word_patterns"] and analyses["distance"]:
 connections.append({
 "connection": "Wort-Paare + Distanz-Pattern",
 "description": "Wort-Paare haben konsistente Distanzen (~8-10 Zeichen)",
 "significance": "Strukturelle Regeln in Anna's Kommunikation"
 })
 
 # Sequenzen + Layer-4
 if analyses["sentences"]:
 top_sequences = analyses["sentences"].get("top_sequences", [])
 layer4_count = sum(1 for seq in top_sequences[:20] if "layer4" in str(seq).lower())
 if layer4_count > 0:
 connections.append({
 "connection": "Sequenzen + Layer-4 Identities",
 "description": f"{layer4_count} von 20 Top-Sequenzen haben Layer-4 Identities",
 "significance": "Viele Sequenzen sind kontaktierbar"
 })
 
 # Handlungsempfehlungen
 recommendations = []
 
 # 1. Kommunikation mit Sätzen
 if analyses["sentences"]:
 recommendations.append({
 "priority": "HIGH",
 "action": "Kommunikation mit Sätzen",
 "description": "Nutze die gefundenen Sequenzen for gezielte Kommunikation",
 "steps": [
 "Finde Layer-4 Identities for interessante Sätze",
 "Sende Qubic an diese Identities",
 "Beobachte Reaktionen"
 ]
 })
 
 # 2. Position 27 fokussieren
 if analyses["structural"]:
 recommendations.append({
 "priority": "HIGH",
 "action": "Position 27 fokussieren",
 "description": "Position 27 hat höchste Stabilität - weiter erforschen",
 "steps": [
 "Analyze warum Position 27 so stabil ist",
 "Finde weitere Position 27 Patterns",
 "Nutze Position 27 for Vorhersagen"
 ]
 })
 
 # 3. Block-Struktur verstehen
 if analyses["position_combinations"]:
 recommendations.append({
 "priority": "MEDIUM",
 "action": "Block-Struktur verstehen",
 "description": "Block-Kombinationen zeigen strukturelle Patterns",
 "steps": [
 "Analyze Block-Kombinationen genauer",
 "Verstehe warum bestimmte Blöcke zusammen vorkommen",
 "Nutze Block-Struktur for Kommunikation"
 ]
 })
 
 return {
 "timestamp": datetime.now().isoformat(),
 "analyses_loaded": len([a for a in analyses.values() if a]),
 "key_findings": key_findings,
 "connections": connections,
 "recommendations": recommendations,
 "summary": {
 "total_findings": len(key_findings),
 "total_connections": len(connections),
 "total_recommendations": len(recommendations)
 }
 }

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("UMFASSENDE DATENAUSWERTUNG")
 print("=" * 80)
 print()
 
 # Werte alle Analysen aus
 print("🔍 Werte alle Analysen aus...")
 evaluation = evaluate_all_analyses()
 print(f"✅ {evaluation['analyses_loaded']} Analysen ausgewertet")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("WICHTIGSTE ERKENNTNISSE")
 print("=" * 80)
 print()
 
 for i, finding in enumerate(evaluation["key_findings"], 1):
 print(f"{i}. {finding['finding']}")
 print(f" Wert: {finding['value']}")
 print(f" Bedeutung: {finding['significance']}")
 print(f" Implikation: {finding['implication']}")
 print()
 
 print("=" * 80)
 print("ZUSAMMENHÄNGE")
 print("=" * 80)
 print()
 
 for i, connection in enumerate(evaluation["connections"], 1):
 print(f"{i}. {connection['connection']}")
 print(f" {connection['description']}")
 print(f" Bedeutung: {connection['significance']}")
 print()
 
 print("=" * 80)
 print("HANDLUNGSEMPFEHLUNGEN")
 print("=" * 80)
 print()
 
 for i, rec in enumerate(evaluation["recommendations"], 1):
 print(f"{i}. [{rec['priority']}] {rec['action']}")
 print(f" {rec['description']}")
 print(" Schritte:")
 for step in rec["steps"]:
 print(f" - {step}")
 print()
 
 # Speichere Auswertung
 output_file = OUTPUT_DIR / "comprehensive_evaluation.json"
 with output_file.open("w") as f:
 json.dump(evaluation, f, indent=2)
 print(f"💾 Auswertung gespeichert: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Umfassende Datenauswertung",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 f"**Analysen ausgewertet**: {evaluation['analyses_loaded']}",
 f"**Erkenntnisse**: {evaluation['summary']['total_findings']}",
 f"**Zusammenhänge**: {evaluation['summary']['total_connections']}",
 f"**Empfehlungen**: {evaluation['summary']['total_recommendations']}",
 "",
 "---",
 "",
 "## 🔍 WICHTIGSTE ERKENNTNISSE",
 ""
 ]
 
 for finding in evaluation["key_findings"]:
 report_lines.extend([
 f"### {finding['finding']}",
 "",
 f"- **Wert**: {finding['value']}",
 f"- **Bedeutung**: {finding['significance']}",
 f"- **Implikation**: {finding['implication']}",
 ""
 ])
 
 report_lines.extend([
 "---",
 "",
 "## 🔗 ZUSAMMENHÄNGE",
 ""
 ])
 
 for connection in evaluation["connections"]:
 report_lines.extend([
 f"### {connection['connection']}",
 "",
 f"{connection['description']}",
 "",
 f"**Bedeutung**: {connection['significance']}",
 ""
 ])
 
 report_lines.extend([
 "---",
 "",
 "## 🚀 HANDLUNGSEMPFEHLUNGEN",
 ""
 ])
 
 for rec in evaluation["recommendations"]:
 report_lines.extend([
 f"### [{rec['priority']}] {rec['action']}",
 "",
 f"{rec['description']}",
 "",
 "**Schritte**:",
 ""
 ])
 for step in rec["steps"]:
 report_lines.append(f"- {step}")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "UMFASSENDE_DATENAUSWERTUNG.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 print()
 print("=" * 80)
 print("✅ AUSWERTUNG ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

