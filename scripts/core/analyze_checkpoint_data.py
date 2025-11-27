#!/usr/bin/env python3
"""
Analyze die bereits validierten Identities aus dem Checkpoint.

Erstellt:
- Statistiken
- Seed-Mapping
- Pattern-Analyse
"""

import json
from pathlib import Path
from typing import List, Dict
from collections import Counter

OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs" / "derived"
CHECKPOINT_FILE = OUTPUT_DIR / "onchain_validation_checkpoint.json"
OUTPUT_FILE = OUTPUT_DIR / "checkpoint_data_analysis.json"
REPORT_FILE = OUTPUT_DIR / "checkpoint_data_analysis_report.md"

def identity_to_seed(identity: str) -> str:
 """Konvertiere Identity zu Seed."""
 return identity.lower()[:55]

def analyze_checkpoint_data(results: List[Dict]) -> Dict:
 """Analyze Checkpoint-Daten."""
 
 onchain_identities = [r["identity"] for r in results if r.get("exists")]
 offchain_identities = [r["identity"] for r in results if not r.get("exists")]
 
 # Seed-Analyse
 onchain_seeds = [identity_to_seed(id) for id in onchain_identities]
 unique_seeds = len(set(onchain_seeds))
 
 # Pattern-Analyse
 first_chars = Counter(id[0] for id in onchain_identities)
 last_chars = Counter(id[-1] for id in onchain_identities)
 seed_starts = Counter(seed[:5] for seed in onchain_seeds)
 
 # Balance-Analyse
 balances = [r.get("balance", "0") for r in results if r.get("exists")]
 balance_values = []
 for b in balances:
 try:
 if isinstance(b, str):
 balance_values.append(int(b) if b.isdigit() else 0)
 else:
 balance_values.append(int(b))
 except:
 balance_values.append(0)
 
 total_balance = sum(balance_values)
 non_zero_balances = sum(1 for b in balance_values if b > 0)
 
 return {
 "total_checked": len(results),
 "onchain_count": len(onchain_identities),
 "offchain_count": len(offchain_identities),
 "onchain_rate": len(onchain_identities) / len(results) * 100 if results else 0,
 "unique_seeds": unique_seeds,
 "seed_duplicates": len(onchain_seeds) - unique_seeds,
 "first_chars": dict(first_chars.most_common(10)),
 "last_chars": dict(last_chars.most_common(10)),
 "seed_starts": dict(seed_starts.most_common(10)),
 "total_balance": total_balance,
 "non_zero_balances": non_zero_balances,
 "average_balance": total_balance / len(onchain_identities) if onchain_identities else 0,
 }

def main():
 """Analyze Checkpoint-Daten."""
 
 print("=" * 80)
 print("CHECKPOINT-DATEN ANALYSE")
 print("=" * 80)
 print()
 
 if not CHECKPOINT_FILE.exists():
 print(f"❌ Checkpoint-Datei nicht gefunden: {CHECKPOINT_FILE}")
 return
 
 # Load Checkpoint
 print("Load Checkpoint-Daten...")
 with CHECKPOINT_FILE.open() as f:
 checkpoint = json.load(f)
 
 results = checkpoint.get("results", [])
 total_checked = checkpoint.get("total_checked", 0)
 onchain_count = checkpoint.get("onchain_count", 0)
 
 print(f"✅ {len(results):,} Ergebnisse geloadn")
 print(f" Total geprüft: {total_checked:,}")
 print(f" On-chain: {onchain_count:,}")
 print()
 
 if not results:
 print("❌ Keine Ergebnisse gefunden!")
 return
 
 # Analyze
 print("Analyze Daten...")
 analysis = analyze_checkpoint_data(results)
 print()
 
 # Zeige Ergebnisse
 print("=" * 80)
 print("ERGEBNISSE")
 print("=" * 80)
 print()
 
 print(f"Total geprüft: {analysis['total_checked']:,}")
 print(f"On-chain: {analysis['onchain_count']:,} ({analysis['onchain_rate']:.1f}%)")
 print(f"Off-chain: {analysis['offchain_count']:,}")
 print()
 
 print(f"Unique Seeds: {analysis['unique_seeds']:,}")
 print(f"Seed-Duplikate: {analysis['seed_duplicates']:,}")
 print()
 
 print("Häufigste erste Zeichen:")
 for char, count in sorted(analysis['first_chars'].items(), key=lambda x: x[1], reverse=True)[:5]:
 print(f" {char}: {count}x ({count/analysis['onchain_count']*100:.1f}%)")
 print()
 
 print("Häufigste letzte Zeichen:")
 for char, count in sorted(analysis['last_chars'].items(), key=lambda x: x[1], reverse=True)[:5]:
 print(f" {char}: {count}x ({count/analysis['onchain_count']*100:.1f}%)")
 print()
 
 print(f"Total Balance: {analysis['total_balance']:,} QU")
 print(f"Non-zero Balances: {analysis['non_zero_balances']:,}")
 print(f"Average Balance: {analysis['average_balance']:.2f} QU")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 with OUTPUT_FILE.open("w") as f:
 json.dump(analysis, f, indent=2)
 
 print(f"💾 Ergebnisse gespeichert in: {OUTPUT_FILE}")
 
 # Erstelle Report
 report_content = f"""# Checkpoint-Daten Analyse

**Datum**: 2025-11-22 
**Total geprüft**: {analysis['total_checked']:,}

## Zusammenfassung

- **On-chain**: {analysis['onchain_count']:,} ({analysis['onchain_rate']:.1f}%)
- **Off-chain**: {analysis['offchain_count']:,}
- **Unique Seeds**: {analysis['unique_seeds']:,}
- **Seed-Duplikate**: {analysis['seed_duplicates']:,}

## Pattern-Analyse

### Häufigste erste Zeichen
"""
 
 for char, count in sorted(analysis['first_chars'].items(), key=lambda x: x[1], reverse=True)[:10]:
 report_content += f"- `{char}`: {count}x ({count/analysis['onchain_count']*100:.1f}%)\n"
 
 report_content += "\n### Häufigste letzte Zeichen\n"
 for char, count in sorted(analysis['last_chars'].items(), key=lambda x: x[1], reverse=True)[:10]:
 report_content += f"- `{char}`: {count}x ({count/analysis['onchain_count']*100:.1f}%)\n"
 
 report_content += "\n## Balance-Analyse\n\n"
 report_content += f"- **Total Balance**: {analysis['total_balance']:,} QU\n"
 report_content += f"- **Non-zero Balances**: {analysis['non_zero_balances']:,}\n"
 report_content += f"- **Average Balance**: {analysis['average_balance']:.2f} QU\n"
 
 with REPORT_FILE.open("w") as f:
 f.write(report_content)
 
 print(f"📄 Report erstellt: {REPORT_FILE}")
 print()
 print("✅ Analyse abgeschlossen!")

if __name__ == "__main__":
 main()

