"""
Administrative Prefix Handler for Vietnamese Addresses (v3 - Dictionary-Based)

This version uses dictionary-based prefix configuration for better extensibility.

Architecture Evolution:
    v1: Hardcoded PROVINCES = {'hcm': 'ho chi minh', ...}
    v2: Class-based AdminPrefixPatterns with regex lists
    v3: Dictionary-based ADMIN_PREFIXES with metadata

Benefits of v3:
    - Rich metadata per level (priority, ambiguity flags, etc.)
    - Easy to extend with new fields
    - Self-documenting structure
    - Preserves all v2 functionality
"""

from typing import Dict, List, Tuple, Optional, Set
import re
from pathlib import Path
from abbreviation_builder import AbbreviationBuilder


# ========================================================================
# ADMINISTRATIVE PREFIX CONFIGURATION
# ========================================================================

ADMIN_PREFIXES = {
    # Level 1: Province/City
    'province': {
        'patterns': [
            # Full forms (must check before abbreviations!)
            r'thanh pho truc thuoc trung uong',
            r'thanh pho',
            r'tinh',
            
            # Abbreviated forms with dots
            r'tp\.',
            r't\.',
            
            # Abbreviated forms without dots  
            r'tp',
            r't',
        ],
        'type': 'province',
        'priority': 1,  # Check first
        'ambiguous_prefixes': {'tp', 'tp.', 'thanh pho'},  # Overlap with district
        'context_required': False,  # Can identify independently
    },
    
    # Level 2: District
    'district': {
        'patterns': [
            # Full forms
            r'thanh pho',  # Provincial city (ambiguous with Level 1!)
            r'thi xa',
            r'quan',
            r'huyen',
            
            # Abbreviated forms with dots
            r'tp\.',
            r'tx\.',
            r'q\.',
            r'h\.',
            
            # Abbreviated forms without dots
            r'tp',
            r'tx',
            r'q',
            r'h',
        ],
        'type': 'district',
        'priority': 2,  # Check after province
        'ambiguous_prefixes': {'tp', 'tp.', 'thanh pho'},  # Overlap with province
        'context_required': True,  # May need province context for TP disambiguation
    },
    
    # Level 3: Ward/Commune
    'ward': {
        'patterns': [
            # Full forms
            r'thi tran',
            r'phuong',
            r'xa',
            
            # Abbreviated forms with dots
            r'tt\.',
            r'p\.',
            r'x\.',
            
            # Abbreviated forms without dots
            r'tt',
            r'p',
            r'x',
        ],
        'type': 'ward',
        'priority': 3,  # Check last
        'ambiguous_prefixes': set(),  # No overlaps
        'context_required': False,  # Can identify independently
    },
}


# ========================================================================
# HELPER FUNCTIONS FOR PREFIX CONFIG
# ========================================================================

def get_patterns_for_level(level: str) -> List[str]:
    """
    Get regex patterns for a specific administrative level
    
    Args:
        level: 'province', 'district', or 'ward'
    
    Returns:
        List of regex patterns
    
    Example:
        get_patterns_for_level('province')
        → [r'thanh pho truc thuoc trung uong', r'thanh pho', ...]
    """
    if level in ADMIN_PREFIXES:
        return ADMIN_PREFIXES[level]['patterns']
    return []


def get_all_patterns_ordered() -> List[str]:
    """
    Get all patterns across all levels, ordered by priority
    
    Returns:
        Flattened list of patterns in priority order
    
    Usage:
        When level='auto', try patterns in this order
    """
    sorted_levels = sorted(
        ADMIN_PREFIXES.items(),
        key=lambda x: x[1]['priority']
    )
    
    all_patterns = []
    for level, config in sorted_levels:
        all_patterns.extend(config['patterns'])
    
    return all_patterns


def is_ambiguous_prefix(prefix: str, level: str) -> bool:
    """
    Check if a prefix is ambiguous at a given level
    
    Args:
        prefix: Prefix to check (e.g., 'tp', 'tp.')
        level: Administrative level
    
    Returns:
        True if prefix appears in multiple levels
    
    Example:
        is_ambiguous_prefix('tp', 'district') → True
        is_ambiguous_prefix('q', 'district') → False
    """
    if level not in ADMIN_PREFIXES:
        return False
    
    return prefix.lower() in ADMIN_PREFIXES[level]['ambiguous_prefixes']


# ========================================================================
# PREFIX HANDLER CLASS (v3)
# ========================================================================

