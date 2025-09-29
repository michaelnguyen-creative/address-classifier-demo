# Phase 4-6 Implementation Guide
## Advanced Matching Algorithms for Vietnamese Address Parser

---

## 📋 Overview

**Goal:** Extend the existing Trie-based parser with fallback mechanisms to handle:
- ✅ Extra words in input (street names, building numbers)  
- ✅ Token reordering ("ha noi nam tu liem" vs "nam tu liem ha noi")  
- ✅ OCR errors and typos ("ha nol" → "ha noi")

**Strategy:** Multi-tier matching system with progressive fallback

```
                    Address Parser
                          │
           ┌──────────────┼──────────────┐
           │              │              │
      Tier 1          Tier 2         Tier 3
   ┌────────────┐  ┌───────────┐  ┌──────────────┐
   │ Trie Match │  │ LCS Match │  │ Edit Distance│
   │   O(m)     │  │  O(n×m)   │  │   O(k×m)     │
   └────────────┘  └───────────┘  └──────────────┘
   Exact (80%)     Aligned (15%)  Fuzzy (5%)
```

---

## 🎯 Phase 4: LCS Implementation ✅ COMPLETE

See `lcs_matcher.py` for full implementation.

**Key Files:**
- `Src/lcs_matcher.py` - Core LCS algorithm
- `Src/test_lcs.py` - Unit and integration tests

**Status:** Ready for integration into main parser

---

## 🎯 Phase 5: Edit Distance (Ukkonen's Algorithm)

### When to Use

**Problem**: Even LCS fails with typos:
```python
# OCR errors
Input: "ha nol"  # Should be "ha noi"
LCS:   FAIL (no common tokens)

# Keyboard typos
Input: "dinh cong"  # Should be "định công"
LCS:   FAIL after normalization
```

**Solution**: Edit distance measures character-level similarity

### Algorithm: Bounded Edit Distance

**Standard Edit Distance**: O(n × m) for all cells

**Ukkonen's Optimization**: O(k × m) for k-approximate matching
- Only compute cells within diagonal band of width 2k+1
- Early termination if distance exceeds k

```
Standard DP (compute ALL cells):
      h  a  n  o  i
  0   1  2  3  4  5
h 1   ▓  ▓  ▓  ▓  ▓
a 2   ▓  ▓  ▓  ▓  ▓
n 3   ▓  ▓  ▓  ▓  ▓
o 4   ▓  ▓  ▓  ▓  ▓
l 5   ▓  ▓  ▓  ▓  ▓

Ukkonen (only diagonal band for k=2):
      h  a  n  o  i
  0   1  2  X  X  X
h 1   ▓  ▓  ▓  X  X
a 2   ▓  ▓  ▓  ▓  X
n 3   X  ▓  ▓  ▓  ▓
o 4   X  X  ▓  ▓  ▓
l 5   X  X  X  ▓  ▓

X = not computed (beyond band)
▓ = computed
```

### DP Recurrence

```
Edit[i][j] = minimum edit distance between s1[0:i] and s2[0:j]

Base cases:
  Edit[0][j] = j  (insert j characters)
  Edit[i][0] = i  (delete i characters)

Recurrence:
  if s1[i-1] == s2[j-1]:
      cost = 0
  else:
      cost = 1
  
  Edit[i][j] = min(
      Edit[i-1][j] + 1,      # Delete from s1
      Edit[i][j-1] + 1,      # Insert into s1
      Edit[i-1][j-1] + cost  # Substitute
  )
```

### Example Walkthrough

```python
s1 = "ha nol"
s2 = "ha noi"

# Full DP table
        ε   h   a   _   n   o   i
    ε   0   1   2   3   4   5   6
    h   1   0   1   2   3   4   5
    a   2   1   0   1   2   3   4
    _   3   2   1   0   1   2   3
    n   4   3   2   1   0   1   2
    o   5   4   3   2   1   0   1
    l   6   5   4   3   2   1   1  ← distance = 1

Operations: Change 'l' to 'i' (1 substitution)
```

