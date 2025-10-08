"""
Alias Generator for Vietnamese Address Entities

Generates normalized variants of entity names for matching:
- Normalized form: "ho chi minh"
- No-space: "hochiminh"
- Initials: "hcm"
- Dotted initials: "h.c.m"
- First + last: "ho minh"
- First initial + rest: "h. chi minh"

REFACTORED: Now uses normalizer_v2 with aggressive mode for consistency
"""

from typing import List, Set
from text_normalizer import TextNormalizer


# ========================================================================
# ALIAS GENERATION
# ========================================================================

def generate_aliases(
    original_name: str,
    normalizer: TextNormalizer
) -> Set[str]:
    """
    Generate all matching variants for an entity name
    
    DESIGN DECISION: Uses AGGRESSIVE normalization mode
    
    Why aggressive?
    - Removes ALL punctuation (dots, commas, slashes)
    - Produces clean tokens for alias generation
    - Ensures consistency with parser (which also uses aggressive)
    - Example: "TP.HCM" → "tp hcm" (not "tp.hcm")
    
    Args:
        original_name: Original entity name from database (e.g., "Hồ Chí Minh")
        normalizer: TextNormalizer instance (from normalizer_v2)
    
    Returns:
        Set of normalized alias strings (deduplicated)
    
    Algorithm:
        1. Normalize with AGGRESSIVE mode (strips punctuation → spaces)
        2. Generate 6 types of variants from clean tokens
        3. Deduplicate using set
    
    Examples:
        "Hồ Chí Minh" → {
            "ho chi minh",      # full normalized
            "hochiminh",        # no spaces
            "hcm",              # initials
            "h.c.m",            # dotted initials
            "ho minh",          # first + last (3+ tokens)
            "h. chi minh",      # first initial + rest (dotted)
            "h chi minh"        # first initial + rest (no dot)
        }
        
        "Thành phố Hồ Chí Minh" → {
            "thanh pho ho chi minh",  # full (no prefix stripping here!)
            "thanhphohochiminh",
            "tphcm",
            "t.p.h.c.m",
            "thanh minh",             # first + last
            "t. pho ho chi minh"
        }
        
        NOTE: Admin prefix stripping (if needed) should happen BEFORE 
        calling this function. This function just generates aliases from 
        whatever normalized text it receives.
        
        "Quận 1" → {
            "quan 1",           # full normalized
            "quan1",            # no space
            "q1",               # initials
            "q.1"               # dotted
        }
        
        "Phường 1" → {
            "phuong 1",
            "phuong1", 
            "p1",
            "p.1"
        }
    
    Time: O(n) where n = len(original_name)
    """
    aliases = set()
    
    # Step 1: Normalize with AGGRESSIVE mode
    # This removes diacritics, lowercases, and converts punctuation → spaces
    base_name = normalizer.normalize(original_name, aggressive=True)
    
    # Step 2: Tokenize (aggressive mode already gives us clean tokens)
    tokens = base_name.split()
    num_tokens = len(tokens)
    
    # Edge case: empty after normalization
    if num_tokens == 0:
        return aliases
    
    # --- Variant 1: Normalized full form ---
    aliases.add(base_name)
    
    # --- Variant 2: No-space compact ---
    aliases.add(''.join(tokens))
    
    # For single-token names, stop here (remaining variants are redundant)
    if num_tokens == 1:
        return aliases
    
    # --- Variant 3: Initials acronym ---
    initials = ''.join(t[0] for t in tokens)
    aliases.add(initials)
    
    # --- Variant 4: Dotted initials ---
    dotted = '.'.join(t[0] for t in tokens)
    aliases.add(dotted)
    
    # --- Variant 5: First + last token ---
    # Only meaningful for 3+ tokens
    if num_tokens >= 3:
        first_last = f"{tokens[0]} {tokens[-1]}"
        aliases.add(first_last)
    
    # --- Variant 6: First initial + rest (with dot) ---
    first_initial_rest = f"{tokens[0][0]}. {' '.join(tokens[1:])}"
    aliases.add(first_initial_rest)

    # --- Variant 7: First initial + rest (no dot) ---
    first_initial_rest_no_dot = f"{tokens[0][0]} {' '.join(tokens[1:])}"
    aliases.add(first_initial_rest_no_dot)
    
    return aliases


# ========================================================================
# BATCH PROCESSING
# ========================================================================

def generate_aliases_batch(
    entity_names: List[str],
    normalizer: TextNormalizer
) -> List[tuple]:
    """
    Generate aliases for a batch of entities
    
    Args:
        entity_names: List of original entity names
        normalizer: TextNormalizer instance
    
    Returns:
        List of (original_name, set_of_aliases) tuples
    
    Time: O(n × m) where n = number of entities, m = avg name length
    """
    results = []
    
    for name in entity_names:
        aliases = generate_aliases(name, normalizer)
        results.append((name, aliases))
    
    return results


# ========================================================================
# TESTING
# ========================================================================

if __name__ == "__main__":
    from text_normalizer import TextNormalizer
    
    # Create normalizer (uses Vietnamese defaults)
    normalizer = TextNormalizer()
    
    print("="*70)
    print("ALIAS GENERATOR TESTS (REFACTORED VERSION)")
    print("="*70)
    
    # First, test normalization behavior
    print("\n" + "="*70)
    print("STEP 1: Testing aggressive normalization")
    print("="*70)
    
    test_norm = [
        "Hồ Chí Minh",
        "Thành phố Hồ Chí Minh",
        "TP.HCM",
        "Quận Bình Thạnh",
        "Q.1",
        "Phường 1",
        "P.Bến Nghé"
    ]
    
    for name in test_norm:
        normalized = normalizer.normalize(name, aggressive=True)
        print(f"  '{name:30}' → '{normalized}'")
    
    # Now test alias generation
    print("\n" + "="*70)
    print("STEP 2: Alias generation from aggressive-normalized base")
    print("="*70)
    
    test_cases = [
        # Province names
        "Hồ Chí Minh",
        "Thành phố Hồ Chí Minh",
        "Hà Nội",
        "Đà Nẵng",
        "Cần Thơ",
        
        # Abbreviated forms (test how aggressive handles these)
        "TP.HCM",
        "TP HCM",
        
        # District names
        "Quận Bình Thạnh",
        "Quận 1",
        "Q.1",
        "Huyện Củ Chi",
        
        # Ward names
        "Phường 1",
        "P.1",
        "Phường Bến Nghé",
        "Xã Tân Thông Hội",
        
        # Edge cases
        "Thị Xã Thủ Dầu Một",
        "Thành phố Thủ Đức",
    ]
    
    for name in test_cases:
        aliases = generate_aliases(name, normalizer)
        print(f"\n'{name}':")
        for alias in sorted(aliases):
            print(f"  - '{alias}'")
    
    print("\n" + "="*70)
    print("KEY OBSERVATIONS:")
    print("="*70)
    print("""
1. ✓ All aliases use aggressive normalization (no dots in base form)
2. ✓ "TP.HCM" → "tp hcm" → generates {"tp hcm", "tphcm", "th", ...}
3. ✓ "Hồ Chí Minh" → "ho chi minh" → generates {"hcm", "hochiminh", ...}
4. ✓ Consistent tokenization (spaces separate words)
5. ✓ Parser must also use aggressive mode to match these aliases!

IMPORTANT: If the database needs to strip admin prefixes (like "thanh pho"),
that should happen BEFORE calling generate_aliases(). This function just
creates variants of whatever normalized text it receives.
    """)