class AdminPrefixHandler:
    """
    Main class for handling Vietnamese administrative prefixes (v3)
    
    Changes from v2:
        - Uses dictionary-based ADMIN_PREFIXES instead of class constants
        - Preserves all v2 functionality
        - Adds metadata support for future enhancements
    
    Responsibilities:
        1. Detect and remove administrative prefixes
        2. Expand known abbreviations (using AbbreviationBuilder)
        3. Return clean entity names for matching
    
    Usage:
        handler = AdminPrefixHandler(data_dir="../data")
        result = handler.expand("tp.hcm", level='province')
        # result = "ho chi minh"
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize handler with optional data directory
        
        Args:
            data_dir: Path to directory containing provinces.txt,
                     districts.txt, ward.txt
        """
        # Build dynamic abbreviation mappings
        self.abbrev_builder = None
        if data_dir:
            self.abbrev_builder = AbbreviationBuilder(data_dir)
            self.abbrev_builder.build_all()
    
    def expand(
        self, 
        text: str, 
        level: str = 'auto'
    ) -> str:
        """
        Expand administrative prefixes and abbreviations
        
        Algorithm:
            1. Detect and remove prefix (TP, Q, P, etc.)
            2. Try to expand known abbreviations (using AbbreviationBuilder)
            3. Return clean entity name
        
        Args:
            text: Normalized text (e.g., "tp.hcm", "q.1", "p.ben nghe")
            level: 'province', 'district', 'ward', or 'auto'
        
        Returns:
            Expanded entity name (e.g., "ho chi minh", "1", "ben nghe")
        
        Examples:
            expand("tp.hcm", 'province') → "ho chi minh"
            expand("q.1", 'district') → "1"
            expand("p.ben nghe", 'ward') → "ben nghe"
            expand("quan tan binh", 'district') → "tan binh"
        """
        # Step 1: Remove prefix
        core_name = self._remove_prefix(text, level)
        
        # Step 2: Expand abbreviations (using AbbreviationBuilder)
        expanded = self._expand_abbreviation(core_name, level)
        
        # Step 3: Clean and return
        return expanded.strip()
    
    def _remove_prefix(self, text: str, level: str) -> str:
        """
        Remove administrative prefix from text
        
        Strategy:
            - Try level-specific prefixes first (if level known)
            - Fall back to all prefixes (if level='auto')
            - Check longer patterns before shorter ones
        
        Args:
            text: Input text
            level: Administrative level
        
        Returns:
            Text with prefix removed
        """
        text = text.strip()
        
        # Select prefix patterns based on level
        if level in ADMIN_PREFIXES:
            patterns = ADMIN_PREFIXES[level]['patterns']
        elif level == 'auto':
            # Get all patterns ordered by priority
            patterns = get_all_patterns_ordered()
        else:
            # Unknown level, return as-is
            return text
        
        # Try each pattern (longest first for greedy matching)
        for pattern in patterns:
            # Create regex: pattern at start, followed by space or end
            regex = re.compile(r'^' + pattern + r'[\s\.]?', re.IGNORECASE)
            match = regex.match(text)
            
            if match:
                # Remove the matched prefix
                result = text[match.end():].strip()
                
                # Remove leading dots/spaces if any
                result = result.lstrip('. ')
                
                return result
        
        # No prefix found, return as-is
        return text
    
    def _expand_abbreviation(self, text: str, level: str) -> str:
        """
        Expand known abbreviations to full names (using AbbreviationBuilder)
        
        Strategy:
            1. Check if text is a known abbreviation (via AbbreviationBuilder)
            2. If yes, expand it
            3. If ambiguous, use level context or return first candidate
            4. If unknown, return as-is
        
        Args:
            text: Core entity name (prefix already removed)
            level: Administrative level for disambiguation
        
        Returns:
            Expanded name or original text
        
        Examples:
            _expand_abbreviation("hcm", "province") → "ho chi minh"
            _expand_abbreviation("dn", "province") → "da nang" (first candidate)
            _expand_abbreviation("tan binh", "district") → "tan binh" (no expansion needed)
        """
        if not self.abbrev_builder:
            # No abbreviation builder available, return as-is
            return text
        
        text_lower = text.lower().strip()
        
        # Determine which level to check
        if level == 'auto':
            # Try all levels in priority order
            for lvl_key in ['province', 'district', 'ward']:
                level_data_key = self._level_to_key(lvl_key)
                expanded = self.abbrev_builder.get_full_name(text_lower, level_data_key)
                if expanded:
                    return expanded
        else:
            # Check specific level
            level_key = self._level_to_key(level)
            expanded = self.abbrev_builder.get_full_name(text_lower, level_key)
            if expanded:
                return expanded
        
        # No expansion found, return as-is
        return text
    
    def _level_to_key(self, level: str) -> str:
        """Convert level name to AbbreviationBuilder key"""
        mapping = {
            'province': 'provinces',
            'district': 'districts',
            'ward': 'wards'
        }
        return mapping.get(level, level)
    
    def batch_expand(
        self, 
        texts: List[str], 
        level: str = 'auto'
    ) -> List[str]:
        """
        Expand multiple texts at once
        
        Useful for preprocessing entire datasets
        
        Args:
            texts: List of texts to expand
            level: Administrative level
        
        Returns:
            List of expanded texts
        """
        return [self.expand(text, level) for text in texts]
    
    def is_ambiguous(self, text: str, level: str = 'auto') -> bool:
        """
        Check if a text has ambiguous abbreviation
        
        Args:
            text: Text to check
            level: Administrative level
        
        Returns:
            True if abbreviation is ambiguous
        """
        if not self.abbrev_builder:
            return False
        
        core_name = self._remove_prefix(text, level)
        text_lower = core_name.lower().strip()
        
        if level == 'auto':
            # Check all levels
            for lvl in ['provinces', 'districts', 'wards']:
                if self.abbrev_builder.is_ambiguous(text_lower, lvl):
                    return True
            return False
        else:
            level_key = self._level_to_key(level)
            return self.abbrev_builder.is_ambiguous(text_lower, level_key)
    
    def get_all_expansions(self, text: str, level: str = 'auto') -> List[str]:
        """
        Get all possible expansions for ambiguous abbreviations
        
        Args:
            text: Text to expand
            level: Administrative level
        
        Returns:
            List of all possible full names
        
        Example:
            get_all_expansions("dn", "province")
            → ["da nang", "dong nai", "dak nong"]
        """
        if not self.abbrev_builder:
            return [text]
        
        core_name = self._remove_prefix(text, level)
        text_lower = core_name.lower().strip()
        
        if level == 'auto':
            # Collect from all levels
            all_candidates = []
            for lvl in ['provinces', 'districts', 'wards']:
                candidates = self.abbrev_builder.get_all_candidates(text_lower, lvl)
                all_candidates.extend(candidates)
            return all_candidates if all_candidates else [text]
        else:
            level_key = self._level_to_key(level)
            candidates = self.abbrev_builder.get_all_candidates(text_lower, level_key)
            return candidates if candidates else [text]
    
    def get_prefix_metadata(self, level: str) -> Dict:
        """
        Get metadata for a specific administrative level
        
        New in v3: Access to rich metadata
        
        Args:
            level: 'province', 'district', or 'ward'
        
        Returns:
            Dictionary with metadata (priority, ambiguous_prefixes, etc.)
        
        Example:
            handler.get_prefix_metadata('district')
            → {
                'patterns': [...],
                'type': 'district',
                'priority': 2,
                'ambiguous_prefixes': {'tp', 'tp.', 'thanh pho'},
                'context_required': True
              }
        """
        return ADMIN_PREFIXES.get(level, {})


