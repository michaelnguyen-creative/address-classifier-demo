# Planning Phase 1: Smarter Normalization

Let me first address your Socratic question, then design a **principled, generalizable solution**.

---

## 🤔 Answer to "Why did removing prefixes backfire?"

The original normalization tried to solve **variation tolerance** ("P.1" vs "P 1" vs "Phường 1") by stripping everything to lowest common denominator. But this created a worse problem: **type ambiguity**.

**The core trade-off:**
- **Too aggressive normalization** → loses signal (current problem)
- **No normalization** → can't match variants
- **Smart normalization** → preserves type info while canonicalizing format

---

## 🎯 Design Principles for Phase 1

Before coding, let's establish principles to avoid hardcoding:

### Principle 1: **Separation of Concerns**
```
Raw Input → [Type Extraction] → [Canonicalization] → [Tokenization]
                     ↓
              Type Hints (metadata)
```

**Why?** Keep type information *separate* from normalized text. This allows:
- Downstream modules (Trie/LCS) to use hints **without** re-parsing
- Easy testing of each stage independently

### Principle 2: **Data-Driven Type Detection**
Instead of hardcoding "P., Q., TT", define a **configuration schema**:

```python
# Config: maps patterns → entity types
TYPE_MARKERS = {
    'ward': ['phường', 'p.', 'p', 'phư', 'f'],
    'district': ['quận', 'q.', 'q', 'huyện', 'h.', 'tx', 'tp'],
    'province': ['tỉnh', 'thành phố', 'tp.'],
    'town': ['thị trấn', 'tt.', 'tt'],
    'commune': ['xã', 'x.', 'x']
}
```

**Benefits:**
- Add new markers without changing code
- Handle regional variations (e.g., Northern vs Southern dialects)
- Easy to extend for other countries/languages

### Principle 3: **Preserve Position Context**
Don't just extract types—remember **where** they appeared:

```python
# Instead of: {"ward": "1"}
# Store: {"ward": {"value": "1", "position": 12, "original": "P.1"}}
```

**Why?** Position helps resolve ambiguity later (wards usually come before districts).

---

## 📐 High-Level Algorithm Design

Here's the conceptual flow:

```
Input: "357/28, Ng-T- Thuật, P.1, Q.3, TP.Hồ Chí Minh"

Step 1: IDENTIFY type markers (rule-based)
  ↓
  Markers found: [
    {type: 'ward', value: '1', marker: 'P.', span: (22,25)},
    {type: 'district', value: '3', marker: 'Q.', span: (27,30)},
    {type: 'province', value: 'Hồ Chí Minh', marker: 'TP.', span: (32,48)}
  ]

Step 2: EXTRACT & REMOVE markers from text
  ↓
  "357/28, Ng-T- Thuật, 1, 3, Hồ Chí Minh"

Step 3: CANONICALIZE remaining text
  ↓
  "357 28 ng t thuat 1 3 ho chi minh"

Step 4: RETURN normalized text + metadata
  ↓
  (
    text: "357 28 ng t thuat 1 3 ho chi minh",
    hints: {
      'ward': {'value': '1', 'confidence': 0.95},
      'district': {'value': '3', 'confidence': 0.95},
      'province': {'value': 'ho chi minh', 'confidence': 0.95}
    }
  )
```

---

## 🧩 Key Algorithmic Choices

Let me highlight three critical decisions and their trade-offs:

### Choice 1: Pattern Matching Strategy

| Approach | Pros | Cons | When to use |
|----------|------|------|-------------|
| **Regex** | Fast, explicit control | Brittle with typos | Clean input data |
| **Fuzzy matching** | Handles typos | Slower, false positives | Noisy user input |
| **Hybrid** | Best of both | More complex | Production (our case) |

**Recommendation:** Start with **regex for exact markers**, fall back to fuzzy for malformed text.

---

### Choice 2: Marker Extraction Order

**Question for you:** Should we extract markers in a specific order (e.g., province → district → ward)?

<details>
<summary>💡 Hint (click to reveal)</summary>

**Answer:** Yes! Extract in **decreasing granularity** order:
1. Province markers (longest, most distinctive)
2. District markers
3. Ward markers (shortest, most ambiguous)

**Why?** Prevents "Quận 3" from being mis-split if "Q" accidentally matches part of "Quảng".
</details>

---

### Choice 3: Confidence Scoring

Each extracted hint should have a **confidence score**:

```python
confidence = f(marker_explicitness, context_support)

Examples:
"P.1"     → 0.95  # Explicit marker
"Phường 1" → 0.90  # Full word
"1"       → 0.30  # Ambiguous (could be house number)
```

**Why?** Later modules can weight hints appropriately.

---

## 🏗️ Proposed Implementation Structure

```python
class SmartNormalizer:
    def __init__(self, type_marker_config: dict):
        self.markers = self._compile_patterns(type_marker_config)
    
    def normalize(self, raw_input: str) -> NormalizedAddress:
        """
        Returns: NormalizedAddress(
            canonical_text: str,
            type_hints: dict[str, TypeHint],
            debug_info: dict
        )
        """
        # 1. Detect markers
        markers = self._extract_markers(raw_input)
        
        # 2. Extract values & remove markers
        cleaned_text, hints = self._process_markers(raw_input, markers)
        
        # 3. Canonicalize remaining text
        canonical = self._canonicalize(cleaned_text)
        
        return NormalizedAddress(canonical, hints)
    
    def _extract_markers(self, text: str) -> list[Marker]:
        """Find all type markers with positions"""
        pass
    
    def _process_markers(self, text: str, markers: list) -> tuple[str, dict]:
        """Remove markers, extract values, build hints"""
        pass
    
    def _canonicalize(self, text: str) -> str:
        """Standard normalization: lowercase, remove punctuation, etc."""
        pass
```

---

## ✅ Validation Strategy

Before implementing, let's define **success criteria**:

1. **Coverage:** Can handle 95%+ of marker variations in your dataset
2. **Precision:** Extracted hints are correct 90%+ of the time
3. **Graceful degradation:** Missing markers shouldn't break normalization
4. **Debuggability:** Can trace why each hint was extracted

---

## 🎯 Your Turn: Design Decisions

Before I write code, answer these to ensure we're aligned:

### Q1: Ambiguity Resolution
```
Input: "1, Tân Bình, Hồ Chí Minh"
```
The "1" could be:
- Ward number (if context supports)
- House number (if no marker present)

**How should we resolve this?** 
- A) Require explicit marker (strict)
- B) Use position heuristics (ward usually comes first)
- C) Both A and B with confidence weighting

---

### Q2: Normalization Depth
```
Input: "Phường Tân Bình"
```
Should we:
- A) Keep "phuong tan binh" (preserve marker in text)
- B) Extract to hint, output "tan binh" (cleaner)
- C) Configurable based on downstream module needs

**Which aligns better with your Trie/LCS modules?**

---

### Q3: Fuzzy Marker Matching
```
Input: "Ph.1" (typo: should be "P.1")
```
Should we:
- A) Match "Ph." → ward (lenient)
- B) Require exact "P." (strict)
- C) Fuzzy match with confidence penalty

