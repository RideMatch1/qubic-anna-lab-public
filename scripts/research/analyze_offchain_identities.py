#!/usr/bin/env python3
"""Analyze die 3 Off-Chain Identities im Detail."""

import json
from pathlib import Path
from collections import Counter
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
EXTENDED_FILE = project_root / "outputs" / "derived" / "layer3_derivation_extended.json"
REPORTS_DIR = project_root / "outputs" / "reports"

def analyze_offchain_identities():
 """Analyze Off-Chain Identities."""
 with EXTENDED_FILE.open() as f:
 data = json.load(f)
 
 results = data.get("results", [])
 offchain = [r for r in results if r.get("layer3_onchain") == False]
 onchain = [r for r in results if r.get("layer3_onchain") == True]
 
 print("=" * 80)
 print("OFF-CHAIN IDENTITIES ANALYSE")
 print("=" * 80)
 print()
 print(f"Gefunden: {len(offchain)} Off-Chain Identities")
 print(f"Vergleich: {len(onchain)} On-Chain Identities")
 print()
 
 if not offchain:
 print("✅ Keine Off-Chain Identities gefunden!")
 return
 
 # Analyze Position 30/4
 offchain_pos30 = Counter()
 offchain_pos4 = Counter()
 onchain_pos30 = Counter()
 onchain_pos4 = Counter()
 
 for entry in offchain:
 identity = entry.get("layer3_identity", "")
 if len(identity) > 30:
 offchain_pos30[identity[30].upper()] += 1
 if len(identity) > 4:
 offchain_pos4[identity[4].upper()] += 1
 
 for entry in onchain[:1000]: # Sample for Vergleich
 identity = entry.get("layer3_identity", "")
 if len(identity) > 30:
 onchain_pos30[identity[30].upper()] += 1
 if len(identity) > 4:
 onchain_pos4[identity[4].upper()] += 1
 
 report_lines = [
 "# Off-Chain Identities Analyse",
 "",
 f"**Gefunden**: {len(offchain)} Off-Chain Identities",
 f"**Vergleich**: {len(onchain)} On-Chain Identities",
 "",
 "## Off-Chain Identities Details",
 ""
 ]
 
 for i, entry in enumerate(offchain, 1):
 identity = entry.get("layer3_identity", "")
 layer2 = entry.get("layer2_identity", "")
 seed = entry.get("seed", "")
 
 report_lines.append(f"### {i}. {identity}")
 report_lines.append(f"- Layer-2: {layer2[:40]}...")
 report_lines.append(f"- Seed: {seed[:40]}...")
 report_lines.append(f"- Position 30: {identity[30] if len(identity) > 30 else 'N/A'}")
 report_lines.append(f"- Position 4: {identity[4] if len(identity) > 4 else 'N/A'}")
 report_lines.append("")
 
 report_lines.extend([
 "## Position 30 Verteilung",
 "",
 "### Off-Chain:",
 ])
 for char, count in sorted(offchain_pos30.items()):
 report_lines.append(f"- {char}: {count}")
 
 report_lines.extend([
 "",
 "### On-Chain (Sample):",
 ])
 for char, count in sorted(onchain_pos30.most_common(10)):
 report_lines.append(f"- {char}: {count}")
 
 report_lines.extend([
 "",
 "## Position 4 Verteilung",
 "",
 "### Off-Chain:",
 ])
 for char, count in sorted(offchain_pos4.items()):
 report_lines.append(f"- {char}: {count}")
 
 report_lines.extend([
 "",
 "### On-Chain (Sample):",
 ])
 for char, count in sorted(onchain_pos4.most_common(10)):
 report_lines.append(f"- {char}: {count}")
 
 report_lines.extend([
 "",
 "## Erkenntnisse",
 "",
 "### Position 30:",
 f"- Off-Chain verwendet: {', '.join(sorted(offchain_pos30.keys()))}",
 f"- Häufigste On-Chain: {', '.join([c for c, _ in onchain_pos30.most_common(5)])}",
 "",
 "### Position 4:",
 f"- Off-Chain verwendet: {', '.join(sorted(offchain_pos4.keys()))}",
 f"- Häufigste On-Chain: {', '.join([c for c, _ in onchain_pos4.most_common(5)])}",
 "",
 "### Mögliche Marker:",
 ])
 
 # Check ob Position 4 Marker zutreffen
 pos4_off_markers = set("UJGHI MOSW".replace(" ", ""))
 for entry in offchain:
 identity = entry.get("layer3_identity", "")
 if len(identity) > 4:
 char = identity[4].upper()
 if char in pos4_off_markers:
 report_lines.append(f"- ✅ Position 4 = '{char}' ist ein bekannter Off-Chain Marker!")
 
 out_file = REPORTS_DIR / "OFFCHAIN_IDENTITIES_ANALYSIS.md"
 with out_file.open("w") as f:
 f.write("\n".join(report_lines) + "\n")
 
 print(f"📝 Report gespeichert: {out_file}")

if __name__ == "__main__":
 analyze_offchain_identities()

