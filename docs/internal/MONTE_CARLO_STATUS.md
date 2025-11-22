# Monte-Carlo Simulation Status

## Current Status

**Simulation**: 10,000 random matrices with same distribution as Anna Matrix

**Purpose**: Prove that random matrices don't produce on-chain identities, even with 10,000 attempts.

## How to Run

```bash
cd /path/to/repo
export PYTHONPATH=$(pwd):$PYTHONPATH
python3 scripts/verify/monte_carlo_full_simulation.py --matrices 10000 --no-rpc
```

**Note**: With `--no-rpc`, this tests structure only (no on-chain checks). For full validation, run without `--no-rpc` (requires QubiPy and takes longer).

## Expected Results

If the Anna Matrix findings are real (not random chance):
- **0 on-chain identities** should be found in 10,000 random matrices
- This would prove statistical significance beyond Bonferroni correction

If random chance:
- Some identities might be found by chance
- This would reduce the statistical significance

## Why This Matters

Bonferroni correction is theoretical. A real 10,000-run simulation is empirical proof.

**This is the gold standard for statistical validation.**

## Current Run

**Status**: Ready to run (script exists, tested)

**To execute**: Run the command above. This will take 2-3 hours depending on system.

**Output**: `outputs/reports/monte_carlo_simulation.md` and `.json`

## Important Note

The simulation script exists and is functional. Running it requires:
- Python environment with numpy
- 2-3 hours computation time
- Optional: QubiPy for on-chain verification (adds significant time)

**The script is ready - it just needs to be executed.**

