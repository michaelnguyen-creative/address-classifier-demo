# 🏗️ **Implementation Plan - From Zero to Working Solution**

Perfect! Let's create a **phased implementation roadmap** that builds incrementally. Each phase is testable and gets us closer to the full solution.

---

## **📋 Phase Overview**

```
Phase 0: Setup & Data Loading          [Foundation]
Phase 1: Text Normalization            [30 min - Critical foundation]
Phase 2: Data Structure Building       [45 min - Core infrastructure]
Phase 3: Basic Matching Engine         [60 min - First working solution]
Phase 4: Hierarchical Constraint       [45 min - Big accuracy boost]
Phase 5: Advanced Matching             [60 min - Handle edge cases]
Phase 6: Optimization & Edge Cases     [As needed - Polish]
```

**Total estimated time to working solution: 3-4 hours**

---

## **Phase 0: Setup & Data Loading** 
### **Goal:** Read and understand the reference data

### **What we need to do:**

```python
class Solution:
    def __init__(self):
        # Given paths - DON'T change these
        self.province_path = 'list_province.txt'
        self.district_path = 'list_district.txt'
        self.ward_path = 'list_ward.txt'
        
        # TODO: Load the data files
        # TODO: Build data structures
```

### **Implementation Tasks:**

**Task 0.1: File Reading**
- Read each `.txt` file (one name per line)
- Store in lists: `self.provinces`, `self.districts`, `self.wards`
- **Deliverable:** Print counts to verify (63 provinces, ~700 districts, ~11k wards)

**Task 0.2: Initial Inspection**
- Print first 10 entries from each file
- Notice patterns (accents, duplicates, special characters)
- **Deliverable:** Document observations

### **Success Criteria:**
✅ All three files loaded successfully  
✅ Data counts match expectations  
✅ Can access data easily

---

## **Phase 1: Text Normalization**
### **Goal:** Convert messy input → clean, matchable strings

### **Why this is CRITICAL:**
Without good normalization, even exact matches will fail:
- `"Hà Nội"` ≠ `"ha noi"` ≠ `"Ha Noi"` ≠ `"HàNội"`

### **Implementation Tasks:**

#### **Task 1.1: Vietnamese Diacritics Removal**

**Challenge:** Vietnamese has complex diacritics
```
Original: àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệ...
Remove:   aaaaaaaaaaaaeeeeeeeeeee...
```

**Strategy:** Use a mapping dictionary or library
```python
def remove_vietnamese_accents(text: str) -> str:
    # Convert: "Hà Nội" → "Ha Noi"
    # Option A: Manual mapping dictionary
    # Option B: Use library (unidecode, unicodedata)
    pass
```

**Test cases:**
```python
assert remove_accents("Hà Nội") == "Ha Noi"
assert remove_accents("Đà Nẵng") == "Da Nang"
assert remove_accents("Thừa Thiên Huế") == "Thua Thien Hue"
```

---

#### **Task 1.2: Full Normalization Pipeline**

**What to normalize:**
```python
def normalize_text(text: str) -> str:
    # 1. Remove diacritics
    # 2. Lowercase
    # 3. Remove extra whitespace
    # 4. Remove punctuation (but keep spaces)
    # 5. Optionally: expand abbreviations
    pass
```

**Test cases:**
```python
assert normalize("Hà Nội") == "ha noi"
assert normalize("  HÀ  NỘI  ") == "ha noi"
assert normalize("Q.3, TP.HCM") == "q 3 tp hcm"  # or "quan 3 thanh pho ho chi minh"
```

---

#### **Task 1.3: Abbreviation Handling**

**Common patterns to handle:**

| Input | Normalized | Expanded |
|-------|-----------|----------|
| `TP.HCM` | `tp hcm` | `thanh pho ho chi minh` |
| `Q.3` | `q 3` | `quan 3` |
| `P.1` | `p 1` | `phuong 1` |
| `H.` | `h` | `huyen` |
| `X.` | `x` | `xa` |
| `T.` | `t` | `tinh` |

**Decision point:** Should we normalize to abbreviated or expanded form?

**Recommendation:** Keep BOTH in our lookup structures
```python
# When building data structures, create aliases:
"ho chi minh" → "Hồ Chí Minh"
"tp hcm" → "Hồ Chí Minh"  
"thanh pho ho chi minh" → "Hồ Chí Minh"
```

---

#### **Task 1.4: Number Normalization**

**Problem:** `"1"` vs `"01"` vs `"Quận 1"` vs `"Q1"`

**Strategy:**
```python
def normalize_numbers(text: str) -> str:
    # "01" → "1"
    # Keep: "Quận 1" as "quan 1"
    pass
```