### Implementation

```python
class EditDistanceMatcher:
    def __init__(self, max_distance: int = 2):
        """
        Args:
            max_distance: Maximum allowed edit distance
                         2 = tolerate up to 2 typos
        """
        self.max_distance = max_distance
    
    def bounded_edit_distance(self, s1: str, s2: str, max_k: int) -> int:
        """
        Compute edit distance with early termination
        
        Time: O(k × min(n,m)) where k = max_k
        Space: O(min(n,m))
        
        Returns:
            Edit distance, or max_k+1 if exceeds max_k
        """
        n, m = len(s1), len(s2)
        
        # Quick check: length difference > k means distance > k
        if abs(n - m) > max_k:
            return max_k + 1
        
        # Space optimization: only keep previous row
        prev = list(range(m + 1))
        
        for i in range(1, n + 1):
            curr = [i]  # First column
            
            # Compute only diagonal band
            start = max(1, i - max_k)
            end = min(m, i + max_k)
            
            for j in range(start, end + 1):
                if s1[i-1] == s2[j-1]:
                    cost = 0
                else:
                    cost = 1
                
                curr.append(min(
                    prev[j] + 1,      # deletion
                    curr[-1] + 1,     # insertion
                    prev[j-1] + cost  # substitution
                ))
            
            # Early termination
            if min(curr) > max_k:
                return max_k + 1
            
            prev = curr
        
        return prev[m]
    
    def find_fuzzy_matches(self, query: str, candidates: List[str]) -> List[Tuple[str, int]]:
        """
        Find all candidates within edit distance threshold
        
        Args:
            query: Search string
            candidates: List of candidate strings
        
        Returns:
            List of (candidate, distance) tuples, sorted by distance
        """
        matches = []
        
        for candidate in candidates:
            distance = self.bounded_edit_distance(
                query, 
                candidate, 
                self.max_distance
            )
            
            if distance <= self.max_distance:
                matches.append((candidate, distance))
        
        # Sort by distance (best first)
        matches.sort(key=lambda x: x[1])
        
        return matches
```

### Integration Strategy

**When to trigger Edit Distance:**
1. Trie matching fails
2. LCS matching fails OR returns low confidence (<0.5)
3. Input suggests typos (very short tokens, unusual characters)

**Token-level vs Word-level:**

```python
def _fuzzy_match(self, text):
    """
    Apply edit distance at TOKEN level
    
    Why? Vietnamese names are multi-token:
    - "Nam Từ Liêm" = 3 tokens
    - Apply edit distance to EACH token separately
    - Then combine results
    """
    input_tokens = self.db._normalize(text).split()
    
    results = {}
    
    for entity_type, candidates in self.candidates.items():
        best_match = None
        best_total_distance = float('inf')
        
        for candidate_name in candidates:
            candidate_tokens = self.db._normalize(candidate_name).split()
            
            # Match token-by-token
            if len(candidate_tokens) > len(input_tokens):
                continue  # Can't match if candidate longer
            
            # Find best alignment of candidate tokens in input
            total_distance = self._align_tokens(
                input_tokens,
                candidate_tokens
            )
            
            if total_distance < best_total_distance:
                best_total_distance = total_distance
                best_match = candidate_name
        
        results[entity_type] = best_match
    
    return results

def _align_tokens(self, input_tokens, candidate_tokens):
    """
    Find best alignment of candidate tokens within input
    
    Example:
        input = ["ha", "nol", "nam", "tu"]
        candidate = ["ha", "noi"]
        
        Try aligning at each position:
        - Position 0-1: ["ha", "nol"] vs ["ha", "noi"]
          → distance = 0 + 1 = 1 ✓ BEST
        - Position 1-2: ["nol", "nam"] vs ["ha", "noi"]
          → distance = 2 + 2 = 4
    
    Returns minimum total distance across all positions
    """
    min_distance = float('inf')
    
    for start in range(len(input_tokens) - len(candidate_tokens) + 1):
        total_dist = 0
        
        for i, candidate_token in enumerate(candidate_tokens):
            input_token = input_tokens[start + i]
            
            dist = self.edit_matcher.bounded_edit_distance(
                input_token,
                candidate_token,
                self.max_distance
            )
            
            total_dist += dist
            
            if total_dist >= min_distance:
                break  # Early termination
        
        min_distance = min(min_distance, total_dist)
    
    return min_distance
```

