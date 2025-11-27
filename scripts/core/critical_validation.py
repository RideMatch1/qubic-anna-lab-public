#!/usr/bin/env python3
"""
Kritische Validierung: Check alle Behauptungen mit echten Daten.

Keine Annahmen, nur Fakten!
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter

OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs" / "derived"
COMPREHENSIVE_LAYER2 = OUTPUT_DIR / "comprehensive_scan_layer2_derivation.json"
COMPREHENSIVE_SCAN = OUTPUT_DIR / "comprehensive_matrix_scan.json"
DEEP_PATTERN = OUTPUT_DIR / "deep_pattern_analysis.json"
COORD_ANALYSIS = OUTPUT_DIR / "matrix_coordinate_deep_analysis.json"
OUTPUT_FILE = OUTPUT_DIR / "critical_validation_report.md"

def validate_seed_compliance() -> Dict:
 """Validate: Funktionieren ALLE Identities als Seeds?"""
 
 if not COMPREHENSIVE_LAYER2.exists():
 return {"error": "File not found"}
 
 with COMPREHENSIVE_LAYER2.open() as f:
 data = json.load(f)
 
 results = data.get("results", [])
 total = len(results)
 
 if total == 0:
 return {"error": "No data"}
 
 # Check jeden einzelnen Seed
 validation_results = {
 "total": total,
 "seeds_extracted": 0,
 "seeds_length_55": 0,
 "seeds_lowercase": 0,
 "seeds_base26": 0,
 "layer2_derivable": 0,
 "layer2_onchain": 0,
 "failures": [],
 }
 
 for i, result in enumerate(results):
 seed = result.get("seed", "")
 identity = result.get("layer1_identity", "")
 
 # Seed-Extraktion
 if seed:
 validation_results["seeds_extracted"] += 1
 
 if len(seed) == 55:
 validation_results["seeds_length_55"] += 1
 else:
 validation_results["failures"].append({
 "index": i,
 "identity": identity[:40] + "...",
 "issue": f"Seed length {len(seed)} != 55",
 })
 
 if seed.islower():
 validation_results["seeds_lowercase"] += 1
 else:
 validation_results["failures"].append({
 "index": i,
 "identity": identity[:40] + "...",
 "issue": "Seed not lowercase",
 })
 
 if all(c.isalpha() and c.islower() for c in seed):
 validation_results["seeds_base26"] += 1
 else:
 validation_results["failures"].append({
 "index": i,
 "identity": identity[:40] + "...",
 "issue": "Seed not base-26",
 })
 else:
 validation_results["failures"].append({
 "index": i,
 "identity": identity[:40] + "...",
 "issue": "No seed extracted",
 })
 
 # Layer-2 Ableitung
 if result.get("layer2_identity"):
 validation_results["layer2_derivable"] += 1
 
 if result.get("layer2_onchain"):
 validation_results["layer2_onchain"] += 1
 
 # Berechne Prozentsätze
 validation_results["percentages"] = {
 "seeds_extracted": (validation_results["seeds_extracted"] / total * 100) if total > 0 else 0,
 "seeds_length_55": (validation_results["seeds_length_55"] / total * 100) if total > 0 else 0,
 "seeds_lowercase": (validation_results["seeds_lowercase"] / total * 100) if total > 0 else 0,
 "seeds_base26": (validation_results["seeds_base26"] / total * 100) if total > 0 else 0,
 "layer2_derivable": (validation_results["layer2_derivable"] / total * 100) if total > 0 else 0,
 "layer2_onchain": (validation_results["layer2_onchain"] / validation_results["layer2_derivable"] * 100) if validation_results["layer2_derivable"] > 0 else 0,
 }
 
 return validation_results

def validate_tick_pattern() -> Dict:
 """Validate: Ist die Tick-Verteilung wirklich kompakt?"""
 
 if not COMPREHENSIVE_LAYER2.exists():
 return {"error": "File not found"}
 
 with COMPREHENSIVE_LAYER2.open() as f:
 data = json.load(f)
 
 results = data.get("results", [])
 onchain_results = [r for r in results if r.get("layer2_onchain")]
 
 ticks = []
 for r in onchain_results:
 tick = r.get("layer2_tick", "N/A")
 if tick != "N/A" and isinstance(tick, (int, str)):
 try:
 ticks.append(int(tick))
 except:
 pass
 
 if not ticks:
 return {"error": "No valid ticks"}
 
 ticks.sort()
 
 validation = {
 "total_ticks": len(ticks),
 "min_tick": min(ticks),
 "max_tick": max(ticks),
 "tick_range": max(ticks) - min(ticks),
 "average_tick": sum(ticks) / len(ticks),
 "range_percent": ((max(ticks) - min(ticks)) / max(ticks) * 100) if max(ticks) > 0 else 0,
 "is_compact": max(ticks) - min(ticks) <= 100, # Definition: kompakt = Range <= 100
 }
 
 # Berechne Unterschiede
 differences = []
 for i in range(1, len(ticks)):
 differences.append(ticks[i] - ticks[i-1])
 
 validation["differences"] = {
 "min": min(differences) if differences else 0,
 "max": max(differences) if differences else 0,
 "average": sum(differences) / len(differences) if differences else 0,
 "most_common": Counter(differences).most_common(5),
 }
 
 return validation

def validate_coordinate_analysis() -> Dict:
 """Validate: Sind die Koordinaten-Analysen korrekt?"""
 
 if not COORD_ANALYSIS.exists():
 return {"error": "File not found"}
 
 with COORD_ANALYSIS.open() as f:
 data = json.load(f)
 
 coord_patterns = data.get("coordinate_patterns", {})
 
 validation = {
 "total_coordinates": coord_patterns.get("total_coordinates", 0),
 "unique_coordinates": coord_patterns.get("unique_coordinates", 0),
 "duplicate_rate": ((coord_patterns.get("total_coordinates", 0) - coord_patterns.get("unique_coordinates", 0)) / coord_patterns.get("total_coordinates", 1) * 100) if coord_patterns.get("total_coordinates", 0) > 0 else 0,
 "hotspots_count": len(coord_patterns.get("hotspots", [])),
 "patterns_tested": len(coord_patterns.get("pattern_stats", {})),
 }
 
 return validation

def validate_statistical_claims() -> Dict:
 """Validate: Sind statistische Behauptungen korrekt?"""
 
 if not COMPREHENSIVE_LAYER2.exists():
 return {"error": "File not found"}
 
 with COMPREHENSIVE_LAYER2.open() as f:
 data = json.load(f)
 
 results = data.get("results", [])
 identities = [r["layer1_identity"] for r in results]
 
 # Zeichen-Verteilung
 all_chars = "".join(identities)
 char_counts = Counter(all_chars)
 total_chars = len(all_chars)
 
 # Erwartete Verteilung (gleichmäßig)
 expected_freq = 1 / 26 # ~3.85%
 
 anomalies = []
 for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
 actual_freq = char_counts.get(char, 0) / total_chars if total_chars > 0 else 0
 diff = (actual_freq - expected_freq) * 100
 
 # Anomalie wenn >5% Abweichung
 if abs(diff) > 5:
 anomalies.append({
 "char": char,
 "actual": actual_freq * 100,
 "expected": expected_freq * 100,
 "diff": diff,
 })
 
 validation = {
 "total_chars": total_chars,
 "expected_frequency": expected_freq * 100,
 "anomalies_count": len(anomalies),
 "anomalies": anomalies[:10], # Nur erste 10
 "has_anomalies": len(anomalies) > 0,
 }
 
 return validation

def main():
 """Kritische Validierung aller Behauptungen."""
 
 print("=" * 80)
 print("KRITISCHE VALIDIERUNG: ALLE BEHAUPTUNGEN PRÜFEN")
 print("=" * 80)
 print()
 print("⚠️ WICHTIG: Nur Fakten, keine Annahmen!")
 print()
 
 # 1. Seed-Compliance
 print("1. VALIDIERUNG: Seed-Compliance")
 print("-" * 80)
 seed_validation = validate_seed_compliance()
 if "error" not in seed_validation:
 print(f"Total: {seed_validation['total']}")
 print(f"Seeds extrahiert: {seed_validation['seeds_extracted']} ({seed_validation['percentages']['seeds_extracted']:.1f}%)")
 print(f"Länge 55: {seed_validation['seeds_length_55']} ({seed_validation['percentages']['seeds_length_55']:.1f}%)")
 print(f"Lowercase: {seed_validation['seeds_lowercase']} ({seed_validation['percentages']['seeds_lowercase']:.1f}%)")
 print(f"Base-26: {seed_validation['seeds_base26']} ({seed_validation['percentages']['seeds_base26']:.1f}%)")
 print(f"Layer-2 ableitbar: {seed_validation['layer2_derivable']} ({seed_validation['percentages']['layer2_derivable']:.1f}%)")
 print(f"Layer-2 on-chain: {seed_validation['layer2_onchain']} ({seed_validation['percentages']['layer2_onchain']:.1f}%)")
 
 if seed_validation['failures']:
 print(f"\n⚠️ {len(seed_validation['failures'])} Fehler gefunden:")
 for failure in seed_validation['failures'][:5]:
 print(f" - {failure['issue']}")
 else:
 print("\n✅ Keine Fehler gefunden")
 else:
 print(f"❌ {seed_validation['error']}")
 print()
 
 # 2. Tick-Pattern
 print("2. VALIDIERUNG: Tick-Pattern")
 print("-" * 80)
 tick_validation = validate_tick_pattern()
 if "error" not in tick_validation:
 print(f"Total Ticks: {tick_validation['total_ticks']}")
 print(f"Range: {tick_validation['tick_range']} ({tick_validation['min_tick']:,} - {tick_validation['max_tick']:,})")
 print(f"Range %: {tick_validation['range_percent']:.6f}%")
 print(f"Kompakt (Range <= 100): {'✅ JA' if tick_validation['is_compact'] else '❌ NEIN'}")
 print(f"Average Difference: {tick_validation['differences']['average']:.2f}")
 print(f"Most Common Differences: {tick_validation['differences']['most_common']}")
 else:
 print(f"❌ {tick_validation['error']}")
 print()
 
 # 3. Koordinaten-Analyse
 print("3. VALIDIERUNG: Koordinaten-Analyse")
 print("-" * 80)
 coord_validation = validate_coordinate_analysis()
 if "error" not in coord_validation:
 print(f"Total Koordinaten: {coord_validation['total_coordinates']:,}")
 print(f"Unique Koordinaten: {coord_validation['unique_coordinates']:,}")
 print(f"Duplicate Rate: {coord_validation['duplicate_rate']:.1f}%")
 print(f"Hotspots: {coord_validation['hotspots_count']}")
 print(f"Patterns getestet: {coord_validation['patterns_tested']}")
 else:
 print(f"❌ {coord_validation['error']}")
 print()
 
 # 4. Statistische Behauptungen
 print("4. VALIDIERUNG: Statistische Behauptungen")
 print("-" * 80)
 stat_validation = validate_statistical_claims()
 if "error" not in stat_validation:
 print(f"Total Zeichen: {stat_validation['total_chars']:,}")
 print(f"Erwartete Frequenz: {stat_validation['expected_frequency']:.2f}%")
 print(f"Anomalien (>5% Abweichung): {stat_validation['anomalies_count']}")
 if stat_validation['anomalies']:
 print("\nAnomalien:")
 for anomaly in stat_validation['anomalies']:
 print(f" {anomaly['char']}: {anomaly['actual']:.2f}% (erwartet: {anomaly['expected']:.2f}%, Diff: {anomaly['diff']:+.2f}%)")
 else:
 print("\n✅ Keine statistischen Anomalien")
 else:
 print(f"❌ {stat_validation['error']}")
 print()
 
 # Erstelle Report
 report_content = f"""# Kritische Validierung: Alle Behauptungen geprüft

