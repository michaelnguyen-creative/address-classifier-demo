# Test Failure Analysis & Recommended Fixes

**Date:** 2025-01-02  
**Test Run:** `test_handoff_logic.py`  
**Results:** 3/6 tests failed

---

## 🔍 Detailed Analysis

### Test 1: Invalid District Should Be Cleared ❌

**Expected Behavior:**
```
Trie finds wrong district → Pass to LCS → LCS finds correct district
```

**Actual Behavior:**
```
Trie finds wrong district → _is_valid_result() clears it → Returns province only
```

**Root Cause:**

The `_is_valid_result()` function (line 343-392) is **both validating AND cleaning**:

```python
def _is_valid_result(self, result, debug=True):
    # ... validation ...
    
    # PROBLEM: This modifies the result!
    if result.district and not result.district_code:
        result.district = None  # ← Cleaning happens here
        result.district_code = None
```

Then it returns `True` because province is valid, so the parser returns immediately without trying LCS.

**Decision Point:**

This is actually a **design choice**:

**Option A: Keep current behavior (graceful degradation)**
- Tier 1 returns partial valid results
- Faster (no LCS needed)
- User gets province even if district is wrong
- **Test expectation is wrong**

**Option B: Change to strict validation**
- Tier 1 only returns if ALL components are valid
- Falls through to LCS for any invalid component
- Slower but potentially more accurate
- **Test expectation is correct**

**Recommendation:** Choose Option B for better accuracy.

---

### Test 2: District Without Province Should Be Cleared ❌

**Expected:** LCS should find province from tokens  
**Actual:** LCS returns empty because it didn't find province

**Root Cause:**

LCS threshold (0.4) may be too strict, or the input tokens don't have enough overlap:

```python
Input tokens: ['cau', 'dien', 'nam', 'tu', 'liem']
Province candidates: Full names like ['ha noi', 'ho chi minh', ...]
```

No province mentioned in input → LCS can't find it!

**This test case is actually INVALID** - if the user doesn't mention a province, how can we find it?

**Recommendation:** Update test to expect failure (this is correct behavior).

---

### Test 5: Confidence Adjustment ❌

**Problem:** Both test cases succeeded in Tier 1, so we can't compare LCS confidence with/without context.

**Test A:**
```
Input: "random words Cầu Diễn, Nam Từ Liêm, Hà Nội"
Result: Trie found everything → confidence=1.0
```

**Test B:**
```
Input: "Cầu Diễn, Nam Từ Liêm"  
Result: Trie failed, LCS failed (no province) → confidence=0.0
```

**Recommendation:** Design better test cases that actually trigger LCS.

---

## ✅ Recommended Fixes

### Fix 1: Separate Validation from Cleaning

**Add new function:**

```python
def _has_complete_hierarchy(self, result: ParsedAddress) -> bool:
    """
    Check if result has COMPLETE valid hierarchy (strict check)
    
    Does NOT modify the result.
    
    Returns:
        True only if ALL present components are valid
    """
    if not result or not result.province or not result.province_code:
        return False
    
    # If district is present, it must be valid
    if result.district and not result.district_code:
        return False
    
    # If ward is present, it must be valid
    if result.ward and not result.ward_code:
        return False
    
    return True
```

**Update parse() logic:**

```python
def parse(self, text: str, debug: bool = True) -> ParsedAddress:
    # ... normalization ...
    
    trie_result = self._try_trie_match(normalized, debug)
    
    # Use strict check - only return if fully valid
    if self._has_complete_hierarchy(trie_result):
        if debug:
            print("✓ Trie match SUCCESS - complete valid hierarchy")
        trie_result.match_method = "trie"
        trie_result.confidence = 1.0
        return trie_result
    
    # Either partial match or invalid - proceed to handoff
    tier2_context = self._prepare_tier2_context(trie_result, debug)
    
    lcs_result = self._try_lcs_match(input_tokens, tier2_context, debug)
    
    # Use lenient check for LCS results
    if self._is_valid_result(lcs_result, debug):
        lcs_result.match_method = "lcs"
        # ... confidence scoring ...
        return lcs_result
    
    return ParsedAddress()
```

###

 Fix 2: Update Invalid Test Cases

**Test 2 should expect failure:**

```python
def test_district_without_province_cleared():
    """
    Test Case 2: No province in input
    
    Expected: System cannot infer province → fails gracefully
    """
    test_input = "Cầu Diễn, Nam Từ Liêm"
    
    result = parser.parse(test_input, debug=True)
    
    # This SHOULD fail - no province mentioned!
    success = (result.province is None and not result.valid)
    
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success
```

### Fix 3: Better Test Cases for Confidence

**Need cases that force LCS to run:**

```python
def test_confidence_with_context():
    # Test A: Trie finds province, LCS finds district/ward
    test_a = "Cau Dien, randomgarbage, Ha Noi"  # Breaks district match
    
    # Test B: Trie finds nothing, LCS finds everything
    test_b = "caudien namtuliem hanoi"  # No separators, might break Trie
    
    result_a = parser.parse(test_a, debug=False)
    result_b = parser.parse(test_b, debug=False)
    
    # Both should use LCS
    if result_a.match_method == "lcs" and result_b.match_method == "lcs":
        # A has province context, B doesn't
        success = result_a.confidence > result_b.confidence
    # ...
```

---

## 📋 Implementation Checklist

- [ ] Add `_has_complete_hierarchy()` function
- [ ] Update `parse()` to use strict validation for Tier 1
- [ ] Keep `_is_valid_result()` lenient for Tier 2
- [ ] Update Test 2 expectations (should fail when no province)
- [ ] Design better Test 5 cases (force LCS usage)
- [ ] Re-run tests and verify fixes

---

## 💡 Design Philosophy Clarification

**Key Question:** Should Tier 1 return partial matches?

**Current behavior:**
```
Input: "Cau Dien, Wrong District, Ha Noi"
Tier 1: Finds P=Ha Noi, D=Wrong District (invalid)
→ Clears invalid district
→ Returns {P=Ha Noi, D=None} with confidence=1.0
```

**Proposed behavior:**
```
Input: "Cau Dien, Wrong District, Ha Noi"  
Tier 1: Finds P=Ha Noi, D=Wrong District (invalid)
→ Marks as incomplete
→ Falls through to Tier 2
Tier 2: Uses P=Ha Noi as context, searches for district
→ Finds correct district
→ Returns complete address with confidence=0.8
```

**Recommendation:** Proposed behavior is better because:
- More accurate (uses LCS to fix errors)
- Confidence score is more meaningful
- Matches test expectations

---

## 🎯 Next Steps

1. **Make decision:** Strict vs. lenient Tier 1 validation
2. **Implement chosen approach**
3. **Update test expectations** to match design
4. **Re-run tests**
5. **Update ADR-002** with findings

Would you like me to implement the strict validation approach?
