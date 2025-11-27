#!/usr/bin/env python3
"""
sanitize_text.py
---------------
Usage:
 python3 scripts/utils/sanitize_text.py --input path/to/file.md [--output path/to/clean.md]

Purpose:
 - Remove local paths (/Users/...).
 - Strip emojis / unusual unicode.
 - Replace obvious LLM-style phrases.
 - Ensure neutral, human tone.
 - Works on markdown and plain text. For JSON or code, double-check manually.
"""

import argparse
import re
import sys
from pathlib import Path

LLM_PATTERNS = [
 (r"\bLet's\b", "We will"),
 (r"\bLet me\b", ""),
 (r"\bIn this section\b", ""),
 (r"\bTo summarize\b", "Summary:"),
 (r"\bIt's important to\b", ""),
 (r"\bPlease note\b", "Note"),
]

EMOJI_PATTERN = re.compile(
 "["
 "\U0001F600-\U0001F64F"
 "\U0001F300-\U0001F5FF"
 "\U0001F680-\U0001F6FF"
 "\U0001F1E0-\U0001F1FF"
 "]+",
 flags=re.UNICODE
)

PATH_PATTERN = re.compile(r"/Users/[\\w\\-]+(?:/[\\w\\-\\.]+)*")

def sanitize_text(content: str) -> str:
 result = EMOJI_PATTERN.sub("", content)
 result = PATH_PATTERN.sub("${PROJECT_ROOT}", result)
 for pattern, replacement in LLM_PATTERNS:
 result = re.sub(pattern, replacement, result)
 result = re.sub(r"\n{3,}", "\n\n", result)
 return result.strip() + "\n"

def main():
 parser = argparse.ArgumentParser(description="Sanitize markdown/text files for public release.")
 parser.add_argument("--input", required=True, help="Path to source file")
 parser.add_argument("--output", help="Path to sanitized file (optional)")
 args = parser.parse_args()

 src = Path(args.input)
 if not src.exists():
 print(f"Source file not found: {src}")
 sys.exit(1)

 dst = Path(args.output) if args.output else src
 text = src.read_text(encoding="utf-8", errors="ignore")
 cleaned = sanitize_text(text)
 dst.write_text(cleaned, encoding="utf-8")
 print(f"Sanitized: {dst}")

if __name__ == "__main__":
 main()

