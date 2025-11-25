# Matrix Value Correlation Analysis: Facts

**Date**: 2025-11-22  
**Objective**: Check correlations between matrix values and identities

Wondering if the actual matrix values at the coordinates where identities were extracted tell us anything. Do certain values correlate with certain identity properties?

## IMPORTANT

**Facts only, no interpretations!**

## 1. Matrix Values at Identity Coordinates (FACTS)

- **Total coordinate sets**: 90
- **Total matrix values analyzed**: 5,040

### Overall Statistics
- **Mean**: 5.85
- **Std**: 73.98
- **Min**: -126.0
- **Max**: 127.0

### Pattern-specific means

Different extraction patterns sample different parts of the matrix, so they have different mean values:

- **diag_main**: 3.17
- **diag_reverse**: 2.81
- **vertical_stride**: -1.65
- **horizontal_stride**: -6.21
- **zigzag_snake**: -9.22
- **row_scan**: 28.99 (much higher - samples from different region)
- **column_scan**: -6.04
- **spiral**: 10.56
- **l_shape**: 30.23 (also higher)

The row_scan and l_shape patterns have noticeably higher means, which suggests they're sampling from a different part of the matrix. Whether this is meaningful or just random variation is unclear.

## OPEN QUESTIONS

1. Are there correlations between matrix values and identity properties?
2. Why do some patterns have different mean values?
3. What do the matrix values at coordinates mean?

## IMPORTANT

**This analysis shows FACTS only!**  
**No interpretations!**