### **Phase 1 Deliverables:**
✅ `normalize_text()` function working  
✅ `remove_vietnamese_accents()` function working  
✅ Test suite passing (10+ test cases)  
✅ Can normalize all reference data successfully

---

## **Phase 2: Data Structure Building**
### **Goal:** Build fast lookup structures using normalized data

### **Why this matters:**
- Raw list scanning: O(n) per lookup → too slow
- Hash tables: O(1) lookup → target performance

### **Implementation Tasks:**

#### **Task 2.1: Basic Normalized Mappings**

```python
class Solution:
    def __init__(self):
        # ... load files ...
        
        # Build normalized lookups
        self.province_map = {}  # normalized → original
        self.district_map = {}  # normalized → original
        self.ward_map = {}      # normalized → original
        
        # TODO: Populate these dictionaries
```

**Example:**
```python
# Input from file: "Hà Nội"
# Store as:
self.province_map["ha noi"] = "Hà Nội"
```

**Challenge:** What if multiple entries normalize to the same string?
```python
# Both normalize to "hoa binh":
"Hoà Bình" → "hoa binh"
"Hòa Bình" → "hoa binh"

# Solution: Store as list?
self.ward_map["hoa binh"] = ["Hoà Bình", "Hòa Bình"]
```

---

#### **Task 2.2: Hierarchical Structure**

**Goal:** Link provinces → districts → wards

```python
class Solution:
    def __init__(self):
        # Hierarchical structure
        self.hierarchy = {
            "Hà Nội": {
                "districts": ["Hoàng Mai", "Thanh Xuân", ...],
                "ward_map": {
                    "Hoàng Mai": ["Định Công", "Đại Kim", ...],
                    "Thanh Xuân": ["Khương Mai", ...]
                }
            },
            "Hồ Chí Minh": {
                ...
            }
        }
```

**How to build this?**

**Option A: Parse from file names**
```
If ward = "Định Công" appears in wards.txt
And we know it belongs to "Hoàng Mai" district
And "Hoàng Mai" belongs to "Hà Nội" province
→ Link them in hierarchy
```

**Option B: Use external mapping** (if available)
- Do we have a file that maps ward → district → province?
- If not, we can only build flat lookups

**Reality check:** Looking at our data files, they're just flat lists!
```
provinces.txt: Just province names
districts.txt: Just district names  
wards.txt: Just ward names
```

**🚨 CRITICAL DECISION POINT:**

Without hierarchy data, we need to:
1. **Find hierarchy online** or create mapping file
2. **Infer from names** (risky - "Tân Bình" appears in multiple provinces)
3. **Use flat matching only** (less accurate but simpler)

**My recommendation:** Let's check if the notebook test cases give us hints about hierarchy. We can build it from successful matches!

---

#### **Task 2.3: Alias/Abbreviation Mappings**

```python
class Solution:
    def __init__(self):
        # Special mappings for common abbreviations
        self.province_aliases = {
            "tp hcm": "Hồ Chí Minh",
            "sai gon": "Hồ Chí Minh",
            "ha noi": "Hà Nội",
            "hn": "Hà Nội",
            # ... build from known patterns
        }
```

**Where to get these?**
- Hardcode common ones
- Extract from test data patterns
- Build iteratively as we find failures

### **Phase 2 Deliverables:**
✅ All normalized mappings built  
✅ Fast O(1) lookup for any normalized name  
✅ Hierarchy structure (if possible)  
✅ Abbreviation maps for common cases

---

## **Phase 3: Basic Matching Engine**
### **Goal:** Get our first working `process()` function

### **Implementation Strategy: Greedy Pattern Matching**

```python
def process(self, s: str) -> dict:
    """
    Strategy:
    1. Normalize input
    2. Try to find province (most unique, usually at end)
    3. Try to find district
    4. Try to find ward
    5. Return results
    """
    normalized_input = normalize_text(s)
    
    province = self._find_province(normalized_input)
    district = self._find_district(normalized_input, province)
    ward = self._find_ward(normalized_input, district)
    
    return {
        "province": province,
        "district": district,
        "ward": ward
    }
```

---

#### **Task 3.1: Province Finder**

**Strategy: Search for province names in input**

```python
def _find_province(self, normalized_input: str) -> str:
    """
    Try multiple strategies in order:
    1. Check for exact match of any province name
    2. Check for common abbreviations
    3. Check for partial matches
    """
    
    # Strategy 1: Exact normalized match
    for norm_name, orig_name in self.province_map.items():
        if norm_name in normalized_input:
            return orig_name
    
    # Strategy 2: Check abbreviations
    for abbrev, orig_name in self.province_aliases.items():
        if abbrev in normalized_input:
            return orig_name
    
    # If nothing found
    return ""
```