### Performance Optimization

**1. Length Filtering**
```python
# Skip if length difference too large
max_len_diff = max_k * len(candidate_tokens)
if abs(len(input_tokens) - len(candidate_tokens)) > max_len_diff:
    continue
```

**2. Progressive Threshold**
```python
# Try stricter thresholds first
for threshold in [0, 1, 2]:
    matcher = EditDistanceMatcher(max_distance=threshold)
    results = matcher.find_matches(query, candidates)
    if results:
        return results  # Found match with stricter threshold
```

**3. Candidate Filtering**
```python
# Only try edit distance on candidates that:
# 1. Share at least one common token with input
# 2. Have similar length
# 3. Failed LCS but had partial overlap
```

---

## 🎯 Phase 6: Integration & Optimization

### Complete Pipeline Architecture

```python
class EnhancedAddressParser:
    """
    Multi-tier address parser with fallback mechanisms
    """
    
    def __init__(self, db: AddressDatabase):
        self.db = db
        
        # Tier 1: Trie (existing)
        self.trie_parser = TrieBasedMatcher()
        
        # Tier 2: LCS (NEW)
        self.lcs_matcher = LCSMatcher(threshold=0.4)
        self.lcs_candidates = self._prepare_lcs_candidates()
        
        # Tier 3: Edit Distance (NEW)
        self.edit_matcher = EditDistanceMatcher(max_distance=2)
    
    def parse(self, text: str, debug: bool = False) -> ParsedAddress:
        """
        Parse address with multi-tier fallback
        
        Flow:
        1. Try Trie (fast, exact)
        2. If fail → Try LCS (medium, aligned)
        3. If fail → Try Edit Distance (slow, fuzzy)
        4. Validate hierarchy
        5. Return best result
        """
        normalized = self.db._normalize(text)
        input_tokens = normalized.split()
        
        if debug:
            print(f"\n{'='*60}")
            print(f"PARSING: {text}")
            print(f"Normalized: {normalized}")
            print(f"Tokens: {input_tokens}")
            print(f"{'='*60}")
        
        # ===== TIER 1: TRIE EXACT MATCH =====
        if debug: print("\n[TIER 1] Trying Trie exact match...")
        
        trie_result = self._try_trie_match(normalized)
        
        if self._is_valid_result(trie_result):
            if debug: print("✓ Trie match SUCCESS")
            trie_result.match_method = "trie"
            return trie_result
        
        if debug: print("✗ Trie match failed, trying LCS...")
        
        # ===== TIER 2: LCS ALIGNMENT =====
        if debug: print("\n[TIER 2] Trying LCS alignment...")
        
        lcs_result = self._try_lcs_match(input_tokens)
        
        if self._is_valid_result(lcs_result):
            if debug: print("✓ LCS match SUCCESS")
            lcs_result.match_method = "lcs"
            return lcs_result
        
        if debug: print("✗ LCS match failed, trying Edit Distance...")
        
        # ===== TIER 3: EDIT DISTANCE =====
        if debug: print("\n[TIER 3] Trying Edit Distance...")
        
        edit_result = self._try_edit_distance_match(input_tokens)
        
        if self._is_valid_result(edit_result):
            if debug: print("✓ Edit Distance match SUCCESS")
            edit_result.match_method = "edit_distance"
            return edit_result
        
        if debug: print("✗ All methods failed")
        
        # Return empty result
        return ParsedAddress()
    
    def _is_valid_result(self, result: ParsedAddress) -> bool:
        """
        Check if parse result is valid
        
        Valid if:
        - Has at least province
        - Confidence > threshold
        - Hierarchy is consistent
        """
        if not result or not result.province:
            return False
        
        if result.confidence < 0.3:
            return False
        
        # Validate hierarchy if we have multiple levels
        if result.ward and result.district:
            if not self.db.validate_hierarchy(
                result.ward,
                result.district,
                result.province
            ):
                return False
        
        return True
```

