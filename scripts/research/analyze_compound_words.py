#!/usr/bin/env python3
"""
Analyze Zusammensetzungen genauer
- HIGO, HINO, NOGO, HIYES
- Finde alle Vorkommen
- Check Layer-4 Identities
- KEINE Spekulationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

COMPOUNDS_TO_ANALYZE = ["HIGO", "HINO", "NOGO", "HIYES"]

def find_compounds_in_identities(identities: List[str], compounds: List[str]) -> Dict[str, List[Dict]]:
 """Finde Zusammensetzungen in Identities."""
 found = {}
 
 for compound in compounds:
 compound_upper = compound.upper()
 occurrences = []
 
 for idx, identity in enumerate(identities):
 identity_upper = identity.upper()
 
 # Suche nach Zusammensetzung
 start = 0
 while True:
 pos = identity_upper.find(compound_upper, start)
 if pos == -1:
 break
 
 occurrences.append({
 "identity_index": idx,
 "identity": identity,
 "position": pos
 })
 
 start = pos + 1
 
 if occurrences:
 found[compound] = occurrences
 
 return found

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("ZUSAMMENSETZUNGEN ANALYSE")
 print("=" * 80)
 print()
 print("⚠️ KEINE SPEKULATIONEN - NUR ECHTE DATEN!")
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
 
 # Finde Zusammensetzungen
 print("🔍 Suche nach Zusammensetzungen...")
 found_compounds = find_compounds_in_identities(all_identities, COMPOUNDS_TO_ANALYZE)
 print(f"✅ {len(found_compounds)} verschiedene Zusammensetzungen gefunden")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 for compound, occurrences in sorted(found_compounds.items(), key=lambda x: len(x[1]), reverse=True):
 print(f"📊 '{compound}': {len(occurrences)}x gefunden")
 
 # Check ob Layer-4 Identities vorhanden
 layer4_found = 0
 examples_with_layer4 = []
 
 for occ in occurrences[:10]: # Erste 10 checkn
 identity = occ["identity"]
 if identity in layer4_map:
 layer4_found += 1
 examples_with_layer4.append({
 "layer3": identity,
 "layer4": layer4_map[identity],
 "position": occ["position"]
 })
 
 print(f" Layer-4 Identities: {layer4_found}/{min(10, len(occurrences))}")
 
 # Zeige Beispiele
 for i, occ in enumerate(occurrences[:5], 1):
 print(f" {i}. {occ['identity']} (Position: {occ['position']})")
 if identity in layer4_map:
 print(f" Layer-4: {layer4_map[identity]}")
 
 if len(occurrences) > 5:
 print(f" ... und {len(occurrences) - 5} weitere")
 
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_identities": len(all_identities),
 "found_compounds": {k: len(v) for k, v in found_compounds.items()},
 "compound_examples": {k: v[:10] for k, v in found_compounds.items()},
 "layer4_mappings": {}
 }
 
 # Füge Layer-4 Mappings hinzu
 for compound, occurrences in found_compounds.items():
 layer4_list = []
 for occ in occurrences:
 identity = occ["identity"]
 if identity in layer4_map:
 layer4_list.append({
 "layer3": identity,
 "layer4": layer4_map[identity],
 "position": occ["position"]
 })
 output_data["layer4_mappings"][compound] = layer4_list
 
 output_file = OUTPUT_DIR / "compound_words_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Ergebnisse gespeichert: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Zusammensetzungen Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 f"**Total Identities**: {len(all_identities)}",
 "",
 "## Gefundene Zusammensetzungen",
 ""
 ]
 
 for compound, occurrences in sorted(found_compounds.items(), key=lambda x: len(x[1]), reverse=True):
 report_lines.append(f"### '{compound}' ({len(occurrences)}x gefunden)")
 report_lines.append("")
 
 # Zeige Beispiele
 for i, occ in enumerate(occurrences[:10], 1):
 report_lines.append(f"{i}. `{occ['identity']}` (Position {occ['position']})")
 if occ['identity'] in layer4_map:
 report_lines.append(f" - Layer-4: `{layer4_map[occ['identity']]}`")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "compound_words_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 print()
 print("=" * 80)
 print("✅ ANALYSE ABGESCHLOSSEN")
 print("=" * 80)

if __name__ == "__main__":
 main()

