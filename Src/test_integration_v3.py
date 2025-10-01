"""
Integration Test: Three-Tier Address Parser
============================================

Tests the complete system with Trie + LCS + Edit Distance
"""

import sys
sys.path.append('.')

from address_parser_v3 import AddressParser


def test_tier_routing():
    """
    Test that requests are routed to correct tier
    """
    print("\n" + "="*70)
    print("TEST: Tier Routing")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    test_cases = [
        # (input, expected_tier, description)
        ("Hà Nội", "trie", "Clean province name"),
        ("Cầu Diễn, Nam Từ Liêm, Hà Nội", "trie", "Clean full address"),
        ("123 Nguyen Van, Cau Dien, Nam Tu Liem, Ha Noi", "lcs", "Extra words (street number)"),
        ("ha nol", "edit_distance", "Typo in province"),
        ("nam tu leam", "edit_distance", "Typo in district"),
        ("cau dein", "edit_distance", "Typo in ward"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, expected_tier, description in test_cases:
        print(f"\n[TEST] {description}")
        print(f"Input: '{input_text}'")
        
        result = parser.parse(input_text, debug=False)
        
        status = "✓ PASS" if result.match_method == expected_tier else "✗ FAIL"
        if result.match_method == expected_tier:
            passed += 1
        
        print(f"Expected tier: {expected_tier}")
        print(f"Actual tier:   {result.match_method}")
        print(f"Province:      {result.province}")
        print(f"Status:        {status}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


def test_typo_correction():
    """
    Test Edit Distance tier's ability to correct typos
    """
    print("\n" + "="*70)
    print("TEST: Typo Correction (Tier 3)")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    test_cases = [
        # (input_with_typo, expected_province, expected_district, expected_ward)
        ("ha nol", "Hà Nội", None, None),
        ("ha noi nam tu leam", "Hà Nội", "Nam Từ Liêm", None),
        ("cau dein, nam tu liem, ha noi", "Hà Nội", "Nam Từ Liêm", "Cầu Diễn"),
        ("dihn cong, hoang mai, ha noi", "Hà Nội", "Hoàng Mai", "Định Công"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, exp_province, exp_district, exp_ward in test_cases:
        print(f"\n[TEST] '{input_text}'")
        
        result = parser.parse(input_text, debug=False)
        
        # Check if all expected components match
        province_match = (result.province == exp_province) if exp_province else True
        district_match = (result.district == exp_district) if exp_district else True
        ward_match = (result.ward == exp_ward) if exp_ward else True
        
        all_match = province_match and district_match and ward_match
        
        status = "✓ PASS" if all_match else "✗ FAIL"
        if all_match:
            passed += 1
        
        print(f"Province: {result.province} (expected: {exp_province}) {'✓' if province_match else '✗'}")
        print(f"District: {result.district} (expected: {exp_district or 'N/A'}) {'✓' if district_match else '✗'}")
        print(f"Ward:     {result.ward} (expected: {exp_ward or 'N/A'}) {'✓' if ward_match else '✗'}")
        print(f"Method:   {result.match_method}")
        print(f"Status:   {status}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


def test_fallback_chain():
    """
    Test that fallback chain works correctly (Trie → LCS → Edit Distance)
    """
    print("\n" + "="*70)
    print("TEST: Fallback Chain")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    test_cases = [
        # (input, description, should_find_province)
        ("Hà Nội", "Clean - should use Trie", True),
        ("ha noi extra words here", "Extra words - should fallback to LCS", True),
        ("ha nol", "Typo - should fallback to Edit Distance", True),
        ("xyz random garbage", "Unparseable - all tiers should fail", False),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, description, should_find in test_cases:
        print(f"\n[TEST] {description}")
        print(f"Input: '{input_text}'")
        
        result = parser.parse(input_text, debug=False)
        
        found_province = result.province is not None
        
        status = "✓ PASS" if found_province == should_find else "✗ FAIL"
        if found_province == should_find:
            passed += 1
        
        print(f"Expected: {'Found province' if should_find else 'No province'}")
        print(f"Actual:   {'Found ' + result.province if found_province else 'No province'}")
        print(f"Method:   {result.match_method}")
        print(f"Status:   {status}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


def test_confidence_scores():
    """
    Test that confidence scores are appropriate for each tier
    """
    print("\n" + "="*70)
    print("TEST: Confidence Scores")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    test_cases = [
        # (input, expected_tier, min_confidence, max_confidence)
        ("Hà Nội", "trie", 1.0, 1.0),  # Exact match = 1.0
        ("ha noi extra words", "lcs", 0.5, 0.7),  # LCS = 0.5-0.7
        ("ha nol", "edit_distance", 0.3, 0.5),  # Edit = 0.3-0.5
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, expected_tier, min_conf, max_conf in test_cases:
        print(f"\n[TEST] '{input_text}'")
        
        result = parser.parse(input_text, debug=False)
        
        tier_match = result.match_method == expected_tier
        conf_in_range = min_conf <= result.confidence <= max_conf
        
        status = "✓ PASS" if tier_match and conf_in_range else "✗ FAIL"
        if tier_match and conf_in_range:
            passed += 1
        
        print(f"Tier:       {result.match_method} (expected: {expected_tier}) {'✓' if tier_match else '✗'}")
        print(f"Confidence: {result.confidence:.2f} (expected: {min_conf:.2f}-{max_conf:.2f}) {'✓' if conf_in_range else '✗'}")
        print(f"Status:     {status}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


def test_hierarchical_validation():
    """
    Test that hierarchy validation works across all tiers
    """
    print("\n" + "="*70)
    print("TEST: Hierarchical Validation")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    # These should all produce valid, hierarchically consistent results
    test_cases = [
        "Cầu Diễn, Nam Từ Liêm, Hà Nội",  # Clean
        "cau dien nam tu liem ha noi",     # No separators
        "cau dein nam tu liem ha noi",     # Typo in ward
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text in test_cases:
        print(f"\n[TEST] '{input_text}'")
        
        result = parser.parse(input_text, debug=False)
        
        # Check codes exist (proving hierarchy is valid)
        has_province_code = result.province_code is not None
        
        # If we have district, it should have a code
        district_valid = (result.district_code is not None) if result.district else True
        
        # If we have ward, it should have a code
        ward_valid = (result.ward_code is not None) if result.ward else True
        
        all_valid = has_province_code and district_valid and ward_valid
        
        status = "✓ PASS" if all_valid else "✗ FAIL"
        if all_valid:
            passed += 1
        
        print(f"Province: {result.province} (code: {result.province_code}) {'✓' if has_province_code else '✗'}")
        print(f"District: {result.district or 'N/A'} (code: {result.district_code or 'N/A'}) {'✓' if district_valid else '✗'}")
        print(f"Ward:     {result.ward or 'N/A'} (code: {result.ward_code or 'N/A'}) {'✓' if ward_valid else '✗'}")
        print(f"Method:   {result.match_method}")
        print(f"Status:   {status}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


def test_edge_cases():
    """
    Test edge cases and corner scenarios
    """
    print("\n" + "="*70)
    print("TEST: Edge Cases")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    test_cases = [
        # (input, should_succeed, description)
        ("", False, "Empty string"),
        ("   ", False, "Whitespace only"),
        ("xyz", False, "Random text"),
        ("ha", False, "Too short/ambiguous"),
        ("ha noi", True, "Minimal valid input"),
        ("HÀNỘI", True, "All caps with diacritics"),
        ("hànội", True, "All lowercase with diacritics"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, should_succeed, description in test_cases:
        print(f"\n[TEST] {description}")
        print(f"Input: '{input_text}'")
        
        result = parser.parse(input_text, debug=False)
        
        succeeded = result.province is not None
        
        status = "✓ PASS" if succeeded == should_succeed else "✗ FAIL"
        if succeeded == should_succeed:
            passed += 1
        
        print(f"Expected: {'Success' if should_succeed else 'Fail'}")
        print(f"Actual:   {'Success - ' + (result.province or '') if succeeded else 'Fail'}")
        print(f"Status:   {status}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


# ========================================================================
# MAIN TEST RUNNER
# ========================================================================

def run_all_tests():
    """Run complete integration test suite"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + " "*12 + "THREE-TIER ADDRESS PARSER - INTEGRATION TESTS" + " "*11 + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    results = {
        "Tier Routing": test_tier_routing(),
        "Typo Correction": test_typo_correction(),
        "Fallback Chain": test_fallback_chain(),
        "Confidence Scores": test_confidence_scores(),
        "Hierarchical Validation": test_hierarchical_validation(),
        "Edge Cases": test_edge_cases(),
    }
    
    # Summary
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + " "*25 + "FINAL RESULTS" + " "*31 + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n  {status}  {test_name}")
        all_passed = all_passed and passed
    
    print("\n" + "█"*70)
    if all_passed:
        print("█" + " "*68 + "█")
        print("█" + " "*17 + "🎉 ALL INTEGRATION TESTS PASSED! 🎉" + " "*16 + "█")
        print("█" + " "*68 + "█")
        print("█"*70)
        print("\n✅ Three-tier parser (Trie + LCS + Edit Distance) is working correctly!")
        print("✅ Ready for production use!")
        print("\n📊 Coverage Summary:")
        print("   - Tier 1 (Trie): Clean addresses ✓")
        print("   - Tier 2 (LCS): Extra words, reordering ✓")
        print("   - Tier 3 (Edit Distance): Typos, OCR errors ✓")
        print("   - Hierarchical validation ✓")
        print("   - Edge cases ✓")
    else:
        print("█" + " "*68 + "█")
        print("█" + " "*20 + "❌ SOME INTEGRATION TESTS FAILED" + " "*15 + "█")
        print("█" + " "*68 + "█")
        print("█"*70)
        print("\n⚠️  Please review failed tests above.")
    
    print("\n" + "="*70)
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
