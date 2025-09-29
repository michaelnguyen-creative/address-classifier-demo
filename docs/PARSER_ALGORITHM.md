# **Redesigning with Classic Algorithms**

Based on the literature, here are the better approaches:

---

## **Option 1: Trie-Based Matching** ⭐ RECOMMENDED

From the literature: *"Tries provide the most natural way to search for words in applications where the set of keys has significant prefix structure."*

### **Algorithm: Multi-Level Hierarchical Trie**

```
Build Phase:
1. Create 3 separate tries: province_trie, district_trie, ward_trie
2. Insert all normalized names into respective tries
3. Each leaf stores entity metadata (codes, parent relationships)

Search Phase:
1. Tokenize input text
2. For each token position, traverse all 3 tries simultaneously
3. Collect all matches with their positions
4. Validate hierarchy using parent relationships
5. Return best match based on completeness

Time: O(n × m) where n=tokens, m=max_name_length
Space: O(total_chars_in_all_names)
```

**Why better than sliding window:**
- Natural prefix matching (handles "Ha Noi" vs "Hanoi City")
- O(m) per lookup instead of O(k × entities)
- Memory-efficient shared prefixes

---

## **Option 2: Dynamic Programming (Longest Common Subsequence)**

From the literature: *"LCS provides optimal alignment of hierarchical address components"*

### **Algorithm: DP-Based Component Alignment**

```python
def align_address(ocr_tokens, known_addresses):
    """
    Use LCS to find best alignment between input and database
    """
    best_score = 0
    best_match = None
    
    for candidate in known_addresses:
        candidate_tokens = tokenize(candidate)
        
        # LCS DP table
        lcs_length = longest_common_subsequence(ocr_tokens, candidate_tokens)
        
        # Similarity score
        similarity = 2 * lcs_length / (len(ocr_tokens) + len(candidate_tokens))
        
        if similarity > best_score:
            best_score = similarity
            best_match = candidate
    
    return best_match, best_score
```

**Time:** O(k × n × m) where k=candidates, n=input_length, m=candidate_length  
**When to use:** High OCR noise, reordered tokens

---

## **Option 3: Edit Distance with Early Termination (Ukkonen's Algorithm)**

From the literature: *"Process only O(k×n) cells for k-approximate matching"*

### **Algorithm: Bounded Edit Distance**

```python
def fuzzy_match_ukkonen(query, candidates, max_distance=2):
    """
    Ukkonen's diagonal-band edit distance
    Only compute cells within distance k of diagonal
    """
    matches = []
    
    for candidate in candidates:
        # Only compute diagonal band
        distance = bounded_edit_distance(query, candidate, max_distance)
        
        if distance <= max_distance:
            matches.append((candidate, distance))
    
    return sorted(matches, key=lambda x: x[1])
```

**Time:** O(k × n) instead of O(n × m) full DP  
**When to use:** Spell checking, OCR error correction

---

## **My Recommendation: Hybrid Trie + DP Approach**

Combine the strengths of multiple algorithms:

```
Phase 1: TRIE EXACT MATCH (Fast Path)
  - Try exact trie lookup for each token
  - O(m) per token, very fast
  - Handles 80%+ of cases

Phase 2: FUZZY MATCH (Fallback)
  - For unmatched tokens, use bounded edit distance
  - O(k × m) per candidate
  - Handles OCR errors

Phase 3: LCS ALIGNMENT (Full Text)
  - If phases 1-2 fail, try LCS against full addresses
  - O(n × m) but only for hard cases
  - Handles reordering, partial matches
```