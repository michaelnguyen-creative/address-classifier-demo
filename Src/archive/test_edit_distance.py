"""
Comprehensive Unit Tests for Edit Distance Matcher (Tier 3)
============================================================

Tests bounded edit distance algorithm and EditDistanceMatcher class
"""

import sys
sys.path.append('.')

from edit_distance_matcher import bounded_edit_distance, EditDistanceMatcher
from trie_parser import normalize_text


# ========================================================================
# TEST SUITE 1: CORE ALGORITHM
# ========================================================================

def test_basic_edit_distance():
    """Test basic edit distance computation"""
    print("\n" + "="*70)
    print("[TEST 1] Basic Edit Distance Computation")
    print("="*70)
    
    test_cases = [
        # (source, target, max_k, expected, description)
        ("cat", "bat", 2, 1, "single substitution"),
        ("ha noi", "ha nol", 2, 1, "typo: i→l"),
        ("cau dien", "cauv dien", 2, 1, "extra character v"),
        ("dinh cong", "dihn cong", 2, 2, "transposition h↔n (Levenshtein=2)"),
        ("test", "test", 2, 0, "exact match"),
        ("abc", "xyz", 2, 3, "all different (exceeds k)"),
        ("short", "verylongstring", 2, 3, "length diff > k"),
        ("", "abc", 2, 3, "empty source (exceeds k)"),
        ("abc", "", 2, 3, "empty target (exceeds k)"),
        ("", "", 2, 0, "both empty"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for s, t, max_k, expected, desc in test_cases:
        result = bounded_edit_distance(s, t, max_k)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        if result == expected:
            passed += 1
        
        print(f"\n  {status}")
        print(f"  Source:   '{s}'")
        print(f"  Target:   '{t}'")
        print(f"  Max k:    {max_k}")
        print(f"  Result:   {result}")
        print(f"  Expected: {expected}")
        print(f"  Case:     {desc}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


# ========================================================================
# TEST SUITE 2: VIETNAMESE ADDRESSES
# ========================================================================

def test_vietnamese_addresses():
    """Test with real Vietnamese address typos"""
    print("\n" + "="*70)
    print("[TEST 2] Vietnamese Address Typos")
    print("="*70)
    
    test_cases = [
        # (input_with_typo, correct_address, expected_distance, description)
        ("ha nol", "ha noi", 1, "province typo i→l"),
        ("nam tu leam", "nam tu liem", 2, "district typo: ea→ie (2 edits)"),
        ("cau dein", "cau dien", 2, "ward typo: ei→ie (2 edits)"),
        ("dihn cong", "dinh cong", 2, "ward transposition (Levenshtein=2)"),
        ("hoang mal", "hoang mai", 1, "district typo i→l"),
        ("tan bnih", "tan binh", 2, "district typo: nh→nh (2 edits)"),
        ("ba dinh", "ba dinh", 0, "exact match"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for typo, correct, expected, desc in test_cases:
        # Normalize both (important!)
        typo_norm = normalize_text(typo)
        correct_norm = normalize_text(correct)
        
        result = bounded_edit_distance(typo_norm, correct_norm, 2)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        if result == expected:
            passed += 1
        
        print(f"\n  {status}")
        print(f"  Input (typo):    '{typo}' → '{typo_norm}'")
        print(f"  Correct:         '{correct}' → '{correct_norm}'")
        print(f"  Edit distance:   {result}")
        print(f"  Expected:        {expected}")
        print(f"  Description:     {desc}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    return passed == total


# ========================================================================
# TEST SUITE 3: MATCHER CLASS
# ========================================================================

def test_matcher_class():
    """Test EditDistanceMatcher class functionality"""
    print("\n" + "="*70)
    print("[TEST 3] EditDistanceMatcher Class")
    print("="*70)
    
    matcher = EditDistanceMatcher(max_distance=2)
    
    # Test Case 1: Basic matching
    print("\n[Test 3.1] Basic Candidate Matching")
    print("-" * 50)
    
    candidates = [
        ("Hà Nội", ["ha", "noi"]),
        ("Hà Nam", ["ha", "nam"]),
        ("Hải Phòng", ["hai", "phong"]),
        ("Hải Dương", ["hai", "duong"])
    ]
    
    # Input with typo: "ha nol" should match "Hà Nội"
    input_tokens = ["ha", "nol"]
    match = matcher.find_best_match(input_tokens, candidates, "province")
    
    test_passed = False
    if match:
        print(f"  Input tokens:    {input_tokens}")
        print(f"  Best match:      {match.entity_name}")
        print(f"  Edit distance:   {match.edit_distance}")
        print(f"  Norm score:      {match.normalized_score:.3f}")
        print(f"  Entity type:     {match.entity_type}")
        
        if match.entity_name == "Hà Nội" and match.edit_distance == 1:
            print(f"  Status:          ✓ PASS")
            test_passed = True
        else:
            print(f"  Status:          ✗ FAIL (expected 'Hà Nội' with distance 1)")
    else:
        print(f"  Status:          ✗ FAIL (no match found)")
    
    # Test Case 2: No match beyond threshold
    print("\n[Test 3.2] Threshold Filtering")
    print("-" * 50)
    
    input_tokens = ["completely", "random", "text"]
    match = matcher.find_best_match(input_tokens, candidates, "province")
    
    if match is None:
        print(f"  Input tokens:    {input_tokens}")
        print(f"  Best match:      None")
        print(f"  Status:          ✓ PASS (correctly rejected)")
        test_passed = test_passed and True
    else:
        print(f"  Input tokens:    {input_tokens}")
        print(f"  Best match:      {match.entity_name}")
        print(f"  Status:          ✗ FAIL (should be None)")
        test_passed = False
    
    # Test Case 3: Tie breaking (prefer shorter distance)
    print("\n[Test 3.3] Tie Breaking")
    print("-" * 50)
    
    candidates_tie = [
        ("Nam Từ Liêm", ["nam", "tu", "liem"]),
        ("Nam Đàn", ["nam", "dan"]),
    ]
    
    # "nam tu leam" should match "Nam Từ Liêm" (distance 1)
    # not "Nam Đàn" (distance > 2)
    input_tokens = ["nam", "tu", "leam"]
    match = matcher.find_best_match(input_tokens, candidates_tie, "district")
    
    if match and match.entity_name == "Nam Từ Liêm":
        print(f"  Input tokens:    {input_tokens}")
        print(f"  Best match:      {match.entity_name}")
        print(f"  Edit distance:   {match.edit_distance}")
        print(f"  Status:          ✓ PASS")
        test_passed = test_passed and True
    else:
        print(f"  Input tokens:    {input_tokens}")
        print(f"  Best match:      {match.entity_name if match else None}")
        print(f"  Status:          ✗ FAIL (expected 'Nam Từ Liêm')")
        test_passed = False
    
    print(f"\n{'='*70}")
    print(f"Matcher class: {'✓ ALL PASS' if test_passed else '✗ SOME FAILED'}")
    print(f"{'='*70}")
    
    return test_passed


# ========================================================================
# TEST SUITE 4: PERFORMANCE & EDGE CASES
# ========================================================================

def test_edge_cases():
    """Test edge cases and performance characteristics"""
    print("\n" + "="*70)
    print("[TEST 4] Edge Cases & Performance")
    print("="*70)
    
    all_passed = True
    
    # Test 4.1: Very long strings
    print("\n[Test 4.1] Long String Handling")
    print("-" * 50)
    
    long_s = "a" * 100
    long_t = "a" * 100
    result = bounded_edit_distance(long_s, long_t, 2)
    
    if result == 0:
        print(f"  Long identical strings: ✓ PASS (distance = {result})")
    else:
        print(f"  Long identical strings: ✗ FAIL (distance = {result}, expected 0)")
        all_passed = False
    
    # Test 4.2: Early termination check
    print("\n[Test 4.2] Early Termination")
    print("-" * 50)
    
    s = "abcdefghij"
    t = "zyxwvutsrq"
    result = bounded_edit_distance(s, t, 2)
    
    if result > 2:
        print(f"  Very different strings: ✓ PASS (distance > 2, terminated early)")
    else:
        print(f"  Very different strings: ✗ FAIL (distance = {result}, expected > 2)")
        all_passed = False
    
    # Test 4.3: Single character differences
    print("\n[Test 4.3] Single Character Operations")
    print("-" * 50)
    
    single_char_tests = [
        ("test", "tesst", 1, "insertion"),
        ("test", "tst", 1, "deletion"),
        ("test", "best", 1, "substitution"),
    ]
    
    for s, t, expected, op in single_char_tests:
        result = bounded_edit_distance(s, t, 2)
        if result == expected:
            print(f"  {op}: ✓ PASS ('{s}' → '{t}', distance = {result})")
        else:
            print(f"  {op}: ✗ FAIL ('{s}' → '{t}', distance = {result}, expected {expected})")
            all_passed = False
    
    print(f"\n{'='*70}")
    print(f"Edge cases: {'✓ ALL PASS' if all_passed else '✗ SOME FAILED'}")
    print(f"{'='*70}")
    
    return all_passed


# ========================================================================
# MAIN TEST RUNNER
# ========================================================================

def run_all_tests():
    """Run all test suites and report results"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + " "*15 + "EDIT DISTANCE MATCHER TEST SUITE" + " "*21 + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    results = {
        "Basic Algorithm": test_basic_edit_distance(),
        "Vietnamese Addresses": test_vietnamese_addresses(),
        "Matcher Class": test_matcher_class(),
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
        print("█" + " "*20 + "🎉 ALL TESTS PASSED! 🎉" + " "*25 + "█")
        print("█" + " "*68 + "█")
        print("█"*70)
        print("\n✅ Edit Distance Matcher is working correctly!")
        print("✅ Ready for integration into address parser.")
    else:
        print("█" + " "*68 + "█")
        print("█" + " "*22 + "❌ SOME TESTS FAILED" + " "*25 + "█")
        print("█" + " "*68 + "█")
        print("█"*70)
        print("\n⚠️  Please review failed tests above.")
    
    print("\n" + "="*70)
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
