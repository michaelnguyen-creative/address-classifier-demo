"""
Test Fix for Issue #1: Compact Text Without Spaces

This tests the preprocessing step that inserts spaces before uppercase letters
to fix compact text like "TỉnhThái Nguyên" → "Tỉnh Thái Nguyên"
"""

from text_normalizer import TextNormalizer

def test_compact_text_preprocessing():
    """
    Test that preprocessing correctly fixes compact text
    """
    print("="*70)
    print("TEST: Compact Text Preprocessing (Issue #1 Fix)")
    print("="*70)
    
    normalizer = TextNormalizer()
    
    # Test cases from the failed tests
    test_cases = [
        # Issue: Compact province names
        ("TỉnhThái Nguyên", "tinh thai nguyen", "Thai Nguyên"),
        ("TỉnhLạng Son", "tinh lang son", "Lạng Son"),
        ("TP.HồChíMinh", "tp ho chi minh", "Hồ Chí Minh"),
        
        # Similar patterns
        ("HuyệnYên Sơn", "huyen yen son", "Yên Sơn"),
        ("QuậnTân Bình", "quan tan binh", "Tân Bình"),
        ("PhườngBến Nghé", "phuong ben nghe", "Bến Nghé"),
        
        # Already correctly formatted (should not change)
        ("Tỉnh Thái Nguyên", "tinh thai nguyen", "Thai Nguyên"),
        ("TP. Hồ Chí Minh", "tp ho chi minh", "Hồ Chí Minh"),
        
        # Edge cases
        ("TPHồChíMinh", "tp ho chi minh", "Hồ Chí Minh"),  # No dot
        ("T.GiangMỹTho", "t giang my tho", "Giang Mỹ Tho"),  # Abbreviated
    ]
    
    print("\nTesting preprocessing + aggressive normalization:")
    print("-"*70)
    
    passed = 0
    failed = 0
    
    for input_text, expected_normalized, entity_name in test_cases:
        # Test with preprocessing (default)
        result_with_prep = normalizer.normalize(input_text, aggressive=True, preprocess=True)
        
        # Test without preprocessing (for comparison)
        result_without_prep = normalizer.normalize(input_text, aggressive=True, preprocess=False)
        
        # Check if preprocessing fixed the issue
        success = (result_with_prep == expected_normalized)
        
        if success:
            passed += 1
            status = "✅"
        else:
            failed += 1
            status = "❌"
        
        print(f"\n{status} '{input_text}'")
        print(f"   Expected:       '{expected_normalized}'")
        print(f"   With preproc:   '{result_with_prep}'")
        print(f"   Without preproc: '{result_without_prep}'")
        if success:
            print(f"   → Can find entity: '{entity_name}'")
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed}/{len(test_cases)} passed ({passed/len(test_cases)*100:.1f}%)")
    print("="*70)
    
    return passed == len(test_cases)


def test_preprocessing_integration():
    """
    Test the complete pipeline: preprocessing → normalization → matching
    """
    print("\n" + "="*70)
    print("TEST: Full Integration with Address Parser")
    print("="*70)
    
    # Import parser to test end-to-end
    from address_parser import AddressParser
    
    parser = AddressParser(data_dir="../Data")
    
    # The problematic test cases from before
    test_cases = [
        ("Liên Minh,,TỉnhThái Nguyên", "Thái Nguyên", "Should find province"),
        ("TT Tân Bình Huyện Yên Sơn, TuyênQuang", "Tuyên Quang", "Should find province"),
        ("357/28,Ng-T- Thuật,P1,Q3,TP.HồChíMinh.", "Hồ Chí Minh", "Should find province"),
    ]
    
    print("\nParsing addresses with preprocessing:")
    print("-"*70)
    
    passed = 0
    for input_addr, expected_province, description in test_cases:
        result = parser.parse(input_addr, debug=False)
        success = (result.province == expected_province)
        
        if success:
            passed += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"\n{status} {description}")
        print(f"   Input:    '{input_addr}'")
        print(f"   Expected: '{expected_province}'")
        print(f"   Got:      '{result.province or 'NOT FOUND'}'")
        print(f"   Valid:    {result.valid}, Method: {result.match_method}")
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed}/{len(test_cases)} passed")
    print("="*70)
    
    return passed == len(test_cases)


if __name__ == "__main__":
    print("="*70)
    print("TESTING ISSUE #1 FIX: Compact Text Preprocessing")
    print("="*70)
    
    # Test 1: Preprocessing function alone
    test1_passed = test_compact_text_preprocessing()
    
    # Test 2: Full integration with parser
    test2_passed = test_preprocessing_integration()
    
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    
    if test1_passed and test2_passed:
        print("✅ All tests PASSED! Issue #1 is FIXED!")
        print("\nThe preprocessing step successfully:")
        print("  - Inserts spaces in compact text")
        print("  - Allows entities to be recognized")
        print("  - Integrates seamlessly with parser")
    else:
        print("⚠️ Some tests failed. Need more investigation.")
        if not test1_passed:
            print("  - Preprocessing function needs adjustment")
        if not test2_passed:
            print("  - Integration with parser needs work")
    
    print("="*70)
