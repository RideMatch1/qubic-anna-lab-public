# Method Selection Rationale

## Critical Disclosure

**IMPORTANT**: We must be transparent about how methods were selected.

## What We Know

We tested 14 different extraction/decoding methods (see `METHODS_TESTED.md`). Only 2 methods found on-chain identities:
- Base-26 Diagonal Extraction
- Base-26 Vortex Extraction

## The Critical Question

**Were these methods selected a-priori (before seeing results) or data-driven (after finding hits)?**

### Honest Answer

**We cannot prove a-priori selection with timestamps or signed documents.**

The methods were developed iteratively:
1. Started with Base-26 diagonal extraction (logical first step)
2. Found identities
3. Explored variations and alternatives
4. Found vortex patterns also worked
5. Tested many other methods that didn't work

**This means the successful methods were partially data-driven.**

## What This Means for Statistical Significance

**This invalidates formal p-value calculations.**

If methods are selected after seeing results, you cannot use standard statistical tests. This is the classic "p-hacking" or "multiple testing" problem, but worse - it's not just multiple tests, it's adaptive testing.

## Our Position

**We treat the findings as a strong anomaly, not a formally statistically significant event.**

The evidence:
- 8 identities exist on-chain (fact)
- They're reproducible from the matrix (fact)
- Random matrices don't produce the same results (fact)
- Monte-Carlo simulation with 10,000 matrices shows 0 hits (fact)

**But**: We cannot claim formal statistical significance because:
- Methods were partially data-driven
- Multiple testing problem
- Unknown baseline (total on-chain identities)

## What Would Prove A-Priori Selection?

To prove a-priori selection, we would need:
1. Timestamped commit or document dated BEFORE first identity extraction
2. Signed statement from before discovery
3. Independent witness who saw the method list before results

**We don't have this.**

## Conclusion

**We acknowledge this limitation fully.**

The findings are interesting, reproducible, and anomalous. But they are not formally statistically significant due to method selection process.

**This is the nuclear honesty move** - we're telling you exactly what we know and what we don't know.

If you want to evaluate the findings, you must account for this limitation.

