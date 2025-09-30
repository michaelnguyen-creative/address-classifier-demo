# Alias Generation Strategy for Vietnamese Addresses

Let me break down a robust **alias generation system** that balances coverage with precision.

---

## **Core Principle: What Are We Capturing?**

We want to handle **how real users write entity names in the wild**, not just database canonical forms:

- Accent variations: `"Hồ Chí Minh"` vs `"Ho Chi Minh"`
- Spacing: `"Ho Chi Minh"` vs `"HoChiMinh"` vs `"ho chi minh"`
- Abbreviations: `"HCM"`, `"H.C.M"`, `"H. Chi Minh"`
- Partial forms: `"Ho Minh"` (first + last token)

**Key constraint**: Only generate variants of the **base entity name** itself (no administrative prefixes).

---

## **Step-by-Step Design**

### **Phase 1: Input Preprocessing**

Before generating aliases, we need the **clean base name**:

```
Input: "Thành phố Hồ Chí Minh"
↓
Strip admin indicators: ["thành phố", "tỉnh", "huyện", "quận", "phường", "xã", "thị xã", "thị trấn"]
↓
Extract: "Hồ Chí Minh"
↓
Normalize: "ho chi minh" (lowercase, no accents, clean spaces)
```

**Why this order?**
- Strip prefixes **first** so we don't generate acronyms like "TPHCM"
- Normalize **after** to preserve original for canonical storage

---

### **Phase 2: Alias Generation Rules**

Here's a **layered generation strategy** from most specific to most abbreviated:

```python
def generate_aliases(base_name: str) -> List[str]:
    """
    Generate all practical variants of a base entity name
    
    Input: "Hồ Chí Minh" (original with accents)
    Output: [
        "Hồ Chí Minh",      # (1) Canonical original
        "ho chi minh",      # (2) Normalized
        "hochiminh",        # (3) No spaces
        "hcm",              # (4) Initials
        "h.c.m",            # (5) Dotted initials
        "ho minh",          # (6) First + last token
        "h. chi minh"       # (7) First initial + rest
    ]
    """
```

Let me explain each variant type:

---

#### **(1) Canonical Original**
Store the **exact database form** for display purposes.

```
"Hồ Chí Minh" → "Hồ Chí Minh"
"Thủ Đức" → "Thủ Đức"
```

**Why?** User sees the official name in results.

---

#### **(2) Normalized Full Form**
Lowercase + no accents + clean spacing.

```
"Hồ Chí Minh" → "ho chi minh"
"Bình Thạnh" → "binh thanh"
"Thủ Đức" → "thu duc"
```

**Coverage:** Handles accent-free typing (most common variation).

---

#### **(3) No-Space Compact**
Remove all whitespace.

```
"ho chi minh" → "hochiminh"
"binh thanh" → "binhthanh"
```

**Coverage:** Social media style (`"liveinhanoi"`, `"gotothuducnow"`).

---

#### **(4) Initials Acronym**
First letter of each token, no dots.

```
"ho chi minh" → "hcm"
"binh thanh" → "bt"
"nam tu liem" → "ntl"
```

**Coverage:** Common abbreviations in addresses (`"HCM"`, `"NT"`, `"BThanh"`).

**Edge case:** Single-token names like `"Huế"` → just `"hue"` (skip this variant).

---

#### **(5) Dotted Initials**
First letter of each token with dots between.

```
"ho chi minh" → "h.c.m"
"binh thanh" → "b.t"
```

**Coverage:** Formal abbreviations in documents.

---

#### **(6) First + Last Token**
Skip middle tokens, keep endpoints.

```
"ho chi minh" → "ho minh"
"thua thien hue" → "thua hue"
```

**Why?** Users often drop filler words:
- `"Thừa Thiên Huế"` → spoken as `"Huế"` or `"Thừa Huế"`
- `"Hồ Chí Minh"` → sometimes `"Hồ Minh"`

**Skip if:** Less than 3 tokens (redundant with full form).

---

#### **(7) First Initial + Rest**
Abbreviate first token, keep rest full.

```
"ho chi minh" → "h. chi minh"
"binh thanh" → "b. thanh"
```

**Coverage:** Casual writing style (`"B. Thanh"`, `"H. Mai"`).

---

## **Implementation Considerations**

### **Question 1: Should we store ALL these in the Trie?**

**Yes**, but with **deduplication**:

```python
aliases = set()  # Use set to auto-deduplicate

# Generate all variants
aliases.add(original)           # "Hồ Chí Minh"
aliases.add(normalized)         # "ho chi minh"
aliases.add(no_space)          # "hochiminh"
aliases.add(initials)          # "hcm"
# ... etc

# Insert each unique variant into Trie
for alias in aliases:
    trie.insert(alias, original_name)
```

