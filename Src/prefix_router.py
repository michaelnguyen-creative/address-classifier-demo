"""
Prefix Router - Intelligent Trie Routing using AdminPrefixHandler

PURPOSE: Route queries to appropriate Trie based on administrative prefix
STRATEGY: Reuse AdminPrefixHandler's patterns instead of duplicating

KEY INSIGHT:
    AdminPrefixHandler already knows how to detect and remove prefixes.
    We just need to map: which prefix type → which Trie to search.

EXAMPLE:
    "TT Tân Bình" → AdminPrefixHandler.expand(level='ward') → "Tân Bình"
                  → Route to ward_trie
                  → Search "Tân Bình" → ✅ Match!
"""

from typing import Optional, Tuple
from admin_prefix_handler import AdminPrefixHandler


class PrefixRouter:
    """
    Route queries to appropriate Trie using AdminPrefixHandler
    
    Design Philosophy:
        - Don't Repeat Yourself (DRY): Reuse existing pattern matching
        - Composition over duplication
        - Single responsibility: routing logic only
    
    Benefits:
        - Leverages tested AdminPrefixHandler patterns
        - Automatic updates when patterns change
        - Cleaner, more maintainable code
    """
    
    def __init__(self, admin_handler: AdminPrefixHandler):
        """
        Initialize router with AdminPrefixHandler instance
        
        Args:
            admin_handler: Configured AdminPrefixHandler instance
        """
        self.admin_handler = admin_handler
    
    def detect_level_and_extract(
        self, 
        text: str
    ) -> Tuple[Optional[str], str]:
        """
        Detect administrative level from prefix and extract core name
        
        Strategy:
            Try each level in priority order (province → district → ward)
            Use AdminPrefixHandler.expand() to detect & remove prefix
            If text changes after expansion, prefix was detected
        
        Args:
            text: Normalized text (e.g., "tt tan binh")
        
        Returns:
            (level, core_name) tuple
            - level: 'province', 'district', 'ward', or None
            - core_name: Text with prefix removed
        
        Examples:
            "tt tan binh"      → ("ward", "tan binh")
            "q 3"              → ("district", "3")
            "t ha noi"         → ("province", "ha noi")
            "tp hcm"           → ("province", "hcm")
            "tan binh"         → (None, "tan binh")  # No prefix
        
        Time: O(p) where p = number of patterns in AdminPrefixHandler
        """
        # Try province level first (highest priority)
        core = self.admin_handler.expand(text, level='province')
        if core != text:  # Prefix was detected and removed
            return ('province', core)
        
        # Try district level
        core = self.admin_handler.expand(text, level='district')
        if core != text:
            return ('district', core)
        
        # Try ward level
        core = self.admin_handler.expand(text, level='ward')
        if core != text:
            return ('ward', core)
        
        # No prefix detected
        return (None, text)
    
    def detect_level(self, text: str) -> Tuple[Optional[str], str]:
        """
        Alias for detect_level_and_extract (for backward compatibility)
        """
        return self.detect_level_and_extract(text)
    
    def route_and_search(
        self,
        text: str,
        province_trie,
        district_trie,
        ward_trie
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Detect level and search appropriate Trie
        
        Args:
            text: Normalized query
            province_trie: Province Trie instance
            district_trie: District Trie instance
            ward_trie: Ward Trie instance
        
        Returns:
            (result, level) tuple
        
        Example:
            router.route_and_search("tt tan binh", p_trie, d_trie, w_trie)
            → ("Tân Bình", "ward")
        """
        level, core_name = self.detect_level_and_extract(text)
        
        if level == 'province':
            result = province_trie.search(core_name)
            return (result, 'province')
        elif level == 'district':
            result = district_trie.search(core_name)
            return (result, 'district')
        elif level == 'ward':
            result = ward_trie.search(core_name)
            return (result, 'ward')
        else:
            # No prefix - level unknown
            return (None, None)


# ========================================================================
# TESTING
# ========================================================================

if __name__ == "__main__":
    print("="*70)
    print("PREFIX ROUTER - TESTING (Using AdminPrefixHandler)")
    print("="*70)
    
    # Initialize with AdminPrefixHandler
    handler = AdminPrefixHandler(data_dir="../data")
    router = PrefixRouter(handler)
    
    test_cases = [
        # Province level
        ("tp hcm", "province", "hcm"),
        ("t ha noi", "province", "ha noi"),
        ("t.binh duong", "province", "binh duong"),
        ("tinh quang ninh", "province", "quang ninh"),
        
        # District level
        ("q 1", "district", "1"),
        ("q.3", "district", "3"),
        ("h cu chi", "district", "cu chi"),
        ("huyen tan binh", "district", "tan binh"),
        ("tx thuan an", "district", "thuan an"),
        
        # Ward level - THE KEY TEST!
        ("tt tan binh", "ward", "tan binh"),
        ("p 1", "ward", "1"),
        ("p.12", "ward", "12"),
        ("phuong ben nghe", "ward", "ben nghe"),
        ("xa tan thong hoi", "ward", "tan thong hoi"),
        ("thi tran ea knop", "ward", "ea knop"),
        
        # No prefix
        ("tan binh", None, "tan binh"),
        ("ho chi minh", None, "ho chi minh"),
    ]
    
    print("\n🧪 TEST RESULTS:")
    print("-"*70)
    
    passed = 0
    failed = 0
    
    for text, expected_level, expected_core in test_cases:
        level, core = router.detect_level(text)
        
        level_match = (level == expected_level)
        core_match = (core == expected_core)
        success = level_match and core_match
        
        if success:
            passed += 1
            status = "✅"
        else:
            failed += 1
            status = "❌"
        
        print(f"{status} '{text:25}' → level={str(level):10} core='{core}'")
        if not success:
            print(f"     Expected: level={expected_level}, core='{expected_core}'")
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed}/{len(test_cases)} passed")
    print("="*70)
    
    if failed == 0:
        print("\n✅ All tests PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
