"""
Test Enhanced Parser with Phase 1 Improvements
===============================================

This test compares:
1. Original parser (with original normalization)
2. Enhanced parser (with Phase 1 smart prefix removal)

Goal: Validate 10-15% accuracy improvement on failure cases
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from address_database import AddressDatabase
from archive.normalizer import normalize_text as normalize_text_original
from normalizer_enhanced import normalize_text_enhanced


def test_normalization_comparison():
    """Compare original vs enhanced normalization"""
    
    print("="*70)
    print("PHASE 1 TEST: Normalization Comparison")
    print("="*70)
    
    # Initialize database
    db = AddressDatabase(data_dir="../Data")
    
    # Test cases from actual failures
    test_cases = [
        {
            'input': "TT Tân Bình Huyện Yên Sơn, Tuyên Quang",
            'expected_province': "Tuyên Quang",
            'expected_district': "Yên Sơn",
            'expected_ward': "Tân Bình",
            'issue': "Ward prefix (TT) blocking match"
        },
        {
            'input': "357/28,Ng-T- Thuật,P1,Q3,TP.HồChíMinh.",
            'expected_province': "Hồ Chí Minh",
            'expected_district': "3",
            'expected_ward': "1",
            'issue': "Numeric ward/district with prefixes"
        },
        {
            'input': "284DBis Ng Văn Giáo, P3, Mỹ Tho, T.Giang.",
            'expected_province': "Tiền Giang",
            'expected_district': "Mỹ Tho",
            'expected_ward': "3",
            'issue': "Numeric ward P3 → should be 3"
        },
        {
            'input': "T18,Cẩm Bình, Cẩm Phả, Quảng Ninh.",
            'expected_province': "Quảng Ninh",
            'expected_district': "Cẩm Phả",
            'expected_ward': "Cẩm Bình",
            'issue': "Ward name after prefix"
        },
        {
            'input': "Thanh Long, Yên Mỹ Hưng Yên",
            'expected_province': "Hưng Yên",
            'expected_district': "Yên Mỹ",
            'expected_ward': "Thanh Long",
            'issue': "No prefixes but need good matching"
        },
        {
            'input': "Xã Cao Dương, Huyện Thanh Oai, Thành phố Hà Nội",
            'expected_province': "Hà Nội",
            'expected_district': "Thanh Oai",
            'expected_ward': "Cao Dương",
            'issue': "Full prefixes that should be removed"
        },
    ]
    
    results = {
        'original': {'better': 0, 'same': 0, 'worse': 0},
        'enhanced': {'better': 0, 'same': 0, 'worse': 0}
    }
    
    for i, tc in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST CASE {i}: {tc['issue']}")
        print(f"{'='*70}")
        print(f"Input: {tc['input']}")
        print(f"Expected: P={tc['expected_province']}, D={tc['expected_district']}, W={tc['expected_ward']}")
        
        # Original normalization
        original_norm = normalize_text_original(tc['input'], db.norm_config)
        print(f"\nOriginal normalized: '{original_norm}'")
        print(f"  Tokens: {original_norm.split()}")
        
        # Enhanced normalization
        enhanced_norm = normalize_text_enhanced(tc['input'], db.norm_config, debug=False)
        print(f"\nEnhanced normalized: '{enhanced_norm}'")
        print(f"  Tokens: {enhanced_norm.split()}")
        
        # Compare token counts
        orig_tokens = len(original_norm.split())
        enh_tokens = len(enhanced_norm.split())
        
        print(f"\nToken count: {orig_tokens} → {enh_tokens} (diff: {orig_tokens - enh_tokens})")
        
        # Check if enhanced is cleaner
        if enh_tokens < orig_tokens:
            print("  ✓ Enhanced has FEWER tokens (cleaner for matching)")
            results['enhanced']['better'] += 1
        elif enh_tokens == orig_tokens:
            print("  = Same token count")
            results['enhanced']['same'] += 1
        else:
            print("  ✗ Enhanced has MORE tokens")
            results['enhanced']['worse'] += 1
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    total = len(test_cases)
    print(f"Total tests: {total}")
    print(f"\nEnhanced normalization:")
    print(f"  Better (cleaner): {results['enhanced']['better']} ({results['enhanced']['better']/total*100:.1f}%)")
    print(f"  Same:             {results['enhanced']['same']} ({results['enhanced']['same']/total*100:.1f}%)")
    print(f"  Worse:            {results['enhanced']['worse']} ({results['enhanced']['worse']/total*100:.1f}%)")
    
    return results


def test_trie_matching_with_enhanced_norm():
    """Test Trie matching with enhanced normalization"""
    
    print(f"\n{'='*70}")
    print("PHASE 1 TEST: Trie Matching with Enhanced Normalization")
    print(f"{'='*70}")
    
    db = AddressDatabase(data_dir="../Data")
    
    test_cases = [
        {
            'input': "TT Tân Bình, Yên Sơn, Tuyên Quang",
            'expected_ward': "Tân Bình",
            'reasoning': "After removing TT, should match 'tan binh'"
        },
        {
            'input': "P.3, Mỹ Tho",
            'expected_ward': "3",
            'reasoning': "After removing P., should match ward '3'"
        },
        {
            'input': "X.Cao Dương, H.Thanh Oai",
            'expected_ward': "Cao Dương",
            'expected_district': "Thanh Oai",
            'reasoning': "Remove X. and H. prefixes"
        },
    ]
    
    for i, tc in enumerate(test_cases, 1):
        print(f"\n[TEST {i}] {tc['reasoning']}")
        print(f"  Input: {tc['input']}")
        
        # Enhanced normalization
        enhanced = normalize_text_enhanced(tc['input'], db.norm_config)
        print(f"  Normalized: '{enhanced}'")
        
        # Try Trie matching on normalized text
        if 'expected_ward' in tc:
            ward_matches = db.ward_trie.search_in_text(enhanced)
            print(f"  Ward matches: {ward_matches}")
            
            if ward_matches:
                # Get first match
                ward_name = ward_matches[0][0]
                status = "✓" if ward_name == tc['expected_ward'] else "✗"
                print(f"  {status} Found: '{ward_name}' (expected: '{tc['expected_ward']}')")
            else:
                print(f"  ✗ No ward matches found")
        
        if 'expected_district' in tc:
            district_matches = db.district_trie.search_in_text(enhanced)
            print(f"  District matches: {district_matches}")
            
            if district_matches:
                district_name = district_matches[0][0]
                status = "✓" if district_name == tc['expected_district'] else "✗"
                print(f"  {status} Found: '{district_name}' (expected: '{tc['expected_district']}')")


if __name__ == "__main__":
    print("PHASE 1 ENHANCED NORMALIZATION TEST SUITE")
    print("="*70)
    print("Testing smart prefix removal and its impact on matching\n")
    
    # Test 1: Compare normalizations
    norm_results = test_normalization_comparison()
    
    # Test 2: Validate Trie matching improvements
    test_trie_matching_with_enhanced_norm()
    
    print(f"\n{'='*70}")
    print("NEXT STEPS")
    print(f"{'='*70}")
    print("1. If tests pass → integrate into address_parser.py")
    print("2. Run full test suite (test_parser.py) to measure improvement")
    print("3. Target: 10-15% accuracy boost on ward detection")
    print("="*70)
