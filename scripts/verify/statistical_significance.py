#!/usr/bin/env python3
"""
Calculate statistical significance of finding on-chain identities.

This script addresses the critical question: "How likely is it to find
8 on-chain identities by chance in a 128x128 matrix?"

We need to calculate:
1. How many valid Qubic identities exist on-chain (total population)
2. How many identities our extraction method can generate from a matrix
3. The probability of a random identity being on-chain
4. The probability of finding 8+ on-chain identities by chance

This is essential for understanding if our findings are statistically significant
or just the birthday paradox in action.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

import numpy as np

OUTPUT_JSON = Path("outputs/reports/statistical_significance.json")
OUTPUT_MARKDOWN = Path("outputs/reports/statistical_significance.md")

def calculate_identity_space() -> Dict:
    """
    Calculate the total space of possible Qubic identities.
    
    Qubic identities are:
    - 60 characters
    - Uppercase letters only (A-Z)
    - Valid checksum required
    
    Total possible identities: 26^60
    But with checksum constraint, the actual valid space is smaller.
    """
    # Total possible 60-char strings: 26^60
    total_possible = 26 ** 60
    
    # Checksum is 4 characters, so it reduces the space
    # Rough estimate: checksum reduces valid space by factor of 26^4
    # This is an approximation - actual checksum algorithm may have different properties
    checksum_factor = 26 ** 4
    estimated_valid = total_possible / checksum_factor
    
    return {
        "total_possible_60char": total_possible,
        "checksum_factor": checksum_factor,
        "estimated_valid_identities": estimated_valid,
    }

def estimate_onchain_identities() -> Dict:
    """
    Estimate how many identities exist on the Qubic blockchain.
    
    This is a rough estimate based on:
    - Number of active computors (680+)
    - Historical identity creation
    - Typical blockchain growth patterns
    
    This is an ESTIMATE - we don't have exact numbers.
    """
    # Conservative estimate: 10,000 - 100,000 identities
    # This is a guess based on typical blockchain metrics
    # Real number could be higher or lower
    conservative_estimate = 10_000
    optimistic_estimate = 100_000
    high_estimate = 1_000_000
    
    return {
        "conservative": conservative_estimate,
        "optimistic": optimistic_estimate,
        "high": high_estimate,
        "note": "These are rough estimates. Actual number unknown.",
    }

def calculate_extraction_space() -> Dict:
    """
    Calculate how many identities our extraction method can generate.
    
    From a 128x128 matrix:
    - Diagonal extraction: 4 identities per matrix
    - Vortex extraction: 4 identities per matrix
    - Total: 8 identities per matrix
    
    But we can also consider:
    - Different starting positions
    - Different patterns
    - Different Base-26 mappings
    
    For now, we focus on the specific patterns we used.
    """
    # Our specific extraction:
    # - 4 diagonal patterns (fixed positions)
    # - 4 vortex patterns (fixed positions)
    # Total: 8 identities per matrix
    
    identities_per_matrix = 8
    
    # If we consider all possible diagonal patterns:
    # - Starting positions: 128 possible rows, 128 possible cols
    # - But we use specific patterns, not all combinations
    # This is a simplification
    
    return {
        "identities_per_matrix": identities_per_matrix,
        "extraction_method": "Fixed diagonal + vortex patterns",
        "note": "This is for our specific extraction method only.",
    }

def calculate_probability(
    onchain_count: int,
    valid_identity_space: float,
    identities_tested: int,
) -> Dict:
    """
    Calculate probability of finding identities by chance.
    
    Using birthday paradox / collision probability:
    P(at least k hits) = 1 - P(no hits)
    
    For each identity:
    P(hit) = onchain_count / valid_identity_space
    P(no hit) = 1 - P(hit)
    
    For n identities:
    P(no hits) = (1 - P(hit))^n
    P(at least 1 hit) = 1 - (1 - P(hit))^n
    """
    if valid_identity_space == 0:
        return {"error": "Invalid identity space"}
    
    p_hit = onchain_count / valid_identity_space
    p_no_hit = 1 - p_hit
    
    # Probability of at least 1 hit in n identities
    p_at_least_one = 1 - (p_no_hit ** identities_tested)
    
    # Probability of exactly k hits (binomial)
    # Using approximation for large n, small p
    # P(k hits) ≈ (n choose k) * p^k * (1-p)^(n-k)
    
    # For our case: 8 hits out of 8 identities
    k = 8
    n = identities_tested
    
    # Binomial coefficient approximation
    # (n choose k) = n! / (k! * (n-k)!)
    # For k=8, n=8: (8 choose 8) = 1
    
    p_exactly_k = (p_hit ** k) * (p_no_hit ** (n - k))
    
    return {
        "p_hit_per_identity": p_hit,
        "p_no_hit_per_identity": p_no_hit,
        "p_at_least_one_hit": p_at_least_one,
        "p_exactly_8_hits": p_exactly_k,
        "identities_tested": identities_tested,
        "onchain_count": onchain_count,
        "valid_identity_space": valid_identity_space,
    }

def main() -> None:
    """Calculate and report statistical significance."""
    
    identity_space = calculate_identity_space()
    onchain_estimates = estimate_onchain_identities()
    extraction_space = calculate_extraction_space()
    
    # Calculate probabilities for different on-chain estimates
    results = {
        "identity_space": identity_space,
        "onchain_estimates": onchain_estimates,
        "extraction_space": extraction_space,
        "probabilities": {},
    }
    
    identities_tested = extraction_space["identities_per_matrix"]
    valid_space = identity_space["estimated_valid_identities"]
    
    for estimate_name, onchain_count in [
        ("conservative", onchain_estimates["conservative"]),
        ("optimistic", onchain_estimates["optimistic"]),
        ("high", onchain_estimates["high"]),
    ]:
        prob = calculate_probability(onchain_count, valid_space, identities_tested)
        results["probabilities"][estimate_name] = prob
    
    # Write JSON
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    
    # Write Markdown
    lines = [
        "# Statistical Significance Analysis",
        "",
        "## Question",
        "",
        "How likely is it to find 8 on-chain identities by chance in a 128×128 matrix?",
        "",
        "## Identity Space",
        "",
        f"- Total possible 60-char identities: 26^60 ≈ {identity_space['total_possible_60char']:.2e}",
        f"- Estimated valid identities (with checksum): ≈ {identity_space['estimated_valid_identities']:.2e}",
        "",
        "## On-Chain Identity Estimates",
        "",
        "**Note**: These are rough estimates. We don't have exact numbers.",
        "",
        f"- Conservative: {onchain_estimates['conservative']:,} identities",
        f"- Optimistic: {onchain_estimates['optimistic']:,} identities",
        f"- High: {onchain_estimates['high']:,} identities",
        "",
        "## Extraction Method",
        "",
        f"- Identities per matrix: {extraction_space['identities_per_matrix']}",
        f"- Method: {extraction_space['extraction_method']}",
        "",
        "## Probability Calculations",
        "",
        "### Conservative Estimate",
        "",
    ]
    
    conservative = results["probabilities"]["conservative"]
    lines.extend([
        f"- P(hit per identity): {conservative['p_hit_per_identity']:.2e}",
        f"- P(at least 1 hit in 8): {conservative['p_at_least_one_hit']:.2e}",
        f"- P(exactly 8 hits): {conservative['p_exactly_8_hits']:.2e}",
        "",
        "### Optimistic Estimate",
        "",
    ])
    
    optimistic = results["probabilities"]["optimistic"]
    lines.extend([
        f"- P(hit per identity): {optimistic['p_hit_per_identity']:.2e}",
        f"- P(at least 1 hit in 8): {optimistic['p_at_least_one_hit']:.2e}",
        f"- P(exactly 8 hits): {optimistic['p_exactly_8_hits']:.2e}",
        "",
        "## Multiple-Testing Problem",
        "",
        "**Critical issue**: We tested multiple extraction methods (see `METHODS_TESTED.md`).",
        "",
        "- Total methods tested: ~14",
        "- Methods with hits: 2",
        "- Total patterns/variations tested: ~50+",
        "",
        "**What this means**:",
        "- If you test many methods, some will produce \"significant\" results by chance",
        "- The probability of finding identities increases with the number of methods tested",
        "- This analysis doesn't account for multiple testing",
        "",
        "**Bonferroni correction** (rough estimate):",
        "- If we tested ~50 different patterns/methods",
        "- Adjusted significance level: 0.05 / 50 = 0.001",
        "- Our findings would need p < 0.001 to be statistically significant after correction",
        "",
        "**We don't have exact p-values**, but the multiple-testing problem significantly reduces the statistical significance of our findings.",
        "",
        "## Limitations",
        "",
        "1. **On-chain count is unknown** - We're using estimates",
        "2. **Checksum algorithm** - Our estimate of valid identity space may be inaccurate",
        "3. **Extraction method** - We only tested specific patterns, not all possible extractions",
        "4. **Birthday paradox** - With enough random attempts, collisions become likely",
        "5. **Multiple-testing problem** - We tested many methods, only report successful ones",
        "6. **Cherry-picking** - We show hits, not all the methods that found nothing",
        "",
        "## Conclusion",
        "",
        "This analysis shows the mathematical probability of finding identities by chance **for a single method**.",
        "",
        "**However**:",
        "- We tested many methods (see `METHODS_TESTED.md`)",
        "- Multiple-testing correction would significantly increase the probability",
        "- The adjusted probability is likely much higher than calculated here",
        "",
        "**What we can say**:",
        "- The control group (1000 random matrices, 0 hits) provides some evidence",
        "- But the multiple-testing problem means our findings are less statistically significant than they appear",
        "",
        "**Critical question**: Is the probability low enough to rule out chance **after accounting for multiple testing**?",
        "This depends on:",
        "- The actual number of on-chain identities (unknown)",
        "- How many methods/patterns we actually tested (see `METHODS_TESTED.md`)",
        "- Proper statistical correction (Bonferroni or similar)",
    ])
    
    OUTPUT_MARKDOWN.write_text("\n".join(lines), encoding="utf-8")
    print(f"[statistical-significance] ✓ report -> {OUTPUT_MARKDOWN}")

if __name__ == "__main__":
    main()

