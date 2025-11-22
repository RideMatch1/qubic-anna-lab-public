# Deep Matrix Coordinate Analysis

**Date**: 2025-11-22  
**Total on-chain identities**: 180

Analyzing where in the matrix the 180 identities were extracted from. Looking for coordinate hotspots, clusters, patterns in spatial distribution.

## 1. Coordinate Patterns

### Overview

Across all 180 identities, I extracted 5,040 total coordinates (56 per identity). But many coordinates are reused across different identities:

- **Total coordinates**: 5,040 (56 per identity × 180 identities)
- **Unique coordinates**: 1,570 (so about 31% are unique)
- **Hotspots**: 20 (coordinates used 10+ times)

Some coordinates appear in multiple identities, which suggests certain parts of the matrix are more "productive" for identity extraction.

### Pattern Statistics

#### diag_main
- Identities found: 85
- On-chain: 20
- Success Rate: 23.5%

#### diag_reverse
- Identities found: 85
- On-chain: 20
- Success Rate: 23.5%

#### vertical_stride
- Identities found: 91
- On-chain: 20
- Success Rate: 22.0%

#### horizontal_stride
- Identities found: 91
- On-chain: 20
- Success Rate: 22.0%

#### zigzag_snake
- Identities found: 85
- On-chain: 20
- Success Rate: 23.5%

#### row_scan
- Identities found: 91
- On-chain: 20
- Success Rate: 22.0%

#### column_scan
- Identities found: 91
- On-chain: 20
- Success Rate: 22.0%

#### spiral
- Identities found: 91
- On-chain: 20
- Success Rate: 22.0%

#### l_shape
- Identities found: 98
- On-chain: 20
- Success Rate: 20.4%

### Hotspots (most frequent coordinates)
- `[8, 24]`: 20x
- `[24, 24]`: 20x
- `[16, 32]`: 20x
- `[8, 40]`: 20x
- `[24, 40]`: 20x
- `[16, 48]`: 20x
- `[8, 56]`: 20x
- `[24, 56]`: 20x
- `[16, 64]`: 20x
- `[8, 72]`: 20x

### Block Usage (16x16 blocks)
- Block (1, 2): 504x
- Block (1, 3): 504x
- Block (1, 4): 504x
- Block (1, 1): 474x
- Block (0, 2): 434x
- Block (0, 3): 434x
- Block (0, 4): 434x
- Block (0, 1): 413x
- Block (1, 5): 282x
- Block (0, 5): 238x

## 2. Geometric Structure

- **Center**: (16.9, 48.0)
- **Spread**: 0.1 - 56.7 (avg 23.8)
- **Clusters**: 21

## 3. Hidden Structures

### Pattern Hierarchy (by success rate)
- **diag_main**: 23.5% (20/85)
- **diag_reverse**: 23.5% (20/85)
- **zigzag_snake**: 23.5% (20/85)
- **vertical_stride**: 22.0% (20/91)
- **horizontal_stride**: 22.0% (20/91)

### Dominant Patterns
- diag_main
- diag_reverse
- zigzag_snake

## Observations

### 1. Coordinate Hotspots

Some coordinates appear more frequently than others. No clear explanation yet.

### 2. Block Usage

The matrix appears divided into 16x16 blocks. Block usage varies significantly.

### 3. Pattern Hierarchy

Pattern success rates differ. diag_main, diag_reverse, and zigzag_snake show highest rates.

## Next Steps

1. Detailed block analysis
2. Comparison with systematic identities
3. Coordinate mapping to seeds
4. Deeper geometric analysis
