"""
Test the trie-based parser implementation
"""

import sys
sys.path.append('.')

from trie_parser import normalize_text, Trie, TrieNode, TrieBasedMatcher


def test_normalization():
    """Test Phase 1: Normalization"""
    print("="*70)
    print("TEST: Normalization")
    print("="*70)
    
    tests = [
        ("Hà Nội", "ha noi"),
        ("Đà Nẵng", "da nang"),
        ("Hồ Chí Minh", "ho chi minh"),
        ("  TP.HCM  ", "tp.hcm"),
        ("Thừa Thiên Huế", "thua thien hue"),
        ("QUẬN 1", "quan 1"),
        ("phường  cầu   diễn", "phuong cau dien"),
    ]
    
    passed = 0
    for input_text, expected in tests:
        result = normalize_text(input_text)
        if result == expected:
            print(f"✓ '{input_text}' → '{result}'")
            passed += 1
        else:
            print(f"✗ '{input_text}' → '{result}' (expected: '{expected}')")
    
    print(f"\nPassed: {passed}/{len(tests)}\n")
    return passed == len(tests)


def test_trie_basic():
    """Test Phase 2: Basic Trie Operations"""
    print("="*70)
    print("TEST: Trie Basic Operations")
    print("="*70)
    
    trie = Trie()
    
    # Insert test data
    entries = [
        ("ha noi", "Hà Nội"),
        ("ho chi minh", "Hồ Chí Minh"),
        ("da nang", "Đà Nẵng"),
        ("can tho", "Cần Thơ"),
    ]
    
    print("\nInserting:")
    for norm, orig in entries:
        trie.insert(norm, orig)
        print(f"  '{norm}' → '{orig}'")
    
    # Search tests
    print("\nSearching:")
    search_tests = [
        ("ha noi", "Hà Nội", True),
        ("ho chi minh", "Hồ Chí Minh", True),
        ("invalid", None, True),
        ("ha", None, True),  # Prefix, not complete word
    ]
    
    passed = 0
    for query, expected, should_pass in search_tests:
        result = trie.search(query)
        if result == expected:
            print(f"✓ search('{query}') → {result}")
            passed += 1
        else:
            print(f"✗ search('{query}') → {result} (expected: {expected})")
    
    print(f"\nPassed: {passed}/{len(search_tests)}\n")
    return passed == len(search_tests)


def test_trie_search_in_text():
    """Test Phase 2: Search in Text"""
    print("="*70)
    print("TEST: Trie Search in Text")
    print("="*70)
    
    trie = Trie()
    trie.insert("ha noi", "Hà Nội")
    trie.insert("ho chi minh", "Hồ Chí Minh")
    trie.insert("quan 1", "Quận 1")
    
    tests = [
        ("dia chi o ha noi", ["Hà Nội"]),
        ("ha noi va ho chi minh", ["Hà Nội", "Hồ Chí Minh"]),
        ("quan 1 ho chi minh", ["Quận 1", "Hồ Chí Minh"]),
        ("khong co gi", []),
    ]
    
    passed = 0
    for text, expected_values in tests:
        matches = trie.search_in_text(text)
        found_values = [m[0] for m in matches]
        
        if set(found_values) == set(expected_values):
            print(f"✓ '{text}' → {found_values}")
            passed += 1
        else:
            print(f"✗ '{text}' → {found_values} (expected: {expected_values})")
    
    print(f"\nPassed: {passed}/{len(tests)}\n")
    return passed == len(tests)


def test_matcher():
    """Test Phase 3: TrieBasedMatcher"""
    print("="*70)
    print("TEST: TrieBasedMatcher")
    print("="*70)
    
    matcher = TrieBasedMatcher()
    
    # Build with test data
    provinces = ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng"]
    districts = ["Hoàng Mai", "Quận 1", "Hải Châu"]
    wards = ["Định Công", "Bến Nghé", "Hòa Thuận Tây"]
    
    matcher.build_from_lists(provinces, districts, wards)
    
    tests = [
        ("Định Công, Hoàng Mai, Hà Nội", 
         {"province": "Hà Nội", "district": "Hoàng Mai", "ward": "Định Công"}),
        
        ("Quận 1, Hồ Chí Minh",
         {"province": "Hồ Chí Minh", "district": "Quận 1", "ward": ""}),
        
        ("Hải Châu, Đà Nẵng",
         {"province": "Đà Nẵng", "district": "Hải Châu", "ward": ""}),
        
        ("Hà Nội",
         {"province": "Hà Nội", "district": "", "ward": ""}),
    ]
    
    passed = 0
    for addr, expected in tests:
        result = matcher.match(addr)
        
        if result == expected:
            print(f"✓ '{addr}'")
            print(f"  → {result}")
            passed += 1
        else:
            print(f"✗ '{addr}'")
            print(f"  Got:      {result}")
            print(f"  Expected: {expected}")
    
    print(f"\nPassed: {passed}/{len(tests)}\n")
    return passed == len(tests)


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("TRIE-BASED PARSER - TEST SUITE")
    print("="*70 + "\n")
    
    all_passed = True
    
    all_passed &= test_normalization()
    all_passed &= test_trie_basic()
    all_passed &= test_trie_search_in_text()
    all_passed &= test_matcher()
    
    print("="*70)
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("="*70)


if __name__ == "__main__":
    main()
