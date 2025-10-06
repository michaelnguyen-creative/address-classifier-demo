"""
Vietnamese Address Text Normalization v2 - Clean Separation of Concerns

ARCHITECTURE:
    Layer 1: Generic normalization (domain-agnostic) - IMPROVED
    Layer 2: Admin prefix handling (Vietnamese-specific)

DESIGN PRINCIPLE:
    Each layer has single responsibility and doesn't know about other layers

NORMALIZATION PIPELINE:
    "TP.HCM, Quận 1"
    → [Layer 1] → "tp.hcm, quan 1"  (lowercase, remove diacritics, preserve structure)
    → [Layer 2] → "ho chi minh", "1"  (expand prefixes, extract core)
    → Output: Clean entity names ready for use

SEPARATE SYSTEM (not in this module):
    TRIE DATABASE:
    Clean names → [Alias Generator] → Multiple search keys → Insert into trie

NEW IN V2:
    ✓ Unicode symbol removal (™, ®, ©, etc.)
    ✓ Smart punctuation (preserve ., comma, / by default)
    ✓ Space-preserving aggressive mode
    ✓ Hyphen handling (word separator)
    ✓ Comma-space normalization
    ✓ Layer 2 integration (admin prefix handling)
"""

# Import Layer 1: Text Normalizer
from text_normalizer import (
    TextNormalizer,
    normalize_text,
    normalize_text_aggressive,
)

# Import Layer 2: Admin Prefix Handler
from admin_prefix_handler import (
    AdminPrefixHandler,
    expand_province,
    expand_district,
    expand_ward,
)

from typing import Dict, Optional, List


# ========================================================================
# LAYER 1 + LAYER 2: UNIFIED PIPELINE
# ========================================================================

class AddressNormalizer:
    """
    Unified pipeline combining Layer 1 (text normalization) and Layer 2 (prefix handling)
    
    This is the main entry point for address normalization.
    
    Pipeline:
        Raw address → Layer 1 (normalize) → Layer 2 (expand prefixes) → Clean components
    
    Example:
        normalizer = AddressNormalizer(data_dir="../data")
        result = normalizer.process_address("TP.HCM, Quận 1, P.Bến Nghé")
        # result = {
        #     'raw': 'TP.HCM, Quận 1, P.Bến Nghé',
        #     'normalized': 'tp.hcm, quan 1, p.ben nghe',
        #     'components': {
        #         'city': 'ho chi minh',
        #         'district': '1',
        #         'ward': 'ben nghe'
        #     }
        # }
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the unified normalizer
        
        Args:
            data_dir: Path to data directory for abbreviation expansion
        """
        # Layer 1: Text normalizer (with Vietnamese defaults)
        self.text_normalizer = TextNormalizer()
        
        # Layer 2: Admin prefix handler
        self.prefix_handler = AdminPrefixHandler(data_dir=data_dir)
    
    def normalize_only(self, text: str, aggressive: bool = False) -> str:
        """
        Layer 1 only: Normalize text without expanding prefixes
        
        Args:
            text: Raw address text
            aggressive: Use aggressive mode
        
        Returns:
            Normalized text
        
        Example:
            normalize_only("TP.HCM") → "tp.hcm"
        """
        return self.text_normalizer.normalize(text, aggressive=aggressive)
    
    def expand_only(self, normalized_text: str, level: str = 'auto') -> str:
        """
        Layer 2 only: Expand prefixes from already-normalized text
        
        Args:
            normalized_text: Text that's already been through Layer 1
            level: 'province', 'district', 'ward', or 'auto'
        
        Returns:
            Expanded entity name
        
        Example:
            expand_only("tp.hcm", 'province') → "ho chi minh"
        """
        return self.prefix_handler.expand(normalized_text, level=level)
    
    def process(self, text: str, level: str = 'auto') -> str:
        """
        Full pipeline: Layer 1 + Layer 2
        
        Args:
            text: Raw address text
            level: Administrative level
        
        Returns:
            Fully processed entity name
        
        Example:
            process("TP.HCM", 'province') → "ho chi minh"
            process("Quận 1", 'district') → "1"
        """
        # Step 1: Normalize (Layer 1)
        normalized = self.text_normalizer.normalize(text)
        
        # Step 2: Expand prefixes (Layer 2)
        expanded = self.prefix_handler.expand(normalized, level=level)
        
        return expanded
    
    def process_address(self, address: str, separator: str = ',') -> Dict[str, any]:
        """
        Process a full hierarchical address
        
        Args:
            address: Full address string (e.g., "TP.HCM, Quận 1, P.Bến Nghé")
            separator: Component separator (default: comma)
        
        Returns:
            Dictionary with processed components
        
        Example:
            process_address("TP.HCM, Quận 1, P.Bến Nghé")
            → {
                'raw': 'TP.HCM, Quận 1, P.Bến Nghé',
                'normalized': 'tp.hcm, quan 1, p.ben nghe',
                'components': {
                    'city': 'ho chi minh',
                    'district': '1',
                    'ward': 'ben nghe'
                },
                'levels': ['province', 'district', 'ward']
            }
        """
        # Step 1: Normalize the entire address (Layer 1)
        normalized = self.text_normalizer.normalize(address)
        
        # Step 2: Split into components
        parts = [p.strip() for p in normalized.split(separator) if p.strip()]
        
        # Step 3: Detect levels and expand (Layer 2)
        components = {}
        levels = []
        
        if len(parts) >= 1:
            # First part is likely city/province
            components['city'] = self.prefix_handler.expand(parts[0], level='province')
            levels.append('province')
        
        if len(parts) >= 2:
            # Second part is likely district
            components['district'] = self.prefix_handler.expand(parts[1], level='district')
            levels.append('district')
        
        if len(parts) >= 3:
            # Third part is likely ward
            components['ward'] = self.prefix_handler.expand(parts[2], level='ward')
            levels.append('ward')
        
        return {
            'raw': address,
            'normalized': normalized,
            'components': components,
            'levels': levels
        }
    
    def batch_process(self, texts: List[str], level: str = 'auto') -> List[str]:
        """
        Process multiple texts efficiently
        
        Args:
            texts: List of address texts
            level: Administrative level
        
        Returns:
            List of processed texts
        """
        return [self.process(text, level) for text in texts]


