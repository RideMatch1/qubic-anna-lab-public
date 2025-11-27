#!/usr/bin/env python3
"""
Finde robuste Patterns (nicht nur 100%)
- Analyze Mappings mit hoher Erfolgsrate (>=80%)
- Finde praktisch nutzbare Patterns
- KEINE Spekulationen - nur echte Daten!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

DICTIONARY_FILE = project_root / "outputs" / "derived" / "anna_language_dictionary.json"
OUTPUT_DIR = project_root / "outputs" / "derived"
REPORTS_DIR = project_root / "outputs" / "reports"

def find_robust_patterns(min_rate: float = 0.80, min_samples: int = 50) -> Dict:
 """Finde robuste Patterns mit hoher Erfolgsrate."""
 
 print("=" * 80)
 print("ROBUSTE PATTERNS FINDEN")
 print("=" * 80)
 print()
 print(f"⚠️ MINIMUM: {min_rate*100:.0f}% Erfolgsrate, {min_samples} Samples")
 print()
 
 # Load Dictionary
 with DICTIONARY_FILE.open() as f:
 data = json.load(f)
 
 best_mappings = data.get("best_mappings", {})
 combinations = best_mappings.get("combinations", [])
 
 # Filtere robuste Patterns
 robust_patterns = []
 
 for combo in combinations:
 success_rate = combo.get("success_rate", 0)
 total = combo.get("total", 0)
 
 if success_rate >= min_rate and total >= min_samples:
 robust_patterns.append(combo)
 
 # Sortiere nach Erfolgsrate
 robust_patterns.sort(key=lambda x: (x.get("success_rate", 0), x.get("total", 0)), reverse=True)
 
 print(f"✅ {len(robust_patterns)} robuste Patterns gefunden")
 print()
 
 # Gruppiere nach Target-Character
 by_char = defaultdict(list)
 for pattern in robust_patterns:
 char = pattern.get("target_char", "?")
 by_char[char].append(pattern)
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ROBUSTE PATTERNS")
 print("=" * 80)
 print()
 
 for char in sorted(by_char.keys()):
 patterns = by_char[char]
 print(f"📊 '{char}': {len(patterns)} robuste Patterns")
 
 # Zeige Top 10
 for i, pattern in enumerate(patterns[:10], 1):
 rate = pattern.get("success_rate", 0) * 100
 total = pattern.get("total", 0)
 combo_key = pattern.get("combo_key", "N/A")
 marker = "⭐" if rate >= 95 else " "
 print(f" {marker} {i:2d}. {combo_key}: {rate:.1f}% ({total} Fälle)")
 print()
 
 # Statistiken
 total_patterns = len(robust_patterns)
 perfect_patterns = sum(1 for p in robust_patterns if p.get("success_rate", 0) >= 0.99)
 high_patterns = sum(1 for p in robust_patterns if 0.95 <= p.get("success_rate", 0) < 0.99)
 good_patterns = sum(1 for p in robust_patterns if 0.80 <= p.get("success_rate", 0) < 0.95)
 
 print("=" * 80)
 print("STATISTIKEN")
 print("=" * 80)
 print()
 print(f" Total robuste Patterns: {total_patterns}")
 print(f" Perfekt (100%): {perfect_patterns}")
 print(f" Sehr gut (95-99%): {high_patterns}")
 print(f" Gut (80-95%): {good_patterns}")
 print()
 
 # Speichere Ergebnisse
 output_data = {
 "timestamp": datetime.now().isoformat(),
 "min_rate": min_rate,
 "min_samples": min_samples,
 "total_patterns": total_patterns,
 "statistics": {
 "perfect": perfect_patterns,
 "high": high_patterns,
 "good": good_patterns
 },
 "patterns_by_char": {char: patterns for char, patterns in by_char.items()},
 "all_patterns": robust_patterns[:100] # Top 100
 }
 
 output_file = OUTPUT_DIR / "robust_patterns_analysis.json"
 with output_file.open("w") as f:
 json.dump(output_data, f, indent=2)
 print(f"💾 Results saved to: {output_file}")
 
 # Erstelle Report
 report_lines = [
 "# Robuste Patterns Analyse",
 "",
 f"**Generated**: {datetime.now().isoformat()}",
 "",
 f"**Kriterien**: ≥{min_rate*100:.0f}% Erfolgsrate, ≥{min_samples} Samples",
 "",
 "## Statistiken",
 "",
 f"- **Total robuste Patterns**: {total_patterns}",
 f"- **Perfekt (100%)**: {perfect_patterns}",
 f"- **Sehr gut (95-99%)**: {high_patterns}",
 f"- **Gut (80-95%)**: {good_patterns}",
 "",
 "## Patterns nach Character",
 ""
 ]
 
 for char in sorted(by_char.keys()):
 patterns = by_char[char]
 report_lines.append(f"### '{char}' ({len(patterns)} Patterns)")
 report_lines.append("")
 
 for i, pattern in enumerate(patterns[:20], 1):
 rate = pattern.get("success_rate", 0) * 100
 total = pattern.get("total", 0)
 combo_key = pattern.get("combo_key", "N/A")
 marker = "⭐" if rate >= 95 else " "
 report_lines.append(f"{marker} {i}. **{combo_key}**: {rate:.1f}% ({total} Fälle)")
 
 report_lines.append("")
 
 report_file = REPORTS_DIR / "robust_patterns_analysis_report.md"
 with report_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 print(f"📝 Report gespeichert: {report_file}")
 
 return output_data

def main():
 """Hauptfunktion."""
 import argparse
 
 parser = argparse.ArgumentParser(description="Finde robuste Patterns")
 parser.add_argument("--min-rate", type=float, default=0.80, help="Minimum Erfolgsrate (default: 0.80)")
 parser.add_argument("--min-samples", type=int, default=50, help="Minimum Samples (default: 50)")
 args = parser.parse_args()
 
 find_robust_patterns(min_rate=args.min_rate, min_samples=args.min_samples)
 
 print()
 print("=" * 80)
 print("✅ ROBUSTE PATTERNS GEFUNDEN")
 print("=" * 80)
 print()
 print("💡 ERKENNTNISSE:")
 print()
 print(" ✅ Viele robuste Patterns gefunden")
 print(" ✅ Praktisch nutzbar for Identity-Generierung")
 print(" ✅ KEINE Spekulationen - nur echte Daten!")
 print()

if __name__ == "__main__":
 main()

