# Payload Analysis - Hypothesis Testing Results

## Test Results Summary

### Hypothesis 1: `[Block-ID, Layer-Index]`
**Format:** `"1,2"`, `"2,2"`, ... `"8,2"`

**Result:** **FAILED**
- All 8 transactions were sent successfully
- 400 QU were paid to the contract
- **NO new assets were paid out**
- The payload format was valid enough to send transactions, but not correct enough to trigger the payout mechanism

**Conclusion:** The Smart Contract requires more than just Block-ID and Layer-Index.

---

### Hypothesis 2: `[Block-ID, Layer-Index, Tick-Gap]`
**Format:** `"1,2,1649"`, `"2,2,1649"`, ... `"8,2,1649"`

**Result:** **PARTIAL SUCCESS**
- All 8 transactions were sent successfully
- 8 QU were paid to the contract (reduced amount)
- **Block #7 (Vortex #3) received NEW assets!** (50 GENESIS units)
- Blocks #1-6 and #8 did NOT receive new assets

**Key Observation:**
- Only Block #7 (Vortex #3, Block-ID 7) received a payout
- This suggests the Time Code (1649) is relevant, but:
 - Either the format is still not quite right
 - Or there's a specific condition for Block #7
 - Or the Time Code needs to be different for different blocks

---

## Analysis of Block #7 Success

**Why did only Block #7 work?**

Possible explanations:
1. **Vortex-specific condition:** Block #7 is the third Vortex block (Vortex #3)
2. **Block-ID specific:** Block-ID 7 might have special significance
3. **Payload format variation:** The format might need to be different for Vortex vs Diagonal
4. **Time Code variation:** Different blocks might need different tick gaps

---

## Next Hypotheses to Test

### Hypothesis 3: Different Time Code for Each Block
**Format:** `"1,2,<tick_gap_1>"`, `"2,2,<tick_gap_2>"`, etc.

**Rationale:** Each block might need its own specific tick gap value.

### Hypothesis 4: Time Code as Separate Number (Not String)
**Format:** Payload might need to be binary-encoded, not string-encoded.

### Hypothesis 5: Different Format for Vortex Blocks
**Format:** Diagonal blocks: `"1,2,1649"`, Vortex blocks: `"5,2,<different_value>"`

### Hypothesis 6: Layer-Index Variation
**Format:** Maybe Layer-Index should be different (e.g., 1 instead of 2, or the actual layer depth)

---

## Key Insights

1. **Block-ID is correct** - The coordinate-based discovery (r // 32 + 1) is valid
2. **Layer-Index is relevant** - Layer 2 is the correct sending layer
3. **Time Code is partially correct** - 1649 works for Block #7, but not for others
4. **Payload format needs refinement** - The exact encoding might be different

---

## Recommended Next Steps

1. **Analyze Block #7 in detail** - Why did it work when others didn't?
2. **Test Hypothesis 3** - Different tick gaps for each block
3. **Test Hypothesis 4** - Binary-encoded payload instead of string
4. **Check if Vortex blocks need different format** - Test with different payloads for Vortex vs Diagonal
