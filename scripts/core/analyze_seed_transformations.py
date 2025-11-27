#!/usr/bin/env python3
"""
Analyze Seed-Transformationen: Layer-1 Seed → Layer-2 Identity → Layer-2 Seed.

Prüft:
- Wie ändern sich Seeds zwischen Layer-1 und Layer-2?
- Gibt es Patterns in den Transformationen?
- Mathematische Eigenschaften der Transformationen
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter

OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs" / "derived"
COMPREHENSIVE_LAYER2 = OUTPUT_DIR / "comprehensive_scan_layer2_derivation.json"
OUTPUT_FILE = OUTPUT_DIR / "seed_transformation_analysis.json"
REPORT_FILE = OUTPUT_DIR / "seed_transformation_analysis_report.md"
VENV_PYTHON = Path(__file__).parent.parent.parent / "venv-tx" / "bin" / "python"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def derive_layer2_seed(layer1_seed: str) -> Optional[str]:
 """Leite Layer-2 Seed aus Layer-1 Seed ab."""
 # Layer-1 Seed → Layer-2 Identity → Layer-2 Seed
 script = f"""
from qubipy.crypto.utils import (
 get_subseed_from_seed,
 get_private_key_from_subseed,
 get_public_key_from_private_key,
 get_identity_from_public_key,
)

seed = "{layer1_seed}"
seed_bytes = seed.encode('utf-8')
subseed = get_subseed_from_seed(seed_bytes)
private_key = get_private_key_from_subseed(subseed)
public_key = get_public_key_from_private_key(private_key)
identity = get_identity_from_public_key(public_key)
layer2_seed = identity.lower()[:55]
print(layer2_seed)
"""
 
 try:
 result = subprocess.run(
 [str(VENV_PYTHON), "-c", script],
 capture_output=True,
 text=True,
 timeout=10,
 cwd=Path(__file__).parent.parent.parent
 )
 
 if result.returncode != 0:
 return None
 
 seed = result.stdout.strip()
 if len(seed) == 55 and seed.islower():
 return seed
 return None
 except Exception:
 return None

def analyze_transformation(layer1_seed: str, layer2_seed: str) -> Dict:
 """Analyze die Transformation zwischen zwei Seeds."""
 
 if len(layer1_seed) != 55 or len(layer2_seed) != 55:
 return {}
 
 # Position-for-Position Vergleich
 same_positions = sum(1 for i in range(55) if layer1_seed[i] == layer2_seed[i])
 different_positions = 55 - same_positions
 
 # Charakter-Änderungen
 char_changes = []
 for i in range(55):
 if layer1_seed[i] != layer2_seed[i]:
 char_changes.append({
 "position": i,
 "from": layer1_seed[i],
 "to": layer2_seed[i],
 })
 
 # Hamming-Distanz (Anzahl unterschiedlicher Zeichen)
 hamming_distance = different_positions
 
 # Finde Positionen die sich ändern
 changed_positions = [i for i in range(55) if layer1_seed[i] != layer2_seed[i]]
 
 return {
 "same_positions": same_positions,
 "different_positions": different_positions,
 "hamming_distance": hamming_distance,
 "similarity_percent": (same_positions / 55 * 100),
 "char_changes": char_changes[:20], # Nur erste 20
 "changed_positions": changed_positions,
 "first_change": changed_positions[0] if changed_positions else None,
 "last_change": changed_positions[-1] if changed_positions else None,
 }

def main():
 """Analyze Seed-Transformationen."""
 
 print("=" * 80)
 print("SEED-TRANSFORMATIONS-ANALYSE")
 print("=" * 80)
 print()
 print("⚠️ WICHTIG: Nur Fakten, keine Interpretationen!")
 print()
 
 if not COMPREHENSIVE_LAYER2.exists():
 print(f"❌ Datei nicht gefunden: {COMPREHENSIVE_LAYER2}")
 return
 
 if not VENV_PYTHON.exists():
 print(f"❌ venv-tx Python nicht gefunden: {VENV_PYTHON}")
 return
 
 print("Load Comprehensive Scan Layer-2 Daten...")
 with COMPREHENSIVE_LAYER2.open() as f:
 comprehensive_data = json.load(f)
 
 results = comprehensive_data.get("results", [])
 onchain_results = [r for r in results if r.get("layer2_onchain")]
 
 print(f"✅ {len(onchain_results)} on-chain Layer-2 Identities gefunden")
 print()
 
 print("Analyze Seed-Transformationen...")
 print("(Dies kann eine Weile dauern...)")
 print()
 
 transformations = []
 for i, result in enumerate(onchain_results[:50]): # Nur erste 50 for Performance
 if i % 10 == 0:
 print(f" Progress: {i+1}/{min(50, len(onchain_results))}")
 
 layer1_seed = result.get("seed", "")
 layer2_identity = result.get("layer2_identity", "")
 
 if layer1_seed and layer2_identity:
 layer2_seed = identity_to_seed(layer2_identity)
 transformation = analyze_transformation(layer1_seed, layer2_seed)
 
 if transformation:
 transformation["layer1_seed"] = layer1_seed[:20] + "..."
 transformation["layer2_seed"] = layer2_seed[:20] + "..."
 transformations.append(transformation)
 
 print()
 
 if not transformations:
 print("❌ Keine Transformationen analysiert!")
 return
 
 # Analyze Patterns
 print("Analyze Patterns in Transformationen...")
 
 # Hamming-Distanzen
 hamming_distances = [t["hamming_distance"] for t in transformations]
 avg_hamming = sum(hamming_distances) / len(hamming_distances) if hamming_distances else 0
 min_hamming = min(hamming_distances) if hamming_distances else 0
 max_hamming = max(hamming_distances) if hamming_distances else 0
 
 # Ähnlichkeiten
 similarities = [t["similarity_percent"] for t in transformations]
 avg_similarity = sum(similarities) / len(similarities) if similarities else 0
 
 # Positionen die sich ändern
 all_changed_positions = []
 for t in transformations:
 all_changed_positions.extend(t.get("changed_positions", []))
 
 position_counts = Counter(all_changed_positions)
 most_changed_positions = position_counts.most_common(10)
 
 print(f" ✅ Durchschnittliche Hamming-Distanz: {avg_hamming:.1f}")
 print(f" ✅ Durchschnittliche Ähnlichkeit: {avg_similarity:.1f}%")
 print(f" ✅ Häufigste geänderte Positionen: {len(most_changed_positions)}")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "total_analyzed": len(transformations),
 "statistics": {
 "avg_hamming_distance": avg_hamming,
 "min_hamming_distance": min_hamming,
 "max_hamming_distance": max_hamming,
 "avg_similarity_percent": avg_similarity,
 },
 "most_changed_positions": [{"position": pos, "count": count} for pos, count in most_changed_positions],
 "sample_transformations": transformations[:10],
 }
 
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 json.dump(output_data, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 
 # Erstelle Report
 report_content = f"""# Seed-Transformationen-Analyse: Fakten

