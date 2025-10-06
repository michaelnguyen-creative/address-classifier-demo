"""
Vietnamese Address Text Normalization v2 - Clean Separation of Concerns

ARCHITECTURE:
    Layer 1: Generic normalization (domain-agnostic)
    Layer 2: Admin prefix handling (Vietnamese-specific) 
    Layer 3: Alias generation (for trie insertion)

DESIGN PRINCIPLE:
    Each layer has single responsibility and doesn't know about other layers

FLOW:
    "TP.HCM, Quận 1"
    → [Layer 1] → "tp.hcm, quan 1"  (lowercase, remove diacritics, KEEP dots)
    → [Layer 2] → "ho chi minh", "1"  (expand prefixes, extract core)
    → [Layer 3] → ["ho chi minh", "hcm", ...], ["1"]  (generate aliases)
"""

import re
import string
from typing import List, Set


# ========================================================================
# VIETNAMESE CHARACTER MAPPING (Domain-specific but pure data)
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
# LAYER 1: GENERIC TEXT NORMALIZATION (Domain-Agnostic)
# ========================================================================

def normalize_text(text: str) -> str:
    """
    Layer 1: Generic text normalization
    
    Operations:
        1. Lowercase
        2. Remove Vietnamese diacritics
        3. Clean whitespace
        4. PRESERVE dots (needed for Layer 2)
    
    DOES NOT:
        - Know about TP, Q, P, etc. (that's Layer 2)
        - Remove administrative prefixes
        - Expand abbreviations
    
    Examples:
        "TP.HCM" → "tp.hcm"  (lowercase, keep dots!)
        "Quận 1" → "quan 1"  (remove diacritics)
        "Phường Bến Nghé" → "phuong ben nghe"
    
    Args:
        text: Raw input text
    
    Returns:
        Normalized text with dots preserved
    """
    # Step 1: Lowercase
    text = text.lower()
    
    # Step 2: Map Vietnamese characters to ASCII
    result = []
    for char in text:
        result.append(VIETNAMESE_CHAR_MAP.get(char, char))
    text = ''.join(result)
    
    # Step 3: Clean whitespace (but preserve structure)
    text = ' '.join(text.split())
    
    return text.strip()


def normalize_text_aggressive(text: str) -> str:
    """
    Layer 1 variant: More aggressive normalization
    
    Additional operations:
        - Remove ALL punctuation (including dots)
        - More aggressive whitespace cleaning
    
    Use when:
        - You've already extracted prefix information
        - You need clean text for final matching
    
    Examples:
        "tp.hcm" → "tphcm"
        "q.1" → "q1"
    
    Args:
        text: Partially normalized text
    
    Returns:
        Fully cleaned text
    """
    # Start with basic normalization
    text = normalize_text(text)
    
    # Remove ALL punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Aggressive whitespace cleaning
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


# ========================================================================
# TEST DATA (Easily Extensible)
# ========================================================================

TEST_SUITES = {
    # Suite 1: Basic normalization with dot preservation
    'basic_normalization': {
        'function': normalize_text,
        'description': 'normalize_text() - PRESERVES DOTS',
        'cases': [
            # (input, expected_output, description)
            ("TP.HCM", "tp.hcm", "Keep dots for Layer 2"),
            ("Quận 1", "quan 1", "Remove diacritics"),
            ("Phường Bến Nghé", "phuong ben nghe", "Full normalization"),
            ("THÀNH PHỐ HỒ CHÍ MINH", "thanh pho ho chi minh", "Uppercase + diacritics"),
            ("  Multiple   Spaces  ", "multiple spaces", "Whitespace cleaning"),
            ("P.Tân Định", "p.tan dinh", "Ward with prefix"),
            # ✅ ADD MORE BASIC TESTS HERE:
            # ("Your Input", "expected output", "What this tests"),
        ]
    },
    
    # Suite 2: Aggressive normalization (removes all punctuation)
    'aggressive_normalization': {
        'function': normalize_text_aggressive,
        'description': 'normalize_text_aggressive() - REMOVES DOTS',
        'cases': [
            ("tp.hcm", "tp hcm", "Remove dots"),
            ("q.1", "q 1", "Remove dots from numbers"),
            ("p.ben nghe", "p ben nghe", "Remove dots from names"),
            ("hello, world!", "hello world", "Remove commas and exclamation"),
            # ✅ ADD MORE AGGRESSIVE TESTS HERE:
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
            ("TP.HCM, Quận 1, P.Bến Nghé", "tp.hcm, quan 1, p.ben nghe", "Full address with commas"),
            # ✅ ADD MORE EDGE CASES HERE:
        ]
    },
    
    # Suite 4: Unicode and special characters
    'unicode_handling': {
        'function': normalize_text,
        'description': 'Unicode and Special Character Handling',
        'cases': [
            ("Đường Nguyễn Huệ", "duong nguyen hue", "Vietnamese Đ character"),
            ("Huyện Củ Chi", "huyen cu chi", "Vietnamese Ủ character"),
            ("Thị Xã Thuận An", "thi xa thuan an", "Multiple diacritics"),
            # ✅ ADD MORE UNICODE TESTS HERE:
        ]
    },
}


# ========================================================================
# TEST RUNNER (Reusable)
# ========================================================================

def run_test_suite(suite_name: str, suite_config: dict) -> dict:
    """
    Run a single test suite and return results
    
    Args:
        suite_name: Name of the test suite
        suite_config: Configuration containing:
            - function: Function to test
            - description: Suite description
            - cases: List of (input, expected, description) tuples
    
    Returns:
        Dictionary with test results and statistics
    """
    print(f"\n{suite_config['description']}")
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
    
    Args:
        all_results: List of test suite results
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
        print(f"{status} {result['suite_name']:25} | {result['passed']:3}/{result['total']:3} passed ({percentage:5.1f}%)")
    
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
    print("LAYER 1: GENERIC NORMALIZATION TESTS")
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
    print("KEY PRINCIPLE: Layer 1 is DOMAIN-AGNOSTIC")
    print("="*70)
    print("""
Layer 1 (normalize_text):
  ✅ DOES: lowercase, remove diacritics, clean whitespace
  ❌ DOES NOT: know about TP/Q/P, expand abbreviations, remove prefixes
  
Why preserve dots?
  - Layer 2 needs them to detect "TP.", "Q.", "P."
  - Removing dots too early destroys information
  - Separation of concerns: Layer 1 = generic, Layer 2 = domain-specific

HOW TO ADD NEW TESTS:
  1. Navigate to TEST_SUITES dictionary above
  2. Find the appropriate suite (or create a new one)
  3. Add a tuple: ("input", "expected", "description")
  4. Run this file to see your test executed!
  
Example:
  TEST_SUITES['basic_normalization']['cases'].append(
      ("Thành Phố Cần Thơ", "thanh pho can tho", "Can Tho city")
  )
    """)
