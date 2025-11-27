#!/usr/bin/env python3
"""
Bereite finale Auswertungen vor nach Abschluss der On-Chain Validierung.

Erstellt:
1. Statistische Zusammenfassung
2. Layer-Analyse
3. Seed-Validierung
4. Vergleich mit Control Group
5. Finale Reports
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Any

OUTPUT_DIR = Path("outputs/derived")
REPORTS_DIR = Path("outputs/reports")

def load_onchain_results() -> Dict:
 """Load finale On-Chain Validierungsergebnisse."""
 
 # Check finale Datei zuerst (hat höhere Priorität)
 complete_file = OUTPUT_DIR / "checksum_identities_onchain_validation_complete.json"
 if complete_file.exists():
 with complete_file.open() as f:
 complete_data = json.load(f)
 summary = complete_data.get("summary", {})
 
 # Load Batch-Dateien falls vorhanden
 results = []
 onchain_identities = []
 total_batches = complete_data.get("total_batches", 0)
 
 for i in range(total_batches):
 batch_file = OUTPUT_DIR / f"onchain_identities_batch_{i}.json"
 if batch_file.exists():
 with batch_file.open() as f:
 batch_data = json.load(f)
 if isinstance(batch_data, list):
 # Check Format: Liste von Strings oder Dicts?
 if batch_data and isinstance(batch_data[0], str):
 # Liste von Identity-Strings
 for identity in batch_data:
 results.append({"exists": True, "identity": identity})
 onchain_identities.append({"identity": identity})
 else:
 # Liste von Dicts
 results.extend(batch_data)
 onchain_identities.extend([r for r in batch_data if r.get("exists")])
 
 # Falls keine Batch-Dateien, nutze Summary-Daten
 if not results:
 total_checked = summary.get("total_checked", 0)
 onchain_count = summary.get("onchain_found", 0)
 # Erstelle Platzhalter-Results for Analyse
 results = [{"exists": True} for _ in range(onchain_count)]
 results.extend([{"exists": False} for _ in range(total_checked - onchain_count)])
 onchain_identities = [{"identity": "PLACEHOLDER"} for _ in range(onchain_count)]
 
 return {
 "processed": summary.get("total_checked", len(results)),
 "onchain_identities": onchain_identities,
 "results": results,
 "summary": summary,
 }
 
 # Check Checkpoint
 checkpoint_file = OUTPUT_DIR / "onchain_validation_checkpoint.json"
 if checkpoint_file.exists():
 with checkpoint_file.open() as f:
 return json.load(f)
 
 return {}

def load_comprehensive_scan() -> Dict:
 """Load Comprehensive Scan Ergebnisse."""
 scan_file = OUTPUT_DIR / "comprehensive_identity_seed_scan.json"
 if scan_file.exists():
 with scan_file.open() as f:
 return json.load(f)
 return {}

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def analyze_statistics(onchain_data: Dict) -> Dict:
 """Analyze statistische Eigenschaften."""
 
 results = onchain_data.get("results", [])
 onchain_identities = [r for r in results if r.get("exists")]
 
 stats = {
 "total_checked": len(results),
 "onchain_count": len(onchain_identities),
 "offchain_count": len(results) - len(onchain_identities),
 "onchain_rate": len(onchain_identities) / len(results) * 100 if results else 0,
 }
 
 # Balance-Analyse
 balances = []
 for result in onchain_identities:
 balance = result.get("balance", "0")
 try:
 balances.append(float(balance))
 except:
 balances.append(0.0)
 
 if balances:
 stats["balance_stats"] = {
 "total": sum(balances),
 "average": sum(balances) / len(balances),
 "max": max(balances),
 "min": min(balances),
 "non_zero_count": sum(1 for b in balances if b > 0),
 }
 
 # Tick-Analyse
 ticks = [r.get("validForTick", 0) for r in onchain_identities if r.get("validForTick")]
 if ticks:
 stats["tick_stats"] = {
 "min": min(ticks),
 "max": max(ticks),
 "average": sum(ticks) / len(ticks),
 }
 
 return stats

def analyze_layer_distribution(scan_data: Dict, onchain_data: Dict) -> Dict:
 """Analyze Layer-Verteilung."""
 
 layer_stats = defaultdict(lambda: {"total": 0, "onchain": 0})
 
 # Load Layer-Informationen aus Scan
 seed_results = scan_data.get("seed_results", [])
 onchain_set = {r["identity"] for r in onchain_data.get("results", []) if r.get("exists")}
 
 for seed_result in seed_results:
 layer = seed_result.get("layer", 1)
 identity = seed_result.get("identity", "")
 
 layer_stats[layer]["total"] += 1
 if identity in onchain_set:
 layer_stats[layer]["onchain"] += 1
 
 # Berechne Prozentsätze
 for layer in layer_stats:
 stats = layer_stats[layer]
 stats["onchain_rate"] = (stats["onchain"] / stats["total"] * 100) if stats["total"] > 0 else 0
 
 return dict(layer_stats)

def analyze_seed_patterns(onchain_data: Dict) -> Dict:
 """Analyze Seed-Muster."""
 
 onchain_identities = [r["identity"] for r in onchain_data.get("results", []) if r.get("exists")]
 
 # Extrahiere Seeds
 seeds = [identity_to_seed(identity) for identity in onchain_identities]
 
 # Analyze Charakter-Verteilung
 char_distribution = Counter()
 for seed in seeds:
 char_distribution.update(seed)
 
 # Analyze Wiederholungen
 repeating_patterns = defaultdict(int)
 for seed in seeds:
 # Finde wiederholende Muster (z.B. "aaaaa")
 for i in range(len(seed) - 3):
 pattern = seed[i:i+4]
 if len(set(pattern)) == 1: # Alle gleich
 repeating_patterns[pattern[0]] += 1
 
 return {
 "total_seeds": len(seeds),
 "char_distribution": dict(char_distribution.most_common(10)),
 "repeating_patterns": dict(repeating_patterns),
 }

def compare_with_control_group() -> Dict:
 """Vergleiche mit Control Group Ergebnissen."""
 
 control_file = REPORTS_DIR / "control_group_report.json"
 if not control_file.exists():
 return {"error": "Control group results not found"}
 
 with control_file.open() as f:
 control_data = json.load(f)
 
 # Load Anna Matrix Ergebnisse
 onchain_data = load_onchain_results()
 anna_onchain = len([r for r in onchain_data.get("results", []) if r.get("exists")])
 anna_total = len(onchain_data.get("results", []))
 
 control_onchain = control_data.get("onchain_count", 0)
 control_total = control_data.get("total_tested", 0)
 
 return {
 "anna_matrix": {
 "total": anna_total,
 "onchain": anna_onchain,
 "rate": (anna_onchain / anna_total * 100) if anna_total > 0 else 0,
 },
 "control_group": {
 "total": control_total,
 "onchain": control_onchain,
 "rate": (control_onchain / control_total * 100) if control_total > 0 else 0,
 },
 "difference": {
 "anna_rate": (anna_onchain / anna_total * 100) if anna_total > 0 else 0,
 "control_rate": (control_onchain / control_total * 100) if control_total > 0 else 0,
 "ratio": ((anna_onchain / anna_total) / (control_onchain / control_total)) if (control_total > 0 and anna_total > 0 and control_onchain > 0) else 0,
 },
 }

def create_final_report(analysis: Dict) -> str:
 """Erstelle finalen Markdown-Report."""
 
 lines = [
 "# Final Analysis Report",
 "",
 f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
 "",
 "## Summary",
 "",
 f"- **Total identities checked**: {analysis['statistics']['total_checked']:,}",
 f"- **On-chain identities**: {analysis['statistics']['onchain_count']:,}",
 f"- **Off-chain identities**: {analysis['statistics']['offchain_count']:,}",
 f"- **On-chain rate**: {analysis['statistics']['onchain_rate']:.2f}%",
 "",
 "## Statistics",
 "",
 ]
 
 # Balance Stats
 if "balance_stats" in analysis["statistics"]:
 bs = analysis["statistics"]["balance_stats"]
 lines.extend([
 "### Balance Statistics",
 "",
 f"- **Total balance**: {bs['total']:,.2f} QU",
 f"- **Average balance**: {bs['average']:,.2f} QU",
 f"- **Max balance**: {bs['max']:,.2f} QU",
 f"- **Min balance**: {bs['min']:,.2f} QU",
 f"- **Non-zero balances**: {bs['non_zero_count']:,}",
 "",
 ])
 
 # Layer Distribution
 if analysis.get("layer_distribution"):
 lines.extend([
 "## Layer Distribution",
 "",
 "| Layer | Total | On-Chain | On-Chain Rate |",
 "| --- | --- | --- | --- |",
 ])
 
 for layer in sorted(analysis["layer_distribution"].keys(), key=lambda x: int(x) if str(x).isdigit() else 999):
 stats = analysis["layer_distribution"][layer]
 lines.append(
 f"| {layer} | {stats['total']:,} | {stats['onchain']:,} | {stats['onchain_rate']:.2f}% |"
 )
 lines.append("")
 
 # Control Group Comparison
 if analysis.get("control_comparison") and "error" not in analysis["control_comparison"]:
 cc = analysis["control_comparison"]
 lines.extend([
 "## Control Group Comparison",
 "",
 "### Anna Matrix",
 f"- Total: {cc['anna_matrix']['total']:,}",
 f"- On-chain: {cc['anna_matrix']['onchain']:,}",
 f"- Rate: {cc['anna_matrix']['rate']:.2f}%",
 "",
 "### Control Group (Random Matrices)",
 f"- Total: {cc['control_group']['total']:,}",
 f"- On-chain: {cc['control_group']['onchain']:,}",
 f"- Rate: {cc['control_group']['rate']:.2f}%",
 "",
 "### Difference",
 f"- Ratio: {cc['difference']['ratio']:.2f}x",
 "",
 ])
 
 # Seed Patterns
 if analysis.get("seed_patterns"):
 sp = analysis["seed_patterns"]
 lines.extend([
 "## Seed Pattern Analysis",
 "",
 f"- **Total seeds analyzed**: {sp['total_seeds']:,}",
 "",
 "### Character Distribution (Top 10)",
 "",
 "| Character | Count |",
 "| --- | --- |",
 ])
 
 for char, count in list(sp["char_distribution"].items())[:10]:
 lines.append(f"| {char} | {count:,} |")
 
 lines.append("")
 
 return "\n".join(lines)

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("PREPARE FINAL ANALYSIS")
 print("=" * 80)
 print()
 
 # Load Daten
 print("Loading on-chain validation results...")
 onchain_data = load_onchain_results()
 if not onchain_data:
 print("❌ No on-chain validation data found!")
 return
 
 print(f"✅ Loaded {len(onchain_data.get('results', []))} results")
 print()
 
 print("Loading comprehensive scan data...")
 scan_data = load_comprehensive_scan()
 if scan_data:
 print(f"✅ Loaded scan data")
 else:
 print("⚠️ No comprehensive scan data found")
 print()
 
 # Analyze
 print("Analyzing statistics...")
 statistics = analyze_statistics(onchain_data)
 print("✅ Statistics calculated")
 print()
 
 print("Analyzing layer distribution...")
 layer_distribution = analyze_layer_distribution(scan_data, onchain_data) if scan_data else {}
 print("✅ Layer distribution analyzed")
 print()
 
 print("Analyzing seed patterns...")
 seed_patterns = analyze_seed_patterns(onchain_data)
 print("✅ Seed patterns analyzed")
 print()
 
 print("Comparing with control group...")
 control_comparison = compare_with_control_group()
 print("✅ Control group comparison done")
 print()
 
 # Zusammenfassung
 analysis = {
 "statistics": statistics,
 "layer_distribution": layer_distribution,
 "seed_patterns": seed_patterns,
 "control_comparison": control_comparison,
 }
 
 # Speichere JSON
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 json_file = OUTPUT_DIR / "final_analysis.json"
 with json_file.open("w") as f:
 json.dump(analysis, f, indent=2)
 print(f"💾 Analysis saved to: {json_file}")
 print()
 
 # Erstelle Report
 report = create_final_report(analysis)
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report_file = REPORTS_DIR / "final_analysis_report.md"
 with report_file.open("w") as f:
 f.write(report)
 print(f"📄 Report saved to: {report_file}")
 print()
 
 print("=" * 80)
 print("✅ ANALYSIS PREPARATION COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

