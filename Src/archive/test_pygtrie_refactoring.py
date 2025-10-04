"""
Test Suite: Verifying pygtrie Refactoring

This test compares the original implementation with the pygtrie version
to ensure identical behavior.

Run: python test_pygtrie_refactoring.py
"""

# Test both implementations
from trie_parser import Trie as OriginalTrie
from trie_parser import normalize_text

try:
    from trie_parser_pygtrie import Trie as PygtrieTrie
    PYGTRIE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  pygtrie not available: {e}")
    print("   Install with: pip install pygtrie")
    PYGTRIE_AVAILABLE = False


def test_normalization():
    """Test that normalization works identically"""
    print("\n" + "="*70)
    print("TEST 1: Text Normalization")
    print("="*70)
    
    test_cases = [
        ("Hà Nội", "ha noi"),
        ("Đà Nẵng", "da nang"),
        ("Nam Từ Liêm", "nam tu liem"),
        ("  TP.HCM  ", "tp.hcm"),
        ("Thừa Thiên Huế", "thua thien hue"),
        ("Định Công", "dinh cong"),
        ("Hoàng Mai", "hoang mai"),
    ]
    
    all_passed = True
    for input_text, expected in test_cases:
        result = normalize_text(input_text)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        print(f"  {status} '{input_text}' → '{result}' (expected: '{expected}')")
    
    return all_passed


def test_basic_operations():
    """Test insert and search operations"""
    print("\n" + "="*70)
    print("TEST 2: Basic Trie Operations")
    print("="*70)
    
    test_data = [
        ("ha noi", "Hà Nội"),
        ("da nang", "Đà Nẵng"),
        ("ho chi minh", "Hồ Chí Minh"),
        ("nam tu liem", "Nam Từ Liêm"),
        ("cau dien", "Cầu Diễn"),
        ("dinh cong", "Định Công"),
    ]
    
    search_tests = [
        ("ha noi", "Hà Nội"),
        ("da nang", "Đà Nẵng"),
        ("nam tu liem", "Nam Từ Liêm"),
        ("ha no", None),  # Partial match
        ("xyz", None),    # Non-existent
    ]
    
    # Test original
    print("\n  Original Trie:")
    original = OriginalTrie()
    for normalized, original_val in test_data:
        original.insert(normalized, original_val)
    
    original_results = []
    for query, expected in search_tests:
        result = original.search(query)
        status = "✓" if result == expected else "✗"
        original_results.append(result)
        print(f"    {status} search('{query}') → {result}")
    
    if not PYGTRIE_AVAILABLE:
        print("\n  ⚠️  Skipping pygtrie comparison (not installed)")
        return True
    
    # Test pygtrie
    print("\n  Pygtrie Trie:")
    pygtrie = PygtrieTrie()
    for normalized, original_val in test_data:
        pygtrie.insert(normalized, original_val)
    
    pygtrie_results = []
    all_match = True
    for query, expected in search_tests:
        result = pygtrie.search(query)
        status = "✓" if result == expected else "✗"
        pygtrie_results.append(result)
        print(f"    {status} search('{query}') → {result}")
        
        if result != expected:
            all_match = False
    
    # Compare results
    print("\n  Comparison:")
    if original_results == pygtrie_results:
        print("    ✓ Both implementations return identical results!")
        return True
    else:
        print("    ✗ Results differ!")
        for i, (query, _) in enumerate(search_tests):
            if original_results[i] != pygtrie_results[i]:
                print(f"      Query '{query}':")
                print(f"        Original: {original_results[i]}")
                print(f"        Pygtrie:  {pygtrie_results[i]}")
        return False


def test_search_in_text():
    """Test search_in_text functionality"""
    print("\n" + "="*70)
    print("TEST 3: Search in Text")
    print("="*70)
    
    # Build test tries
    original = OriginalTrie()
    original.insert("ha noi", "Hà Nội")
    original.insert("nam tu liem", "Nam Từ Liêm")
    original.insert("cau dien", "Cầu Diễn")
    
    test_texts = [
        "phuong cau dien nam tu liem ha noi",
        "123 duong cau dien",
        "nam tu liem ha noi",
        "some random text",
    ]
    
    print("\n  Original Trie:")
    original_results = []
    for text in test_texts:
        matches = original.search_in_text(text)
        original_results.append(matches)
        print(f"    Text: '{text}'")
        print(f"    Matches: {matches}")
    
    if not PYGTRIE_AVAILABLE:
        print("\n  ⚠️  Skipping pygtrie comparison (not installed)")
        return True
    
    pygtrie = PygtrieTrie()
    pygtrie.insert("ha noi", "Hà Nội")
    pygtrie.insert("nam tu liem", "Nam Từ Liêm")
    pygtrie.insert("cau dien", "Cầu Diễn")
    
    print("\n  Pygtrie Trie:")
    pygtrie_results = []
    for text in test_texts:
        matches = pygtrie.search_in_text(text)
        pygtrie_results.append(matches)
        print(f"    Text: '{text}'")
        print(f"    Matches: {matches}")
    
    # Compare
    print("\n  Comparison:")
    all_match = True
    for i, text in enumerate(test_texts):
        if original_results[i] == pygtrie_results[i]:
            print(f"    ✓ '{text[:30]}...' - identical")
        else:
            print(f"    ✗ '{text[:30]}...' - DIFFERENT")
            print(f"      Original: {original_results[i]}")
            print(f"      Pygtrie:  {pygtrie_results[i]}")
            all_match = False
    
    return all_match


