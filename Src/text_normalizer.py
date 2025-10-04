"""
Layer 1: Generic Text Normalization (Domain-Agnostic)

DESIGN PRINCIPLES:
    1. Domain-agnostic: Works with any character mapping
    2. Single Responsibility: Only normalizes text
    3. No business logic: Doesn't know about prefixes, abbreviations, etc.
    4. Configurable: Support multiple normalization strategies

USAGE:
    # Vietnamese normalization
    normalizer = TextNormalizer(VIETNAMESE_CHAR_MAP)
    result = normalizer.normalize("TP.HCM")  # → "tp.hcm"
    
    # Custom normalization
    custom_map = {'ñ': 'n', 'ç': 'c'}
    normalizer = TextNormalizer(custom_map)
    result = normalizer.normalize("España")  # → "espana"
"""

import re
import string
from typing import List, Dict, Optional


# ========================================================================
# VIETNAMESE CHARACTER MAPPING (Can be imported separately)
# ========================================================================

VIETNAMESE_CHAR_MAP = {
    # Lowercase vowels with tones
    'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
    'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
    'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    'đ': 'd',
    'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
    'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
    'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
    'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
    'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
    'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
    'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    # Uppercase
    'À': 'a', 'Á': 'a', 'Ả': 'a', 'Ã': 'a', 'Ạ': 'a',
    'Ă': 'a', 'Ằ': 'a', 'Ắ': 'a', 'Ẳ': 'a', 'Ẵ': 'a', 'Ặ': 'a',
    'Â': 'a', 'Ầ': 'a', 'Ấ': 'a', 'Ẩ': 'a', 'Ẫ': 'a', 'Ậ': 'a',
    'Đ': 'd',
    'È': 'e', 'É': 'e', 'Ẻ': 'e', 'Ẽ': 'e', 'Ẹ': 'e',
    'Ê': 'e', 'Ề': 'e', 'Ế': 'e', 'Ể': 'e', 'Ễ': 'e', 'Ệ': 'e',
    'Ì': 'i', 'Í': 'i', 'Ỉ': 'i', 'Ĩ': 'i', 'Ị': 'i',
    'Ò': 'o', 'Ó': 'o', 'Ỏ': 'o', 'Õ': 'o', 'Ọ': 'o',
    'Ô': 'o', 'Ồ': 'o', 'Ố': 'o', 'Ổ': 'o', 'Ỗ': 'o', 'Ộ': 'o',
    'Ơ': 'o', 'Ờ': 'o', 'Ớ': 'o', 'Ở': 'o', 'Ỡ': 'o', 'Ợ': 'o',
    'Ù': 'u', 'Ú': 'u', 'Ủ': 'u', 'Ũ': 'u', 'Ụ': 'u',
    'Ư': 'u', 'Ừ': 'u', 'Ứ': 'u', 'Ử': 'u', 'Ữ': 'u', 'Ự': 'u',
    'Ỳ': 'y', 'Ý': 'y', 'Ỷ': 'y', 'Ỹ': 'y', 'Ỵ': 'y',
}


# ========================================================================
# TEXT NORMALIZER CLASS (Layer 1)
# ========================================================================

