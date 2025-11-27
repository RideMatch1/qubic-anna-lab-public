# GitHub Preparation Plan

**IMPORTANT**: This plan does NOT modify local files. All changes are for GitHub upload only.

## Critical Issues Found (120 total)

### 1. Absolute Paths (42 issues)
- Scripts with `/Users/${USER}/` paths
- Scripts with `/tmp/` paths
- Need to be replaced with relative paths or environment variables

### 2. Personal Names (54 issues)
- "${USER}" in scripts
- Need to be removed or anonymized

### 3. IP Addresses (21 issues)
- Qubic node IPs in `analysis/72_live_node_check.py`
- These are public Qubic nodes - OK to keep, but should be documented

### 4. Localhost References (3 issues)
- Only in audit script itself - OK

## Files That Need Cleaning (Before GitHub Upload)

### Critical Files (Must Fix):
1. `scripts/core/resume_onchain_validation.sh` - Contains username
2. `scripts/verify/export_cfb_*.py` - Multiple files with paths
3. `scripts/verify/monitor_live_output.sh` - Contains path
4. `scripts/verify/run_cfb_export_*.sh` - Contains paths
5. `scripts/core/check_onchain_validation_status.py` - `/tmp/` path
6. `scripts/core/check_scan_status.py` - `/tmp/` path
7. `outputs/derived/*.md` - Several files with paths (but these shouldn't be uploaded anyway)

### Files to Exclude from GitHub:
- `outputs/derived/` - Contains internal documentation
- `venv-tx/` - Virtual environment (already in .gitignore)
- `venv/` - Virtual environment (already in .gitignore)
- `outputs/derived/cfb_discord_messages/` - Discord data
- All `*.log` files
- All checkpoint files

## Strategy

1. **Create a clean export script** that:
 - Copies files to a temporary directory
 - Cleans sensitive data
 - Prepares for GitHub upload
 - Does NOT modify original files

2. **Update .gitignore** to exclude:
 - All internal documentation
 - Checkpoint files
 - Log files
 - Discord data

3. **Create sanitized versions** of scripts with:
 - Relative paths instead of absolute
 - Environment variables for user-specific paths
 - Removed personal names

## Next Steps

1. Create `scripts/utils/prepare_github_export.py` - Export script
2. Update `.gitignore` - Add exclusions
3. Create sanitized script versions - For GitHub only
4. Test export - Verify no sensitive data leaks
