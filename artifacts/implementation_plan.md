# 🏗️ **Implementation Plan - Algorithm-Driven Approach**

Updated to use proper algorithms from lecture slides: **Trie-based matching, Dynamic Programming, and Edit Distance**

---

## **📋 Revised Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Address Parser System                     │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
   │  TRIE   │         │   DP    │        │  Edit   │
   │  Exact  │         │   LCS   │        │Distance │
   │ O(m)    │         │ O(n×m)  │        │ O(k×m)  │
   └─────────┘         └─────────┘        └─────────┘
   Fast Path           Alignment          Fuzzy Match
   (80% cases)         (15% cases)        (5% cases)
```

---

## **Phase 0: Setup & Data Loading**
### **Goal:** Read reference data and understand structure

### **Implementation:**

```python
class Solution:
    def __init__(self):
        # Data paths
        self.province_path = 'list_province.txt'
        self.district_path = 'list_district.txt'
        self.ward_path = 'list_ward.txt'
        
        # Load raw data
        self.provinces = self._load_file(self.province_path)
        self.districts = self._load_file(self.district_path)
        self.wards = self._load_file(self.ward_path)
    
    def _load_file(self, path: str) -> list:
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
```

### **Deliverable:**
✅ Load 63 provinces, ~700 districts, ~11,000 wards  
✅ Verify no encoding issues

---

## **Phase 1: Text Normalization**
### **Goal:** Canonical form for matching

### **Algorithm: Unicode NFKD + Character Filtering**

From literature: *"Vietnamese text contains complex diacritics requiring consistent normalization"*

```python
import unicodedata

def normalize_text(text: str) -> str:
    """
    Normalization pipeline:
    1. Unicode NFKD decomposition
    2. Remove combining characters (diacritics)
    3. Lowercase
    4. Clean whitespace
    
    Time: O(n) where n = text length
    """
    # Decompose: "Hà Nội" → "Ha ̀Nô ̣i"
    text = unicodedata.normalize('NFKD', text)
    
    # Remove combining chars: "Ha ̀Nô ̣i" → "Ha Noi"
    text = ''.join(c for c in text if not unicodedata.combining(c))
    
    # Lowercase and clean
    text = text.lower().strip()
    text = ' '.join(text.split())
    
    return text
```

### **Test Cases:**
```python
assert normalize_text("Hà Nội") == "ha noi"
assert normalize_text("Đà Nẵng") == "da nang"
assert normalize_text("TP.HCM") == "tp.hcm"
```

### **Deliverable:**
✅ Normalization function with 10+ passing tests  
✅ All reference data normalized successfully

---

## **Phase 2: Trie Data Structure**
### **Goal:** O(m) exact matching for fast path

### **Algorithm: Multi-Level Hierarchical Trie**

From literature: *"Tries provide the most natural way to search for words in applications where the set of keys has significant prefix structure"*

### **Trie Node Structure:**

```python
class TrieNode:
    def __init__(self):
        self.children = {}  # char → TrieNode
        self.is_end = False
        self.value = None   # Original name if this is a word end

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, normalized_word: str, original_value: str):
        """
        Insert a word into trie
        Time: O(m) where m = len(word)
        Space: O(m) per unique path
        """
        node = self.root
        for char in normalized_word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        node.is_end = True
        node.value = original_value
    
    def search(self, normalized_word: str) -> str:
        """
        Exact search
        Time: O(m)
        """
        node = self.root
        for char in normalized_word:
            if char not in node.children:
                return None
            node = node.children[char]
        
        return node.value if node.is_end else None
    
    def search_in_text(self, text: str) -> list:
        """
        Find all trie words that appear as substrings in text
        Time: O(n × m) where n = len(text), m = max word length
        """
        matches = []
        tokens = text.split()
        
        # Try starting from each position
        for i in range(len(tokens)):
            # Try different lengths
            for j in range(i + 1, min(i + 6, len(tokens) + 1)):
                candidate = " ".join(tokens[i:j])
                result = self.search(candidate)
                if result:
                    matches.append((result, i, j))
        
        return matches
```

### **Build Tries:**

```python
class Solution:
    def __init__(self):
        # ... load data ...
        
        # Build tries
        self.province_trie = Trie()
        self.district_trie = Trie()
        self.ward_trie = Trie()
        
        # Insert all entities
        for prov in self.provinces:
            normalized = normalize_text(prov)
            self.province_trie.insert(normalized, prov)
        
        # Similar for districts and wards