class TextNormalizer:
    """
    Generic text normalizer for any language/domain
    
    Responsibilities:
        - Character normalization (diacritics → ASCII)
        - Case normalization (uppercase → lowercase)
        - Whitespace cleaning
        - Optional punctuation removal
    
    Does NOT handle:
        - Administrative prefixes (that's Layer 2)
        - Abbreviation expansion (that's Layer 2)
        - Domain-specific logic
    
    Design:
        - Configurable via character map
        - Reusable across domains
        - Efficient batch processing
    
    Examples:
        # Vietnamese addresses
        normalizer = TextNormalizer(VIETNAMESE_CHAR_MAP)
        normalizer.normalize("TP.HCM") → "tp.hcm"
        
        # Spanish text
        spanish_map = {'ñ': 'n', 'ç': 'c', 'á': 'a', ...}
        normalizer = TextNormalizer(spanish_map)
        normalizer.normalize("España") → "espana"
    """
    
    def __init__(
        self, 
        char_map: Optional[Dict[str, str]] = None,
        preserve_dots: bool = True,
        preserve_numbers: bool = True
    ):
        """
        Initialize normalizer with character mapping
        
        Args:
            char_map: Character replacement mapping (e.g., Vietnamese diacritics)
                     If None, only lowercase/whitespace cleaning is performed
            preserve_dots: Keep dots in output (needed for prefix detection)
            preserve_numbers: Keep numeric characters (needed for addresses like "Q.1")
        
        Design note:
            We use dependency injection (char_map parameter) to make this
            class reusable for any language, not just Vietnamese.
        """
        self.char_map = char_map or {}
        self.preserve_dots = preserve_dots
        self.preserve_numbers = preserve_numbers
        
        # Pre-compile regex patterns for efficiency
        self._whitespace_pattern = re.compile(r'\s+')
        
        # Build punctuation translation table (exclude dots if needed)
        if preserve_dots:
            # Remove dots from punctuation set
            punct_to_remove = string.punctuation.replace('.', '')
        else:
            punct_to_remove = string.punctuation
        
        self._punct_translator = str.maketrans('', '', punct_to_remove)
    
    def normalize(self, text: str, aggressive: bool = False) -> str:
        """
        Normalize text using configured strategy
        
        Algorithm:
            1. Lowercase
            2. Map special characters using char_map
            3. Clean whitespace
            4. Optionally remove punctuation (if aggressive=True)
        
        Args:
            text: Raw input text
            aggressive: If True, remove ALL punctuation (including dots)
        
        Returns:
            Normalized text
        
        Examples:
            normalize("TP.HCM") → "tp.hcm"  (dots preserved)
            normalize("TP.HCM", aggressive=True) → "tphcm"  (dots removed)
            normalize("Quận 1") → "quan 1"
            normalize("Phường Bến Nghé") → "phuong ben nghe"
        
        Complexity:
            Time: O(n) where n = length of text
            Space: O(n) for result string
        """
        if not text:
            return ""
        
        # Step 1: Lowercase
        text = text.lower()
        
        # Step 2: Character mapping (diacritics removal)
        if self.char_map:
            text = self._apply_char_map(text)
        
        # Step 3: Whitespace cleaning
        text = self._clean_whitespace(text)
        
        # Step 4: Punctuation removal (if aggressive mode)
        if aggressive:
            text = self._remove_punctuation(text, remove_all=True)
        elif not self.preserve_dots:
            text = self._remove_punctuation(text, remove_all=False)
        
        return text.strip()
    
    def normalize_aggressive(self, text: str) -> str:
        """
        Convenience method: Aggressive normalization with all punctuation removed
        
        Equivalent to: normalize(text, aggressive=True)
        
        Use when:
            - You've already extracted prefix information
            - You need clean text for final matching
            - Dots are no longer needed
        
        Args:
            text: Input text
        
        Returns:
            Aggressively normalized text (no punctuation)
        
        Examples:
            normalize_aggressive("tp.hcm") → "tphcm"
            normalize_aggressive("q.1") → "q1"
            normalize_aggressive("p.ben nghe") → "pben nghe"
        """
        return self.normalize(text, aggressive=True)
    
    def normalize_batch(
        self, 
        texts: List[str], 
        aggressive: bool = False
    ) -> List[str]:
        """
        Normalize multiple texts efficiently
        
        More efficient than calling normalize() in a loop because:
            - Single method call overhead
            - Potential for future optimizations (parallel processing)
        
        Args:
            texts: List of texts to normalize
            aggressive: Use aggressive normalization
        
        Returns:
            List of normalized texts
        
        Complexity:
            Time: O(n*m) where n=number of texts, m=avg text length
            Space: O(n*m) for results
        """
        return [self.normalize(text, aggressive=aggressive) for text in texts]
    
    # ========================================================================
    # INTERNAL HELPER METHODS
    # ========================================================================
    
    def _apply_char_map(self, text: str) -> str:
        """
        Apply character mapping for diacritic removal
        
        Strategy:
            Use character-by-character mapping for simplicity
            Could optimize with str.translate() if char_map is large
        
        Args:
            text: Input text
        
        Returns:
            Text with characters mapped
        """
        result = []
        for char in text:
            result.append(self.char_map.get(char, char))
        return ''.join(result)
    
    def _clean_whitespace(self, text: str) -> str:
        """
        Clean and normalize whitespace
        
        Operations:
            - Replace multiple spaces with single space
            - Remove leading/trailing whitespace
        
        Args:
            text: Input text
        
        Returns:
            Text with cleaned whitespace
        """
        # Use pre-compiled regex for efficiency
        return self._whitespace_pattern.sub(' ', text).strip()
    
    def _remove_punctuation(self, text: str, remove_all: bool = False) -> str:
        """
        Remove punctuation from text
        
        Args:
            text: Input text
            remove_all: If True, remove ALL punctuation including dots
        
        Returns:
            Text with punctuation removed
        """
        if remove_all:
            # Remove everything in string.punctuation
            translator = str.maketrans('', '', string.punctuation)
            return text.translate(translator)
        else:
            # Use pre-configured translator (may preserve dots)
            return text.translate(self._punct_translator)
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_config(self) -> Dict:
        """
        Get current normalizer configuration
        
        Useful for:
            - Debugging
            - Serialization
            - Logging
        
        Returns:
            Dictionary with current configuration
        """
        return {
            'has_char_map': bool(self.char_map),
            'char_map_size': len(self.char_map),
            'preserve_dots': self.preserve_dots,
            'preserve_numbers': self.preserve_numbers,
        }


