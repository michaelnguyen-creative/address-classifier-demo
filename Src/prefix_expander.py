"""
Prefix Expander - Expand Vietnamese Address Abbreviations

PURPOSE: Expand user abbreviations BEFORE searching database
DIFFERENT FROM: AdminPrefixHandler (which REMOVES prefixes from database entities)

ARCHITECTURE:
    This is a PARSER-SIDE tool that preprocesses user input
    AdminPrefixHandler is a DATABASE-SIDE tool that cleans entity names

USE CASE:
    User types: "P1,Q3,TP.HCM"
    After normalization: "p1 q3 tp hcm"
    After prefix expansion: "phuong 1 quan 3 thanh pho hcm"
    Then search in trie → MATCH!

DESIGN PRINCIPLE:
    - Simple regex-based expansion
    - Handles Vietnamese admin level abbreviations
    - Works on already-normalized text (after TextNormalizer)
"""

import re
from typing import Dict, List


class PrefixExpander:
    """
    Expands Vietnamese administrative abbreviations in user input
    
    Examples:
        "p1" → "phuong 1"
        "q3" → "quan 3"
        "tp hcm" → "thanh pho hcm"
        "h yen son" → "huyen yen son"
    
    Design:
        - Works on NORMALIZED text (already lowercased, no diacritics)
        - Expands abbreviations to full Vietnamese admin prefixes
        - Uses regex patterns for flexibility
    """
    
    def __init__(self):
        """
        Initialize with Vietnamese admin prefix expansion patterns
        
        Pattern Order: CRITICAL!
        - More specific patterns first (e.g., "tp." before "t.")
        - Prevents incorrect expansions
        """
        # Ward/Commune level (bottom of hierarchy)
        self.ward_patterns = [
            # Phường (ward in cities)
            (re.compile(r'\bp\.?\s*(\d+)\b'), r'phuong \1'),          # P.1, P1 → phuong 1
            (re.compile(r'\bph\.?\s+([a-z]+)'), r'phuong \1'),        # Ph.X → phuong x
            (re.compile(r'\bphuong\s+'), r'phuong '),                 # Already correct
            
            # Xã (commune in rural areas)
            (re.compile(r'\bx\.?\s+(\d+)'), r'xa \1'),              # X.1 → xa 1
            (re.compile(r'\bx\.?\s+([a-z]+)'), r'xa \1'),            # X.Name → xa name
            (re.compile(r'\bxa\s+'), r'xa '),                         # Already correct
            
            # Thị trấn (town)
            (re.compile(r'\btt\.?\s+(\d+)'), r'thi tran \1'),       # TT.1 → thi tran 1
            (re.compile(r'\btt\.?\s+([a-z]+)'), r'thi tran \1'),    # TT.X → thi tran x
            (re.compile(r'\bt\.t\.?\s+([a-z]+)'), r'thi tran \1'),  # T.T.X → thi tran x
            (re.compile(r'\bthi\s+tran\s+'), r'thi tran '),         # Already correct
        ]
        
        # District level (middle of hierarchy)
        self.district_patterns = [
            # Quận (urban district)
            (re.compile(r'\bq\.?\s*(\d+)\b'), r'quan \1'),            # Q.3, Q3 → quan 3
            (re.compile(r'\bqu\.?\s+([a-z]+)'), r'quan \1'),          # Qu.X → quan x
            (re.compile(r'\bquan\s+'), r'quan '),                     # Already correct
            
            # Huyện (rural district)
            (re.compile(r'\bh\.\s*(\d+)'), r'huyen \1'),             # H.1 → huyen 1 (with dot)
            (re.compile(r'\bh\.\s*([a-z]{3,})\b'), r'huyen \1'),    # H.X → huyen x (with dot)
            (re.compile(r'\bh\s+([a-z]+)'), r'huyen \1'),            # h X → huyen x (with space)
            (re.compile(r'\bhuy\.?\s+([a-z]+)'), r'huyen \1'),       # Huy.X → huyen x
            (re.compile(r'\bhuyen\s+'), r'huyen '),                   # Already correct
            
            # Thị xã (town-level city)
            (re.compile(r'\btx\.?\s+(\d+)'), r'thi xa \1'),         # TX.1 → thi xa 1
            (re.compile(r'\btx\.?\s+([a-z]+)'), r'thi xa \1'),       # TX.X → thi xa x
            (re.compile(r'\bt\.x\.?\s+([a-z]+)'), r'thi xa \1'),    # T.X.X → thi xa x
            (re.compile(r'\bthi\s+xa\s+'), r'thi xa '),              # Already correct
        ]
        
        # Province/City level (top of hierarchy)
        self.province_patterns = [
            # Thành phố (city)
            (re.compile(r'\btp\.?\s+(\d+)'), r'thanh pho \1'),      # TP.1 → thanh pho 1
            (re.compile(r'\btp\.?\s+([a-z]+)'), r'thanh pho \1'),   # TP.X → thanh pho x
            (re.compile(r'\bt\.p\.?\s+(\d+)'), r'thanh pho \1'),   # T.P.1 → thanh pho 1
            (re.compile(r'\bt\.p\.?\s+([a-z]+)'), r'thanh pho \1'), # T.P.X → thanh pho x
            (re.compile(r'\bthanh\s+pho\s+'), r'thanh pho '),       # Already correct
            
            # Tỉnh (province)
            # Only expand when there's explicit separation (space or dot)
            (re.compile(r'\bt\.\s*([a-z]{3,})\b'), r'tinh \1'),    # T.Name → tinh name (with dot)
            (re.compile(r'\bt\s+([a-z]{3,})\b'), r'tinh \1'),      # t name → tinh name (with space)
            (re.compile(r'\btinh\s+([a-z]+)'), r'tinh \1'),         # tinh X → tinh x
        ]
        
        # Combine all patterns (order matters!)
        # Province first, then district, then ward
        # Why? More specific patterns should match before general ones
        self.all_patterns = (
            self.province_patterns +
            self.district_patterns +
            self.ward_patterns
        )
    
    def expand(self, text: str, level: str = 'all') -> str:
        """
        Expand abbreviations in normalized text
        
        Args:
            text: Normalized text (already lowercased, no diacritics)
            level: 'all', 'province', 'district', 'ward'
        
        Returns:
            Text with abbreviations expanded
        
        Algorithm:
            1. Apply patterns in order (province → district → ward)
            2. Each pattern only matches once per position
            3. Already-expanded text is preserved
        
        Examples:
            expand("p1 q3 tp hcm") → "phuong 1 quan 3 thanh pho hcm"
            expand("h yen son tinh tuyen quang") → "huyen yen son tinh tuyen quang"
        
        Time Complexity: O(n × p) where n = text length, p = pattern count
        """
        if not text:
            return text
        
        # Select patterns based on level
        if level == 'province':
            patterns = self.province_patterns
        elif level == 'district':
            patterns = self.district_patterns
        elif level == 'ward':
            patterns = self.ward_patterns
        else:  # 'all'
            patterns = self.all_patterns
        
        # Apply each pattern
        for pattern, replacement in patterns:
            text = pattern.sub(replacement, text)
        
        return text
    
    def expand_batch(self, texts: List[str], level: str = 'all') -> List[str]:
        """
        Expand abbreviations in multiple texts
        
        Args:
            texts: List of normalized texts
            level: 'all', 'province', 'district', 'ward'
        
        Returns:
            List of texts with abbreviations expanded
        """
        return [self.expand(text, level) for text in texts]