### Performance Benchmarks

**Target Metrics:**

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Accuracy** | >85% | Test suite pass rate |
| **Latency P50** | <50ms | Median processing time |
| **Latency P95** | <200ms | 95th percentile |
| **Memory** | <100MB | Peak usage |

**Expected Distribution:**

| Method | % of Queries | Avg Latency |
|--------|--------------|-------------|
| Trie | 80% | 5ms |
| LCS | 15% | 30ms |
| Edit Distance | 5% | 100ms |

### Testing Strategy

**Unit Tests** (per component):
```python
# test_lcs_matcher.py
def test_lcs_basic()
def test_lcs_similarity()
def test_lcs_threshold()

# test_edit_distance.py
def test_edit_distance_basic()
def test_bounded_distance()
def test_fuzzy_matching()
```

**Integration Tests** (end-to-end):
```python
# test_enhanced_parser.py
def test_tier1_trie_path()
def test_tier2_lcs_fallback()
def test_tier3_edit_fallback()
def test_hierarchy_validation()
```

**Benchmark Tests** (performance):
```python
# benchmark_parser.py
def benchmark_public_test_cases()
def measure_latency_distribution()
def measure_accuracy_by_tier()
```

---

## 🚀 Implementation Checklist

### Phase 4: LCS ✅
- [x] Implement core LCS algorithm
- [x] Add similarity scoring
- [x] Create unit tests
- [ ] Integrate with main parser
- [ ] Add to address_parser.py
- [ ] Test on public.json

### Phase 5: Edit Distance ⏳
- [ ] Implement bounded edit distance
- [ ] Add token-level alignment
- [ ] Create unit tests
- [ ] Integrate with main parser
- [ ] Optimize for performance

### Phase 6: Integration ⏳
- [ ] Create EnhancedAddressParser class
- [ ] Add debug logging
- [ ] Implement tier fallback logic
- [ ] Add performance monitoring
- [ ] Run full test suite
- [ ] Measure accuracy on public.json

---

## 📊 Next Steps

1. **Test LCS Implementation**
   ```bash
   cd Src
   python lcs_matcher.py  # Run unit tests
   python test_lcs.py     # Run integration tests
   ```

2. **Integrate LCS into Parser**
   - Modify `address_parser.py`
   - Add LCS as Tier 2 fallback
   - Test on sample cases

3. **Implement Edit Distance**
   - Create `edit_distance_matcher.py`
   - Follow same pattern as LCS
   - Add tests

4. **Full Integration**
   - Create `enhanced_parser.py`
   - Combine all three tiers
   - Benchmark performance

5. **Evaluation**
   - Run on all public.json cases
   - Measure accuracy
   - Analyze failure cases
   - Iterate on thresholds

---

## 🤔 Discussion Questions

**For you to think about:**

1. **Threshold Tuning**: 
   - LCS threshold = 0.4 is initial guess
   - Should we use different thresholds for province/district/ward?
   - How to auto-tune based on test data?

2. **Token Weighting**:
   - Should some tokens matter more? (e.g., "ha" + "noi" together is strong signal)
   - Could we use TF-IDF or similar?

3. **Performance vs Accuracy Trade-off**:
   - Edit distance is slow (O(k×m) per candidate)
   - Can we filter candidates more aggressively?
   - Worth the 5% accuracy gain?

4. **Confidence Scoring**:
   - How to combine confidence from different tiers?
   - Trie = 1.0, LCS = similarity score, Edit = ???

Would you like me to continue with implementing Phase 5 (Edit Distance) or first integrate Phase 4 (LCS) into the main parser?