```

### **Time Complexity:**
- Build: O(total_chars_in_all_names)
- Search: O(m) per query
- Space: O(total_chars) with shared prefixes

### **Deliverable:**
✅ Three tries built (province, district, ward)  
✅ Can find "ha noi" in O(6) time  
✅ Memory usage < 10MB

---

## **Phase 3: Trie-Based Matching (Fast Path)**
### **Goal:** Handle 80% of cases with exact trie matching

### **Algorithm: Multi-Trie Simultaneous Search**

```python
def process(self, s: str) -> dict:
    """
    Fast path: Trie exact matching
    
    Time: O(n × k) where n = tokens, k = tries
    """
    normalized = normalize_text(s)
    
    # Search all three tries simultaneously
    province_matches = self.province_trie.search_in_text(normalized)
    district_matches = self.district_trie.search_in_text(normalized)
    ward_matches = self.ward_trie.search_in_text(normalized)
    
    # Select best matches
    province = self._select_best(province_matches)
    district = self._select_best(district_matches)
    ward = self._select_best(ward_matches)
    
    return {
        "province": province,
        "district": district,
        "ward": ward
    }

def _select_best(self, matches: list) -> str:
    """
    If multiple matches, select:
    1. Longest match (more specific)
    2. Rightmost position (provinces usually last)
    """
    if not matches:
        return ""
    
    # Sort by length (longest first), then position (rightmost first)
    sorted_matches = sorted(matches, 
                           key=lambda x: (len(x[0]), x[2]), 
                           reverse=True)
    
    return sorted_matches[0][0]  # Return value
