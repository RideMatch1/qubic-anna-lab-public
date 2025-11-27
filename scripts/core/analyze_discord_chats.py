#!/usr/bin/env python3
"""
Analyze Discord Chats nach Keywords zu Anna, Aigarth, Oracle Machines, etc.

Sucht nach CFB Antworten und relevanten Informationen.
"""

import re
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

# Keywords for Suche
KEYWORDS = {
 "anna": ["anna", "Anna", "ANNA"],
 "aigarth": ["aigarth", "Aigarth", "AIGARTH"],
 "oracle_machine": ["oracle machine", "Oracle Machine", "oracle machines", "Oracle Machines"],
 "identity": ["identity", "identities", "Identity", "Identities"],
 "matrix": ["matrix", "Matrix", "anna matrix", "Anna Matrix"],
 "layer": ["layer", "Layer", "layer-2", "Layer-2", "layer 2", "Layer 2"],
 "cfb": ["CFB", "cfb", "ComeFromBeyond"],
 "helix": ["helix", "Helix", "helix gate", "Helix gate"],
 "evolutionary": ["evolutionary", "Evolutionary", "evolution"],
}

def find_discord_files(base_dir: Path) -> List[Path]:
 """Finde alle Discord-Chat-Dateien."""
 discord_files = []
 
 # Suche in verschiedenen Verzeichnissen
 search_dirs = [
 base_dir,
 base_dir / "data",
 base_dir / "docs",
 base_dir / "outputs",
 ]
 
 for search_dir in search_dirs:
 if search_dir.exists():
 # Suche nach verschiedenen Formaten
 for pattern in ["*discord*", "*chat*", "*CFB*", "*.txt", "*.md"]:
 discord_files.extend(search_dir.rglob(pattern))
 
 # Entferne Duplikate und sortiere
 return sorted(set(discord_files))

def search_keywords_in_file(file_path: Path, keywords: Dict[str, List[str]]) -> Dict:
 """Suche Keywords in einer Datei."""
 
 if not file_path.exists() or not file_path.is_file():
 return {}
 
 try:
 content = file_path.read_text(encoding='utf-8', errors='ignore')
 except Exception:
 return {}
 
 results = defaultdict(list)
 
 for category, keyword_list in keywords.items():
 for keyword in keyword_list:
 # Suche nach Keyword mit Context
 pattern = re.compile(
 re.escape(keyword),
 re.IGNORECASE
 )
 
 matches = pattern.finditer(content)
 for match in matches:
 # Extrahiere Context (50 Zeichen vor/nach)
 start = max(0, match.start() - 50)
 end = min(len(content), match.end() + 50)
 context = content[start:end].replace('\n', ' ').strip()
 
 results[category].append({
 "keyword": keyword,
 "context": context,
 "position": match.start(),
 })
 
 return dict(results)

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("ANALYZE DISCORD CHATS FOR KEYWORDS")
 print("=" * 80)
 print()
 
 base_dir = Path(__file__).parent.parent.parent
 
 print("Searching for Discord chat files...")
 discord_files = find_discord_files(base_dir)
 print(f"✅ Found {len(discord_files)} potential files")
 print()
 
 if not discord_files:
 print("⚠️ No Discord files found")
 print(" Searching in:", base_dir)
 print()
 return
 
 print("Analyzing files for keywords...")
 print()
 
 all_results = {}
 file_results = {}
 
 for file_path in discord_files:
 # Überspringe große Binärdateien
 try:
 if file_path.stat().st_size > 10 * 1024 * 1024: # > 10MB
 continue
 except Exception:
 continue
 
 results = search_keywords_in_file(file_path, KEYWORDS)
 
 if results:
 file_results[str(file_path)] = results
 
 # Aggregiere Ergebnisse
 for category, matches in results.items():
 if category not in all_results:
 all_results[category] = []
 all_results[category].extend(matches)
 
 # Zeige Zusammenfassung
 print("=" * 80)
 print("KEYWORD SEARCH RESULTS")
 print("=" * 80)
 print()
 
 for category, matches in sorted(all_results.items()):
 print(f"{category.upper()}: {len(matches)} matches")
 if matches:
 # Zeige erste 3 Matches
 for match in matches[:3]:
 context = match["context"][:100] + "..." if len(match["context"]) > 100 else match["context"]
 print(f" - {context}")
 if len(matches) > 3:
 print(f" ... and {len(matches) - 3} more")
 print()
 
 # Speichere Ergebnisse
 output_dir = Path("outputs/derived")
 output_dir.mkdir(parents=True, exist_ok=True)
 
 json_file = output_dir / "discord_keyword_analysis.json"
 with json_file.open("w") as f:
 import json
 json.dump({
 "summary": {cat: len(matches) for cat, matches in all_results.items()},
 "file_results": file_results,
 "all_matches": all_results,
 }, f, indent=2)
 
 print(f"💾 Results saved to: {json_file}")
 print()
 
 # Erstelle Report
 reports_dir = Path("outputs/reports")
 reports_dir.mkdir(parents=True, exist_ok=True)
 
 report_file = reports_dir / "discord_keyword_analysis_report.md"
 with report_file.open("w") as f:
 f.write("# Discord Keyword Analysis Report\n\n")
 f.write("## Summary\n\n")
 
 for category, matches in sorted(all_results.items()):
 f.write(f"### {category.upper()}\n\n")
 f.write(f"**Total matches**: {len(matches)}\n\n")
 
 if matches:
 f.write("**Sample matches**:\n\n")
 for i, match in enumerate(matches[:10], 1):
 context = match["context"]
 f.write(f"{i}. `{context}`\n\n")
 
 f.write("\n## Files Analyzed\n\n")
 for file_path in discord_files[:20]:
 f.write(f"- `{file_path}`\n")
 
 print(f"📄 Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("✅ DISCORD ANALYSIS COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

