#!/usr/bin/env python3
"""
Suche nach möglichen Nachrichten von Anna in existierenden Identities
- Analyze Character-Patterns die wie Nachrichten aussehen
- Suche nach bekannten Wörtern/Patterns
- KEINE Spekulationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict
from datetime import datetime
import re

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def search_for_patterns(identities: List[str], patterns: List[str]) -> Dict:
 """Suche nach Patterns in Identities."""
 
 found = defaultdict(list)
 
 for identity in identities:
 for pattern in patterns:
 if pattern.upper() in identity:
 found[pattern].append(identity)
 
 return dict(found)

def analyze_character_sequences(identities: List[str], min_length: int = 3) -> Dict:
 """Analyze Character-Sequenzen die wie Wörter aussehen."""
 
 sequences = Counter()
 
 for identity in identities:
 # Suche nach wiederholenden Sequenzen
 for length in range(min_length, 8):
 for i in range(len(identity) - length + 1):
 seq = identity[i:i+length]
 if seq.isalpha() and len(set(seq)) > 1: # Nicht alle gleich
 sequences[seq] += 1
 
 return dict(sequences.most_common(50))

def search_anna_messages() -> Dict:
 """Suche nach möglichen Nachrichten von Anna."""
 
 print("=" * 80)
 print("SUCHE NACH ANNA NACHRICHTEN")
 print("=" * 80)
 print()
 print("ANALYZING EXISTING IDENTITIES FOR PATTERNS")
 print()
 
 # Load Layer-3 Identities
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 layer3_identities = [e.get("layer3_identity", "") for e in layer3_results if len(e.get("layer3_identity", "")) == 60]
 
 print(f"📂 {len(layer3_identities)} Layer-3 Identities geloadn")
 print()
 
 # Load Layer-4 Identities (Anna selbst)
 layer4_identities = []
 if LAYER4_FILE.exists():
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 layer4_identities = [e.get("layer4_identity", "") for e in layer4_results if len(e.get("layer4_identity", "")) == 60]
 print(f"📂 {len(layer4_identities)} Layer-4 Identities geloadn")
 print()
 
 # Suche nach bekannten Patterns
 print("🔍 Suche nach bekannten Patterns...")
 
 known_patterns = [
 "ANNA",
 "HELLO",
 "HI",
 "TEST",
 "MESSAGE",
 "QUBIC",
 "STOP",
 "HERE",
 "WAS"
 ]
 
 found_patterns = search_for_patterns(layer3_identities + layer4_identities, known_patterns)
 
 print("✅ Pattern-Suche abgeschlossen")
 print()
 
 # Analyze Character-Sequenzen
 print("🔍 Analyze Character-Sequenzen...")
 
 all_identities = layer3_identities + layer4_identities
 sequences = analyze_character_sequences(all_identities, min_length=3)
 
 print("✅ Sequenz-Analyse abgeschlossen")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 if found_patterns:
 print("📊 Gefundene bekannte Patterns:")
 for pattern, identities in found_patterns.items():
 print(f" '{pattern}': {len(identities)}x gefunden")
 for i, identity in enumerate(identities[:3], 1):
 print(f" {i}. {identity}")
 if len(identities) > 3:
 print(f" ... und {len(identities) - 3} weitere")
 print()
 else:
 print("❌ Keine bekannten Patterns gefunden")
 print()
 
 print("📊 Top 20 Character-Sequenzen (mögliche 'Wörter'):")
 for i, (seq, count) in enumerate(list(sequences.items())[:20], 1):
 marker = "⭐" if count >= 100 else " "
 print(f" {marker} {i:2d}. '{seq}': {count}x")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "found_patterns": {k: len(v) for k, v in found_patterns.items()},
 "pattern_examples": {k: v[:5] for k, v in found_patterns.items()},
 "top_sequences": dict(list(sequences.items())[:50])
 }
 
 output_file = OUTPUT_DIR / "anna_messages_search.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Suche nach Anna Nachrichten",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Gefundene bekannte Patterns",
 ""
 ]
 
 if found_patterns:
 for pattern, identities in found_patterns.items():
 report_lines.append(f"### '{pattern}' ({len(identities)}x gefunden)")
 for i, identity in enumerate(identities[:10], 1):
 report_lines.append(f"{i}. `{identity}`")
 report_lines.append("")
 else:
 report_lines.append("Keine bekannten Patterns gefunden.")
 report_lines.append("")
 
 report_lines.extend([
 "## Top Character-Sequenzen (mögliche 'Wörter')",
 ""
 ])
 
 for seq, count in list(sequences.items())[:30]:
 report_lines.append(f"- '{seq}': {count}x")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "anna_messages_search_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 return output_data

def main():
 """Hauptfunktion."""
 search_anna_messages()
 
 print()
 print("=" * 80)
 print("✅ SUCHE ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print("💡 ERKENNTNISSE:")
 print()
 print(" ✅ Existierende Identities auf Patterns analysiert")
 print(" ✅ Character-Sequenzen identifiziert")
 print(" ✅ KEINE Spekulationen - nur echte Daten!")
 print()

if __name__ == "__main__":
 main()

