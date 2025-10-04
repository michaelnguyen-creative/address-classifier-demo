"""
Three-Layer Architecture - Complete Integration Example

This demonstrates how Layer 1 (normalization), Layer 2 (admin prefix handling),
and Layer 3 (alias generation) work together in the complete pipeline.

ARCHITECTURE:
    Layer 1: Generic normalization (normalizer_v2.py)
    Layer 2: Admin prefix expansion (admin_prefix_handler_v2.py)
    Layer 3: Alias generation (alias_generator.py)
"""

from archive.normalizer_v2 import normalize_text
from admin_prefix_handler import AdminPrefixHandler
from alias_generator import generate_aliases
from typing import List, Set, Tuple


# ========================================================================
# COMPLETE PIPELINE
# ========================================================================

class AddressNormalizationPipeline:
    """
    Complete 3-layer normalization pipeline
    
    Responsibilities:
        1. Coordinate all three layers
        2. Handle edge cases
        3. Provide clean API for address processing
    
    Usage:
        pipeline = AddressNormalizationPipeline(data_dir="../data")
        aliases = pipeline.process_entity("TP.HCM", level='province')
        # → ["ho chi minh", "hcm", "hochiminh", ...]
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize pipeline with data directory
        
        Args:
            data_dir: Path to data files (provinces.txt, districts.txt, ward.txt)
        """
        # Layer 2: Admin prefix handler
        self.prefix_handler = AdminPrefixHandler(data_dir) if data_dir else None
    
    def process_entity(
        self, 
        entity_name: str, 
        level: str = 'auto'
    ) -> Set[str]:
        """
        Process a single entity through all 3 layers
        
        Algorithm:
            1. Layer 1: Generic normalization
            2. Layer 2: Admin prefix expansion
            3. Layer 3: Alias generation
        
        Args:
            entity_name: Raw entity name (e.g., "TP.HCM", "Quận 1")
            level: 'province', 'district', 'ward', or 'auto'
        
        Returns:
            Set of all searchable aliases
        
        Examples:
            process_entity("TP.HCM", "province")
            → {"ho chi minh", "hcm", "hochiminh", "h.c.m", ...}
            
            process_entity("Q.1", "district")
            → {"1"}
            
            process_entity("P.Bến Nghé", "ward")
            → {"ben nghe", "bennnghe", "bn", "b.n", ...}
        """
        # LAYER 1: Generic normalization
        normalized = normalize_text(entity_name)
        
        # LAYER 2: Admin prefix expansion
        if self.prefix_handler:
            expanded = self.prefix_handler.expand(normalized, level)
        else:
            # Fallback: just use normalized text
            expanded = normalized
        
        # LAYER 3: Alias generation
        # Note: alias_generator expects NormalizationConfig, but we can
        # create a simple mock or use it directly with the expanded name
        from archive.normalizer import NormalizationConfig
        config = NormalizationConfig(provinces=[])  # Empty config for now
        aliases = generate_aliases(expanded, config)
        
        return aliases
    
    def process_address(
        self, 
        address: str
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Process a complete address and extract entities
        
        Args:
            address: Full address string (e.g., "P.1, Q.3, TP.HCM")
        
        Returns:
            Tuple of (province_aliases, district_aliases, ward_aliases)
        
        Example:
            process_address("P.1, Q.3, TP.HCM")
            → (
                ["ho chi minh", "hcm", "hochiminh", ...],
                ["3"],
                ["1"]
              )
        """
        # LAYER 1: Normalize entire address
        normalized = normalize_text(address)
        
        # Split by commas
        parts = [p.strip() for p in normalized.split(',')]
        
        # LAYER 2: Detect and expand each part
        province_aliases = set()
        district_aliases = set()
        ward_aliases = set()
        
        for part in parts:
            if not part:
                continue
            
            # Try to detect what type of entity this is
            if self.prefix_handler:
                # Check which level this part belongs to
                if any(prefix in part for prefix in ['tp.', 'tp', 'thanh pho', 'tinh']):
                    aliases = self.process_entity(part, 'province')
                    province_aliases.update(aliases)
                elif any(prefix in part for prefix in ['q.', 'q', 'quan', 'h.', 'h', 'huyen']):
                    aliases = self.process_entity(part, 'district')
                    district_aliases.update(aliases)
                elif any(prefix in part for prefix in ['p.', 'p', 'phuong', 'x.', 'x', 'xa']):
                    aliases = self.process_entity(part, 'ward')
                    ward_aliases.update(aliases)
                else:
                    # Unknown, try auto-detect
                    aliases = self.process_entity(part, 'auto')
                    # Just add to all (will be filtered later)
                    province_aliases.update(aliases)
        
        return (
            list(province_aliases),
            list(district_aliases),
            list(ward_aliases)
        )


# ========================================================================
# TESTING & EXAMPLES
# ========================================================================

if __name__ == "__main__":
    print("="*70)
    print("THREE-LAYER ARCHITECTURE - INTEGRATION TEST")
    print("="*70)
    
    # Initialize pipeline
    pipeline = AddressNormalizationPipeline(data_dir="../data")
    
    # Test individual entities
    print("\n🧪 SINGLE ENTITY PROCESSING:")
    print("-" * 70)
    
    test_entities = [
        ("TP.HCM", "province", "Province with prefix"),
        ("Hồ Chí Minh", "province", "Province without prefix"),
        ("Q.1", "district", "District number"),
        ("Quận Tân Bình", "district", "District with name"),
        ("P.Bến Nghé", "ward", "Ward with prefix"),
        ("Phường 12", "ward", "Numbered ward"),
    ]
    
    for entity, level, description in test_entities:
        print(f"\nInput: '{entity}' (level={level})")
        print(f"Description: {description}")
        
        # Show step-by-step
        print(f"\n  Layer 1 (normalize_text):")
        normalized = normalize_text(entity)
        print(f"    '{entity}' → '{normalized}'")
        
        print(f"\n  Layer 2 (expand_admin_prefixes):")
        if pipeline.prefix_handler:
            expanded = pipeline.prefix_handler.expand(normalized, level)
            print(f"    '{normalized}' → '{expanded}'")
        else:
            expanded = normalized
            print(f"    (No prefix handler, using normalized)")
        
        print(f"\n  Layer 3 (generate_aliases):")
        aliases = pipeline.process_entity(entity, level)
        print(f"    Generated {len(aliases)} aliases:")
        for alias in sorted(list(aliases)[:10]):  # Show first 10
            print(f"      - {alias}")
        if len(aliases) > 10:
            print(f"      ... and {len(aliases) - 10} more")
    
    # Test complete addresses
    print("\n" + "="*70)
    print("🏢 COMPLETE ADDRESS PROCESSING:")
    print("-" * 70)
    
    test_addresses = [
        "TP.HCM, Quận 1, Phường Bến Nghé",
        "357/28 Lê Hồng Phong, P.1, Q.3, TP.HCM",
        "Thị Trấn Tân Bình, Huyện Củ Chi, Hồ Chí Minh",
    ]
    
    for address in test_addresses:
        print(f"\n📍 Input: {address}")
        
        # Layer 1
        normalized = normalize_text(address)
        print(f"\n  Layer 1 Output: {normalized}")
        
        # Complete processing
        province, district, ward = pipeline.process_address(address)
        
        print(f"\n  Extracted Entities:")
        if province:
            print(f"    Province: {province[:3]}")  # Show first 3 aliases
        if district:
            print(f"    District: {district[:3]}")
        if ward:
            print(f"    Ward: {ward[:3]}")
    
    # Architecture summary
    print("\n" + "="*70)
    print("📐 ARCHITECTURE SUMMARY:")
    print("="*70)
    print("""
┌─────────────────────────────────────────────────────────────────┐
│ INPUT: "TP.HCM, Quận 1, Phường Bến Nghé"                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: Generic Normalization (normalizer_v2.py)              │
│   - Lowercase                                                    │
│   - Remove Vietnamese diacritics                                │
│   - Clean whitespace                                            │
│   - PRESERVE dots                                               │
│                                                                  │
│ Output: "tp.hcm, quan 1, phuong ben nghe"                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: Admin Prefix Handling (admin_prefix_handler_v2.py)    │
│   - Detect prefixes (TP., Q., P.)                              │
│   - Remove prefixes                                             │
│   - Expand abbreviations (using AbbreviationBuilder)           │
│                                                                  │
│ Output: "ho chi minh", "1", "ben nghe"                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: Alias Generation (alias_generator.py)                 │
│   - Generate initials: "hcm", "bn"                             │
│   - Generate no-space: "hochiminh", "bennghe"                  │
│   - Generate dotted: "h.c.m", "b.n"                           │
│   - Generate first+last: "ho minh"                             │
│                                                                  │
│ Output: ["ho chi minh", "hcm", "hochiminh", ...]              │
│         ["1"]                                                   │
│         ["ben nghe", "bn", "bennghe", ...]                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 4: Trie Insertion (pygtrie)                              │
│   - Insert all aliases into appropriate tries                   │
│   - Enable fast prefix matching                                │
└─────────────────────────────────────────────────────────────────┘

KEY PRINCIPLES:
  ✅ Separation of Concerns - each layer has single responsibility
  ✅ Domain Independence - Layer 1 knows nothing about Vietnamese admin
  ✅ Composability - layers can be tested/swapped independently
  ✅ Extensibility - easy to add new normalization rules
    """)
