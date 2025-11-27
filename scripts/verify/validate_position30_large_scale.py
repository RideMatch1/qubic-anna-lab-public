#!/usr/bin/env python3
"""Large-Scale Validierung von Position 30/4 auf allen verfügbaren Identities."""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
PREDICTION_FILE = project_root / "outputs" / "derived" / "layer3_predictions_full.json"
REPORTS_DIR = project_root / "outputs" / "reports"

def validate_position30_large_scale():
 """Validate Position 30/4 auf großem Datensatz."""
 with PREDICTION_FILE.open() as f:
 data = json.load(f)
 
 entries = data.get("entries", [])
 
 # Filtere nur bekannte Status
 known_entries = [e for e in entries if e.get("actual_onchain") is not None]
 
 print("=" * 80)
 print("LARGE-SCALE POSITION 30/4 VALIDIERUNG")
 print("=" * 80)
 print()
 print(f"Total Identities: {len(entries)}")
 print(f"Mit bekanntem Status: {len(known_entries)}")
 print()
 
 if not known_entries:
 print("❌ Keine Identities mit bekanntem Status gefunden!")
 return
 
 # Position 30 Analyse
 pos30_stats = defaultdict(lambda: {"onchain": 0, "offchain": 0, "total": 0})
 pos4_stats = defaultdict(lambda: {"onchain": 0, "offchain": 0, "total": 0})
 
 correct_pos30 = 0
 correct_pos4 = 0
 total = len(known_entries)
 
 for entry in known_entries:
 identity = entry.get("layer3_identity", "")
 actual = entry.get("actual_onchain")
 pos30_char = entry.get("position30_char")
 pos4_char = entry.get("position4_char")
 prediction = entry.get("prediction")
 
 if pos30_char:
 pos30_stats[pos30_char]["total"] += 1
 if actual:
 pos30_stats[pos30_char]["onchain"] += 1
 else:
 pos30_stats[pos30_char]["offchain"] += 1
 
 if pos4_char:
 pos4_stats[pos4_char]["total"] += 1
 if actual:
 pos4_stats[pos4_char]["onchain"] += 1
 else:
 pos4_stats[pos4_char]["offchain"] += 1
 
 # Position 4 Prediction Accuracy
 if prediction:
 predicted_onchain = prediction == "ON-CHAIN"
 if predicted_onchain == actual:
 correct_pos4 += 1
 
 # Position 30 Accuracy (vereinfacht: häufigeres Label)
 for char, stats in pos30_stats.items():
 if stats["onchain"] > stats["offchain"]:
 # Mehrheit on-chain
 correct_pos30 += stats["onchain"]
 else:
 # Mehrheit off-chain
 correct_pos30 += stats["offchain"]
 
 pos30_accuracy = (correct_pos30 / total * 100) if total > 0 else 0
 pos4_accuracy = (correct_pos4 / total * 100) if total > 0 else 0
 
 print("## Position 30 Validierung")
 print(f"Accuracy: {pos30_accuracy:.1f}%")
 print()
 
 print("## Position 4 Validierung")
 print(f"Accuracy: {pos4_accuracy:.1f}%")
 print()
 
 # Perfect Markers finden
 perfect_on_pos4 = []
 perfect_off_pos4 = []
 
 for char, stats in pos4_stats.items():
 if stats["total"] >= 5: # Mindestens 5 Fälle
 if stats["offchain"] == 0:
 perfect_on_pos4.append((char, stats["total"]))
 elif stats["onchain"] == 0:
 perfect_off_pos4.append((char, stats["total"]))
 
 print("## Perfect Markers (Position 4, n >= 5)")
 if perfect_on_pos4:
 print("On-Chain:")
 for char, count in sorted(perfect_on_pos4, key=lambda x: x[1], reverse=True):
 print(f" {char}: {count} Fälle")
 if perfect_off_pos4:
 print("Off-Chain:")
 for char, count in sorted(perfect_off_pos4, key=lambda x: x[1], reverse=True):
 print(f" {char}: {count} Fälle")
 print()
 
 # Report
 report_lines = [
 "# Large-Scale Position 30/4 Validierung",
 "",
 f"**Dataset**: {len(entries)} Identities",
 f"**Mit bekanntem Status**: {len(known_entries)}",
 "",
 "## Position 30",
 f"- **Accuracy**: {pos30_accuracy:.1f}%",
 f"- **Total Validated**: {total}",
 "",
 "## Position 4",
 f"- **Accuracy**: {pos4_accuracy:.1f}%",
 f"- **Total Validated**: {total}",
 "",
 "## Perfect Markers (Position 4, n >= 5)",
 ]
 
 if perfect_on_pos4:
 report_lines.append("### On-Chain:")
 for char, count in sorted(perfect_on_pos4, key=lambda x: x[1], reverse=True):
 report_lines.append(f"- {char}: {count} Fälle (100% on-chain)")
 
 if perfect_off_pos4:
 report_lines.append("### Off-Chain:")
 for char, count in sorted(perfect_off_pos4, key=lambda x: x[1], reverse=True):
 report_lines.append(f"- {char}: {count} Fälle (100% off-chain)")
 
 report_lines.extend([
 "",
 "## Position 30 Verteilung (Top 10)",
 ])
 for char, stats in sorted(pos30_stats.items(), key=lambda x: x[1]["total"], reverse=True)[:10]:
 on_rate = (stats["onchain"] / stats["total"] * 100) if stats["total"] > 0 else 0
 report_lines.append(f"- {char}: {stats['total']} Fälle ({on_rate:.1f}% on-chain)")
 
 report_lines.extend([
 "",
 "## Position 4 Verteilung (Top 10)",
 ])
 for char, stats in sorted(pos4_stats.items(), key=lambda x: x[1]["total"], reverse=True)[:10]:
 on_rate = (stats["onchain"] / stats["total"] * 100) if stats["total"] > 0 else 0
 report_lines.append(f"- {char}: {stats['total']} Fälle ({on_rate:.1f}% on-chain)")
 
 out_file = REPORTS_DIR / "POSITION30_LARGE_SCALE_VALIDATION.md"
 with out_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 
 print(f"📝 Report gespeichert: {out_file}")

if __name__ == "__main__":
 validate_position30_large_scale()
