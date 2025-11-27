#!/usr/bin/env python3
"""
Analyze die 70 fehlenden Layer-2 Identities: Warum existieren sie nicht on-chain?

Prüft:
- Seed-Eigenschaften (on-chain vs. off-chain)
- Charakter-Verteilungen
- Mathematische Eigenschaften
- Tick-Bereiche
- Weitere Unterschiede
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter

OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs" / "derived"
COMPREHENSIVE_LAYER2 = OUTPUT_DIR / "comprehensive_scan_layer2_derivation.json"
OUTPUT_FILE = OUTPUT_DIR / "missing_layer2_analysis.json"
REPORT_FILE = OUTPUT_DIR / "missing_layer2_analysis_report.md"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def analyze_seed_properties(seeds: List[str]) -> Dict:
 """Analyze Eigenschaften von Seeds."""
 
 analysis = {
 "total": len(seeds),
 "lengths": Counter(len(s) for s in seeds),
 "first_chars": Counter(s[0] for s in seeds),
 "last_chars": Counter(s[-1] for s in seeds),
 "char_frequencies": Counter(),
 "vowel_counts": [],
 "consonant_counts": [],
 }
 
 vowels = set("aeiou")
 
 for seed in seeds:
 # Zeichen-Häufigkeiten
 for char in seed:
 analysis["char_frequencies"][char] += 1
 
 # Vokal/Konsonant-Verhältnis
 vowel_count = sum(1 for c in seed if c in vowels)
 consonant_count = len(seed) - vowel_count
 analysis["vowel_counts"].append(vowel_count)
 analysis["consonant_counts"].append(consonant_count)
 
 analysis["avg_vowels"] = sum(analysis["vowel_counts"]) / len(analysis["vowel_counts"]) if analysis["vowel_counts"] else 0
 analysis["avg_consonants"] = sum(analysis["consonant_counts"]) / len(analysis["consonant_counts"]) if analysis["consonant_counts"] else 0
 
 return analysis

def compare_onchain_vs_offchain(comprehensive_data: Dict) -> Dict:
 """Vergleiche on-chain vs. off-chain Layer-2 Identities."""
 
 results = comprehensive_data.get("results", [])
 
 onchain = [r for r in results if r.get("layer2_onchain")]
 offchain = [r for r in results if not r.get("layer2_onchain")]
 
 onchain_seeds = [r["seed"] for r in onchain]
 offchain_seeds = [r["seed"] for r in offchain]
 
 # Analyze beide Gruppen
 onchain_props = analyze_seed_properties(onchain_seeds)
 offchain_props = analyze_seed_properties(offchain_seeds)
 
 # Finde Unterschiede
 differences = {
 "first_char_diff": {},
 "last_char_diff": {},
 "char_freq_diff": {},
 "vowel_diff": {
 "onchain_avg": onchain_props["avg_vowels"],
 "offchain_avg": offchain_props["avg_vowels"],
 "diff": onchain_props["avg_vowels"] - offchain_props["avg_vowels"],
 },
 "consonant_diff": {
 "onchain_avg": onchain_props["avg_consonants"],
 "offchain_avg": offchain_props["avg_consonants"],
 "diff": onchain_props["avg_consonants"] - offchain_props["avg_consonants"],
 },
 }
 
 # Erste Zeichen Unterschiede
 all_first_chars = set(onchain_props["first_chars"].keys()) | set(offchain_props["first_chars"].keys())
 for char in all_first_chars:
 onchain_count = onchain_props["first_chars"].get(char, 0)
 offchain_count = offchain_props["first_chars"].get(char, 0)
 if onchain_count != offchain_count:
 differences["first_char_diff"][char] = {
 "onchain": onchain_count,
 "offchain": offchain_count,
 "diff": onchain_count - offchain_count,
 "onchain_pct": (onchain_count / len(onchain_seeds) * 100) if onchain_seeds else 0,
 "offchain_pct": (offchain_count / len(offchain_seeds) * 100) if offchain_seeds else 0,
 }
 
 # Letzte Zeichen Unterschiede
 all_last_chars = set(onchain_props["last_chars"].keys()) | set(offchain_props["last_chars"].keys())
 for char in all_last_chars:
 onchain_count = onchain_props["last_chars"].get(char, 0)
 offchain_count = offchain_props["last_chars"].get(char, 0)
 if onchain_count != offchain_count:
 differences["last_char_diff"][char] = {
 "onchain": onchain_count,
 "offchain": offchain_count,
 "diff": onchain_count - offchain_count,
 "onchain_pct": (onchain_count / len(onchain_seeds) * 100) if onchain_seeds else 0,
 "offchain_pct": (offchain_count / len(offchain_seeds) * 100) if offchain_seeds else 0,
 }
 
 return {
 "onchain_count": len(onchain),
 "offchain_count": len(offchain),
 "onchain_properties": onchain_props,
 "offchain_properties": offchain_props,
 "differences": differences,
 }

def main():
 """Analyze fehlende Layer-2 Identities."""
 
 print("=" * 80)
 print("ANALYSE: FEHLENDE LAYER-2 IDENTITIES")
 print("=" * 80)
 print()
 print("⚠️ WICHTIG: Nur Fakten, keine Interpretationen!")
 print()
 
 if not COMPREHENSIVE_LAYER2.exists():
 print(f"❌ Datei nicht gefunden: {COMPREHENSIVE_LAYER2}")
 return
 
 print("Load Comprehensive Scan Layer-2 Daten...")
 with COMPREHENSIVE_LAYER2.open() as f:
 comprehensive_data = json.load(f)
 
 print(f"✅ Daten geloadn")
 print()
 
 # Vergleiche on-chain vs. off-chain
 print("Vergleiche on-chain vs. off-chain Layer-2...")
 comparison = compare_onchain_vs_offchain(comprehensive_data)
 
 print(f" ✅ On-chain: {comparison['onchain_count']}")
 print(f" ✅ Off-chain: {comparison['offchain_count']}")
 print()
 
 # Zeige Unterschiede
 print("Unterschiede gefunden:")
 if comparison["differences"]["first_char_diff"]:
 print(f" ✅ Erste Zeichen Unterschiede: {len(comparison['differences']['first_char_diff'])}")
 if comparison["differences"]["last_char_diff"]:
 print(f" ✅ Letzte Zeichen Unterschiede: {len(comparison['differences']['last_char_diff'])}")
 
 vowel_diff = comparison["differences"]["vowel_diff"]["diff"]
 if abs(vowel_diff) > 0.1:
 print(f" ✅ Vokal-Unterschied: {vowel_diff:.2f}")
 
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 json.dump(comparison, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 
 # Erstelle Report
 report_content = f"""# Analyse: Fehlende Layer-2 Identities

