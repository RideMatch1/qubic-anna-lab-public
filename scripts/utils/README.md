# Utility Scripts

## Forensic Audit

**Script**: `forensic_audit.py`

Scans the repository for sensitive data that should not be uploaded to GitHub:
- Absolute file paths
- Personal names
- IP addresses
- API keys/tokens
- Localhost references

**Usage**:
```bash
python3 scripts/utils/forensic_audit.py
```

**Output**: Lists all issues found, grouped by category.

## GitHub Export Preparation

**Script**: `prepare_github_export.py`

Creates a clean, sanitized copy of the repository for GitHub upload.

**IMPORTANT**: Does NOT modify original files!

**Usage**:
```bash
python3 scripts/utils/prepare_github_export.py
```

**Output**: Creates `github_export/` directory with cleaned files.

**What it does**:
- Copies all files (except excluded ones)
- Sanitizes sensitive data
- Replaces absolute paths with variables
- Removes personal names
- Excludes internal documentation

**What it doesn't do**:
- Modify original files
- Delete anything
- Change git history
