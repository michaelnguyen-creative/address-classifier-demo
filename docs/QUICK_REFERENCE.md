# 🎯 Quick Reference: Phase 4+ Implementation

## 📁 File Structure

```
Src/
├── lcs_matcher.py          ✅ LCS algorithm (DONE)
├── test_lcs.py            ✅ Tests (DONE)
├── trie_parser_quiet.py   ✅ Clean Trie (DONE)
├── address_parser.py      ⏳ Main parser (needs LCS integration)
├── address_database.py    ✅ Database (existing)
└── trie_parser.py         ✅ Trie (existing)
```

## 🚀 Quick Start

### Run Tests
```bash
cd C:\Users\luannvm\ClaudeManaged\address-classifier-demo\Src
python test_lcs.py
```

### Expected Output
```
LCS MATCHER - BASIC UNIT TESTS
  [TEST 1] Identical sequences ✓ PASS
  [TEST 2] Subsequence ✓ PASS
  [TEST 3] No overlap ✓ PASS
  [TEST 4] Partial overlap ✓ PASS
  [TEST 5] Reordered ✓ PASS

LCS MATCHER - INTEGRATION WITH TRIE PARSER
  [TEST 1] Extra words... ✓ PASS
  [TEST 2] Clean... ✓ PASS
  [TEST 3] Reordered... ✓ PASS
  [TEST 4] Prefixes... ✓ PASS

Success Rate: 100%
```

## 🎓 Algorithm Cheat Sheet

### LCS Formula
```
LCS[i][j] = {
    LCS[i-1][j-1] + 1       if tokens match
    max(LCS[i-1][j],        otherwise
        LCS[i][j-1])
}

Similarity = 2 × LCS_length / (n + m)
```

### Complexity
| Operation | Time | Space |
|-----------|------|-------|
| LCS per candidate | O(n×m) | O(n×m) |
| All provinces (63) | ~2ms | negligible |
| All districts (696) | ~20ms | negligible |
| All wards (10,047) | ~300ms | negligible |

### When LCS Helps
✅ Extra words: "123 street name cau dien"
✅ No separators: "ha noi nam tu liem"
✅ Prefixes: "P. Cau Dien, Q. Nam"
❌ Typos: "ha nol" (need Edit Distance)

## 🔧 Integration Code Snippet

```python
# In address_parser.py
from lcs_matcher import LCSMatcher, prepare_candidate_tokens
from trie_parser import normalize_text

class AddressParser:
    def __init__(self, db):
        # Existing
        self.trie_parser = TrieBasedMatcher()
        
        # NEW
        self.lcs_matcher = LCSMatcher(threshold=0.4)
        self.lcs_candidates = {
            "province": [(p, normalize_text(p).split()) 
                        for p in province_names],
            # ... similar for district and ward
        }
    
    def parse(self, text):
        # Try Trie
        result = self.trie_parser.match(text)
        if result['province']:
            return result
        
        # Fallback to LCS
        tokens = normalize_text(text).split()
        lcs_result = self.lcs_matcher.find_all_matches(
            tokens, 
            self.lcs_candidates
        )
        return lcs_result
```

## 📊 Performance Targets

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Accuracy | 80% (Trie) | >85% | ⏳ Need LCS |
| P50 Latency | 5ms | <50ms | ✅ |
| P95 Latency | 10ms | <200ms | ✅ |
| Memory | <50MB | <100MB | ✅ |

## 🐛 Troubleshooting

### Test fails: "ModuleNotFoundError"
```bash
# Make sure you're in Src/ directory
cd C:\Users\luannvm\ClaudeManaged\address-classifier-demo\Src
python test_lcs.py
```

### Low similarity scores
- Check threshold (default: 0.4)
- Try lowering: `LCSMatcher(threshold=0.3)`
- Inspect token lengths (very short = low scores)

### Slow performance
- Profile: How many candidates?
- Filter by length before LCS
- Cache tokenized candidates

## 🎯 Next Actions

### Option 1: Integrate (Recommended)
1. Run tests to verify: `python test_lcs.py`
2. Add LCS to `address_parser.py`
3. Test on `public.json`
4. Measure improvement

### Option 2: Implement Edit Distance
1. Create `edit_distance_matcher.py`
2. Implement Ukkonen's algorithm
3. Add token alignment
4. Test with typos

### Option 3: Deep Dive & Optimize
1. Analyze failure cases
2. Tune thresholds per entity type
3. Add length-based filtering
4. Benchmark performance

## 📞 Help

**Stuck?** Review these files:
- Theory: `PHASE4_6_GUIDE.md`
- Complete guide: `PHASE4_COMPLETE.md`
- Learning path: `LEARNING_PATH.md` (partial)

**Want to understand better?**
- Trace the DP table by hand (Exercise 1 in guide)
- Experiment with different thresholds
- Add debug prints in `compute_lcs_length`

---

**Last Updated:** Phase 4 Complete ✅
**Next:** Phase 5 (Edit Distance) or Integration