# ========================================================================
# CONVENIENCE FUNCTIONS (Backward compatibility)
# ========================================================================

# Create default Vietnamese normalizer
_default_vietnamese_normalizer = TextNormalizer(VIETNAMESE_CHAR_MAP)


def normalize_text(text: str) -> str:
    """
    Convenience function: Vietnamese text normalization (dots preserved)
    
    Backward compatible with existing code.
    
    Args:
        text: Raw Vietnamese text
    
    Returns:
        Normalized text with dots preserved
    
    Examples:
        normalize_text("TP.HCM") → "tp.hcm"
        normalize_text("Quận 1") → "quan 1"
    """
    return _default_vietnamese_normalizer.normalize(text, aggressive=False)


def normalize_text_aggressive(text: str) -> str:
    """
    Convenience function: Aggressive Vietnamese normalization (remove all punctuation)
    
    Backward compatible with existing code.
    
    Args:
        text: Raw Vietnamese text
    
    Returns:
        Normalized text with all punctuation removed
    
    Examples:
        normalize_text_aggressive("tp.hcm") → "tphcm"
        normalize_text_aggressive("q.1") → "q1"
    """
    return _default_vietnamese_normalizer.normalize_aggressive(text)



# ========================================================================
# TEST DATA (Easily Extensible)
# ========================================================================