**Datum**: 2025-11-22 
**Analysiert**: {len(transformations)} Transformationen

## ⚠️ WICHTIG

**Nur Fakten, keine Interpretationen!**

## 1. Transformation-Statistiken (FAKTEN)

- **Total analysiert**: {len(transformations)}
- **Durchschnittliche Hamming-Distanz**: {avg_hamming:.1f} von 55 Positionen
- **Min Hamming-Distanz**: {min_hamming}
- **Max Hamming-Distanz**: {max_hamming}
- **Durchschnittliche Ähnlichkeit**: {avg_similarity:.1f}%

**FAKT**: Seeds ändern sich zwischen Layer-1 und Layer-2.

## 2. Geänderte Positionen (FAKTEN)

### Häufigste geänderte Positionen
"""
 
 for pos_data in most_changed_positions:
 report_content += f"- Position {pos_data['position']}: {pos_data['count']}x geändert ({pos_data['count']/len(transformations)*100:.1f}%)\n"
 
 report_content += """
## ❓ OFFENE FRAGEN (NICHT BEANTWORTET)

1. ❓ Warum ändern sich Seeds so?
2. ❓ Gibt es ein Pattern in den Änderungen?
3. ❓ Warum werden manche Positionen häufiger geändert?

## ⚠️ WICHTIG

**Diese Analyse zeigt nur FAKTEN!** 
**Keine Interpretationen!**
"""
 
 with REPORT_FILE.open("w") as f:
 f.write(report_content)
 
 print(f"📄 Report erstellt: {REPORT_FILE}")
 print()
 print("✅ Analyse abgeschlossen!")

if __name__ == "__main__":
 main()