**Why deduplicate?**
- Single-token names: `"Huế"` normalized = no-space form = first+last form
- Avoid redundant Trie entries

---

### **Question 2: What about multi-token edge cases?**

Let's walk through some examples:

| Original | Tokens | Generated Aliases |
|----------|--------|-------------------|
| `"Huế"` | 1 | `"Huế"`, `"hue"` (skip initials, first+last) |
| `"Hà Nội"` | 2 | `"Hà Nội"`, `"ha noi"`, `"hanoi"`, `"hn"`, `"h.n"`, `"h. noi"` |
| `"Hồ Chí Minh"` | 3 | All 7 variants |
| `"Thừa Thiên Huế"` | 3 | All 7 variants including `"thua hue"` |

**Rule of thumb:**
- ≤ 1 token: Skip initials, first+last, first+rest
- 2 tokens: Skip first+last (redundant)
- ≥ 3 tokens: Generate all variants

---

### **Question 3: Should we normalize the canonical form?**

**No!** Store both:

```python
class Trie:
    def insert(self, normalized_key: str, original_value: str):
        """
        normalized_key: Used for matching ("ho chi minh")
        original_value: Returned to user ("Hồ Chí Minh")
        """
```

**Why?**
- Trie matching uses normalized forms (accent-free, lowercase)
- Results display original forms (proper capitalization, accents)

---

## **Complexity Analysis**

Let's analyze the cost of this approach:

### **Generation Cost**
For an entity with `k` tokens:
- Number of aliases: **~7 variants** (constant)
- Generation time: **O(k)** (split tokens, build strings)

**Total preprocessing:** `O(n × k)` where `n` = number of entities

For your dataset:
- 63 provinces × ~2 tokens = 126 token operations
- 700 districts × ~2 tokens = 1,400 operations
- 11,000 wards × ~2 tokens = 22,000 operations

**Total: ~23,500 operations** → negligible (< 100ms).

---

### **Trie Storage Cost**
Each entity generates ~7 aliases → **7× storage**?

**No!** Trie has **prefix compression**:

```
"ho chi minh" ─┐
                ├→ "hochiminh"    (shares "ho chi minh" prefix)
                └→ "hcm"          (separate branch)
```

**Effective space:** `O(unique_characters)`, not `O(aliases × length)`.

For 11,000 wards × 7 aliases = 77,000 strings, but with shared prefixes:
- Estimated storage: **~2-3MB** (very manageable)

---

### **Search Cost**
Same as before: **O(m)** per lookup, where `m` = query length.

The 7× alias multiplier **doesn't affect search time** because we still traverse one path in the Trie.

---

## **Practical Example**

Let's trace through `"Bình Thạnh"`:

```python
# Input from database
original = "Bình Thạnh"

# Step 1: Normalize
normalized = normalize_text(original)  # "binh thanh"
tokens = normalized.split()            # ["binh", "thanh"]

# Step 2: Generate aliases
aliases = {
    original,              # "Bình Thạnh"
    normalized,            # "binh thanh"
    "".join(tokens),       # "binhthanh"
    "".join(t[0] for t in tokens),  # "bt"
    ".".join(t[0] for t in tokens), # "b.t"
    f"{tokens[0]} {tokens[-1]}",    # "binh thanh" (same as normalized for 2 tokens)
    f"{tokens[0][0]}. {' '.join(tokens[1:])}"  # "b. thanh"
}

# Step 3: Deduplicate
aliases = set(aliases)  # Removes duplicate "binh thanh"

# Step 4: Insert into Trie
for alias in aliases:
    trie.insert(alias, original)  # All point to "Bình Thạnh"
```

**Result:** User types any of these → finds `"Bình Thạnh"`:
- `"binh thanh"` ✓
- `"bt"` ✓
- `"b.t"` ✓
- `"binhthanh"` ✓
- `"b. thanh"` ✓

---

## **Reflection Questions**

Before we proceed to implementation:

1. **Should we handle typos?** (e.g., `"Bih Thanh"` with missing 'n')
   - If yes → need edit distance (Tier 3)
   - If no → aliases cover ~95% of cases

2. **What about partial matches?** (e.g., just `"Thanh"` in `"Bình Thạnh"`)
   - Should `search_in_text` match substrings?
   - Or require full alias match?

3. **Do we need case-insensitive variants?** (e.g., `"HCM"` vs `"hcm"`)
   - Current design: normalize query before Trie search
   - Alternative: store both cased variants