TEST_CASES = {
    # Test Suite 1: Basic Vietnamese Normalization
    'vietnamese_basic': {
        'description': 'Vietnamese Normalization (Dots Preserved)',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'preserve_dots': True
        },
        'cases': [
            {
                'input': "TP.HCM",
                'expected': "tp.hcm",
                'description': "Keep dots for Layer 2"
            },
            {
                'input': "Quận 1",
                'expected': "quan 1",
                'description': "Remove diacritics"
            },
            {
                'input': "Phường Bến Nghé",
                'expected': "phuong ben nghe",
                'description': "Full normalization"
            },
            {
                'input': "THÀNH PHỐ HỒ CHÍ MINH",
                'expected': "thanh pho ho chi minh",
                'description': "Uppercase + diacritics"
            },
            {
                'input': "  Multiple   Spaces  ",
                'expected': "multiple spaces",
                'description': "Whitespace cleaning"
            },
            {
                'input': "P.Tân Định",
                'expected': "p.tan dinh",
                'description': "Ward with prefix"
            },
            # ✅ EASY TO ADD MORE:
            # Just uncomment and add your cases here:
            # {
            #     'input': "Your test input",
            #     'expected': "expected output",
            #     'description': "What this tests"
            # },
        ]
    },
    
    # Test Suite 2: Aggressive Normalization
    'aggressive_mode': {
        'description': 'Aggressive Normalization (Remove All Punctuation)',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'preserve_dots': False
        },
        'cases': [
            {
                'input': "tp.hcm",
                'expected': "tp hcm",
                'description': "Remove dots"
            },
            {
                'input': "q.1",
                'expected': "q 1",
                'description': "Remove dots from numbers"
            },
            {
                'input': "p.ben nghe",
                'expected': "p ben nghe",
                'description': "Remove dots from names"
            },
            {
                'input': "hello, world!",
                'expected': "hello world",
                'description': "Remove commas and exclamation"
            },
            # ✅ ADD MORE AGGRESSIVE MODE TESTS HERE
        ]
    },
    
    # Test Suite 3: Domain-Agnostic Mode
    'domain_agnostic': {
        'description': 'Domain-Agnostic Mode (No Character Map)',
        'normalizer_config': {
            'char_map': None,
            'preserve_dots': True
        },
        'cases': [
            {
                'input': "HELLO WORLD",
                'expected': "hello world",
                'description': "Just lowercase"
            },
            {
                'input': "Multiple   Spaces",
                'expected': "multiple spaces",
                'description': "Whitespace cleaning"
            },
            {
                'input': "No.Dots.Removed",
                'expected': "no.dots.removed",
                'description': "Dots preserved"
            },
            # ✅ ADD MORE DOMAIN-AGNOSTIC TESTS HERE
        ]
    },
    
    # Test Suite 4: Edge Cases
    'edge_cases': {
        'description': 'Edge Cases and Special Scenarios',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'preserve_dots': True
        },
        'cases': [
            {
                'input': "",
                'expected': "",
                'description': "Empty string"
            },
            {
                'input': "   ",
                'expected': "",
                'description': "Only whitespace"
            },
            {
                'input': "123",
                'expected': "123",
                'description': "Numbers only"
            },
            {
                'input': "!!!",
                'expected': "",
                'description': "Punctuation only (removed)"
            },
            {
                'input': "a",
                'expected': "a",
                'description': "Single character"
            },
            {
                'input': "TP.HCM, Quận 1, P.Bến Nghé",
                'expected': "tp.hcm quan 1 p.ben nghe",
                'description': "Full address with commas"
            },
            # ✅ ADD MORE EDGE CASES HERE
        ]
    },
    
    # Test Suite 5: Unicode and Special Characters
    'unicode_handling': {
        'description': 'Unicode and Special Character Handling',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'preserve_dots': True
        },
        'cases': [
            {
                'input': "Đường Nguyễn Huệ",
                'expected': "duong nguyen hue",
                'description': "Vietnamese Đ character"
            },
            {
                'input': "Café",
                'expected': "cafe",
                'description': "French accent (é)"
            },
            {
                'input': "Test™",
                'expected': "test",
                'description': "Trademark symbol removal"
            },
            # ✅ ADD MORE UNICODE TESTS HERE
        ]
    },
}


# ========================================================================
# TEST BATCH DATA (For performance testing)
# ========================================================================

BATCH_TEST_DATA = {
    'sample_addresses': {
        'description': 'Batch processing of addresses',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'preserve_dots': True
        },
        'batch_input': [
            "TP.HCM",
            "Quận 1",
            "Phường Bến Nghé",
            "Hà Nội",
            "THÀNH PHỐ ĐÀ NẴNG"
        ],
        'expected_output': [
            "tp.hcm",
            "quan 1",
            "phuong ben nghe",
            "ha noi",
            "thanh pho da nang"
        ]
    },
}


# ========================================================================
# REUSABLE TEST RUNNER FUNCTIONS
# ========================================================================

