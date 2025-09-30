# ========================================================================
# NAME VARIANT GENERATOR
# ========================================================================

def generate_name_variants(name: str) -> List[str]:
    """
    Generate alias variants for province/district/ward names.
    
    Covers:
      - Case folding + diacritic stripping
      - Compact forms (no spaces)
      - Acronyms from initials
      - Dotted acronyms (H.C.M.)
      - First word shortcut (Bình Thạnh → B.Thạnh, B Thạnh, B. Thạnh)
    """
    variants = set()

    # Step 1: Normalize
    base = normalize_text_simple(name)        # e.g. "binh thanh"
    tokens = base.split()

    if not tokens:
        return []

    # Step 2: Add basic variants
    variants.add(base)
    variants.add(''.join(tokens))             # "binhthanh"

    # Step 3: Initials abbreviation
    initials = ''.join(t[0] for t in tokens)
    variants.add(initials)                    # "bt"
    variants.add(initials.upper())            # "BT"

    dotted = '.'.join(t[0] for t in tokens)
    variants.add(dotted)                      # "b.t"
    variants.add(dotted.upper())              # "B.T"

    # Step 4: First word shortcut (only if multi-word)
    if len(tokens) > 1:
        first_initial = tokens[0][0]
        rest = ' '.join(tokens[1:])
        
        # Variants like "B Thanh", "B. Thanh", "B.Thanh"
        variants.add(f"{first_initial} {rest}")
        variants.add(f"{first_initial}.{rest}")
        variants.add(f"{first_initial}. {rest}")
        
        # Uppercase versions
        variants.add(f"{first_initial.upper()} {rest}")
        variants.add(f"{first_initial.upper()}.{rest}")
        variants.add(f"{first_initial.upper()}. {rest}")

    return sorted(variants)


# ========================================================================
# EXTENSION: BUILD VARIANTS FOR ALL ADMIN UNITS
# ========================================================================

def build_admin_name_variants(units: List[Dict], key: str = "Name") -> Dict[str, List[str]]:
    """
    Build alias map for a list of provinces/districts/wards.
    
    Args:
        units: list of dicts with at least a "Name" field
        key:   which field to use (default "Name")
    
    Returns:
        dict: { canonical_name → [variants...] }
    """
    alias_map = {}
    for u in units:
        canonical = normalize_text_simple(u[key])
        alias_map[canonical] = generate_name_variants(u[key])
    return alias_map
