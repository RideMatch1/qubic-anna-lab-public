#!/usr/bin/env python3
"""
Forensic audit script - checks for sensitive data before GitHub upload.

Scans for:
- Absolute file paths
- Personal names
- IP addresses
- Localhost references
- System-specific paths
- API keys/tokens
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Patterns to check
PATTERNS = {
 "absolute_paths": [
 r"/Users/[\w\-]+/",
 r"/home/[\w\-]+/",
 r"/tmp/",
 r"/var/",
 r"C:\\Users\\",
 r"C:\\",
 ],
 "personal_names": [
 r"Lukas\s+Hertle",
 r"${USER}",
 r"${USER}",
 ],
 "ip_addresses": [
 r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
 r"192\.168\.\d{1,3}\.\d{1,3}",
 r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}",
 r"172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}",
 ],
 "localhost": [
 r"localhost",
 r"127\.0\.0\.1",
 ],
 "api_keys": [
 r"api[_-]?key\s*[:=]\s*['\"][\w\-]+['\"]",
 r"token\s*[:=]\s*['\"][\w\-]{20,}['\"]",
 r"secret\s*[:=]\s*['\"][\w\-]+['\"]",
 ],
}

# Files/directories to skip
SKIP_PATTERNS = [
 ".git/",
 "venv/",
 "venv-tx/",
 "__pycache__/",
 ".DS_Store",
 "*.pyc",
 "*.pyo",
 "*.pyd",
 "outputs/derived/cfb_discord_messages/", # Discord data
 "outputs/derived/discord_intelligence_analysis.json",
 "outputs/derived/discord_intelligence_analysis.md",
]

def should_skip(file_path: Path) -> bool:
 """Check if file should be skipped."""
 path_str = str(file_path)
 for pattern in SKIP_PATTERNS:
 if pattern in path_str or file_path.match(pattern):
 return True
 return False

def scan_file(file_path: Path) -> List[Dict]:
 """Scan a single file for sensitive data."""
 issues = []
 
 try:
 with file_path.open('r', encoding='utf-8', errors='ignore') as f:
 content = f.read()
 lines = content.split('\n')
 
 for category, patterns in PATTERNS.items():
 for pattern in patterns:
 regex = re.compile(pattern, re.IGNORECASE)
 for line_num, line in enumerate(lines, 1):
 matches = regex.finditer(line)
 for match in matches:
 # Skip if in comment/docstring (less critical)
 if '#' in line[:match.start()] or '"""' in line[:match.start()]:
 continue
 
 issues.append({
 "file": str(file_path.relative_to(PROJECT_ROOT)),
 "line": line_num,
 "category": category,
 "pattern": pattern,
 "match": match.group(),
 "context": line.strip()[:100],
 })
 except Exception as e:
 # Skip binary files or unreadable files
 pass
 
 return issues

def scan_directory(root: Path) -> List[Dict]:
 """Scan directory recursively for sensitive data."""
 all_issues = []
 
 for file_path in root.rglob('*'):
 if file_path.is_file() and not should_skip(file_path):
 issues = scan_file(file_path)
 all_issues.extend(issues)
 
 return all_issues

def main():
 """Main audit function."""
 print("=" * 80)
 print("FORENSIC AUDIT - Checking for sensitive data")
 print("=" * 80)
 print()
 
 issues = scan_directory(PROJECT_ROOT)
 
 # Group by category
 by_category = {}
 for issue in issues:
 cat = issue["category"]
 if cat not in by_category:
 by_category[cat] = []
 by_category[cat].append(issue)
 
 # Report
 print(f"Total issues found: {len(issues)}")
 print()
 
 for category, category_issues in sorted(by_category.items()):
 print(f"{category.upper()}: {len(category_issues)} issues")
 for issue in category_issues[:5]: # Show first 5
 print(f" {issue['file']}:{issue['line']} - {issue['match']}")
 if len(category_issues) > 5:
 print(f" ... and {len(category_issues) - 5} more")
 print()
 
 # Critical files
 critical_files = set()
 for issue in issues:
 if issue["category"] in ["absolute_paths", "personal_names"]:
 critical_files.add(issue["file"])
 
 if critical_files:
 print("CRITICAL FILES TO FIX:")
 for file in sorted(critical_files):
 print(f" - {file}")
 print()
 
 # Summary
 if issues:
 print("⚠️ ISSUES FOUND - Review and fix before GitHub upload!")
 return 1
 else:
 print("✅ No issues found - ready for GitHub upload!")
 return 0

if __name__ == "__main__":
 exit(main())

