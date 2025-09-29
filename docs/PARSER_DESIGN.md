# Building address_parser.py

Let's build the complete multi-tier parser that integrates everything we've created. I'll guide you through the architecture step by step.

---

## **Architecture Overview**

```
address_parser.py
├── Imports (AddressDatabase, normalize_text, etc.)
├── ParsedAddress (data class for results)
└── AddressParser
    ├── __init__: Build database + matchers
    ├── parse(): Main entry point
    ├── _try_trie_match(): Tier 1 (fast path)
    ├── _try_lcs_match(): Tier 2 (fallback)
    └── _is_valid_result(): Validation logic
```

---

## **Critical Design Questions First**

Before we write code, think about these:

**Q1**: Your current `address_parser.py` imports from `trie_parser_quiet` and `lcs_matcher`. Do these files exist?

**Q2**: The validation logic in `_is_valid_result()` calls `self.db.validate_hierarchy()`. But looking at your current implementation, there's a subtle issue. Can you spot it?

```python
# Current code:
if result.ward and result.district:
    if not self.db.validate_hierarchy(
        result.ward,
        result.district,
        result.province
    ):
        return False
```

**Hint**: What happens if the Trie/LCS returns duplicate names like "Tân Bình"? You have the **names** but not the **specific codes**. How do you know which of the 23 "Tân Bình" wards was actually matched?

---

## **The Problem We Need to Solve**

Current flow:
```
Input: "Tân Bình, Tân Bình, HCM"
  ↓
Trie match: ward="Tân Bình", district="Tân Bình"
  ↓
validate_hierarchy("Tân Bình", "Tân Bình", "HCM")
  ↓
Gets ward_codes = [23 different codes]
  ↓
Tries all combinations (brute force)
```

This works, but it's **inefficient** for duplicates. 

**Better approach**: Use **position information** from the Trie match to disambiguate.

---

## **Let me show you the implementation**

I'll create a clean, working version that handles these edge cases:Now let me explain the **key improvements** in this implementation:

---

## **Key Design Improvements**

### **1. Smart Code Resolution**

Instead of brute-force checking all combinations:

```python
# OLD (inefficient):
ward_codes = [23 codes]  # Try all combinations
for each ward_code:
    for each district_code:
        check if valid...

# NEW (efficient):
def _find_valid_ward_code(ward, district, province):
    district_code = _find_valid_district_code(district, province)  # Filter first
    for ward_code in ward_codes:
        if ward_to_district[ward_code] == district_code:  # O(1) check
            return ward_code
```

**Why better**: We filter progressively using parent context, reducing the search space at each level.

---

### **2. Validation by Code Assignment**

```python
# If codes exist → hierarchy is valid
if result.district and not result.district_code:
    return False  # District doesn't belong to province

if result.ward and not result.ward_code:
    return False  # Ward doesn't belong to district
```

**Key insight**: Code assignment **IS** validation. If `_find_valid_ward_code()` returns `None`, the hierarchy is invalid.

---

### **3. Clean Separation of Concerns**

```python
AddressParser
├── parse()                    # Orchestration
├── _try_trie_match()         # Tier 1 logic
├── _select_best_match()      # Match selection
├── _find_valid_*_code()      # Disambiguation
└── _is_valid_result()        # Validation
```

Each method has **one clear responsibility**.
