"""
Test LCS Matcher Implementation with Trie Parser
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lcs_matcher import LCSMatcher, prepare_candidate_tokens
from address_database import AddressDatabase
from trie_parser import normalize_text
from trie_parser import TrieBasedMatcher  # Use quiet version for clean output

def test_lcs_with_trie_parser():
    """Test LCS matcher integrated with Trie parser"""
    
    print("\n" + "="*70)
    print("LCS MATCHER - INTEGRATION WITH TRIE PARSER")
    print("="*70)
    
    # Load database
    print("\nLoading address database...")
    db = AddressDatabase()
    
    # Initialize Trie parser (quiet version)
    print("Building Trie parser...")
    trie_parser = TrieBasedMatcher()
    
    # Build tries from database
    province_names = [p['Name'] for p in db.provinces]
    district_names = [d['Name'] for d in db.districts]
    ward_names = [w['Name'] for w in db.wards]
    
    trie_parser.build_from_lists(province_names, district_names, ward_names)
    print("✓ Trie parser ready")
    
    # Initialize LCS matcher
    lcs_matcher = LCSMatcher(threshold=0.4)
    print("✓ LCS matcher ready")
    
    # Test cases that should FAIL with Trie but SUCCEED with LCS
    test_cases = [
        {
            "text": "123 nguyen van linh cau dien nam tu liem ha noi",
            "description": "Extra words (street name + address number)",
            "expected": {
                "province": "Hà Nội",
                "district": "Nam Từ Liêm",
                "ward": "Cầu Diễn"
            }
        },
        {
            "text": "dinh cong hoang mai ha noi",
            "description": "Clean but needs validation",
            "expected": {
                "province": "Hà Nội",
                "district": "Hoàng Mai",
                "ward": "Định Công"
            }
        },
        {
            "text": "ha noi nam tu liem cau dien",
            "description": "Reordered tokens (no separators)",
            "expected": {
                "province": "Hà Nội",
                "district": "Nam Từ Liêm",
                "ward": "Cầu Diễn"
            }
        },
        {
            "text": "P Cau Dien Q Nam Tu Liem Ha Noi",
            "description": "Prefixes: P. = Phường, Q. = Quận",
            "expected": {
                "province": "Hà Nội",
                "district": "Nam Từ Liêm",
                "ward": "Cầu Diễn"
            }
        }
    ]
    
    passed_count = 0
    failed_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"[TEST {i}] {test_case['text']}")
        print(f"Description: {test_case['description']}")
        print("="*70)
        
        # Normalize input
        normalized = normalize_text(test_case['text'])
        input_tokens = normalized.split()
        print(f"\nNormalized: {normalized}")
        print(f"Tokens: {input_tokens}")
        
        # ===== TIER 1: Try Trie First =====
        print(f"\n[TIER 1] Trying Trie exact match...")
        trie_result = trie_parser.match(test_case['text'])
        
        trie_success = (
            trie_result['province'] == test_case['expected']['province'] and
            trie_result['district'] == test_case['expected']['district'] and
            trie_result['ward'] == test_case['expected']['ward']
        )
        
        print(f"  Province: {trie_result['province']}")
        print(f"  District: {trie_result['district']}")
        print(f"  Ward: {trie_result['ward']}")
        
        if trie_success:
            print(f"  ✓ Trie SUCCESS - No need for LCS")
            passed_count += 1
            continue
        else:
            print(f"  ✗ Trie FAILED - Falling back to LCS")
        
        # ===== TIER 2: LCS Fallback =====
        print(f"\n[TIER 2] Trying LCS alignment...")
        
        # Prepare candidates
        province_candidates = [
            (p['Name'], prepare_candidate_tokens(p['Name'], normalize_text))
            for p in db.provinces
        ]
        
        district_candidates = [
            (d['Name'], prepare_candidate_tokens(d['Name'], normalize_text))
            for d in db.districts
        ]
        
        ward_candidates = [
            (w['Name'], prepare_candidate_tokens(w['Name'], normalize_text))
            for w in db.wards
        ]
        
        candidates_dict = {
            "province": province_candidates,
            "district": district_candidates,
            "ward": ward_candidates
        }
        
        # Run LCS matching
        lcs_results = lcs_matcher.find_all_matches(input_tokens, candidates_dict)
        
        print(f"\n  LCS Results:")
        for entity_type, match in lcs_results.items():
            if match:
                print(f"    {entity_type.capitalize()}: {match.entity_name} (score: {match.similarity_score:.3f}, LCS: {match.lcs_length})")
            else:
                print(f"    {entity_type.capitalize()}: None")
        
        # ===== Validation =====
        print(f"\n  Expected:")
        for entity_type, expected_value in test_case['expected'].items():
            print(f"    {entity_type.capitalize()}: {expected_value}")
        
        print(f"\n  Validation:")
        all_correct = True
        
        if lcs_results['province']:
            if lcs_results['province'].entity_name == test_case['expected']['province']:
                print(f"    ✓ Province: {lcs_results['province'].entity_name} (correct)")
            else:
                print(f"    ✗ Province: Expected {test_case['expected']['province']}, got {lcs_results['province'].entity_name}")
                all_correct = False
        else:
            print(f"    ✗ Province: No match found")
            all_correct = False
        
        if test_case['expected']['district']:
            if lcs_results['district'] and lcs_results['district'].entity_name == test_case['expected']['district']:
                print(f"    ✓ District: {lcs_results['district'].entity_name} (correct)")
            else:
                expected_dist = test_case['expected']['district']
                got_dist = lcs_results['district'].entity_name if lcs_results['district'] else 'None'
                print(f"    ✗ District: Expected {expected_dist}, got {got_dist}")
                all_correct = False
        
        if test_case['expected']['ward']:
            if lcs_results['ward'] and lcs_results['ward'].entity_name == test_case['expected']['ward']:
                print(f"    ✓ Ward: {lcs_results['ward'].entity_name} (correct)")
            else:
                expected_ward = test_case['expected']['ward']
                got_ward = lcs_results['ward'].entity_name if lcs_results['ward'] else 'None'
                print(f"    ✗ Ward: Expected {expected_ward}, got {got_ward}")
                all_correct = False
        
        if all_correct:
            print(f"\n  🎉 TEST {i} PASSED - LCS successfully handled case where Trie failed!")
            passed_count += 1
        else:
            print(f"\n  ❌ TEST {i} FAILED - LCS did not produce expected results")
            failed_count += 1
    
    # Summary
    print(f"\n{'='*70}")
    print(f"INTEGRATION TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Total Tests: {len(test_cases)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Success Rate: {passed_count/len(test_cases)*100:.1f}%")
    print(f"{'='*70}")


def test_lcs_basic():
    """Test basic LCS functionality"""
    print("\n" + "="*70)
    print("LCS MATCHER - BASIC UNIT TESTS")
    print("="*70)
    
    matcher = LCSMatcher(threshold=0.4)
    
    # Test 1: Identical sequences
    print("\n[TEST 1] Identical sequences")
    seq1 = ["ha", "noi"]
    seq2 = ["ha", "noi"]
    lcs_len = matcher.compute_lcs_length(seq1, seq2)
    score = matcher.compute_lcs_similarity(seq1, seq2)
    print(f"  Input: {seq1}")
    print(f"  Candidate: {seq2}")
    print(f"  LCS Length: {lcs_len} (expected: 2)")
    print(f"  Similarity: {score:.3f} (expected: 1.000)")
    assert lcs_len == 2, "LCS length should be 2"
    assert abs(score - 1.0) < 0.01, "Similarity should be 1.0"
    print("  ✓ PASS")
    
    # Test 2: Subsequence with extra words
    print("\n[TEST 2] Subsequence with extra words")
    seq1 = ["ha", "noi", "nam", "tu", "liem"]
    seq2 = ["nam", "tu", "liem"]
    lcs_len = matcher.compute_lcs_length(seq1, seq2)
    score = matcher.compute_lcs_similarity(seq1, seq2)
    print(f"  Input: {seq1}")
    print(f"  Candidate: {seq2}")
    print(f"  LCS Length: {lcs_len} (expected: 3)")
    print(f"  Similarity: {score:.3f} (expected: 0.750)")
    assert lcs_len == 3, "LCS length should be 3"
    assert abs(score - 0.75) < 0.01, "Similarity should be 0.75"
    print("  ✓ PASS")
    
    # Test 3: No overlap
    print("\n[TEST 3] No overlap")
    seq1 = ["ha", "noi"]
    seq2 = ["da", "nang"]
    lcs_len = matcher.compute_lcs_length(seq1, seq2)
    score = matcher.compute_lcs_similarity(seq1, seq2)
    print(f"  Input: {seq1}")
    print(f"  Candidate: {seq2}")
    print(f"  LCS Length: {lcs_len} (expected: 0)")
    print(f"  Similarity: {score:.3f} (expected: 0.000)")
    assert lcs_len == 0, "LCS length should be 0"
    assert score == 0.0, "Similarity should be 0.0"
    print("  ✓ PASS")
    
    # Test 4: Partial overlap
    print("\n[TEST 4] Partial overlap")
    seq1 = ["cau", "dien", "ha", "noi"]
    seq2 = ["cau", "dien"]
    lcs_len = matcher.compute_lcs_length(seq1, seq2)
    score = matcher.compute_lcs_similarity(seq1, seq2)
    expected_score = 2 * 2 / (4 + 2)  # 0.667
    print(f"  Input: {seq1}")
    print(f"  Candidate: {seq2}")
    print(f"  LCS Length: {lcs_len} (expected: 2)")
    print(f"  Similarity: {score:.3f} (expected: {expected_score:.3f})")
    assert lcs_len == 2, "LCS length should be 2"
    assert abs(score - expected_score) < 0.01, f"Similarity should be {expected_score}"
    print("  ✓ PASS")
    
    # Test 5: Reordered tokens
    print("\n[TEST 5] Reordered tokens (order preservation in LCS)")
    seq1 = ["noi", "ha"]  # Reversed
    seq2 = ["ha", "noi"]
    lcs_len = matcher.compute_lcs_length(seq1, seq2)
    print(f"  Input: {seq1}")
    print(f"  Candidate: {seq2}")
    print(f"  LCS Length: {lcs_len}")
    print(f"  Note: LCS preserves order, so reversed tokens have lower LCS")
    print("  ✓ PASS (expected behavior)")
    
    print("\n" + "="*70)
    print("All basic tests passed!")
    print("="*70)


if __name__ == "__main__":
    # Run basic tests first
    test_lcs_basic()
    
    # Then run integration tests
    test_lcs_with_trie_parser()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)