# ========================================================================
# CONVENIENCE FUNCTIONS FOR FULL PIPELINE
# ========================================================================

def process_province(text: str, data_dir: Optional[str] = None) -> str:
    """
    Convenience: Full pipeline for province-level addresses
    
    Example:
        process_province("TP.HCM") → "ho chi minh"
    """
    normalizer = AddressNormalizer(data_dir=data_dir)
    return normalizer.process(text, level='province')


def process_district(text: str, data_dir: Optional[str] = None) -> str:
    """
    Convenience: Full pipeline for district-level addresses
    
    Example:
        process_district("Quận 1") → "1"
    """
    normalizer = AddressNormalizer(data_dir=data_dir)
    return normalizer.process(text, level='district')


def process_ward(text: str, data_dir: Optional[str] = None) -> str:
    """
    Convenience: Full pipeline for ward-level addresses
    
    Example:
        process_ward("P.Bến Nghé") → "ben nghe"
    """
    normalizer = AddressNormalizer(data_dir=data_dir)
    return normalizer.process(text, level='ward')


def process_full_address(address: str, data_dir: Optional[str] = None) -> Dict[str, any]:
    """
    Convenience: Process a complete hierarchical address
    
    Example:
        process_full_address("TP.HCM, Quận 1, P.Bến Nghé")
        → {
            'city': 'ho chi minh',
            'district': '1',
            'ward': 'ben nghe'
        }
    """
    normalizer = AddressNormalizer(data_dir=data_dir)
    return normalizer.process_address(address)


# ========================================================================
# TEST DATA (Updated for V2 features)
# ========================================================================

