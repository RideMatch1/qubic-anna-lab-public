#!/usr/bin/env python3
"""
Analyze alle Qubic/Aigarth Repositories for relevante Informationen.

Repositories:
- aigarth-analysis
- aigarth-it
- aigarth-ternary-net
- core
- Creation-of-AI-artist-aNNa-Aigarth-to-attract-a-new-Gen-Z-audience
- neuraxon
- oracle-machine
- qubic
- smart-contract-qubic-exercice
"""

import json
import re
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from datetime import datetime

REPOS_BASE = Path("${PROJECTS_ROOT}/qubic-anna-lab-public/repos")
OUTPUT_DIR = Path("${PROJECT_ROOT}/outputs/derived")
REPORTS_DIR = Path("${PROJECT_ROOT}/outputs/reports")

# Keywords for Suche
KEYWORDS = {
 "anna": ["anna", "Anna", "ANNA", "aNNa"],
 "matrix": ["matrix", "Matrix", "anna matrix", "Anna Matrix"],
 "identity": ["identity", "identities", "Identity", "Identities", "public key"],
 "seed": ["seed", "Seed", "seeds"],
 "helix": ["helix", "Helix", "helix gate", "Helix gate", "A+B+C"],
 "evolution": ["evolution", "Evolution", "evolutionary", "selection", "fitness"],
 "intelligent_tissue": ["intelligent tissue", "Intelligent Tissue", "tissue"],
 "layer": ["layer", "Layer", "layer-2", "Layer-2", "layer 2"],
 "oracle": ["oracle", "Oracle", "oracle machine", "Oracle Machine"],
 "aigarth": ["aigarth", "Aigarth", "AIGARTH"],
}

def search_file(file_path: Path, keywords: Dict) -> Dict:
 """Suche Keywords in einer Datei."""
 
 if not file_path.exists() or not file_path.is_file():
 return {}
 
 # Skip binary files
 try:
 content = file_path.read_text(encoding='utf-8', errors='ignore')
 except Exception:
 return {}
 
 # Skip very large files
 if len(content) > 1_000_000: # 1MB
 return {}
 
 matches = defaultdict(list)
 
 for category, keyword_list in keywords.items():
 for keyword in keyword_list:
 pattern = re.compile(re.escape(keyword), re.IGNORECASE)
 
 found_matches = list(pattern.finditer(content))
 if found_matches:
 for match in found_matches[:5]: # Limit matches per file
 start = max(0, match.start() - 100)
 end = min(len(content), match.end() + 100)
 context = content[start:end].replace('\n', ' ').strip()
 
 matches[category].append({
 "keyword": keyword,
 "context": context,
 "position": match.start(),
 })
 
 return dict(matches)

def analyze_repo(repo_path: Path, repo_name: str) -> Dict:
 """Analyze ein Repository."""
 
 print(f" Analyzing {repo_name}...")
 
 results = {
 "repo_name": repo_name,
 "files_analyzed": 0,
 "files_with_matches": 0,
 "keyword_matches": defaultdict(int),
 "relevant_files": [],
 }
 
 # Suche nach relevanten Dateien
 file_patterns = ["*.md", "*.py", "*.txt", "*.json", "README*", "*.rst"]
 
 for pattern in file_patterns:
 for file_path in repo_path.rglob(pattern):
 # Skip hidden files and common ignore patterns
 if any(part.startswith('.') for part in file_path.parts):
 continue
 if 'node_modules' in file_path.parts or '__pycache__' in file_path.parts:
 continue
 
 results["files_analyzed"] += 1
 
 matches = search_file(file_path, KEYWORDS)
 
 if matches:
 results["files_with_matches"] += 1
 
 for category, match_list in matches.items():
 results["keyword_matches"][category] += len(match_list)
 
 results["relevant_files"].append({
 "path": str(file_path.relative_to(repo_path)),
 "matches": {cat: len(ml) for cat, ml in matches.items()},
 "total_matches": sum(len(ml) for ml in matches.values()),
 })
 
 return results

