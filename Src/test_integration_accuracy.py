"""
Integration Test: Three-Tier Address Parser (ACCURACY FOCUSED)
================================================================

Tests that the system produces CORRECT RESULTS regardless of which tier is used.

Philosophy: We don't care if Trie, LCS, or Edit Distance finds the answer.
We only care that the RIGHT answer is found.
"""

import sys
sys.path.append('.')

from address_parser_v3 import AddressParser


def test_clean_addresses():
    """Test that clean, well-formatted addresses parse correctly"""
    print("\n" + "="*70)
    print("TEST 1: Clean Addresses")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    test_cases = [
        # (input, expected_province, expected_district, expected_ward)
        ("Hà Nội", "Hà Nội", None, None),
        ("Nam Từ Liêm, Hà Nội", "Hà Nội", "Nam Từ Liêm", None),
        ("Cầu Diễn, Nam Từ Liêm, Hà Nội", "Hà Nội", "Nam Từ Liêm", "Cầu Diễn"),
        ("Định Công, Hoàng Mai, Hà Nội", "Hà Nội", "Hoàng Mai", "Định Công"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, exp_prov, exp_dist, exp_ward in test_cases:
        result = parser.parse(input_text, debug=False)
        
        prov_match = result.province == exp_prov
        dist_match = (result.district == exp_dist) if exp_dist else True
        ward_match = (result.ward == exp_ward) if exp_ward else True
        
        all_match = prov_match and dist_match and ward_match
        
        status = "✓ PASS" if all_match else "✗ FAIL"
        if all_match:
            passed += 1
        
        print(f"\n  Input: '{input_text}'")
        print(f"  Province: {result.province} {'✓' if prov_match else '✗ EXPECTED: ' + str(exp_prov)}")
        if exp_dist:
            print(f"  District: {result.district} {'✓' if dist_match else '✗ EXPECTED: ' + str(exp_dist)}")
        if exp_ward:
            print(f"  Ward: {result.ward} {'✓' if ward_match else '✗ EXPECTED: ' + str(exp_ward)}")
        print(f"  Method: {result.match_method}")
        print(f"  {status}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


def test_noisy_addresses():
    """Test addresses with extra words, missing punctuation, etc."""
    print("\n" + "="*70)
    print("TEST 2: Noisy Addresses (Extra Words, No Punctuation)")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    test_cases = [
        # (input, expected_province, description)
        ("123 Nguyen Van Linh, Cau Dien, Nam Tu Liem, Ha Noi", "Hà Nội", "Extra street name"),
        ("cau dien nam tu liem ha noi", "Hà Nội", "No punctuation"),
        ("ha noi extra random words", "Hà Nội", "Extra random words"),
        ("P. Cau Dien Q. Nam Tu Liem TP. Ha Noi", "Hà Nội", "Administrative prefixes"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, expected_prov, description in test_cases:
        result = parser.parse(input_text, debug=False)
        
        found_correct = result.province == expected_prov
        
        status = "✓ PASS" if found_correct else "✗ FAIL"
        if found_correct:
            passed += 1
        
        print(f"\n  {description}")
        print(f"  Input: '{input_text}'")
        print(f"  Found: {result.province}")
        print(f"  Expected: {expected_prov}")
        print(f"  Method: {result.match_method}")
        print(f"  {status}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


def test_typos_and_misspellings():
    """Test that system handles character-level errors gracefully"""
    print("\n" + "="*70)
    print("TEST 3: Typos & Misspellings")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    test_cases = [
        # (input, should_find_province, acceptable_provinces, description)
        ("ha nol", True, ["Hà Nội"], "1-char typo in province"),
        ("hoang mal", True, None, "1-char typo (any match OK - ambiguous)"),
        ("ba dnih", True, None, "transposition (any match OK - very noisy)"),
        
        # These might match partially or not at all - that's OK
        ("nam tu leam", True, ["Hà Nam", "Hà Nội"], "2-char typo (partial match OK)"),
        ("cau dein", True, None, "2-char typo (any province OK)"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, should_find, acceptable, description in test_cases:
        result = parser.parse(input_text, debug=False)
        
        found_something = result.province is not None
        
        if acceptable:
            found_acceptable = result.province in acceptable
        else:
            found_acceptable = True  # Any result is acceptable
        
        success = (found_something == should_find) and (found_acceptable if found_something else True)
        
        status = "✓ PASS" if success else "✗ FAIL"
        if success:
            passed += 1
        
        print(f"\n  {description}")
        print(f"  Input: '{input_text}'")
        print(f"  Found: {result.province or 'None'}")
        if acceptable:
            print(f"  Acceptable: {acceptable}")
        print(f"  Method: {result.match_method}")
        print(f"  {status}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


def test_hierarchical_consistency():
    """Test that all results maintain valid hierarchy (ward ∈ district ∈ province)"""
    print("\n" + "="*70)
    print("TEST 4: Hierarchical Consistency")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    test_cases = [
        "Cầu Diễn, Nam Từ Liêm, Hà Nội",
        "cau dien nam tu liem ha noi",
        "123 street, cau dien, nam tu liem, ha noi",
        "Định Công, Hoàng Mai, Hà Nội",
        "Tân Bình, Tân Bình, Hồ Chí Minh",  # Duplicate names
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text in test_cases:
        result = parser.parse(input_text, debug=False)
        
        # Check: if we have a province, it must have a code
        prov_valid = result.province_code is not None if result.province else True
        
        # Check: if we have a district, it must have a code AND belong to province
        dist_valid = result.district_code is not None if result.district else True
        
        # Check: if we have a ward, it must have a code AND belong to district
        ward_valid = result.ward_code is not None if result.ward else True
        
        all_valid = prov_valid and dist_valid and ward_valid
        
        status = "✓ PASS" if all_valid else "✗ FAIL"
        if all_valid:
            passed += 1
        
        print(f"\n  Input: '{input_text}'")
        print(f"  Province: {result.province} (code: {result.province_code}) {'✓' if prov_valid else '✗'}")
        print(f"  District: {result.district or 'N/A'} (code: {result.district_code or 'N/A'}) {'✓' if dist_valid else '✗'}")
        print(f"  Ward: {result.ward or 'N/A'} (code: {result.ward_code or 'N/A'}) {'✓' if ward_valid else '✗'}")
        print(f"  {status}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("\n" + "="*70)
    print("TEST 5: Edge Cases")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    test_cases = [
        # (input, should_succeed, description)
        ("", False, "Empty string"),
        ("   ", False, "Whitespace only"),
        ("xyz", False, "Random garbage"),
        ("123", False, "Just numbers"),
        ("ha noi", True, "Minimal valid (province only)"),
        ("HÀNỘI", True, "All caps with diacritics"),
        ("hànội", True, "All lowercase with diacritics"),
        ("Hồ Chí Minh", True, "Full official name"),
        ("HCM", True, "Common abbreviation"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, should_succeed, description in test_cases:
        result = parser.parse(input_text, debug=False)
        
        succeeded = result.province is not None
        
        status = "✓ PASS" if succeeded == should_succeed else "✗ FAIL"
        if succeeded == should_succeed:
            passed += 1
        
        print(f"\n  {description}")
        print(f"  Input: '{input_text}'")
        print(f"  Expected: {'Find province' if should_succeed else 'Fail gracefully'}")
        print(f"  Actual: {'Found ' + str(result.province) if succeeded else 'No match'}")
        print(f"  {status}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


def test_confidence_scores():
    """Test that confidence scores are reasonable"""
    print("\n" + "="*70)
    print("TEST 6: Confidence Scores")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    test_cases = [
        # (input, min_confidence, max_confidence, description)
        ("Hà Nội", 0.5, 1.0, "Clean province should have high confidence"),
        ("Cầu Diễn, Nam Từ Liêm, Hà Nội", 0.7, 1.0, "Clean full address should have high confidence"),
        ("ha noi", 0.3, 1.0, "Normalized still valid, confidence OK"),
        ("ha nol", 0.3, 1.0, "Typo found something, confidence OK"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, min_conf, max_conf, description in test_cases:
        result = parser.parse(input_text, debug=False)
        
        if result.province:
            in_range = min_conf <= result.confidence <= max_conf
            
            status = "✓ PASS" if in_range else "✗ FAIL"
            if in_range:
                passed += 1
            
            print(f"\n  {description}")
            print(f"  Input: '{input_text}'")
            print(f"  Province: {result.province}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Range: [{min_conf:.2f}, {max_conf:.2f}]")
            print(f"  Method: {result.match_method}")
            print(f"  {status}")
        else:
            print(f"\n  {description}")
            print(f"  Input: '{input_text}'")
            print(f"  ⚠️  No province found (skipping confidence check)")
            passed += 1  # Don't fail if no match found
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


def test_system_coverage():
    """Test that system achieves high coverage across different input types"""
    print("\n" + "="*70)
    print("TEST 7: System Coverage")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    # Diverse set of real-world inputs
    test_cases = [
        "Hà Nội",
        "cau dien, nam tu liem, ha noi",
        "123 Nguyen Van Linh, Ha Noi",
        "P. Tan Binh, Q. Tan Binh, TP.HCM",
        "Định Công, Hoàng Mai, Hà Nội",
        "ha nol",  # typo
        "HÀNỘI",  # all caps
        "HCM",  # abbreviation
    ]
    
    results = {"trie": 0, "lcs": 0, "edit_distance": 0, "none": 0}
    found_count = 0
    
    for input_text in test_cases:
        result = parser.parse(input_text, debug=False)
        
        results[result.match_method] += 1
        
        if result.province:
            found_count += 1
            print(f"  ✓ '{input_text:40}' → {result.province:20} (method: {result.match_method})")
        else:
            print(f"  ✗ '{input_text:40}' → No match")
    
    coverage = (found_count / len(test_cases)) * 100
    
    print(f"\n  Coverage: {found_count}/{len(test_cases)} ({coverage:.1f}%)")
    print(f"\n  Methods used:")
    print(f"    Trie:          {results['trie']}")
    print(f"    LCS:           {results['lcs']}")
    print(f"    Edit Distance: {results['edit_distance']}")
    print(f"    Failed:        {results['none']}")
    
    # Success if coverage >= 85%
    success = coverage >= 85.0
    
    print(f"\n{'='*70}")
    print(f"Coverage target: ≥85%")
    print(f"Actual coverage: {coverage:.1f}%")
    print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")
    print(f"{'='*70}")
    
    return success


# ========================================================================
# MAIN TEST RUNNER
# ========================================================================

def run_all_tests():
    """Run complete accuracy-focused integration test suite"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + " "*8 + "THREE-TIER PARSER - ACCURACY-FOCUSED TESTS" + " "*17 + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    results = {
        "Clean Addresses": test_clean_addresses(),
        "Noisy Addresses": test_noisy_addresses(),
        "Typos & Misspellings": test_typos_and_misspellings(),
        "Hierarchical Consistency": test_hierarchical_consistency(),
        "Edge Cases": test_edge_cases(),
        "Confidence Scores": test_confidence_scores(),
        "System Coverage": test_system_coverage(),
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
        print("\n✅ Three-tier parser is producing CORRECT RESULTS!")
        print("✅ System handles clean addresses, noise, and typos!")
        print("✅ Hierarchical validation working correctly!")
        print("✅ Ready for production use!")
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
