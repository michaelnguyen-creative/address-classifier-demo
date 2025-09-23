
---

**Document Status**: Complete - Ready for Implementation  
**Business Impact**: High - Provides strategic foundation for algorithm success  
**Next Action**: Begin implementation with Week 1 priorities

This business analysis document provides the strategic intelligence needed to build a Vietnamese address classifier that not only meets technical requirements but maximizes business value through domain-informed algorithm design.

---
---

## 2. Trie Integration Strategy - Deep Dive

### **Option A: Autocomplete-style Matching**
**Concept:** Build tries where each character leads to next possible characters. When input is corrupted, explore multiple paths simultaneously.

```python
# Example: Input "Thu" could match:
# - "Thuận Thành" (exact)  
# - "Thịnh Sơn" (if 'u' was misread 'ị')
# - "Thủ Đức" (if 'u' was misread 'ủ')
```

**Pros:**
- Excellent for **prefix corruption** (common in OCR)
- Natural **early termination** - stop when no valid paths exist
- Memory efficient for large dictionaries
- Fast exact matching (O(|query|))

**Cons:**
- Struggles with **middle/suffix errors**
- Complex scoring when multiple paths viable
- Can explode exponentially with fuzzy matching

**Best for:** When OCR errors are primarily at word boundaries or prefixes

### **Option B: Prefix Matching with Cost Penalties**
**Concept:** Allow "errors" in trie traversal, accumulating cost. Each character mismatch, insertion, deletion has a penalty.

```python
# Example traversing trie for "Thuan" → "Thuận":
# T(0) → h(0) → u(0) → a(1) → n(1) → +(1) # Missing 'ậ', total cost = 3
```

**Pros:**
- Handles **all error types** (substitution, insertion, deletion)
- **Tunable sensitivity** via cost parameters
- Can rank matches by confidence
- Mathematical foundation (edit distance)

**Cons:**
- **Computationally expensive** - can be O(|query| × |dict| × k) where k=max edits
- Memory intensive (must track multiple states)
- **Difficult to tune** cost parameters for Vietnamese specifics

**Best for:** When you need robust handling of all error types and can afford computation

### **Option C: Multi-level Tries (Hierarchical)**
**Concept:** Separate tries for provinces, districts (per province), wards (per district). Parse hierarchically using context.

```python
# Structure:
# - Province trie: {"Nghệ An": id1, "Long An": id2, ...}
# - District tries: {province_id: {"Đô Lương": id1, "Cần Giuộc": id2}}  
# - Ward tries: {district_id: {"Thịnh Sơn": id1, ...}}
```

**Pros:**
- **Dramatically reduces search space** (wards only searched within found district)
- **Contextual validation** (impossible combinations filtered out)
- **Performance boost** - O(|provinces|) + O(|districts_in_province|) + O(|wards_in_district|)
- Natural **confidence scoring** (complete hierarchy = higher confidence)

**Cons:**
- **Error propagation** - wrong province ruins everything downstream
- Requires **accurate hierarchy parsing** from noisy input
- More complex data structure management

**Best for:** When input maintains some hierarchical structure and you want maximum performance

### **My Recommendation: Hybrid Multi-level + Fuzzy Fallback**

```python
# Algorithm:
1. Parse input into potential [province, district, ward] segments
2. Try exact matching in hierarchical order
3. If exact fails at any level, try fuzzy within that level
4. If still fails, try fuzzy across all levels (expensive fallback)
```

---

## 3. Address Structure Parsing - Deep Dive

### **Option A: Pattern Recognition for Prefixes**
**Concept:** Use regex/string matching to identify administrative markers and segment the address.

```python
# Patterns to recognize:
patterns = {
    'province': r'(T\.|Tỉnh|TP\.|Thành phố)',
    'district': r'(H\.|Huyện|Q\.|Quận|TX\.|Thị xã)', 
    'ward': r'(X\.|Xã|P\.|Phường|TT\.|Thị trấn)'
}

# "Xã Thịnh Sơn H. Đô Lương T. Nghệ An"
# → segments: [("Xã", "Thịnh Sơn"), ("H.", "Đô Lương"), ("T.", "Nghệ An")]
```