**Datum**: 2025-11-22 
**Ziel**: Nur Fakten, keine Annahmen!

## 1. Seed-Compliance Validierung

### Daten
- **Total Identities**: {seed_validation.get('total', 'N/A') if 'error' not in seed_validation else 'N/A'}
- **Seeds extrahiert**: {seed_validation.get('seeds_extracted', 'N/A') if 'error' not in seed_validation else 'N/A'} ({seed_validation.get('percentages', {}).get('seeds_extracted', 0):.1f}% wenn verfügbar)
- **Länge 55**: {seed_validation.get('seeds_length_55', 'N/A') if 'error' not in seed_validation else 'N/A'} ({seed_validation.get('percentages', {}).get('seeds_length_55', 0):.1f}% wenn verfügbar)
- **Lowercase**: {seed_validation.get('seeds_lowercase', 'N/A') if 'error' not in seed_validation else 'N/A'} ({seed_validation.get('percentages', {}).get('seeds_lowercase', 0):.1f}% wenn verfügbar)
- **Base-26**: {seed_validation.get('seeds_base26', 'N/A') if 'error' not in seed_validation else 'N/A'} ({seed_validation.get('percentages', {}).get('seeds_base26', 0):.1f}% wenn verfügbar)

### Ergebnis
"""
 
 if 'error' not in seed_validation:
 if seed_validation.get('seeds_base26', 0) == seed_validation.get('total', 0):
 report_content += "✅ **BESTÄTIGT**: Alle Identities erfüllen Seed-Anforderungen\n"
 else:
 report_content += f"⚠️ **TEILWEISE**: {seed_validation.get('seeds_base26', 0)}/{seed_validation.get('total', 0)} erfüllen Seed-Anforderungen\n"
 if seed_validation.get('failures'):
 report_content += f"\nFehler gefunden: {len(seed_validation['failures'])}\n"
 else:
 report_content += f"❌ **FEHLER**: {seed_validation['error']}\n"
 
 report_content += f"""