def run_test_suite(suite_name: str, suite_config: dict) -> dict:
    """
    Run a single test suite and return results
    
    Args:
        suite_name: Name of the test suite
        suite_config: Configuration dictionary containing:
            - description: Suite description
            - normalizer_config: Config for TextNormalizer
            - cases: List of test cases
    
    Returns:
        Dictionary with test results and statistics
    """
    print(f"\n✅ {suite_config['description']}")
    print("-" * 70)
    
    # Create normalizer with suite config
    normalizer = TextNormalizer(**suite_config['normalizer_config'])
    
    results = {
        'suite_name': suite_name,
        'total': 0,
        'passed': 0,
        'failed': 0,
        'failures': []
    }
    
    # Run each test case
    for case in suite_config['cases']:
        results['total'] += 1
        
        # Execute test
        actual = normalizer.normalize(case['input'])
        expected = case['expected']
        passed = (actual == expected)
        
        # Update statistics
        if passed:
            results['passed'] += 1
            status = "✅"
        else:
            results['failed'] += 1
            status = "❌"
            results['failures'].append({
                'input': case['input'],
                'expected': expected,
                'actual': actual,
                'description': case['description']
            })
        
        # Print result
        print(f"{status} '{case['input'][:30]:30}' → '{actual[:30]:30}' | {case['description']}")
        
        if not passed:
            print(f"   Expected: '{expected}'")
            print(f"   Actual:   '{actual}'")
    
    return results


def run_batch_test(test_name: str, test_config: dict) -> dict:
    """
    Run a batch processing test
    
    Args:
        test_name: Name of the batch test
        test_config: Configuration dictionary
    
    Returns:
        Test results
    """
    print(f"\n✅ {test_config['description']}")
    print("-" * 70)
    
    normalizer = TextNormalizer(**test_config['normalizer_config'])
    
    # Execute batch
    actual_output = normalizer.normalize_batch(test_config['batch_input'])
    expected_output = test_config['expected_output']
    
    # Check results
    passed = (actual_output == expected_output)
    
    print(f"Input ({len(test_config['batch_input'])} items):")
    for item in test_config['batch_input']:
        print(f"  - {item}")
    
    print(f"\nOutput:")
    for item in actual_output:
        print(f"  - {item}")
    
    if passed:
        print("\n✅ Batch test PASSED")
    else:
        print("\n❌ Batch test FAILED")
        print(f"Expected: {expected_output}")
        print(f"Actual:   {actual_output}")
    
    return {
        'test_name': test_name,
        'passed': passed,
        'input_count': len(test_config['batch_input'])
    }


def run_convenience_function_tests() -> dict:
    """
    Test convenience functions for backward compatibility
    """
    print("\n✅ Backward Compatibility (Convenience Functions)")
    print("-" * 70)
    
    test_input = "TP.HCM"
    
    result1 = normalize_text(test_input)
    result2 = normalize_text_aggressive(test_input)
    
    print(f"normalize_text('{test_input}') → '{result1}'")
    print(f"normalize_text_aggressive('{test_input}') → '{result2}'")
    
    # Verify expected behavior
    expected_normal = "tp.hcm"
    expected_aggressive = "tp hcm"
    
    passed = (result1 == expected_normal and result2 == expected_aggressive)
    
    return {
        'passed': passed,
        'test_count': 2
    }