**Pros:**
- **Simple and fast** - O(|input|) parsing
- **Robust to order variations** (T. X. H. vs H. T. X.)
- Easy to handle **abbreviation variations** (Tỉnh vs T.)
- **Predictable behavior**

**Cons:**
- **Breaks when prefixes are corrupted** ("X" instead of "Xã")
- **Fails on prefix-less input** ("Thịnh Sơn, Đô Lương, Nghệ An")
- May **mis-segment** when punctuation is wrong

**Best for:** When OCR preserves administrative prefixes reasonably well

### **Option B: Contextual Parsing (Geographic Constraints)**
**Concept:** Use geographic knowledge to validate and parse. If we identify any component, use it to constrain others.

```python
# Algorithm:
1. Try to identify ANY component (province, district, ward) in input
2. Use geographic constraints to guide parsing of remaining text
3. Score combinations by geographic validity

# Example: If "Nghệ An" found → only look for districts IN Nghệ An
# If "Đô Lương" found → only look for wards IN Đô Lương
```

**Pros:**
- **Very robust** - works even with heavy corruption
- **Self-correcting** - geographic constraints eliminate impossible combinations
- **High accuracy** when geographic data is complete
- **Natural confidence scoring**

**Cons:**
- **Computationally intensive** - may need to try all combinations
- **Complex logic** for handling partial matches
- **Requires complete geographic database**

**Best for:** When input is heavily corrupted but you have comprehensive geographic data

### **Option C: Confidence Scoring + Multiple Hypotheses**
**Concept:** Generate multiple parsing hypotheses, score each by multiple criteria, return best.

```python
# Scoring factors:
# - Edit distance to known entities
# - Geographic consistency  
# - Pattern match quality
# - String length penalties
# - Frequency/popularity of locations

def score_hypothesis(province, district, ward):
    score = 0
    score += edit_distance_score(province)
    score += geographic_consistency_score(province, district, ward) 
    score += pattern_match_score(original_input, hypothesis)
    return score
```

**Pros:**
- **Maximum accuracy** - considers multiple evidence types
- **Handles ambiguous cases** gracefully
- **Tunable** - can adjust scoring weights
- **Extensible** - easy to add new scoring criteria

**Cons:**
- **Computationally expensive** - generates many hypotheses
- **Complex parameter tuning**
- **Risk of overfitting** to development data

**Best for:** When accuracy is paramount and you can afford computation

### **My Recommendation: Pattern Recognition + Geographic Validation**

```python
# Algorithm:
1. Use pattern recognition for initial segmentation (fast path)
2. If pattern recognition fails/uncertain, use contextual parsing
3. Always validate final result with geographic constraints
4. Use confidence thresholds to decide between hypotheses
```

---

## 4. Performance Optimization - My Assumptions & Recommendations

### **Critical Assumptions:**
1. **Most inputs will be "lightly corrupted"** - pattern recognition will work 70%+ of time
2. **Geographic database is small enough to preload** (~63 provinces, ~700 districts, ~10k wards)
3. **Preprocessing time doesn't count** toward the 0.01s limit
4. **Python dict/set lookups** are acceptable for core operations

### **Optimization Strategy:**

```python
# 1. Aggressive Preprocessing
class AddressClassifier:
    def __init__(self):
        # Precompute ALL possible normalizations
        self.exact_lookup = {}  # normalized_text → (province, district, ward)
        self.fuzzy_tries = {}   # Multi-level tries with common variations
        self.pattern_cache = {} # Regex compilation cache
        
# 2. Fast Path Optimization  
def classify(self, text):
    # Try exact lookup first (microseconds)
    normalized = self.normalize(text)
    if normalized in self.exact_lookup:
        return self.exact_lookup[normalized]
    
    # Try pattern + exact matching (milliseconds)  
    segments = self.parse_patterns(text)
    if segments and self.validate_exact(segments):
        return segments
        
    # Fuzzy fallback (expensive - but rare)
    return self.fuzzy_classify(text)
```

### **Key Performance Decisions:**
- **Precompute everything possible** during initialization
- **Normalize aggressively** - remove all diacritics, spaces, punctuation for exact matching
- **Use tiered fallback** - exact → pattern → fuzzy
- **Early termination** - stop at first confident match
- **Cache common misspellings** from development data
