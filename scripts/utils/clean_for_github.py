#!/usr/bin/env python3
"""
Clean all markdown files for GitHub publication.
Removes emojis and LLM bias phrases.
"""

import re
import sys
from pathlib import Path

# Emoji pattern (all Unicode emoji ranges)
EMOJI_PATTERN = re.compile(
 "["
 "\U0001F600-\U0001F64F" # Emoticons
 "\U0001F300-\U0001F5FF" # Symbols & Pictographs
 "\U0001F680-\U0001F6FF" # Transport & Map
 "\U0001F1E0-\U0001F1FF" # Flags
 "\U00002702-\U000027B0" # Dingbats
 "\U000024C2-\U0001F251" # Enclosed characters
 "]+",
 flags=re.UNICODE
)

# LLM bias phrases (common AI assistant language)
LLM_PATTERNS = [
 (r'\b[Ii]\s+am\s+an?\s+AI\b', ''),
 (r'\b[Ii]\s+am\s+a\s+language\s+model\b', ''),
 (r'\b[Ii]\s+am\s+an?\s+AI\s+assistant\b', ''),
 (r'\b[Ii]\s+am\s+designed\s+to\b', ''),
 (r'\b[Ii]\s+am\s+trained\s+to\b', ''),
 (r'\b[Ii]\s+am\s+programmed\s+to\b', ''),
 (r'\b[Ii]\s+can\s+help\s+you\b', ''),
 (r'\b[Ii]\s+understand\s+that\b', ''),
 (r'\b[Ii]\s+notice\s+that\b', ''),
 (r'\b[Ii]\s+see\s+that\b', ''),
 (r'\b[Ii]\s+would\s+like\s+to\b', ''),
 (r'\b[Ii]\s+would\s+suggest\b', ''),
 (r'\b[Ii]\s+would\s+recommend\b', ''),
 (r'\b[Ii]\s+think\s+that\b', ''),
 (r'\b[Ii]\s+believe\s+that\b', ''),
 (r'\b[Ii]\s+cannot\s+help\b', ''),
 (r'\b[Ii]\s+am\s+unable\s+to\b', ''),
 (r'\b[Ll]et\s+me\s+help\b', ''),
 (r'\b[Ll]et\s+me\s+assist\b', ''),
 (r'\b[Ll]et\s+me\s+explain\b', ''),
 (r'\b[Ll]et\s+me\s+clarify\b', ''),
 (r'\b[Ll]et\s+me\s+show\s+you\b', ''),
 (r'\b[Ll]et\s+me\s+wrap\s+up\b', ''),
 (r'\b[Ll]et\s+me\s+summarize\b', ''),
 (r'\b[Ll]et\s+me\s+conclude\b', ''),
]

def clean_text(content: str) -> str:
 """Remove emojis and LLM bias phrases."""
 # Remove emojis
 result = EMOJI_PATTERN.sub('', content)
 
 # Remove LLM bias phrases
 for pattern, replacement in LLM_PATTERNS:
 result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
 
 # Clean up multiple spaces
 result = re.sub(r' +', ' ', result)
 # Clean up multiple newlines
 result = re.sub(r'\n{3,}', '\n\n', result)
 
 return result.strip() + '\n'

def main():
 """Process all markdown files."""
 repo_root = Path(__file__).parent.parent.parent
 
 md_files = list(repo_root.rglob('*.md'))
 md_files = [f for f in md_files if '.git' not in str(f)]
 
 print(f"Processing {len(md_files)} markdown files...")
 
 cleaned_count = 0
 for md_file in md_files:
 try:
 content = md_file.read_text(encoding='utf-8', errors='ignore')
 cleaned = clean_text(content)
 
 if cleaned != content:
 md_file.write_text(cleaned, encoding='utf-8')
 cleaned_count += 1
 print(f"Cleaned: {md_file.relative_to(repo_root)}")
 except Exception as e:
 print(f"Error processing {md_file}: {e}", file=sys.stderr)
 
 print(f"\nCleaned {cleaned_count} files.")

if __name__ == '__main__':
 main()

