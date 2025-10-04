# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         VIETNAMESE ADDRESS PARSER                        │
│                                                                          │
│  Input: "Cau Dien, Nam Tu Liem, Ha Noi"                                │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │   TEXT NORMALIZATION     │
                    │  - Lowercase             │
                    │  - Remove diacritics     │
                    │  - Expand abbreviations  │
                    │  - Clean whitespace      │
                    └──────────┬───────────────┘
                               │
                               ▼
                    "cau dien nam tu liem ha noi"
                               │
        ┌──────────────────────┴──────────────────────┐
        │                                              │
        ▼                                              ▼
┌───────────────┐                              ┌─────────────┐
│   TIER 1:     │                              │  DATABASE   │
│   TRIE MATCH  │◄─────────────────────────────│  - Provinces│
│               │                              │  - Districts│
│  Algorithm:   │                              │  - Wards    │
│  O(m) lookup  │                              │             │
│               │                              │  + Aliases  │
│  Coverage:    │                              │  + Codes    │
│  ~80%         │                              └─────────────┘
└───────┬───────┘
        │
        │ Found match?
        ├─── Yes ──────────────────────┐
        │                               │
        │ No                            ▼
        │                        ┌─────────────────┐
        ▼                        │   VALIDATION    │
┌───────────────┐                │  - Check codes  │
│  HANDOFF:     │                │  - Verify       │
│  VALIDATION   │                │    hierarchy    │
│               │                └────────┬────────┘
│  • Validate   │                         │
│    province   │                         │ Valid?
│  • Validate   │                         ├─── Yes ──────┐
│    district   │                         │               │
│  • Validate   │                         No              │
│    ward       │                         │               │
│  • Clear      │                         ▼               │
│    invalid    │                 ┌───────────────┐      │
│    components │                 │   TIER 2:     │      │
│               │                 │   LCS MATCH   │      │
│  See ADR-002  │                 │               │      │
└───────┬───────┘                 │  Algorithm:   │      │
        │                         │  O(n×m) DP    │      │
        │                         │               │      │
        │                         │  Coverage:    │      │
        ▼                         │  ~15%         │      │
┌───────────────┐                 │               │      │
│  CLEANED      │                 │  Hierarchical │      │
│  CONTEXT      │                 │  filtering:   │      │
│               │                 │  ~100 cands   │      │
│  Province: ✓  │                 └───────┬───────┘      │
│  District: ✗  │                         │              │
│  Ward: ✗      │                         │ Found?       │
└───────┬───────┘                         ├─── Yes ──────┤
        │                                 │              │
        │                                 No             │
        ▼                                 │              │
┌───────────────┐                         ▼              │
│   TIER 2:     │                 ┌───────────────┐     │
│   LCS MATCH   │                 │   TIER 3:     │     │
│               │                 │   EDIT DIST   │     │
│  Uses cleaned │                 │               │     │
│  context as   │                 │  Algorithm:   │     │
│  constraint   │                 │  O(k×m)       │     │
│               │                 │  bounded      │     │
│  Searches:    │                 │               │     │
│  - Districts  │                 │  Coverage:    │     │
│    in province│                 │  ~5%          │     │
│  - Wards in   │                 │               │     │
│    district   │                 │  Handles:     │     │
└───────┬───────┘                 │  - Typos      │     │
        │                         │  - OCR errors │     │
        │ Found?                  └───────┬───────┘     │
        ├─── Yes ──────────┐             │             │
        │                   │             │ Found?      │
        No                  │             ├─── Yes ─────┤
        │                   │             │             │
        ▼                   │             No            │
┌───────────────┐          │             │             │
│   FAILED      │          │             ▼             │
│   Return ∅    │          │     ┌───────────────┐    │
└───────────────┘          └────►│  SUCCESS!     │◄───┘
                                  │               │
                                  │  • Province   │
                                  │  • District   │
                                  │  • Ward       │
                                  │  • Codes      │
                                  │  • Confidence │
                                  │  • Method     │
                                  └───────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              CONFIDENCE SCORING                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Tier 1 (Trie):           1.0  (Exact match)                           │
│                                                                          │
│  Tier 2 (LCS):                                                          │
│    With province context: 0.7-0.8  (Constrained search)                │
│    Without context:       0.5-0.6  (Full search)                        │
│                                                                          │
│  Tier 3 (Edit Distance):  0.4-0.6  (Fuzzy match)                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          PERFORMANCE CHARACTERISTICS                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Average Query Time:  4.69 ms                                           │
│  95th Percentile:     9.8 ms                                            │
│  99th Percentile:     42 ms                                             │
│                                                                          │
│  Tier Distribution:                                                     │
│    Tier 1: ████████████████████████████████████████████████  80%        │
│    Tier 2: ███████████                                       15%        │
│    Tier 3: ███                                                5%        │
│                                                                          │
│  Memory Footprint:    ~1.1 MB                                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

```

## Key Design Principles

### 1. Fast Path Optimization
- 80% of queries resolve in Tier 1 (O(m) time)
- Only fall through to slower tiers when necessary
- Early termination on success

### 2. Hierarchical Validation
- Province ⊃ District ⊃ Ward relationship enforced
- Invalid components cleared at handoff boundaries
- Prevents error propagation

### 3. Graceful Degradation
- System handles progressively noisier input
- Each tier specialized for specific error types:
  - Tier 1: Clean input + abbreviations
  - Tier 2: Structural errors (reordering, extra words)
  - Tier 3: Character errors (typos, diacritics)

### 4. Adaptive Confidence
- Confidence reflects information quality
- Higher confidence when using valid context
- Lower confidence for unconstrained searches

---

## Data Flow Example

**Input:** `"123 Ng Van Linh, Cau Dien, NTL, Ha Noi"`

```
1. NORMALIZE
   → "123 ng van linh cau dien ntl ha noi"

2. TIER 1 (Trie)
   - Search: "ha noi" ✓ → Province: "Hà Nội"
   - Search: "ntl" ✗ (not in aliases)
   - Search: "cau dien" ✓ → Ward: "Cầu Diễn"
   Result: P=Hà Nội, D=None, W=Cầu Diễn
   Status: INVALID (ward without district)

3. HANDOFF VALIDATION
   - Province "Hà Nội": Valid ✓
   - District: None
   - Ward "Cầu Diễn": No district to validate against → CLEAR
   Cleaned context: P=Hà Nội, D=None, W=None

4. TIER 2 (LCS)
   - Context: Has province "Hà Nội"
   - Search districts in "Hà Nội": ~60 candidates
   - Best match: "ntl" → "Nam Từ Liêm" (score: 0.75)
   - Search wards in "Nam Từ Liêm": ~80 candidates
   - Best match: "cau dien" → "Cầu Diễn" (score: 0.85)
   Result: P=Hà Nội, D=Nam Từ Liêm, W=Cầu Diễn
   Confidence: 0.8 (had province context)

5. OUTPUT
   {
     "province": "Hà Nội",
     "district": "Nam Từ Liêm",
     "ward": "Cầu Diễn",
     "confidence": 0.8,
     "method": "lcs",
     "valid": true
   }
```

---

## See Also

- [ADR-001: Three-Tier Architecture](./ADR-001-Three-Tier-Architecture.md)
- [ADR-002: Tier Handoff Logic](./ADR-002-Tier-Handoff-Logic.md)
- [Algorithm Analysis](./Algorithm-Analysis.md)