TEST_SUITES = {
    # Suite 1: Basic normalization with structure preservation
    'basic_normalization': {
        'function': normalize_text,
        'description': 'normalize_text() - PRESERVES STRUCTURE',
        'cases': [
            ("TP.HCM", "tp.hcm", "Keep dots for Layer 2"),
            ("Quận 1", "quan 1", "Remove diacritics"),
            ("Phường Bến Nghé", "phuong ben nghe", "Full normalization"),
            ("THÀNH PHỐ HỒ CHÍ MINH", "thanh pho ho chi minh", "Uppercase + diacritics"),
            ("  Multiple   Spaces  ", "multiple spaces", "Whitespace cleaning"),
            ("P.Tân Định", "p.tan dinh", "Ward with prefix"),
            ("357/28,Ng-T- Thuật", "357/28, ng t thuat", "Comma-space + hyphen handling"),
            ("Test™ Product®", "test product", "Unicode symbol removal"),
        ]
    },
    
    # Suite 2: Aggressive normalization (removes all punctuation)
    'aggressive_normalization': {
        'function': normalize_text_aggressive,
        'description': 'normalize_text_aggressive() - REMOVES ALL PUNCT',
        'cases': [
            ("tp.hcm", "tp hcm", "Dots → spaces"),
            ("q.1", "q 1", "Preserve word boundaries"),
            ("p.ben nghe", "p ben nghe", "Multiple components"),
            ("hello, world!", "hello world", "Remove commas"),
            ("357/28,Ng-T- Thuật", "357 28 ng t thuat", "Real-world messy address"),
            ("TP.HCM/Q.1", "tp hcm q 1", "Multiple separators"),
        ]
    },
    
    # Suite 3: Edge cases and special scenarios
    'edge_cases': {
        'function': normalize_text,
        'description': 'Edge Cases and Special Scenarios',
        'cases': [
            ("", "", "Empty string"),
            ("   ", "", "Only whitespace"),
            ("123", "123", "Numbers only"),
            ("a", "a", "Single character"),
            ("TP.HCM, Quận 1, P.Bến Nghé", "tp.hcm, quan 1, p.ben nghe", "Full address"),
            ("!!!??", "", "Noise punctuation only"),
            ("357/28", "357/28", "Slash preserved in normal mode"),
        ]
    },
    
    # Suite 4: Unicode and special characters
    'unicode_handling': {
        'function': normalize_text,
        'description': 'Unicode and Special Character Handling',
        'cases': [
            ("Đường Nguyễn Huệ", "duong nguyen hue", "Vietnamese Đ"),
            ("Huyện Củ Chi", "huyen cu chi", "Vietnamese Ủ"),
            ("Test™", "test", "Trademark symbol"),
            ("Price: 50€", "price 50", "Euro symbol + colon"),
            ("25°C", "25c", "Degree symbol"),
            ("©2024 Company", "2024 company", "Copyright symbol"),
        ]
    },
    
    # Suite 5: Punctuation behavior
    'punctuation_handling': {
        'function': normalize_text,
        'description': 'Meaningful vs Noise Punctuation',
        'cases': [
            ("Hello, World!", "hello, world", "Keep comma, remove exclamation"),
            ("TP.HCM/Q.1", "tp.hcm/q.1", "Keep dots and slashes"),
            ("What? Why! How:", "what why how", "Remove question/exclamation/colon"),
            ("123-456-789", "123 456 789", "Hyphens become spaces"),
        ]
    },
}


# ========================================================================
# TEST RUNNER (Reusable)
# ========================================================================

def run_test_suite(suite_name: str, suite_config: dict) -> dict:
    """
    Run a single test suite and return results
    """
    print(f"\n✅ {suite_config['description']}")
    print("-" * 70)
    
    results = {
        'suite_name': suite_name,
        'total': 0,
        'passed': 0,
        'failed': 0,
        'failures': []
    }
    
    test_function = suite_config['function']
    
    for input_text, expected, description in suite_config['cases']:
        results['total'] += 1
        
        # Execute test
        actual = test_function(input_text)
        passed = (actual == expected)
        
        # Update statistics
        if passed:
            results['passed'] += 1
            status = "✅"
        else:
            results['failed'] += 1
            status = "❌"
            results['failures'].append({
                'input': input_text,
                'expected': expected,
                'actual': actual,
                'description': description
            })
        
        # Print result
        print(f"{status} '{input_text[:30]:30}' → '{actual[:30]:30}' | {description}")
        
        if not passed:
            print(f"   Expected: '{expected}'")
            print(f"   Actual:   '{actual}'")
    
    return results


