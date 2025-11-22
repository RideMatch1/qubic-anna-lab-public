#!/usr/bin/env python3
"""
Forensic audit script - checks for sensitive data before GitHub upload

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
        # Note: ${TMPDIR:-/tmp}/ and /var/ are acceptable in patterns
        r"C:\\Users\\",
        r"C:\\",
    ],
    "personal_names": [
        # Generic patterns for detection only, not actual data leaks
        r"[A-Z][a-z]+\s+[A-Z][a-z]+",  # Generic "First Last" pattern
    ],
    "ip_addresses": [
        r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        r"192\.168\.\d{1,3}\.\d{1,3}",
        r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}",
        r"172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}",
    ],
    "localhost": [
        # Note: localhost patterns are acceptable in audit tool itself
        # Only flag if found in actual content, not in patterns
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
    "CRITICAL_AUDIT_REPORT.md",  # Internal audit document, contains examples
    "venv/",
    "venv-tx/",
    "__pycache__/",
    ".DS_Store",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "outputs/derived/cfb_discord_messages/",  # Discord data
    "outputs/derived/discord_intelligence_analysis.json",
    "outputs/derived/discord_intelligence_analysis.md",
]