```

### **Why This Works:**
- Vietnamese addresses: "Ward, District, Province"
- Trie finds all entities in O(n) scan
- Longest match = most specific
- Rightmost = likely province (end of address)

### **Deliverable:**
✅ Trie-based matching working  
✅ Handles 80% of clean test cases  
✅ Performance < 10ms per address

---

## **Phase 4: Dynamic Programming - LCS Alignment**
### **Goal:** Handle cases where tokens are reordered or partial

### **Algorithm: Longest Common Subsequence (LCS)**

From literature: *"LCS provides optimal alignment of hierarchical address components"*

### **When to Use:**
- Trie exact match fails
- Input has extra words: "123 Nguyen Van Linh, Ha Noi"
- Tokens reordered: "Ha Noi Nam Tu Liem Cau Dien"

### **Implementation:**

```python
def lcs_match(self, input_tokens: list, candidate: str) -> float:
    """
    Compute LCS-based similarity
    
    Time: O(n × m) where n = input length, m = candidate length
    Space: O(n × m) DP table
    
    DP Recurrence:
    LCS[i][j] = {
        LCS[i-1][j-1] + 1       if input[i] == candidate[j]
        max(LCS[i-1][j],        otherwise
            LCS[i][j-1])
    }
    """
    candidate_tokens = candidate.split()
    n, m = len(input_tokens), len(candidate_tokens)
    
    # DP table
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    
    # Fill table
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if input_tokens[i-1] == candidate_tokens[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    lcs_length = dp[n][m]
    
    # Similarity score
    return 2 * lcs_length / (n + m)

def fallback_lcs(self, normalized: str, candidates: list) -> str:
    """
    Use LCS to find best match when trie fails
    """
    input_tokens = normalized.split()
    
    best_match = ""
    best_score = 0.0
    
    for candidate in candidates:
        score = self.lcs_match(input_tokens, normalize_text(candidate))
        if score > best_score and score > 0.6:  # Threshold
            best_score = score
            best_match = candidate
    
    return best_match
```

### **Example:**

```
Input: "123 nguyen van linh ha noi"
Candidate: "ha noi"

Input tokens: ["123", "nguyen", "van", "linh", "ha", "noi"]
Candidate tokens: ["ha", "noi"]

LCS: ["ha", "noi"] → length 2
Similarity: 2×2 / (6+2) = 0.5

If threshold = 0.4, this matches!
```

### **Deliverable:**
✅ LCS matching implemented  
✅ Handles noisy inputs with extra words  
✅ Accuracy +10% over trie-only

---

## **Phase 5: Edit Distance (Ukkonen's Algorithm)**
### **Goal:** Handle OCR errors and typos

### **Algorithm: Bounded Edit Distance with Early Termination**

From literature: *"Process only O(k×n) cells for k-approximate matching"*

### **When to Use:**
- Trie AND LCS both fail
- Input has typos: "ha nol" instead of "ha noi"
- OCR errors: "dinh cong" → "dlnh cong"

### **Implementation:**

```python
def bounded_edit_distance(self, s1: str, s2: str, max_k: int = 2) -> int:
    """
    Ukkonen's diagonal-band edit distance
    Only compute cells within distance k of diagonal
    
    Time: O(k × min(n,m)) instead of O(n × m)
    Space: O(k)
    
    Algorithm:
    - Only process diagonal band of width 2k+1
    - Early termination if distance exceeds k
    """
    n, m = len(s1), len(s2)
    
    # Quick checks
    if abs(n - m) > max_k:
        return max_k + 1  # Definitely > max_k
    
    # Previous row of DP
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

def fuzzy_match(self, input_word: str, candidates: list, max_distance: int = 2) -> str:
    """
    Find best match within edit distance threshold
    """
    best_match = ""
    best_distance = max_distance + 1
    
    for candidate in candidates:
        normalized_candidate = normalize_text(candidate)
        distance = self.bounded_edit_distance(input_word, normalized_candidate, max_distance)
        
        if distance < best_distance:
            best_distance = distance
            best_match = candidate
    
    return best_match if best_distance <= max_distance else ""
```

### **Example:**

```
Input: "ha nol" (typo)
Candidate: "ha noi"

Edit operations:
  ha nol
  ha noi
     ↑
  1 substitution: l → i

Distance = 1 ≤ 2 → Match!
```

### **Deliverable:**
✅ Fuzzy matching with edit distance ≤ 2  
✅ Handles OCR errors gracefully  
✅ Final accuracy > 85%

---

## **Phase 6: Hierarchical Validation**
### **Goal:** Use geographic constraints to disambiguate

### **Algorithm: Constraint Propagation**

From literature: *"Geographic relationships provide powerful search space reduction (79× improvement)"*

### **Build Hierarchy:**

```python
class Solution:
    def __init__(self):
        # ... load data and build tries ...
        
        # Build hierarchy from test data or external source
        self.hierarchy = self._build_hierarchy()
    
    def _build_hierarchy(self) -> dict:
        """
        Build province → districts → wards mapping
        
        Options:
        1. Parse from structured data file
        2. Use external database (Vietnamese administrative units)
        3. Build incrementally from test feedback
        """
        # For now, start with empty and populate
        hierarchy = {}
        
        # Load from external JSON if available
        # Or build from known mappings
        
        return hierarchy
    
    def validate_hierarchy(self, ward: str, district: str, province: str) -> bool:
        """
        Check if ward belongs to district in province
        
        Time: O(1) hash lookup
        """
        if province not in self.hierarchy:
            return True  # No data, can't invalidate
        
        if district not in self.hierarchy[province]:
            return False
        
        if ward not in self.hierarchy[province][district]:
            return False
        
        return True
```

### **Use in Matching:**

```python
def process(self, s: str) -> dict:
    """
    Final version with hierarchical validation
    """
    normalized = normalize_text(s)
    
    # Phase 1: Trie exact match
    matches = self._trie_match(normalized)
    
    # Phase 2: Validate hierarchy
    if self.validate_hierarchy(matches['ward'], matches['district'], matches['province']):
        return matches
    
    # Phase 3: LCS fallback
    matches = self._lcs_match(normalized)
    if self.validate_hierarchy(matches['ward'], matches['district'], matches['province']):
        return matches
    
    # Phase 4: Fuzzy fallback
    matches = self._fuzzy_match(normalized)
    
    return matches
```

### **Deliverable:**
✅ Hierarchy validation working  
✅ Rejects invalid combinations  
✅ Accuracy boost +5-10%

---

## **📊 Algorithm Complexity Summary**

| Phase | Algorithm | Time | Space | When Used |
|-------|-----------|------|-------|-----------|
| **Phase 3** | Trie Search | O(m) | O(total_chars) | 80% cases |
| **Phase 4** | LCS DP | O(n×m) | O(n×m) | 15% cases |
| **Phase 5** | Ukkonen Edit Distance | O(k×m) | O(k) | 5% cases |
| **Phase 6** | Hierarchy Validation | O(1) | O(relationships) | Always |

**Overall:** O(n) average case with tiered fallbacks

---

## **🎯 Implementation Timeline**

### **Day 1: Foundation (3 hours)**
- Phase 0: Setup (30 min)
- Phase 1: Normalization (30 min)
- Phase 2: Build tries (90 min)
- Phase 3: Trie matching (30 min)
→ **Checkpoint:** 50-60% accuracy

### **Day 2: Advanced Algorithms (3 hours)**
- Phase 4: LCS implementation (90 min)
- Phase 5: Edit distance (60 min)
- Phase 6: Hierarchy (30 min)
→ **Checkpoint:** 75-85% accuracy

### **Day 3: Polish (2 hours)**
- Edge cases
- Performance optimization
- Final testing
→ **Checkpoint:** >85% accuracy

---

## **Success Metrics**

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Accuracy** | >85% | Test suite pass rate |
| **Performance** | <100ms | Average processing time |
| **Memory** | <100MB | Peak memory usage |
| **Code Quality** | Clean | Documented, tested |

---

## **Key Algorithmic Insights**

1. **Trie = Fast Exact Match**: O(m) beats O(n) linear search
2. **LCS = Robust Alignment**: Handles extra words, reordering
3. **Bounded Edit Distance = OCR Resilience**: k-approximate in O(k×m)
4. **Hierarchy = Disambiguation**: Reduces search space 79×

This approach combines classical algorithms from lecture slides for a robust, performant solution.