# ========================================================================
# CONVENIENCE FUNCTION
# ========================================================================

def expand_prefixes(text: str, level: str = 'all') -> str:
    """
    Convenience function: Expand Vietnamese admin prefixes
    
    Args:
        text: Normalized text
        level: 'all', 'province', 'district', 'ward'
    
    Returns:
        Text with abbreviations expanded
    
    Examples:
        expand_prefixes("p1 q3 tp hcm") → "phuong 1 quan 3 thanh pho hcm"
    """
    expander = PrefixExpander()
    return expander.expand(text, level)


# ========================================================================
# TESTING
# ========================================================================

if __name__ == "__main__":
    print("="*70)
    print("PREFIX EXPANDER - TEST SUITE")
    print("="*70)
    
    expander = PrefixExpander()
    
    # Test cases from real-world data
    test_cases = [
        # Basic cases
        ("p1", "phuong 1", "Ward abbreviation"),
        ("q3", "quan 3", "District abbreviation"),
        ("tp hcm", "thanh pho hcm", "Province abbreviation"),
        ("h yen son", "huyen yen son", "District with name"),
        
        # Dotted forms (with explicit separator)
        ("t.binh duong", "tinh binh duong", "Province with dot (t.)"),
        ("h.hoai an", "huyen hoai an", "District with dot (h.)"),
        ("t ha tinh", "tinh ha tinh", "Province with space (t )"),
        ("h yen son", "huyen yen son", "District with space (h )"),
        
        # Complex cases
        ("p1 q3 tp hcm", "phuong 1 quan 3 thanh pho hcm", "Full address"),
        ("357 28 ng t thuat p1 q3 tp hochiminh", 
         "357 28 ng t thuat phuong 1 quan 3 thanh pho hochiminh",
         "Complex messy address"),
        ("tt tan binh h yen son tinh tuyen quang",
         "thi tran tan binh huyen yen son tinh tuyen quang",
         "Rural address with town"),
        
        # Already expanded
        ("phuong 1 quan 3", "phuong 1 quan 3", "Already expanded (no change)"),
    ]
    
    print("\nTest Results:")
    print("-"*70)
    
    passed = 0
    failed = 0
    
    for input_text, expected, description in test_cases:
        result = expander.expand(input_text)
        success = (result == expected)
        
        if success:
            passed += 1
            status = "✅"
        else:
            failed += 1
            status = "❌"
        
        print(f"\n{status} {description}")
        print(f"   Input:    '{input_text}'")
        print(f"   Expected: '{expected}'")
        print(f"   Got:      '{result}'")
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed}/{len(test_cases)} passed ({passed/len(test_cases)*100:.1f}%)")
    print("="*70)
    
    if failed == 0:
        print("\n✅ All tests PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) failed - need adjustment")
