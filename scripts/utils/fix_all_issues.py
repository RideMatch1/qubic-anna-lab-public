#!/usr/bin/env python3
"""
Fix all remaining issues: local paths, LLM bias, German comments
"""

import re
import sys
from pathlib import Path

# Patterns to replace
REPLACEMENTS = [
    # Local paths
    (r'/Users/lukashertle/projects/qubic-mystery-lab', '${PROJECT_ROOT}'),
    (r'/Users/lukashertle/projects', '${PROJECTS_ROOT}'),
    (r'lukashertle', '${USER}'),
    
    # LLM bias phrases
    (r'\bLet me\b', ''),
    (r'\bI am an AI\b', ''),
    (r'\bI can help\b', ''),
    (r'\bI would like\b', ''),
    (r'\bI think\b', ''),
    (r'\bI believe\b', ''),
    (r'\bI will\b', ''),
    (r'\bI\'ll\b', ''),
    (r'\bI\'ve\b', ''),
    (r'\bI should\b', ''),
    (r'\bI must\b', ''),
]

# German words to check (common in comments)
GERMAN_PATTERNS = [
    r'\bWird\b', r'\bwird\b', r'\bÜber\b', r'\büber\b',
    r'\bFür\b', r'\bfür\b', r'\bDer\b', r'\bDie\b', r'\bDas\b',
    r'\bund\b', r'\boder\b', r'\bnicht\b', r'\bkann\b',
    r'\bsoll\b', r'\bmuss\b', r'\bwird\b', r'\bist\b',
    r'\bseien\b', r'\bwerden\b', r'\bhaben\b', r'\bhat\b',
]

def fix_file(filepath: Path) -> bool:
    """Fix issues in a single file. Returns True if changed."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        original = content
        
        # Apply replacements
        for pattern, replacement in REPLACEMENTS:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # Clean up multiple spaces
        content = re.sub(r' +', ' ', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def main():
    """Process all code files."""
    repo_root = Path(__file__).parent.parent.parent
    
    # File types to process
    extensions = ['.py', '.sh', '.md']
    
    files_to_process = []
    for ext in extensions:
        files_to_process.extend(repo_root.rglob(f'*{ext}'))
    
    # Filter out .git and other excluded dirs
    files_to_process = [
        f for f in files_to_process
        if '.git' not in str(f) and 'node_modules' not in str(f)
    ]
    
    print(f"Processing {len(files_to_process)} files...")
    
    fixed_count = 0
    for filepath in files_to_process:
        if fix_file(filepath):
            fixed_count += 1
            print(f"Fixed: {filepath.relative_to(repo_root)}")
    
    print(f"\nFixed {fixed_count} files.")

if __name__ == '__main__':
    main()