def print_test_summary(all_results: list):
    """
    Print comprehensive test summary with statistics
    """
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    # Calculate totals
    total_tests = sum(r['total'] for r in all_results)
    total_passed = sum(r['passed'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)
    
    # Print suite-by-suite results
    print("\nTest Suite Results:")
    print("-" * 70)
    for result in all_results:
        percentage = (result['passed'] / result['total'] * 100) if result['total'] > 0 else 0
        status = "✅" if result['failed'] == 0 else "⚠️"
        print(f"{status} {result['suite_name']:30} | {result['passed']:3}/{result['total']:3} passed ({percentage:5.1f}%)")
    
    # Overall summary
    print("\n" + "="*70)
    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"OVERALL: {total_passed}/{total_tests} tests passed ({overall_percentage:.1f}%)")
    
    if total_failed > 0:
        print(f"\n⚠️  {total_failed} test(s) failed:")
        for result in all_results:
            if result['failures']:
                print(f"\n  Suite: {result['suite_name']}")
                for failure in result['failures']:
                    print(f"    - {failure['description']}")
                    print(f"      Input:    '{failure['input']}'")
                    print(f"      Expected: '{failure['expected']}'")
                    print(f"      Actual:   '{failure['actual']}'")
    else:
        print("✅ All tests passed!")
    
    print("="*70)


# ========================================================================
# MAIN TEST EXECUTION
# ========================================================================

if __name__ == "__main__":
    print("="*70)
    print("LAYER 1: IMPROVED TEXT NORMALIZATION - INTEGRATION TESTS")
    print("="*70)
    
    # Run all test suites
    all_results = []
    for suite_name, suite_config in TEST_SUITES.items():
        result = run_test_suite(suite_name, suite_config)
        all_results.append(result)
    
    # Print summary
    print_test_summary(all_results)
    
    # Print design principles
    print("\n" + "="*70)
    print("KEY IMPROVEMENTS IN V2:")
    print("="*70)
    print("""
1. ✓ Unicode Symbol Removal:
   - Handles ™, ®, ©, €, °, and other special symbols
   - Uses Unicode category filtering (robust and general)
   
2. ✓ Smart Punctuation:
   - Preserves meaningful punctuation (., comma, /) by default
   - Removes noise punctuation (!, ?, ;, :, etc.)
   - Hyphens treated as word separators
   
3. ✓ Space-Preserving Aggressive Mode:
   - "tp.hcm" → "tp hcm" (NOT "tphcm")
   - Preserves word boundaries for downstream parsing
   
4. ✓ Comma-Space Normalization:
   - "357/28,Ng" → "357/28, ng"
   - Fixes missing spaces in messy addresses
   
5. ✓ Two-Mode Design:
   - Normal mode: For parsing (preserve structure)
   - Aggressive mode: For matching (remove all punctuation)

WHEN TO USE WHICH MODE:
   - normalize_text() → When you need to PARSE (Layer 2 needs structure)
   - normalize_text_aggressive() → When you need to MATCH (trie/fuzzy search)

HOW TO USE THIS MODULE:
   from normalizer_v2 import AddressNormalizer, process_full_address
   
   # Option 1: Full pipeline (most common)
   normalizer = AddressNormalizer(data_dir="../data")
   result = normalizer.process("TP.HCM", level='province')  # → "ho chi minh"
   
   # Option 2: Full address parsing
   result = process_full_address("TP.HCM, Quận 1, P.Bến Nghé", data_dir="../data")
   # → {'city': 'ho chi minh', 'district': '1', 'ward': 'ben nghe'}
   
   # Option 3: Layer-by-layer control
   normalized = normalizer.normalize_only("TP.HCM")  # → "tp.hcm"
   expanded = normalizer.expand_only("tp.hcm", 'province')  # → "ho chi minh"

NOTE: Alias generation for trie database is in a separate module (not here).
    """)
    
    print("\n" + "="*70)
    print("READY FOR LAYER 2: Admin Prefix Handler")
    print("="*70)