def print_summary(all_results: list, batch_results: list, convenience_result: dict):
    """
    Print comprehensive test summary with statistics
    
    Args:
        all_results: List of test suite results
        batch_results: List of batch test results
        convenience_result: Result from convenience function tests
    """
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    # Calculate totals
    total_tests = sum(r['total'] for r in all_results)
    total_passed = sum(r['passed'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)
    
    # Add batch and convenience tests
    batch_passed = sum(1 for r in batch_results if r['passed'])
    total_tests += len(batch_results) + convenience_result['test_count']
    total_passed += batch_passed + (convenience_result['test_count'] if convenience_result['passed'] else 0)
    
    # Print suite-by-suite results
    print("\nTest Suite Results:")
    print("-" * 70)
    for result in all_results:
        percentage = (result['passed'] / result['total'] * 100) if result['total'] > 0 else 0
        status = "✅" if result['failed'] == 0 else "⚠️"
        print(f"{status} {result['suite_name']:20} | {result['passed']:3}/{result['total']:3} passed ({percentage:5.1f}%)")
    
    # Print batch test results
    if batch_results:
        print(f"\n{'✅' if batch_passed == len(batch_results) else '⚠️'} Batch Tests: {batch_passed}/{len(batch_results)} passed")
    
    # Print convenience function results
    status = "✅" if convenience_result['passed'] else "❌"
    print(f"{status} Convenience Functions: {'PASSED' if convenience_result['passed'] else 'FAILED'}")
    
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
    print("LAYER 1: TEXT NORMALIZER - EXTENSIBLE TEST SUITE")
    print("="*70)
    
    # Run all test suites
    all_results = []
    for suite_name, suite_config in TEST_CASES.items():
        result = run_test_suite(suite_name, suite_config)
        all_results.append(result)
    
    # Run batch tests
    batch_results = []
    for test_name, test_config in BATCH_TEST_DATA.items():
        result = run_batch_test(test_name, test_config)
        batch_results.append(result)
    
    # Run convenience function tests
    convenience_result = run_convenience_function_tests()
    
    # Print summary
    print_summary(all_results, batch_results, convenience_result)
    
    # Print design principles
    print("\n" + "="*70)
    print("KEY DESIGN PRINCIPLES:")
    print("="*70)
    print("""
1. Domain-Agnostic:
   - Works with any character map (Vietnamese, Spanish, etc.)
   - No hardcoded assumptions about prefixes or abbreviations
   
2. Single Responsibility:
   - Only normalizes text
   - Doesn't know about TP/Q/P or administrative levels
   
3. Configurable:
   - Can preserve or remove dots
   - Can preserve or remove numbers
   - Can use any character mapping
   
4. Efficient:
   - Pre-compiled regex patterns
   - Batch processing support
   - O(n) time complexity
   
5. Extensible:
   - Easy to add new normalization strategies
   - Can be subclassed for custom behavior
   
6. EASY TO EXTEND TESTS:
   - Add new test cases to TEST_CASES dictionary
   - Add new test suites by creating new entries
   - No code changes needed to test execution logic
    """)
    
    print("\n" + "="*70)
    print("HOW TO ADD NEW TEST CASES:")
    print("="*70)
    print("""
Method 1: Add to existing suite
    Navigate to TEST_CASES['vietnamese_basic']['cases'] and add:
    {
        'input': "Your Input",
        'expected': "expected output",
        'description': "What this tests"
    }

Method 2: Create new test suite
    TEST_CASES['my_new_suite'] = {
        'description': 'My Test Suite',
        'normalizer_config': {...},
        'cases': [...]
    }

Method 3: Add batch test
    BATCH_TEST_DATA['my_batch'] = {
        'description': 'My Batch Test',
        'normalizer_config': {...},
        'batch_input': [...],
        'expected_output': [...]
    }
    """)
    
    print("\n✅ Test suite completed!")


# ========================================================================
# EXAMPLE: EXTENDING WITH CUSTOM TEST SUITE
# ========================================================================

def add_custom_test_suite():
    """
    Example showing how to add a custom test suite programmatically
    
    This function demonstrates extending tests without modifying the main
    TEST_CASES dictionary
    """
    custom_suite = {
        'description': 'Custom Performance Tests',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'preserve_dots': True
        },
        'cases': [
            {
                'input': "Very Long Address String " * 10,
                'expected': "very long address string " * 10,
                'description': "Long text handling"
            },
            # Add more custom cases...
        ]
    }
    
    # Run the custom suite
    result = run_test_suite('custom_performance', custom_suite)
    return result


# Uncomment to test custom suite extension:
# if __name__ == "__main__":
#     custom_result = add_custom_test_suite()
#     print(f"\nCustom suite: {custom_result['passed']}/{custom_result['total']} passed")
