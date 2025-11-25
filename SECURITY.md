# Security Information

## How to Verify This Repository

**Do not trust this document. Verify everything yourself.**

This repository contains Python scripts, bash scripts, and documentation. To verify safety:

1. **Read the code** - All scripts are plain text files
2. **Check file hashes** - Verify integrity using SHA256
3. **Review dependencies** - Check `requirements.txt`
4. **Run in isolation** - Use a virtual environment or Docker

## File Inventory

**Verify this yourself:**
```bash
# List all files
find . -type f | sort

# Check for binaries
find . -type f -exec file {} \; | grep -i "executable\|binary"

# Check for obfuscated code
grep -r "eval\|exec\|__import__\|compile\|marshal\|pickle" --include="*.py" .
```

**What you should find:**
- Python scripts (.py) - readable text files
- Bash scripts (.sh) - readable text files  
- Markdown files (.md) - readable text files
- Excel file (.xlsx) - data file
- JSON files - data files

**What you should NOT find:**
- Executable binaries (.exe, .dll, .so)
- Obfuscated Python code
- Encrypted files

## Code Review

**Review the code yourself before running anything.**

### Check Python Scripts

```bash
# Find all Python scripts
find . -name "*.py" -type f

# Check for suspicious patterns
grep -r "os.system\|subprocess\|eval\|exec" --include="*.py" .
grep -r "rm -rf\|del /f\|format\|fdisk" --include="*.py" .
```

**What the scripts actually do:**
- Read Excel file: `data/anna-matrix/Anna_Matrix.xlsx`
- Write output files: `outputs/` directory
- Optional: Connect to Qubic RPC (Docker only)

### Check Bash Scripts

```bash
# Find all bash scripts
find . -name "*.sh" -type f

# Review each script
cat run_all_verifications.sh
cat organize_repo.sh
cat fix_and_push.sh
```

**What the scripts actually do:**
- `run_all_verifications.sh`: Runs Python scripts, creates output directories
- `organize_repo.sh`: Moves files (organizational, not destructive)
- `fix_and_push.sh`: Git operations only

## Verification Steps

**Do these checks yourself. Don't trust this document.**

### 1. Verify File Integrity

```bash
# Matrix file hash (this is the source data)
shasum -a 256 data/anna-matrix/Anna_Matrix.xlsx
# Expected: bdee333b4006c1b7ab24a0dc61de76b60210c2db7bd8822c50e8509aff907c45
```

### 2. Review All Scripts

```bash
# Read the main verification script
cat run_all_verifications.sh

# Check what Python scripts import
grep -r "^import\|^from" --include="*.py" . | sort | uniq

# Check for network connections
grep -r "http\|socket\|urllib\|requests" --include="*.py" .
```

### 3. Check Dependencies

```bash
# Review requirements
cat requirements.txt

# Install in isolated environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run in Isolation

```bash
# Use Docker (safest)
docker build -f Dockerfile.qubipy -t qubic-proof .
docker run --rm -v "$PWD":/workspace -w /workspace qubic-proof python scripts/verify/rpc_check.py
```

## Virus Scanner Results

**Check VirusTotal yourself:**
1. Upload the repository to VirusTotal
2. Review the results
3. Check which scanners flag it and why

**Common reasons for flags:**
- Python scripts using cryptographic libraries (ed25519, hashlib)
- Hash calculations (SHA256)
- Docker-related scripts
- Research code analyzing patterns

**How to interpret:**
- If only heuristic/behavioral detection: Likely false positive
- If multiple scanners flag the same file: Investigate that file
- If signature-based detection: More concerning, investigate

## Safety Checklist

**Do these checks yourself:**

- [ ] Read `run_all_verifications.sh` - understand what it does
- [ ] Review all Python scripts in `analysis/` and `scripts/`
- [ ] Check `requirements.txt` - verify all dependencies
- [ ] Verify matrix file hash matches expected value
- [ ] Run in virtual environment or Docker (isolated)
- [ ] Monitor file system during execution (check what files are created/modified)
- [ ] Review output files in `outputs/` directory
- [ ] Check network connections (if any) using `netstat` or `lsof`

## Usage Recommendations

**Before running anything:**

1. **Clone to isolated location**
   ```bash
   mkdir ~/test-qubic
   cd ~/test-qubic
   git clone <repo-url>
   ```

2. **Review code first**
   ```bash
   # Read the main script
   less run_all_verifications.sh
   
   # Check what it calls
   grep "python" run_all_verifications.sh
   ```

3. **Use isolation**
   ```bash
   # Virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Or Docker
   docker build -f Dockerfile.qubipy -t qubic-proof .
   ```

4. **Monitor execution**
   ```bash
   # Watch file system (Linux/Mac)
   watch -n 1 'find outputs/ -type f | wc -l'
   
   # Check network connections
   netstat -an | grep ESTABLISHED
   ```

**What happens when you run scripts:**
- Files read: `data/anna-matrix/Anna_Matrix.xlsx`
- Files created: `outputs/reports/*.md`, `outputs/plots/*.png`
- Optional network: Qubic RPC (only if Docker used)

## Reporting Issues

If you find any security concerns:

1. **Open a GitHub issue** - We take security seriously
2. **Do not run suspicious code** - If something looks wrong, don't run it
3. **Report false positives** - Help us improve scanner compatibility

## Independent Verification

**The best security is verification, not trust.**

- All code is visible (read it yourself)
- All operations are explicit (check what scripts do)
- All outputs are verifiable (check the results)
- All hashes are provided (verify file integrity)

**If you find something suspicious:**
1. Document it
2. Open a GitHub issue
3. Don't run the code until resolved

---

**Last Updated**: 2025-11-22  
**Note**: This document cannot prove safety. Verify everything yourself.

