# Statistical Significance Analysis

## Question

How likely is it to find 8 on-chain identities by chance in a 128×128 matrix?

## Identity Space

- Total possible 60-char identities: 26^60 ≈ 7.91e+84
- Estimated valid identities (with checksum): ≈ 1.73e+79

## On-Chain Identity Estimates

**Note**: These are rough estimates. We don't have exact numbers.

- Conservative: 10,000 identities
- Optimistic: 100,000 identities
- High: 1,000,000 identities

## Extraction Method

- Identities per matrix: 8
- Method: Fixed diagonal + vortex patterns

## Probability Calculations

### Conservative Estimate

- P(hit per identity): 5.77e-76
- P(at least 1 hit in 8): 0.00e+00
- P(exactly 8 hits): 0.00e+00

### Optimistic Estimate

- P(hit per identity): 5.77e-75
- P(at least 1 hit in 8): 0.00e+00
- P(exactly 8 hits): 0.00e+00

## Multiple-Testing Problem

**Critical issue**: We tested multiple extraction methods (see `METHODS_TESTED.md`).

- Total methods tested: ~14
- Methods with hits: 2
- Total patterns/variations tested: ~50+

**What this means**:
- If you test many methods, some will produce "significant" results by chance
- The probability of finding identities increases with the number of methods tested
- This analysis doesn't account for multiple testing

**Bonferroni correction** (rough estimate):
- If we tested ~50 different patterns/methods
- Adjusted significance level: 0.05 / 50 = 0.001
- Our findings would need p < 0.001 to be statistically significant after correction

**We don't have exact p-values**, but the multiple-testing problem significantly reduces the statistical significance of our findings.

## Limitations

1. **On-chain count is unknown** - We're using estimates
2. **Checksum algorithm** - Our estimate of valid identity space may be inaccurate
3. **Extraction method** - We only tested specific patterns, not all possible extractions
4. **Birthday paradox** - With enough random attempts, collisions become likely
5. **Multiple-testing problem** - We tested many methods, only report successful ones
6. **Cherry-picking** - We show hits, not all the methods that found nothing

## Conclusion

This analysis shows the mathematical probability of finding identities by chance **for a single method**.

**However**:
- We tested many methods (see `METHODS_TESTED.md`)
- Multiple-testing correction would significantly increase the probability
- The adjusted probability is likely much higher than calculated here

**What we can say**:
- The control group (1000 random matrices, 0 hits) provides some evidence
- But the multiple-testing problem means our findings are less statistically significant than they appear

**Critical question**: Is the probability low enough to rule out chance **after accounting for multiple testing**?
This depends on:
- The actual number of on-chain identities (unknown)
- How many methods/patterns we actually tested (see `METHODS_TESTED.md`)
- Proper statistical correction (Bonferroni or similar)