def main():
 """Hauptfunktion."""
 
 print("=" * 80)
 print("ANALYZE ALL QUBIC/AIGARTH REPOSITORIES")
 print("=" * 80)
 print()
 
 if not REPOS_BASE.exists():
 print(f"❌ Repositories base not found: {REPOS_BASE}")
 return
 
 repos = [
 "aigarth-analysis",
 "aigarth-it",
 "aigarth-ternary-net",
 "core",
 "Creation-of-AI-artist-aNNa-Aigarth-to-attract-a-new-Gen-Z-audience",
 "neuraxon",
 "oracle-machine",
 "qubic",
 "smart-contract-qubic-exercice",
 ]
 
 all_results = {}
 total_matches = defaultdict(int)
 
 for repo_name in repos:
 repo_path = REPOS_BASE / repo_name
 
 if not repo_path.exists():
 print(f"⚠️ Repository not found: {repo_name}")
 continue
 
 print(f"Analyzing {repo_name}...")
 results = analyze_repo(repo_path, repo_name)
 all_results[repo_name] = results
 
 for category, count in results["keyword_matches"].items():
 total_matches[category] += count
 
 print(f" ✅ {results['files_analyzed']} files, {results['files_with_matches']} with matches")
 print()
 
 # Zusammenfassung
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 
 print("Total Keyword Matches by Category:")
 for category, count in sorted(total_matches.items(), key=lambda x: x[1], reverse=True):
 print(f" {category.upper()}: {count:,}")
 print()
 
 print("Top Repositories by Matches:")
 repo_totals = {
 name: sum(r["keyword_matches"].values())
 for name, r in all_results.items()
 }
 for repo_name, total in sorted(repo_totals.items(), key=lambda x: x[1], reverse=True):
 print(f" {repo_name}: {total:,} matches")
 print()
 
 # Speichere Ergebnisse
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 json_file = OUTPUT_DIR / "all_repos_analysis.json"
 with json_file.open("w") as f:
 json.dump({
 "repositories": all_results,
 "total_matches": dict(total_matches),
 "timestamp": datetime.now().isoformat(),
 }, f, indent=2)
 
 print(f"💾 Results saved to: {json_file}")
 
 # Erstelle Report
 REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 report_file = REPORTS_DIR / "all_repos_analysis_report.md"
 
 with report_file.open("w") as f:
 f.write("# All Repositories Analysis Report\n\n")
 f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
 f.write("## Overview\n\n")
 f.write(f"Analyzed {len(repos)} repositories for keywords related to Anna Matrix research.\n\n")
 
 f.write("## Total Matches by Category\n\n")
 for category, count in sorted(total_matches.items(), key=lambda x: x[1], reverse=True):
 f.write(f"- **{category}**: {count:,} matches\n")
 f.write("\n")
 
 f.write("## Repository Details\n\n")
 for repo_name, results in sorted(all_results.items(), key=lambda x: sum(x[1]["keyword_matches"].values()), reverse=True):
 f.write(f"### {repo_name}\n\n")
 f.write(f"- **Files analyzed**: {results['files_analyzed']}\n")
 f.write(f"- **Files with matches**: {results['files_with_matches']}\n")
 f.write(f"- **Total matches**: {sum(results['keyword_matches'].values())}\n\n")
 
 f.write("**Keyword matches**:\n")
 for category, count in sorted(results["keyword_matches"].items(), key=lambda x: x[1], reverse=True):
 if count > 0:
 f.write(f"- {category}: {count}\n")
 f.write("\n")
 
 if results["relevant_files"]:
 f.write("**Top relevant files**:\n")
 top_files = sorted(results["relevant_files"], key=lambda x: x["total_matches"], reverse=True)[:10]
 for file_info in top_files:
 f.write(f"- `{file_info['path']}`: {file_info['total_matches']} matches\n")
 f.write("\n")
 
 print(f"📄 Report saved to: {report_file}")
 print()
 print("=" * 80)
 print("✅ ALL REPOSITORIES ANALYSIS COMPLETE")
 print("=" * 80)

if __name__ == "__main__":
 main()

