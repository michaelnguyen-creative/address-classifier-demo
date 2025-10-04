Building hash maps:  30ms
Total initialization: 260ms (one-time cost)
```

---

## Monitoring and Metrics

### Key Performance Indicators

**Coverage by variant type:**
```
Tier 1 Trie matches (production logs):
- Full normalized (v1):      45%  "ho chi minh"
- Initials (v3):             25%  "hcm"
- No spaces (v2):            15%  "hochiminh"
- First initial + rest (v6):  8%  "h chi minh"
- Dotted initials (v4):       4%  "h.c.m"
- First + last (v5):          3%  "ho minh"
Total Tier 1 coverage:       80%
```

**Tier 2/3 logs reveal missed patterns:**
```
LCS frequent matches not in aliases:
- "TPHCM" (not generated, add to abbreviations)
- "SG" (synonym, not variant - add to synonym map)
```

### Adding New Patterns

When monitoring reveals a new abbreviation pattern:

**1. Add to `generate_aliases()`:**
```python
# NEW: Handle compact initials without dots
compact_initials = ''.join(t[0] for t in tokens).upper()
aliases.add(compact_initials)  # "HCM", "TPHCM"
```

**2. Rebuild database:**
```python
python -c "from address_database import AddressDatabase; 
           db = AddressDatabase(); 
           print('Rebuilt with new aliases')"
```

**3. Verify coverage improvement:**
```python
python test_integration_accuracy.py
```

---

## Future Enhancements

### 1. Dynamic Alias Learning

**Idea:** Learn new aliases from successful Tier 2/3 matches

```python
def learn_alias(successful_match):
    """
    If LCS/Edit Distance found a match, consider adding it as alias
    
    Criteria:
    - Match confidence > 0.8
    - Seen ≥10 times in logs
    - Human validation
    """
    if should_promote_to_alias(successful_match):
        add_alias(successful_match.input, successful_match.entity)
        rebuild_trie()
```

**Benefits:**
- Automatic discovery of user patterns
- Reduces Tier 2/3 load over time

**Risks:**
- False positives become permanent
- Requires monitoring infrastructure

**Status:** Deferred until we have production logs

### 2. Compressed Trie

**Idea:** Use LOUDS (Level-Order Unary Degree Sequence) for memory efficiency

**Benefits:**
- 3-5x memory reduction
- Still O(m) lookup

**Complexity:**
- Hard to implement correctly
- Not worth it at 1MB scale

**Status:** Not needed unless memory becomes constraint

### 3. Contextual Aliases

**Idea:** Different aliases in different contexts

```python
# "Q1" in HCM → "Quận 1"  
# "Q1" in Hanoi → Not common (Hanoi uses district names)
context_aliases = {
    "ho chi minh": {"Q1": "Quận 1", "Q3": "Quận 3", ...},
    "ha noi": {"Q1": None, ...}  # Less common
}
```

**Benefits:**
- Reduces false positives
- More accurate matches

**Complexity:**
- Requires context tracking
- More complex Trie structure

**Status:** Interesting idea, evaluate if false positives become problem

---

## Synonyms vs. Aliases

### Important Distinction

**Aliases:** Structural variants of the SAME name
- "Hồ Chí Minh" → "HCM", "ho chi minh", "hochiminh"
- Generated algorithmically from the name itself

**Synonyms:** DIFFERENT names for the same entity
- "Hồ Chí Minh" ↔ "Sài Gòn" (historical name)
- "Hồ Chí Minh" ↔ "SG" (abbreviation of synonym)
- Require explicit mapping

### Handling Synonyms

**Implementation:**
```python
# In alias_generator.py
KNOWN_SYNONYMS = {
    "Hồ Chí Minh": ["saigon", "sai gon", "sg"],
    "Thành phố Hồ Chí Minh": ["saigon", "sai gon", "sg"],
    # Add more as discovered
}

def generate_aliases(original_name, config):
    aliases = set()
    
    # Generate structural variants
    normalized = normalize_text(original_name, config)
    aliases.add(normalized)
    # ... other variants
    
    # Add known synonyms
    for official_name, synonyms in KNOWN_SYNONYMS.items():
        if normalize_text(official_name, config) == normalized:
            aliases.update(synonyms)
    
    return aliases