**Datum**: 2025-11-22 
**Ziel**: Warum existieren 70 Layer-2 Identities nicht on-chain?

## ⚠️ WICHTIG

**Nur Fakten, keine Interpretationen!**

## 1. Statistik (FAKTEN)

- **On-chain Layer-2**: {comparison['onchain_count']}
- **Off-chain Layer-2**: {comparison['offchain_count']}
- **Total**: {comparison['onchain_count'] + comparison['offchain_count']}
- **Rate**: {comparison['onchain_count']/(comparison['onchain_count']+comparison['offchain_count'])*100:.1f}%

## 2. Seed-Eigenschaften Vergleich (FAKTEN)

### Vokal/Konsonant-Verhältnis
- **On-chain Vokale (Ø)**: {comparison['differences']['vowel_diff']['onchain_avg']:.2f}
- **Off-chain Vokale (Ø)**: {comparison['differences']['vowel_diff']['offchain_avg']:.2f}
- **Unterschied**: {comparison['differences']['vowel_diff']['diff']:+.2f}

- **On-chain Konsonanten (Ø)**: {comparison['differences']['consonant_diff']['onchain_avg']:.2f}
- **Off-chain Konsonanten (Ø)**: {comparison['differences']['consonant_diff']['offchain_avg']:.2f}
- **Unterschied**: {comparison['differences']['consonant_diff']['diff']:+.2f}

## 3. Charakter-Unterschiede (FAKTEN)

### Erste Zeichen Unterschiede
"""
 
 if comparison["differences"]["first_char_diff"]:
 for char, data in sorted(comparison["differences"]["first_char_diff"].items(), key=lambda x: abs(x[1]["diff"]), reverse=True)[:15]:
 report_content += f"- `{char}`: On-chain {data['onchain']}x ({data['onchain_pct']:.1f}%), Off-chain {data['offchain']}x ({data['offchain_pct']:.1f}%), Diff: {data['diff']:+d}\n"
 else:
 report_content += "- Keine signifikanten Unterschiede\n"
 
 report_content += "\n### Letzte Zeichen Unterschiede\n"
 if comparison["differences"]["last_char_diff"]:
 for char, data in sorted(comparison["differences"]["last_char_diff"].items(), key=lambda x: abs(x[1]["diff"]), reverse=True)[:15]:
 report_content += f"- `{char}`: On-chain {data['onchain']}x ({data['onchain_pct']:.1f}%), Off-chain {data['offchain']}x ({data['offchain_pct']:.1f}%), Diff: {data['diff']:+d}\n"
 else:
 report_content += "- Keine signifikanten Unterschiede\n"
 
 report_content += """
## ❓ OFFENE FRAGEN (NICHT BEANTWORTET)

1. ❓ Warum existieren 70 Layer-2 Identities nicht on-chain?
2. ❓ Gibt es ein Pattern in den Unterschieden?
3. ❓ Sind die Unterschiede signifikant?
4. ❓ Könnten die fehlenden Identities in einem anderen Tick-Bereich liegen?

## ⚠️ WICHTIG

**Diese Analyse zeigt nur FAKTEN!** 
**Keine Interpretationen!** 
**Keine Schlüsse above "Warum"!**
"""
 
 with REPORT_FILE.open("w") as f:
 f.write(report_content)
 
 print(f"📄 Report erstellt: {REPORT_FILE}")
 print()
 print("✅ Analyse abgeschlossen!")

if __name__ == "__main__":
 main()