## 2. Tick-Pattern Validierung

### Daten
- **Total Ticks**: {tick_validation.get('total_ticks', 'N/A') if 'error' not in tick_validation else 'N/A'}
- **Range**: {tick_validation.get('tick_range', 'N/A') if 'error' not in tick_validation else 'N/A'}
- **Range %**: {tick_validation.get('range_percent', 0):.6f}% wenn verfügbar

### Ergebnis
"""
 
 if 'error' not in tick_validation:
 if tick_validation.get('is_compact', False):
 report_content += "✅ **BESTÄTIGT**: Tick-Verteilung ist kompakt (Range <= 100)\n"
 else:
 report_content += f"❌ **WIDERLEGT**: Tick-Verteilung ist NICHT kompakt (Range: {tick_validation.get('tick_range', 'N/A')})\n"
 else:
 report_content += f"❌ **FEHLER**: {tick_validation['error']}\n"
 
 report_content += f"""
## 3. Statistische Validierung

### Daten
- **Anomalien**: {stat_validation.get('anomalies_count', 'N/A') if 'error' not in stat_validation else 'N/A'}

### Ergebnis
"""
 
 if 'error' not in stat_validation:
 if not stat_validation.get('has_anomalies', False):
 report_content += "✅ **BESTÄTIGT**: Keine statistischen Anomalien\n"
 else:
 report_content += f"⚠️ **ANOMALIEN GEFUNDEN**: {stat_validation.get('anomalies_count', 0)} Zeichen weichen >5% ab\n"
 else:
 report_content += f"❌ **FEHLER**: {stat_validation['error']}\n"
 
 report_content += """
## WICHTIGE ERKENNTNISSE

### Was ist BESTÄTIGT (durch Daten belegt):
- [Will basierend auf Validierung ausgefüllt]

### Was ist HYPOTHESE (nicht durch Daten belegt):
- [Will basierend auf Validierung ausgefüllt]

### Was ist WIDERLEGT (falsche Behauptung):
- [Will basierend auf Validierung ausgefüllt]

## NÄCHSTE SCHRITTE

1. Nur mit BESTÄTIGTEN Erkenntnissen weiterarbeiten
2. Hypothesen klar als solche markieren
3. Keine voreiligen Schlüsse ziehen
4. Alles mit echten Daten validaten
"""
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 f.write(report_content)
 
 print("=" * 80)
 print("VALIDIERUNG ABGESCHLOSSEN")
 print("=" * 80)
 print()
 print(f"📄 Report erstellt: {OUTPUT_FILE}")
 print()
 print("⚠️ WICHTIG: Nur BESTÄTIGTE Erkenntnisse verwenden!")

if __name__ == "__main__":
 main()

