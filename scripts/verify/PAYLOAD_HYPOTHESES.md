# Final Payload Hypotheses

## The Three Codes

| Code | Status | Value | Function |
| :--- | :--- | :--- | :--- |
| **Horizontal** | **Found** | **1-8** (`r // 32 + 1`) | Identifies the **Slot** (Block 1-8) |
| **Vertical** | **Analyzed** | **1-10** (Layer Index) | Identifies the **Depth** (Layer number) |
| **Time** | ⏳ **Running** | **Tick-Gap** (e.g., 1649) | Identifies the **Timing** (Gap between layers) |

## Payload Hypotheses

### Hypothesis 1: Simple Index Tuple
**Format:** `[block_id, layer_index]`

**Description:** The Smart Contract expects a tuple identifying the slot and layer.

**Payloads:**
- Diagonal #1: `[1, 2]` → `"1,2"`
- Diagonal #2: `[2, 2]` → `"2,2"`
- Diagonal #3: `[3, 2]` → `"3,2"`
- Diagonal #4: `[4, 2]` → `"4,2"`
- Vortex #1: `[5, 2]` → `"5,2"`
- Vortex #2: `[6, 2]` → `"6,2"`
- Vortex #3: `[7, 2]` → `"7,2"`
- Vortex #4: `[8, 2]` → `"8,2"`

**Priority:** **HIGHEST** - Start here

---

### Hypothesis 2: With Timing Code
**Format:** `[block_id, layer_index, tick_gap]`

**Description:** Includes the timing code (tick gap between Layer 1 and Layer 2).

**Payloads:**
- Diagonal #1: `[1, 2, 1649]` → `"1,2,1649"`
- Diagonal #2: `[2, 2, 1649]` → `"2,2,1649"`
- ... (same pattern for all 8)

**Priority:** **HIGH** - Test if Hypothesis 1 fails

---

### Hypothesis 3: Zero-based Index Tuple
**Format:** `[block_id-1, layer_index-1]` (zero-based)

**Description:** Zero-based indexing (common in programming).

**Payloads:**
- Diagonal #1: `[0, 1]` → `"0,1"`
- Diagonal #2: `[1, 1]` → `"1,1"`
- Diagonal #3: `[2, 1]` → `"2,1"`
- Diagonal #4: `[3, 1]` → `"3,1"`
- Vortex #1: `[4, 1]` → `"4,1"`
- Vortex #2: `[5, 1]` → `"5,1"`
- Vortex #3: `[6, 1]` → `"6,1"`
- Vortex #4: `[7, 1]` → `"7,1"`

**Priority:** **MEDIUM** - Test if Hypothesis 1 and 2 fail

---

### Hypothesis 4: Single Encoded Number
**Format:** `block_id * 100 + layer_index`

**Description:** Encodes both values in a single number.

**Payloads:**
- Diagonal #1: `102` → `"102"`
- Diagonal #2: `202` → `"202"`
- Diagonal #3: `302` → `"302"`
- Diagonal #4: `402` → `"402"`
- Vortex #1: `502` → `"502"`
- Vortex #2: `602` → `"602"`
- Vortex #3: `702` → `"702"`
- Vortex #4: `802` → `"802"`

**Priority:** **LOW** - Test if all others fail

---

## Testing Strategy

1. **Start with Hypothesis 1** (Simple Index Tuple)
 - Most straightforward
 - Matches the coordinate-based Block-ID discovery
 - Uses Layer 2 (the layer we're sending from)

2. **If Hypothesis 1 fails, try Hypothesis 2** (With Timing Code)
 - Adds the known tick gap (1649)
 - Provides "Proof of Time"

3. **If Hypothesis 2 fails, try Hypothesis 3** (Zero-based)
 - Common in programming contexts
 - May match Smart Contract implementation

4. **If Hypothesis 3 fails, try Hypothesis 4** (Single Number)
 - Alternative encoding format
 - May be what the contract expects

---

## Implementation

See `scripts/verify/final_contract_trigger.py` for the transaction sending logic.

The payload will be included in the transaction's `input` field (memo/payload).

---

## Waiting for Tick Analysis

The Tick-Pattern Analysis is still running. Once complete, we'll have:
- Complete tick gap table for all 10 layers
- Anomaly detection (unusually large gaps)
- Layer 9→10 gap analysis (possible exit point)

This will help refine the Time Code if needed.
