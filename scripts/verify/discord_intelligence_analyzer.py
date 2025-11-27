#!/usr/bin/env python3
"""
Discord Intelligence Analyzer: Search through all available documents for
Discord messages from VFB/CFB about the matrix, puzzle, contract, or reward.

This script searches through:
- All markdown files
- All text files
- All JSON files
- Looking for keywords related to:
 - VFB, CFB, Come-from-Beyond
 - Matrix, Puzzle, Reward
 - Contract ID
 - Genesis, Asset
 - 26, 676, Block-ID
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path("${PROJECT_ROOT}")
OUTPUT_DIR = Path("outputs/derived")
OUTPUT_JSON = OUTPUT_DIR / "discord_intelligence_analysis.json"
OUTPUT_MD = OUTPUT_DIR / "discord_intelligence_analysis.md"

# Keywords to search for
KEYWORDS = {
 "cfb": ["cfb", "vfb", "come-from-beyond", "come from beyond"],
 "matrix": ["matrix", "anna matrix", "anna-matrix"],
 "puzzle": ["puzzle", "reward", "prize", "solution"],
 "contract": ["contract", "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"],
 "genesis": ["genesis", "asset", "token"],
 "numbers": ["26", "676", "128", "1649"],
 "block": ["block", "block-id", "block id"],
 "layer": ["layer", "seed", "identity"],
}

def search_file(file_path: Path) -> Dict[str, List[Tuple[int, str]]]:
 """Search a file for keywords and return matches with line numbers."""
 matches = defaultdict(list)
 
 try:
 with file_path.open("r", encoding="utf-8", errors="ignore") as f:
 for line_num, line in enumerate(f, 1):
 line_lower = line.lower()
 
 for category, keywords in KEYWORDS.items():
 for keyword in keywords:
 if keyword.lower() in line_lower:
 # Get context (surrounding lines)
 matches[category].append((line_num, line.strip()))
 break # Only count once per category per line
 except Exception as e:
 print(f" ⚠️ Error reading {file_path}: {e}")
 
 return dict(matches)

def analyze_all_files() -> Dict:
 """Search all relevant files in the project."""
 print("Searching for Discord messages and relevant information...")
 print()
 
 results = {
 "files_searched": [],
 "matches_by_category": defaultdict(list),
 "files_with_cfb_mentions": [],
 "files_with_contract_mentions": [],
 "files_with_puzzle_mentions": [],
 "interesting_findings": [],
 }
 
 # Search in project root and subdirectories
 search_paths = [
 PROJECT_ROOT / "docs",
 PROJECT_ROOT / "outputs",
 PROJECT_ROOT / "scripts",
 PROJECT_ROOT,
 ]
 
 file_extensions = [".md", ".txt", ".json", ".py"]
 
 for search_path in search_paths:
 if not search_path.exists():
 continue
 
 print(f"Searching in: {search_path}")
 
 for ext in file_extensions:
 for file_path in search_path.rglob(f"*{ext}"):
 # Skip venv, .git, etc.
 if any(skip in str(file_path) for skip in ["venv", ".git", "__pycache__", "node_modules"]):
 continue
 
 matches = search_file(file_path)
 
 if matches:
 relative_path = file_path.relative_to(PROJECT_ROOT)
 results["files_searched"].append(str(relative_path))
 
 for category, match_list in matches.items():
 results["matches_by_category"][category].append({
 "file": str(relative_path),
 "matches": match_list[:10], # Limit to first 10 matches
 })
 
 # Track special categories
 if "cfb" in matches:
 results["files_with_cfb_mentions"].append(str(relative_path))
 if "contract" in matches:
 results["files_with_contract_mentions"].append(str(relative_path))
 if "puzzle" in matches:
 results["files_with_puzzle_mentions"].append(str(relative_path))
 
 return results

def extract_interesting_findings(results: Dict) -> List[str]:
 """Extract particularly interesting findings."""
 findings = []
 
 # Check for contract ID mentions
 contract_id = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
 for item in results["matches_by_category"].get("contract", []):
 file_path = item["file"]
 matches = item["matches"]
 for line_num, line in matches:
 if contract_id in line:
 findings.append(f"Contract ID found in {file_path}:{line_num}: {line[:100]}")
 
 # Check for CFB + Matrix combinations
 cfb_files = set(results["files_with_cfb_mentions"])
 matrix_matches = results["matches_by_category"].get("matrix", [])
 
 for item in matrix_matches:
 file_path = item["file"]
 if file_path in cfb_files:
 findings.append(f"CFB + Matrix mentioned together in {file_path}")
 
 # Check for Puzzle + Reward combinations
 puzzle_files = set(results["files_with_puzzle_mentions"])
 reward_matches = results["matches_by_category"].get("puzzle", [])
 
 for item in reward_matches:
 file_path = item["file"]
 if "reward" in str(item).lower() or "prize" in str(item).lower():
 findings.append(f"Puzzle/Reward mentioned in {file_path}")
 
 return findings

def main() -> int:
 OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
 
 print("=" * 80)
 print("🔍 DISCORD INTELLIGENCE ANALYZER")
 print("=" * 80)
 print()
 print("Searching for Discord messages and relevant information...")
 print()
 
 results = analyze_all_files()
 results["interesting_findings"] = extract_interesting_findings(results)
 
 # Print summary
 print("=" * 80)
 print("SUMMARY")
 print("=" * 80)
 print()
 print(f"Files searched: {len(results['files_searched'])}")
 print(f"Files with CFB mentions: {len(results['files_with_cfb_mentions'])}")
 print(f"Files with Contract mentions: {len(results['files_with_contract_mentions'])}")
 print(f"Files with Puzzle mentions: {len(results['files_with_puzzle_mentions'])}")
 print()
 
 print("Matches by category:")
 for category, items in results["matches_by_category"].items():
 print(f" {category}: {len(items)} files")
 print()
 
 if results["interesting_findings"]:
 print("=" * 80)
 print("🎯 INTERESTING FINDINGS")
 print("=" * 80)
 print()
 for finding in results["interesting_findings"]:
 print(f" • {finding}")
 print()
 
 # Save results
 with OUTPUT_JSON.open("w", encoding="utf-8") as f:
 json.dump(results, f, indent=2, default=str)
 
 # Create markdown report
 with OUTPUT_MD.open("w", encoding="utf-8") as f:
 f.write("# Discord Intelligence Analysis\n\n")
 f.write("## Summary\n\n")
 f.write(f"- Files searched: {len(results['files_searched'])}\n")
 f.write(f"- Files with CFB mentions: {len(results['files_with_cfb_mentions'])}\n")
 f.write(f"- Files with Contract mentions: {len(results['files_with_contract_mentions'])}\n")
 f.write(f"- Files with Puzzle mentions: {len(results['files_with_puzzle_mentions'])}\n\n")
 
 if results["interesting_findings"]:
 f.write("## Interesting Findings\n\n")
 for finding in results["interesting_findings"]:
 f.write(f"- {finding}\n")
 f.write("\n")
 
 f.write("## Detailed Matches\n\n")
 for category, items in results["matches_by_category"].items():
 if items:
 f.write(f"### {category.upper()}\n\n")
 for item in items[:5]: # Limit to first 5 files per category
 f.write(f"**File:** {item['file']}\n\n")
 for line_num, line in item["matches"][:3]: # First 3 matches
 f.write(f" Line {line_num}: `{line[:150]}`\n")
 f.write("\n")
 
 print("=" * 80)
 print(f"✅ Results saved to:")
 print(f" - {OUTPUT_JSON}")
 print(f" - {OUTPUT_MD}")
 print("=" * 80)
 
 return 0

if __name__ == "__main__":
 raise SystemExit(main())