# ========================================================================
# CONVENIENCE FUNCTIONS
# ========================================================================

def expand_province(text: str, data_dir: Optional[str] = None) -> str:
    """
    Convenience function: Expand province-level entity
    
    Examples:
        expand_province("TP.HCM") → "ho chi minh"
        expand_province("Tỉnh Bình Dương") → "binh duong"
    """
    handler = AdminPrefixHandler(data_dir)
    return handler.expand(text, level='province')


def expand_district(text: str, data_dir: Optional[str] = None) -> str:
    """
    Convenience function: Expand district-level entity
    
    Examples:
        expand_district("Q.1") → "1"
        expand_district("Huyện Củ Chi") → "cu chi"
    """
    handler = AdminPrefixHandler(data_dir)
    return handler.expand(text, level='district')


def expand_ward(text: str, data_dir: Optional[str] = None) -> str:
    """
    Convenience function: Expand ward-level entity
    
    Examples:
        expand_ward("P.Bến Nghé") → "ben nghe"
        expand_ward("Xã Tân Thông Hội") → "tan thong hoi"
    """
    handler = AdminPrefixHandler(data_dir)
    return handler.expand(text, level='ward')


# ========================================================================
# TESTING & EXAMPLES
# ========================================================================

if __name__ == "__main__":
    print("="*70)
    print("ADMINISTRATIVE PREFIX HANDLER v3 - DICTIONARY-BASED")
    print("="*70)
    
    # Initialize handler
    handler = AdminPrefixHandler(data_dir="../data")
    
    print("\n📊 CONFIGURATION OVERVIEW:")
    print("-" * 70)
    
    for level in ['province', 'district', 'ward']:
        metadata = handler.get_prefix_metadata(level)
        print(f"\n{level.upper()}:")
        print(f"  Priority: {metadata.get('priority')}")
        print(f"  Patterns: {len(metadata.get('patterns', []))} patterns")
        print(f"  Ambiguous prefixes: {metadata.get('ambiguous_prefixes')}")
        print(f"  Context required: {metadata.get('context_required')}")
    
    print("\n📊 ABBREVIATION STATISTICS:")
    print("-" * 70)
    
    if handler.abbrev_builder:
        for level in ['provinces', 'districts', 'wards']:
            total = len(handler.abbrev_builder.known_entities[level])
            unique = len(handler.abbrev_builder.abbreviations[level])
            ambiguous = len(handler.abbrev_builder.ambiguous[level])
            
            print(f"\n{level.upper()}:")
            print(f"  Total entities: {total}")
            print(f"  Unique abbreviations: {unique}")
            print(f"  Ambiguous abbreviations: {ambiguous}")
    
    # Test cases by level
    print("\n" + "="*70)
    print("🧪 TEST CASES:")
    print("="*70)
    
    test_cases = [
        # (input, level, description)
        
        # Province level
        ("tp.hcm", "province", "TP.HCM abbreviation"),
        ("thanh pho ha noi", "province", "Full form with prefix"),
        ("hn", "province", "Hanoi abbreviation"),
        ("dn", "province", "Ambiguous DN"),
        ("ct", "province", "Can Tho abbreviation"),
        
        # District level
        ("q.1", "district", "District number"),
        ("quan tan binh", "district", "District full form"),
        ("h.cu chi", "district", "Rural district"),
        ("tx.thuan an", "district", "Town"),
        
        # Ward level
        ("p.ben nghe", "ward", "Ward with prefix"),
        ("phuong 12", "ward", "Numbered ward"),
        ("xa tan thong hoi", "ward", "Commune"),
        
        # Auto level
        ("tp.hcm", "auto", "Auto-detect province"),
        ("q.1", "auto", "Auto-detect district"),
        ("p.12", "auto", "Auto-detect ward"),
    ]
    
    passed = 0
    failed = 0
    
    for input_text, level, description in test_cases:
        result = handler.expand(input_text, level)
        is_amb = handler.is_ambiguous(input_text, level)
        
        status = "⚠️" if is_amb else "✅"
        
        print(f"\n{status} [{level:8}] '{input_text:25}' → '{result}'")
        print(f"   Description: {description}")
        
        if is_amb:
            all_expansions = handler.get_all_expansions(input_text, level)
            print(f"   ⚠️  Ambiguous! All candidates: {all_expansions}")
        
        passed += 1
    
    print("\n" + "="*70)
    print(f"Results: {passed} tests completed")
    print("="*70)
    
    # Test ambiguity detection
    print("\n" + "="*70)
    print("🔍 AMBIGUITY DETECTION:")
    print("="*70)
    
    ambiguity_tests = [
        ("hcm", "province"),
        ("dn", "province"),
        ("bd", "province"),
        ("bt", "district"),
    ]
    
    for abbrev, level in ambiguity_tests:
        is_amb = handler.is_ambiguous(abbrev, level)
        expanded = handler.expand(abbrev, level)
        
        if is_amb:
            all_exp = handler.get_all_expansions(abbrev, level)
            print(f"\n⚠️  AMBIGUOUS: '{abbrev}' ({level})")
            print(f"   → Primary: {expanded}")
            print(f"   → All: {all_exp}")
        else:
            print(f"\n✅ UNIQUE: '{abbrev}' ({level}) → {expanded}")
    
    # Test new metadata access
    print("\n" + "="*70)
    print("🔍 PREFIX METADATA (NEW in v3):")
    print("="*70)
    
    print("\nChecking 'tp' prefix ambiguity across levels:")
    for level in ['province', 'district', 'ward']:
        is_amb = is_ambiguous_prefix('tp', level)
        print(f"  {level}: {'⚠️  Ambiguous' if is_amb else '✅ Unique'}")
