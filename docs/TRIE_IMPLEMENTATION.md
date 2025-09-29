# Trie-Based Address Parser - Implementation Guide

## What We Built

A three-phase algorithm system for Vietnamese address parsing:

1. **Phase 1: Normalization** - O(n) text cleaning
2. **Phase 2: Trie Structure** - O(m) exact matching 
3. **Phase 3: Multi-Trie Matcher** - O(n×k) simultaneous search

---

## Running the Tests

```bash
cd C:\Users\luannvm\ClaudeManaged\address-classifier-demo\Src
python test_trie.py
```

Expected output shows:
- Normalization working (removes diacritics)
- Trie insert/search operations
- Text scanning for matches
- Full matcher integration

---

## Architecture Explanation

### Trie Structure
```
Root
├── 'h' → 'a' → ' ' → 'n' → 'o' → 'i' [value="Hà Nội"]
├── 'h' → 'o' → ' ' → 'c' → 'h' → 'i' → ' ' → 'm' → 'i' → 'n' → 'h' [value="Hồ Chí Minh"]
└── 'd' → 'a' → ' ' → 'n' → 'a' → 'n' → 'g' [value="Đà Nẵng"]
```

### Why Trie Beats Hash Map

**Hash Map Approach:**
```python
# Problem: Must know exact boundaries
if "ha noi" in text:  # Misses "ha noi va da nang"
    return "Hà Nội"
```

**Trie Approach:**
```python
# Solution: Finds all occurrences at any position
matches = trie.search_in_text("ha noi va da nang")
# Returns: [("Hà Nội", 0, 2), ("Đà Nẵng", 3, 5)]
```

---

## Time Complexity Analysis

| Operation | Complexity | Why |
|-----------|------------|-----|
| **Build Trie** | O(Σchars) | Insert each character once |
| **Single Search** | O(m) | Traverse m characters |
| **Search in Text** | O(n×k×m) | n tokens, k=6 window, m=match |
| **Effective** | O(n) | k, m are small constants |

---

## Next Steps

This is **Phase 3** complete. To reach 85%+ accuracy, we need:

**Phase 4: LCS Alignment** (handles reordering)
- When exact trie match fails
- Use dynamic programming O(n×m)

**Phase 5: Edit Distance** (handles typos)
- When LCS fails
- Ukkonen's bounded algorithm O(k×m)

**Phase 6: Hierarchy Validation**
- Cross-check province→district→ward relationships
- Reject invalid combinations

Would you like me to implement these next phases?

---

## Current Capabilities

✅ Exact matching with diacritic normalization  
✅ Multi-word entity recognition  
✅ Order-independent component extraction  
✅ O(n) linear time performance  
✅ Memory-efficient shared prefixes  

⏳ Pending: Fuzzy matching, LCS alignment, hierarchy validation