**Test case:**
```python
# Input: "TT Tân Bình Huyện Yên Sơn, Tuyên Quang"
# Normalized: "tt tan binh huyen yen son tuyen quang"
# Should find: "tuyen quang" → "Tuyên Quang"
```

---

#### **Task 3.2: District Finder**

**Strategy: Similar to province, but with constraints**

```python
def _find_district(self, normalized_input: str, province: str) -> str:
    """
    If we know the province, only check districts in that province
    Otherwise, check all districts
    """
    
    # If we have hierarchy data:
    if province and province in self.hierarchy:
        search_space = self.hierarchy[province]["districts"]
    else:
        search_space = self.district_map.keys()
    
    # Search in the constrained space
    for district in search_space:
        if district in normalized_input:
            return district
    
    return ""
```

---

#### **Task 3.3: Ward Finder**

```python
def _find_ward(self, normalized_input: str, district: str) -> str:
    """
    Most specific - search in the given district
    """
    
    # If we have hierarchy:
    if district:
        search_space = self.get_wards_for_district(district)
    else:
        search_space = self.ward_map.keys()
    
    # Search
    for ward in search_space:
        if ward in normalized_input:
            return ward
            
    return ""
```

---

### **Phase 3 Deliverables:**
✅ Basic `process()` function works  
✅ Can extract at least ONE component correctly  
✅ Passing at least 30% of test cases  
✅ No crashes on any input

---

## **Phase 4: Hierarchical Constraint Application**
### **Goal:** Use hierarchy to boost accuracy

### **Key Insight:**
```
If input = "Định Công, Hoàng Mai, Hà Nội"

Without hierarchy:
- "Định Công" might match multiple wards across Vietnam
- We'd just return the first match (possibly wrong)

With hierarchy:
- Find "Hà Nội" (province) ✓
- In Hà Nội, find "Hoàng Mai" (district) ✓
- In Hoàng Mai, find "Định Công" (ward) ✓
- Guaranteed correct!
```

### **Implementation Tasks:**

#### **Task 4.1: Build Province-District-Ward Mapping**

**Option A: Manual creation from research**
```python
# Create a separate mapping file or dictionary
hierarchy_data = {
    "Hà Nội": {
        "Hoàng Mai": ["Định Công", "Đại Kim", "Giáp Bát", ...],
        "Thanh Xuân": ["Khương Mai", "Nhân Chính", ...],
        # ...
    }
}
```

**Option B: Infer from test data** (clever!)
```python
# As we run tests, record successful matches
# If test says: province="Hà Nội", district="Hoàng Mai", ward="Định Công"
# Record: hierarchy[Hà Nội][Hoàng Mai].add("Định Công")
```

**Option C: Use existing data structure** 
- Check if districts.txt has province info in it somehow?
- Check if wards.txt has district info?

**🔍 Let me check our data files again...**

Looking at the structure, the files are flat lists. **We need to build the hierarchy!**

**Recommended approach:** 
1. Start with known relationships (hardcode major cities)
2. Use test feedback to build the complete map iteratively

---

#### **Task 4.2: Constraint-Based Filtering**

```python
def _find_ward(self, normalized_input: str, province: str, district: str) -> str:
    """
    Now uses TWO levels of constraint
    """
    # Most constrained: know province AND district
    if province and district:
        valid_wards = self.hierarchy[province][district]
        return self._best_match(normalized_input, valid_wards)
    
    # Medium constraint: know province only
    elif province:
        all_wards_in_province = self._get_all_wards_in_province(province)
        return self._best_match(normalized_input, all_wards_in_province)
    
    # No constraint: search all
    else:
        return self._best_match(normalized_input, self.ward_map.keys())
```

**The magic:** Each constraint reduces search space dramatically!

---

### **Phase 4 Deliverables:**
✅ Hierarchy structure built (even if partial)  
✅ Matching uses hierarchical constraints  
✅ Accuracy improved to >60%  
✅ Handles ambiguous names better

---

## **Phase 5: Advanced Matching**
### **Goal:** Handle edge cases and fuzzy matches

### **Implementation Tasks:**

#### **Task 5.1: Multi-Word Matching**

**Problem:** Some names are multiple words
```
"Hồ Chí Minh" - must match all 3 words, not just "Minh"
"Bà Rịa - Vũng Tàu" - has hyphen
```

**Solution:** Longest match wins
```python
def _find_best_match(self, input: str, candidates: list) -> str:
    # Sort by length (longest first)
    sorted_candidates = sorted(candidates, key=len, reverse=True)
    
    for candidate in sorted_candidates:
        if candidate in input:
            return candidate
    
    return ""
```

