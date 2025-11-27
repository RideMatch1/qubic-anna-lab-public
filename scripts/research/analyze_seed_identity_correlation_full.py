#!/usr/bin/env python3
"""
Umfassende Analyse: Korrelation zwischen Seed-Positionen und Identity-Positionen
- Teste alle Seed-Positionen (0-54) auf Korrelation mit Identity-Positionen (0-59)
- Finde Patterns in der Transformation
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np

project_root = Path(__file__).parent.parent.parent
LAYER3_FILE = project_root / "outputs" / "derived" / "layer3_derivation_23k_complete.json"
LAYER4_FILE = project_root / "outputs" / "derived" / "layer4_derivation_full_23k.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def analyze_seed_identity_correlation_full(pairs: List[Dict]) -> Dict:
 """Analyze Korrelation zwischen allen Seed-Positionen und Identity-Positionen."""
 
 print("🔍 Analyze Seed → Identity Korrelationen...")
 
 # Analyze for jede Identity-Position (0-59)
 # Welche Seed-Positionen korrelieren am stärksten?
 
 identity_positions = list(range(60))
 seed_positions = list(range(55)) # Seed hat 55 Characters
 
 # Für jede Identity-Position: Finde beste Seed-Position Korrelation
 correlation_results = {}
 
 for identity_pos in identity_positions:
 if identity_pos % 10 == 0:
 print(f" Analyze Identity-Position {identity_pos}/59...")
 
 # Teste alle Seed-Positionen
 seed_correlations = {}
 
 for seed_pos in seed_positions:
 # Analyze: Beeinflusst Seed-Position seed_pos Identity-Position identity_pos?
 
 # Gruppiere nach Seed-Character an seed_pos
 seed_char_groups = defaultdict(lambda: {"stable": 0, "changing": 0})
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 seed = identity_to_seed(l3_id)
 
 if len(seed) > seed_pos and len(l3_id) > identity_pos and len(l4_id) > identity_pos:
 seed_char = seed[seed_pos].lower()
 identity_stable = l3_id[identity_pos].upper() == l4_id[identity_pos].upper()
 
 if identity_stable:
 seed_char_groups[seed_char]["stable"] += 1
 else:
 seed_char_groups[seed_char]["changing"] += 1
 
 # Berechne Korrelationsstärke
 if seed_char_groups:
 # Für jeden Seed-Character: Berechne Stabilitätsrate
 char_rates = {}
 for char, stats in seed_char_groups.items():
 total = stats["stable"] + stats["changing"]
 if total >= 10: # Mindestens 10 Fälle
 rate = stats["stable"] / total
 char_rates[char] = rate
 
 if char_rates:
 # Berechne Varianz der Raten (höhere Varianz = stärkere Korrelation)
 rates_list = list(char_rates.values())
 variance = np.var(rates_list) if len(rates_list) > 1 else 0
 mean_rate = np.mean(rates_list)
 
 # Anzahl verschiedener Characters mit signifikanter Korrelation
 significant_chars = sum(1 for rate in rates_list if abs(rate - mean_rate) > 0.05)
 
 seed_correlations[seed_pos] = {
 "variance": variance,
 "mean_rate": mean_rate,
 "significant_chars": significant_chars,
 "char_rates": dict(sorted(char_rates.items(), key=lambda x: x[1], reverse=True)[:5])
 }
 
 # Finde beste Seed-Position for diese Identity-Position
 if seed_correlations:
 best_seed_pos = max(seed_correlations.items(), key=lambda x: x[1]["variance"])
 correlation_results[identity_pos] = {
 "best_seed_position": best_seed_pos[0],
 "correlation_strength": best_seed_pos[1]["variance"],
 "mean_rate": best_seed_pos[1]["mean_rate"],
 "significant_chars": best_seed_pos[1]["significant_chars"],
 "char_rates": best_seed_pos[1]["char_rates"]
 }
 
 return correlation_results

def analyze_specific_correlations(pairs: List[Dict]) -> Dict:
 """Analyze spezifische bekannte Korrelationen im Detail."""
 
 # Position 27 (bekannt: Seed-Position 27 korreliert)
 pos27_analysis = {}
 
 for seed_pos in [0, 4, 13, 27, 30, 54]:
 seed_char_to_stability = defaultdict(lambda: {"stable": 0, "changing": 0})
 
 for pair in pairs:
 l3_id = pair["layer3"]
 l4_id = pair["layer4"]
 seed = identity_to_seed(l3_id)
 
 if len(seed) > seed_pos and len(l3_id) > 27 and len(l4_id) > 27:
 seed_char = seed[seed_pos].lower()
 stable = l3_id[27].upper() == l4_id[27].upper()
 
 if stable:
 seed_char_to_stability[seed_char]["stable"] += 1
 else:
 seed_char_to_stability[seed_char]["changing"] += 1
 
 # Berechne Raten
 char_rates = {}
 for char, stats in seed_char_to_stability.items():
 total = stats["stable"] + stats["changing"]
 if total >= 10:
 rate = stats["stable"] / total
 char_rates[char] = {
 "rate": rate,
 "stable": stats["stable"],
 "changing": stats["changing"],
 "total": total
 }
 
 pos27_analysis[seed_pos] = dict(sorted(char_rates.items(), key=lambda x: x[1]["rate"], reverse=True)[:10])
 
 return {
 "position27_seed_correlations": pos27_analysis
 }

def main():
 """Hauptfunktion."""
 print("=" * 80)
 print("SEED → IDENTITY KORRELATION ANALYSE (Vollständig)")
 print("=" * 80)
 print()
 
 # Load Daten
 print("📂 Load Layer-3 und Layer-4 Daten...")
 with LAYER3_FILE.open() as f:
 layer3_data = json.load(f)
 layer3_results = layer3_data.get("results", [])
 
 with LAYER4_FILE.open() as f:
 layer4_data = json.load(f)
 layer4_results = layer4_data.get("results", [])
 
 # Erstelle Paare
 layer4_map = {}
 for entry in layer4_results:
 l3_id = entry.get("layer3_identity", "")
 l4_id = entry.get("layer4_identity", "")
 if l3_id and l4_id:
 layer4_map[l3_id] = l4_id
 
 pairs = []
 for l3_entry in layer3_results:
 l3_id = l3_entry.get("layer3_identity", "")
 l4_id = layer4_map.get(l3_id)
 if l3_id and l4_id and len(l3_id) == 60 and len(l4_id) == 60:
 pairs.append({"layer3": l3_id, "layer4": l4_id})
 
 print(f"✅ {len(pairs)} Paare geloadn")
 print()
 
 # Analyze spezifische Korrelationen (schneller)
 print("🔍 Analyze spezifische Korrelationen (Position 27)...")
 specific_analysis = analyze_specific_correlations(pairs)
 print("✅ Spezifische Korrelationen analysiert")
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 # Position 27 Seed-Korrelationen
 pos27_correlations = specific_analysis.get("position27_seed_correlations", {})
 if pos27_correlations:
 print("📊 Position 27: Seed-Position Korrelationen:")
 for seed_pos in [0, 4, 13, 27, 30, 54]:
 if seed_pos in pos27_correlations:
 char_rates = pos27_correlations[seed_pos]
 if char_rates:
 print(f"\n Seed-Position {seed_pos}:")
 for char, stats in list(char_rates.items())[:5]:
 rate = stats["rate"] * 100
 print(f" Seed '{char}': {rate:.1f}% stabil ({stats['stable']}/{stats['total']})")
 print()
 
 # Finde beste Korrelationen
 print("📊 Top Seed-Positionen for Identity-Position 27:")
 best_correlations = []
 for seed_pos, char_rates in pos27_correlations.items():
 if char_rates:
 # Berechne durchschnittliche Stabilitätsrate
 avg_rate = np.mean([s["rate"] for s in char_rates.values()])
 variance = np.var([s["rate"] for s in char_rates.values()])
 best_correlations.append({
 "seed_pos": seed_pos,
 "avg_rate": avg_rate,
 "variance": variance,
 "char_count": len(char_rates)
 })
 
 sorted_correlations = sorted(best_correlations, key=lambda x: x["variance"], reverse=True)
 for corr in sorted_correlations[:5]:
 print(f" Seed-Position {corr['seed_pos']}: Variance {corr['variance']:.4f}, Avg Rate {corr['avg_rate']*100:.1f}%")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "specific_analysis": specific_analysis
 }
 
 output_file = OUTPUT_DIR / "seed_identity_correlation_full_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Seed → Identity Korrelation Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 "## Position 27: Seed-Position Korrelationen",
 ""
 ]
 
 if pos27_correlations:
 for seed_pos in [0, 4, 13, 27, 30, 54]:
 if seed_pos in pos27_correlations:
 char_rates = pos27_correlations[seed_pos]
 if char_rates:
 report_lines.append(f"### Seed-Position {seed_pos}:")
 for char, stats in list(char_rates.items())[:5]:
 rate = stats["rate"] * 100
 report_lines.append(f"- **Seed '{char}'**: {rate:.1f}% stabil ({stats['stable']}/{stats['total']})")
 report_lines.append("")
 
 report_file = REPORTS_DIR / "seed_identity_correlation_full_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")

if __name__ == "__main__":
 main()

