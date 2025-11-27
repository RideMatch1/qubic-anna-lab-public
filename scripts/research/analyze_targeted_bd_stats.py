#!/usr/bin/env python3
"""
Analysiert aktuelle B/D-Targeted-RPC-Ergebnisse:
- Klassenverteilung, validForTick-Statistiken
- Vergleich der Seeds (häufigste Buchstaben je Position)
- Speichert Ergebnisse als JSON/Report
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent.parent
TARGETED_FILE = PROJECT_ROOT / "outputs" / "derived" / "rpc_validation_targeted_bd_results.json"
OUTPUT_JSON = PROJECT_ROOT / "outputs" / "derived" / "targeted_bd_analysis.json"
OUTPUT_REPORT = PROJECT_ROOT / "outputs" / "reports" / "TARGETED_BD_ANALYSE.md"

def load_targeted_data() -> List[Dict]:
 if not TARGETED_FILE.exists():
 raise FileNotFoundError(f"{TARGETED_FILE} fehlt")
 with TARGETED_FILE.open() as fh:
 data = json.load(fh)
 return data.get("data", [])

def analyze_seeds(entries: List[Dict], class_label: str) -> Dict:
 positions = [Counter() for _ in range(55)]
 for entry in entries:
 if entry.get("target_char") != class_label:
 continue
 seed = entry.get("seed", "")
 if len(seed) < 55:
 continue
 for idx, ch in enumerate(seed[:55]):
 positions[idx][ch.upper()] += 1
 top_chars = []
 for idx, counter in enumerate(positions):
 if counter:
 char, count = counter.most_common(1)[0]
 top_chars.append({"position": idx, "char": char, "count": count})
 return {
 "class": class_label,
 "total": sum(c.total() for c in positions),
 "top_chars": top_chars
 }

def main() -> None:
 entries = load_targeted_data()
 total = len(entries)

 class_counts = Counter(entry.get("target_char") for entry in entries)
 on_chain_counts = sum(1 for entry in entries if entry.get("on_chain"))

 valid_ticks = [entry.get("rpc", {}).get("valid_for_tick") for entry in entries if entry.get("rpc")]
 valid_ticks = [tick for tick in valid_ticks if isinstance(tick, int)]

 seed_analysis = {
 "B": analyze_seeds(entries, "B"),
 "D": analyze_seeds(entries, "D"),
 }

 output_data = {
 "timestamp": datetime.now().isoformat(),
 "total_entries": total,
 "class_counts": dict(class_counts),
 "on_chain_rate": {
 "count": on_chain_counts,
 "percent": (on_chain_counts / total * 100) if total else 0
 },
 "valid_for_tick": {
 "min": int(np.min(valid_ticks)) if valid_ticks else None,
 "max": int(np.max(valid_ticks)) if valid_ticks else None,
 "mean": float(np.mean(valid_ticks)) if valid_ticks else None,
 "count": len(valid_ticks)
 },
 "seed_analysis": seed_analysis,
 }

 OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
 with OUTPUT_JSON.open("w") as fh:
 json.dump(output_data, fh, indent=2)

 OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
 with OUTPUT_REPORT.open("w") as fh:
 fh.write("# Targeted B/D Analyse\n\n")
 fh.write(f"- Gesamt: {total}\n")
 fh.write(f"- Klassenverteilung: {dict(class_counts)}\n")
 fh.write(f"- On-Chain: {on_chain_counts} ({output_data['on_chain_rate']['percent']:.2f}%)\n")
 fh.write(f"- validForTick Range: {output_data['valid_for_tick']}\n\n")
 for label in ["B", "D"]:
 fh.write(f"## Seed-Topchars for Klasse {label}\n")
 top = seed_analysis[label]["top_chars"][:10]
 for entry in top:
 fh.write(f"- Pos {entry['position']}: {entry['char']} ({entry['count']})\n")
 fh.write("\n")

 print(f"✅ Analyse gespeichert: {OUTPUT_JSON} & {OUTPUT_REPORT}")

if __name__ == "__main__":
 main()