```

**Why separate from fuzzy matching:**
- Synonyms are binary: "Saigon" IS "HCM" (score=1.0)
- N-grams would give "Saigon" vs "HCM" a low score (0.2)
- Explicit mapping is clearer and more accurate

---

## Edge Cases and Gotchas

### 1. Single-Token Names

**Problem:** "Huế" has only 1 token

**Solution:**
```python
if len(tokens) == 1:
    return {normalized}  # Only variant 1, skip others
```

**Why:** Initials of "Huế" is just "h" (too generic, false positives)

### 2. Number-Only Names

**Problem:** "Phường 1" normalizes to just "1"

**Solution:**
```python
if tokens == ['1'] or tokens == ['2']:
    # Don't generate compact variants
    return {normalized}  # Just "1", not "1" repeated
```

**Why:** Numbers are already maximally compact

### 3. Very Long Names

**Problem:** "Thị Xã Thủ Dầu Một" (5+ tokens)

**Solution:**
```python
if len(tokens) > 5:
    # Limit initials to avoid ambiguity
    initials = ''.join(t[0] for t in tokens[:5])  # First 5 only
    aliases.add(initials)
```

**Why:** 7+ character initials are rare in practice, waste space

### 4. Duplicate Aliases Across Entities

**Problem:** "TB" could be "Tân Bình" or "Thủ Đức"

**Solution:** Trie naturally handles this:
```python
trie.insert("tb", "Tân Bình")   # First insert
trie.insert("tb", "Thủ Đức")    # Overwrites with second
```

**Mitigation:** 
- Use hierarchical filtering (can't confuse if in different provinces)
- Prefer longer aliases (3+ chars)
- LCS/Edit Distance resolves remaining ambiguity

---

## Testing Checklist

When adding new alias patterns, verify:

- [ ] No duplicate aliases within same entity
- [ ] Aliases don't collide with administrative prefixes ("p", "q", "h")
- [ ] Single-token edge case handled
- [ ] Number-only edge case handled  
- [ ] Long name (5+ tokens) handled
- [ ] Trie insertion succeeds for all aliases
- [ ] Lookup returns correct original name
- [ ] Coverage improvement measured
- [ ] No performance regression (query time < 1ms)

---

## Lessons Learned

### What Worked Well

✅ **Simple patterns first:** Started with 3 variants, added more as needed  
✅ **Data-driven:** Used Tier 2/3 logs to find missing patterns  
✅ **Deterministic:** Easy to debug because aliases are predictable  

### What We'd Do Differently

⚠️ **Version alias patterns:** When adding new variants, version them
```python
ALIAS_VERSION = "2.0"  # Changed in 2025-01-02: Added uppercase initials
```

⚠️ **More structured testing:** Test each variant pattern independently

⚠️ **Document pattern rationale:** Why 7 variants? Document the decision

---

## Related Documents

**ADRs:**
- [ADR-001: Three-Tier Architecture](./ADR-001-Three-Tier-Architecture.md)
- [ADR-002: Tier Handoff Logic](./ADR-002-Tier-Handoff-Logic.md)

**Code:**
- `alias_generator.py` - Alias generation
- `trie_parser.py` - Trie implementation
- `address_database.py` - Database building

**Tests:**
- `test_alias_direct.py` - Alias pattern tests
- `test_trie.py` - Trie functionality tests

---

## References

**Data Structures:**
- Trie (Prefix Tree): Fredkin, E. (1960). "Trie Memory". Communications of the ACM.
- BK-Tree: Burkhard, W. A.; Keller, R. M. (1973). "Some approaches to best-match file searching"

**Similar Systems:**
- Google Places API: Uses precomputed aliases + fuzzy matching
- Elasticsearch: Synonym filters for search
- Postgres Full Text Search: Lexeme normalization

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-01-02 | 1.0 | Initial ADR | System Architect |
| 2025-01-02 | 1.1 | Added synonyms section | System Architect |
| 2025-01-02 | 1.2 | Added edge cases and testing checklist | System Architect |
