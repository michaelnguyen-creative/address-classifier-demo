"""
Alias Generator for Vietnamese Address Entities

Generates normalized variants of entity names for matching:
- Normalized form: "ho chi minh"
- No-space: "hochiminh"
- Initials: "hcm"
- Dotted initials: "h.c.m"
- First + last: "ho minh"
- First initial + rest: "h. chi minh"
"""

from typing import List, Set
from normalizer import normalize_text, NormalizationConfig


# ========================================================================
# ALIAS GENERATION
# ========================================================================

def generate_aliases(
    original_name: str,
    config: NormalizationConfig
) -> Set[str]:
    """
    Generate all matching variants for an entity name
    
    Args:
        original_name: Original entity name from database (e.g., "Hồ Chí Minh")
        config: NormalizationConfig for proper normalization
    
    Returns:
        Set of normalized alias strings (deduplicated)
    
    Algorithm:
        1. Normalize the name (normalize_text already strips admin prefixes!)
        2. Generate 6 types of variants from the normalized base
        3. Deduplicate using set
    
    Examples:
        "Thành phố Hồ Chí Minh" → {
            "ho chi minh",      # normalized (admin prefix already stripped)
            "hochiminh",        # no spaces
            "hcm",              # initials
            "h.c.m",            # dotted initials
            "ho minh",          # first + last
            "h. chi minh"       # first initial + rest
        }
        
        "Quận Bình Thạnh" → {
            "binh thanh",       # normalized
            "binhthanh",        # no spaces
            "bt",               # initials
            "b.t",              # dotted initials
            "b. thanh"          # first initial + rest
        }
        
        "Phường 1" → {
            "1"                 # just the number (single token)
        }
    
    Time: O(n) where n = len(original_name)
    """
    aliases = set()
    
    # Step 1: Normalize (this already strips admin prefixes!)
    base_name = normalize_text(original_name, config)
    
    # Step 2: Tokenize
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
    
    # --- Variant 6: First initial + rest ---
    first_initial_rest = f"{tokens[0][0]}. {' '.join(tokens[1:])}"
    aliases.add(first_initial_rest)
    
    return aliases


# ========================================================================
# BATCH PROCESSING
# ========================================================================

def generate_aliases_batch(
    entity_names: List[str],
    config: NormalizationConfig
) -> List[tuple]:
    """
    Generate aliases for a batch of entities
    
    Args:
        entity_names: List of original entity names
        config: NormalizationConfig instance
    
    Returns:
        List of (original_name, set_of_aliases) tuples
    
    Time: O(n × m) where n = number of entities, m = avg name length
    """
    results = []
    
    for name in entity_names:
        aliases = generate_aliases(name, config)
        results.append((name, aliases))
    
    return results


# ========================================================================
# TESTING
# ========================================================================

if __name__ == "__main__":
    from normalizer import NormalizationConfig
    
    # Mock config for testing
    sample_provinces = [{'Name': 'Hồ Chí Minh'}, {'Name': 'Hà Nội'}]
    config = NormalizationConfig(sample_provinces)
    
    print("="*70)
    print("ALIAS GENERATOR TESTS")
    print("="*70)
    
    # First, let's debug normalize_text to see what it produces
    print("\nDEBUG: Testing normalize_text directly:")
    test_norm = [
        "Hồ Chí Minh",
        "Thành phố Hồ Chí Minh",
        "Quận Bình Thạnh",
        "Phường 1",
    ]
    for name in test_norm:
        normalized = normalize_text(name, config)
        print(f"  '{name}' → '{normalized}'")
    
    print("\n" + "="*70)
    print("ALIAS GENERATION:")
    print("="*70)
    
    test_cases = [
        # Province names
        "Hồ Chí Minh",
        "Thành phố Hồ Chí Minh",
        "Hà Nội",
        "Đà Nẵng",
        "Cần Thơ",
        "Huế",
        "Thừa Thiên Huế",
        
        # District names
        "Quận Bình Thạnh",
        "Quận 1",
        "Quận 10",
        "Huyện Nam Từ Liêm",
        "Huyện Củ Chi",
        "Huyện Nhà Bè",
        
        # Ward names
        "Phường 1",
        "Phường Bến Nghé",
        "Phường Đa Kao",
        "Xã Tân Thông Hội",
        "Thị trấn Tân Phú",
        
        # Edge cases
        "Thị Xã Thủ Dầu Một",  # multi-word with admin prefix
        "Thành phố Thủ Đức",   # Đ character
        "Phường Thảo Điền",    # Đ in middle
    ]
    
    for name in test_cases:
        aliases = generate_aliases(name, config)
        print(f"\n'{name}':")
        for alias in sorted(aliases):
            print(f"  - {alias}")