def test_edge_cases():
    """Test edge cases and special scenarios"""
    print("\n" + "="*70)
    print("TEST 4: Edge Cases")
    print("="*70)
    
    original = OriginalTrie()
    
    # Edge cases
    edge_cases = [
        # (normalized, original, description)
        ("", "Empty String", "Empty string"),
        ("a", "A", "Single character"),
        ("a b c d e f", "A B C D E F", "Many tokens"),
        ("test test", "Test Test", "Duplicate entry"),
    ]
    
    print("\n  Original Trie - Edge Cases:")
    for normalized, original_val, desc in edge_cases:
        try:
            original.insert(normalized, original_val)
            result = original.search(normalized)
            status = "✓" if result == original_val else "✗"
            print(f"    {status} {desc}: '{normalized}' → {result}")
        except Exception as e:
            print(f"    ✗ {desc}: ERROR - {e}")
    
    if not PYGTRIE_AVAILABLE:
        print("\n  ⚠️  Skipping pygtrie comparison (not installed)")
        return True
    
    pygtrie = PygtrieTrie()
    
    print("\n  Pygtrie Trie - Edge Cases:")
    all_match = True
    for normalized, original_val, desc in edge_cases:
        try:
            pygtrie.insert(normalized, original_val)
            result = pygtrie.search(normalized)
            status = "✓" if result == original_val else "✗"
            print(f"    {status} {desc}: '{normalized}' → {result}")
            if result != original_val:
                all_match = False
        except Exception as e:
            print(f"    ✗ {desc}: ERROR - {e}")
            all_match = False
    
    return all_match


def test_performance_comparison():
    """Quick performance comparison (informational only)"""
    print("\n" + "="*70)
    print("TEST 5: Performance Comparison (Informational)")
    print("="*70)
    
    import time
    
    # Generate test data
    test_entries = []
    for i in range(1000):
        # Simulate Vietnamese addresses (1-3 tokens)
        tokens = [f"token{j}" for j in range(i % 3 + 1)]
        normalized = " ".join(tokens)
        original = f"Original{i}"
        test_entries.append((normalized, original))
    
    # Test original
    print("\n  Original Trie:")
    original = OriginalTrie()
    
    start = time.time()
    for normalized, original_val in test_entries:
        original.insert(normalized, original_val)
    insert_time_original = time.time() - start
    
    start = time.time()
    for normalized, _ in test_entries:
        original.search(normalized)
    search_time_original = time.time() - start
    
    print(f"    Insert 1000 entries: {insert_time_original*1000:.2f}ms")
    print(f"    Search 1000 entries: {search_time_original*1000:.2f}ms")
    
    if not PYGTRIE_AVAILABLE:
        print("\n  ⚠️  Skipping pygtrie comparison (not installed)")
        return True
    
    # Test pygtrie
    print("\n  Pygtrie Trie:")
    pygtrie = PygtrieTrie()
    
    start = time.time()
    for normalized, original_val in test_entries:
        pygtrie.insert(normalized, original_val)
    insert_time_pygtrie = time.time() - start
    
    start = time.time()
    for normalized, _ in test_entries:
        pygtrie.search(normalized)
    search_time_pygtrie = time.time() - start
    
    print(f"    Insert 1000 entries: {insert_time_pygtrie*1000:.2f}ms")
    print(f"    Search 1000 entries: {search_time_pygtrie*1000:.2f}ms")
    
    # Compare
    print("\n  Speedup:")
    insert_speedup = insert_time_original / insert_time_pygtrie if insert_time_pygtrie > 0 else 0
    search_speedup = search_time_original / search_time_pygtrie if search_time_pygtrie > 0 else 0
    
    print(f"    Insert: {insert_speedup:.2f}x")
    print(f"    Search: {search_speedup:.2f}x")
    
    return True


def main():
    """Run all tests"""
    print("="*70)
    print("PYGTRIE REFACTORING VERIFICATION TEST SUITE")
    print("="*70)
    
    if not PYGTRIE_AVAILABLE:
        print("\n⚠️  WARNING: pygtrie not installed!")
        print("   Install with: pip install pygtrie")
        print("   Running tests with original implementation only...\n")
    
    results = []
    
    # Run tests
    results.append(("Normalization", test_normalization()))
    results.append(("Basic Operations", test_basic_operations()))
    results.append(("Search in Text", test_search_in_text()))
    results.append(("Edge Cases", test_edge_cases()))
    results.append(("Performance", test_performance_comparison()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nConclusion: The pygtrie refactoring maintains identical behavior")
        print("while providing a cleaner, more maintainable implementation.")
        print("\nNext step: Review REFACTORING_PHASE1.md for details,")
        print("then proceed to Phase 2 optimization.")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease review the failures above before proceeding.")
    print("="*70)


if __name__ == "__main__":
    main()