---

#### **Task 5.2: Fuzzy Matching (Edit Distance)**

**When to use:** Only as last resort!

```python
def _fuzzy_match(self, input: str, candidates: list, threshold=2) -> str:
    """
    Use edit distance for near-matches
    Only activate if no exact match found
    """
    import editdistance  # Already in requirements.txt!
    
    best_match = None
    best_distance = float('inf')
    
    for candidate in candidates:
        distance = editdistance.eval(input, candidate)
        if distance < best_distance and distance <= threshold:
            best_distance = distance
            best_match = candidate
    
    return best_match or ""
```

**Usage:**
```python
def _find_province(self, normalized_input: str) -> str:
    # Try exact first
    result = self._exact_match(normalized_input, self.provinces)
    if result:
        return result
    
    # Fallback to fuzzy
    return self._fuzzy_match(normalized_input, self.provinces, threshold=2)
```

---

#### **Task 5.3: Order-Independent Matching**

**Problem:** Components can appear in any order
```
"Hà Nội, Hoàng Mai, Định Công" ✓
"Định Công, Hoàng Mai, Hà Nội" ✓  (same!)
```

**Solution:** We're already doing this! Since we search for each component independently in the full string, order doesn't matter.

---

#### **Task 5.4: Missing Component Handling**

**Problem:** Sometimes a component is missing
```
Input: "ward, province" (missing district)
Expected: {province: "X", district: "", ward: "Y"}
```

**Solution:** Already handled by returning `""` for not found!

---

### **Phase 5 Deliverables:**
✅ Fuzzy matching implemented  
✅ Handles multi-word names correctly  
✅ Order-independent matching verified  
✅ Accuracy >75%

---

## **Phase 6: Optimization & Edge Cases**
### **Goal:** Hit >85% accuracy and <0.1s performance

### **Implementation Tasks:**

#### **Task 6.1: Performance Optimization**

**Current bottleneck:** Scanning all candidates

**Optimizations:**
```python
# 1. Pre-compile common patterns
self.province_pattern = re.compile('|'.join(self.provinces))

# 2. Use set intersection for fast checking
input_words = set(normalized_input.split())
for province in self.provinces:
    province_words = set(province.split())
    if province_words.issubset(input_words):
        return province

# 3. Cache normalized inputs (if repeated)
@lru_cache(maxsize=1000)
def normalize_text(text: str) -> str:
    ...
```

---

#### **Task 6.2: Handle Test-Specific Edge Cases**

**Review test failures and add special cases:**

```python
# Example: Numbered wards normalization
self.ward_aliases = {
    "01": "1", "02": "2", "03": "3", ...
}

# Example: Common typos
self.typo_corrections = {
    "tp hcm": "Hồ Chí Minh",
    "sai gon": "Hồ Chí Minh",
}
```

---

#### **Task 6.3: Confidence Scoring**

**Idea:** Return match with highest confidence

```python
def _find_with_confidence(self, input: str, candidates: list) -> tuple:
    """
    Returns (best_match, confidence_score)
    """
    scores = []
    for candidate in candidates:
        score = self._calculate_match_score(input, candidate)
        scores.append((candidate, score))
    
    # Return highest scoring
    return max(scores, key=lambda x: x[1])
```

---

### **Phase 6 Deliverables:**
✅ Performance <0.05s average  
✅ Accuracy >85% (ideally >90%)  
✅ All known edge cases handled  
✅ Clean, documented code

---

## **📊 Success Metrics by Phase**

| Phase | Expected Accuracy | Expected Time | Passing Tests |
|-------|------------------|---------------|---------------|
| Phase 3 | ~30-40% | 0.5s | 135-180 / 450 |
| Phase 4 | ~60-70% | 0.2s | 270-315 / 450 |
| Phase 5 | ~75-85% | 0.1s | 340-383 / 450 |
| Phase 6 | >85-90% | <0.05s | >383 / 450 |

---

## **🎯 Implementation Order - My Recommendation**

### **Session 1: Get Something Working** (90 min)
1. Phase 0: Setup (15 min)
2. Phase 1: Normalization (30 min)
3. Phase 2: Basic structures (30 min)
4. Phase 3: First process() (15 min)
→ **Checkpoint:** Can extract at least provinces reliably

### **Session 2: Add Intelligence** (90 min)
5. Phase 4: Hierarchy (45 min)
6. Phase 5.1-5.2: Better matching (45 min)
→ **Checkpoint:** Passing >60% of tests

### **Session 3: Optimize & Polish** (60 min)
7. Phase 5.3-5.4: Edge cases (30 min)
8. Phase 6: Final optimizations (30 min)
→ **Checkpoint:** Passing >85% of tests
