#!/usr/bin/env python3
"""
Finde LÄNGERE Nachrichten von Anna (6+ Wörter)
- Suche nach komplexeren Sätzen
- Finde längere "Nachrichten"
- KEINE Halluzinationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

ALL_MESSAGES_FILE = project_root / "outputs" / "derived" / "all_anna_messages.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def load_layer4_map() -> Dict[str, str]:
 """Load Layer-4 Mapping."""
 layer4_map = {}
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 for entry in layer4_data.get("results", []):
 layer3_id = entry.get("layer3_identity", "")
 layer4_id = entry.get("layer4_identity", "")
 if len(layer3_id) == 60 and len(layer4_id) == 60:
 layer4_map[layer3_id] = layer4_id
 return layer4_map

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("FINDE LÄNGERE NACHRICHTEN VON ANNA (6+ WÖRTER)")
 print("=" * 80)
 print()
 
 if not ALL_MESSAGES_FILE.exists():
 print(f"❌ Datei nicht gefunden: {ALL_MESSAGES_FILE}")
 print(" Führe zuerst find_all_anna_messages.py aus!")
 return
 
 # Load alle Sätze
 print("📂 Load alle Sätze...")
 with ALL_MESSAGES_FILE.open() as f:
 messages_data = json.load(f)
 
 top_sentences = messages_data.get("top_sentences", [])
 print(f"✅ {len(top_sentences)} Sätze geloadn")
 print()
 
 # Filtere nach 6+ Wörtern
 long_sentences = [s for s in top_sentences if s.get("word_count", 0) >= 6]
 
 if not long_sentences:
 print("⚠️ Keine Sätze mit 6+ Wörtern gefunden")
 print(" Suche nach 5+ Wörtern...")
 long_sentences = [s for s in top_sentences if s.get("word_count", 0) >= 5]
 
 print(f"✅ {len(long_sentences)} längere Sätze gefunden (≥{long_sentences[0]['word_count'] if long_sentences else 5} Wörter)")
 print()
 
 # Load Layer-4 Map
 layer4_map = load_layer4_map()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("LÄNGERE NACHRICHTEN")
 print("=" * 80)
 print()
 
 if long_sentences:
 print(f"📊 Alle längeren Sätze (≥{long_sentences[0]['word_count']} Wörter):")
 for i, sentence in enumerate(long_sentences, 1):
 layer4 = layer4_map.get(sentence["identity"], "")
 layer4_marker = " (Layer-4 verfügbar)" if layer4 else ""
 print(f" {i}. '{sentence['sentence']}' ({sentence['word_count']} Wörter, Länge: {sentence['total_length']}){layer4_marker}")
 if layer4:
 print(f" Layer-4: {layer4}")
 else:
 print("⚠️ Keine längeren Sätze gefunden")
 print(" Die längsten Sätze haben 5 Wörter")
 
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_long_sentences": len(long_sentences),
 "min_word_count": long_sentences[0]["word_count"] if long_sentences else 0,
 "long_sentences": long_sentences
 }
 
 output_file = OUTPUT_DIR / "long_anna_messages.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Längere Nachrichten von Anna",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 f"**Total längere Sätze**: {len(long_sentences)}",
 f"**Mindest-Wort-Anzahl**: {long_sentences[0]['word_count'] if long_sentences else 0}",
 "",
 "---",
 "",
 "## 📊 ALLE LÄNGEREN SÄTZE",
 ""
 ]
 
 for i, sentence in enumerate(long_sentences, 1):
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
 
 report_file = REPORTS_DIR / "LAENGERE_ANNA_NACHRICHTEN.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

