"""
Integration Tests for Layer 1 + Layer 2 Pipeline

Tests the complete address normalization pipeline combining:
- Layer 1: Text Normalizer (generic normalization)
- Layer 2: Admin Prefix Handler (Vietnamese-specific expansion)
"""

from normalizer_v2 import (
    AddressNormalizer,
    process_province,
    process_district,
    process_ward,
    process_full_address
)


# ========================================================================
# INTEGRATION TEST CASES
# ========================================================================

INTEGRATION_TESTS = {
    'province_level': {
        'description': 'Province-Level Address Processing',
        'cases': [
            ("TP.HCM", "ho chi minh", "Full abbreviation"),
            ("Thành Phố Hồ Chí Minh", "ho chi minh", "Full form with diacritics"),
            ("tp.hcm", "ho chi minh", "Lowercase abbreviation"),
            ("Hà Nội", "ha noi", "Capital city"),
            ("Đà Nẵng", "da nang", "Central city"),
        ]
    },
    
    'district_level': {
        'description': 'District-Level Address Processing',
        'cases': [
            ("Quận 1", "1", "Numbered district"),
            ("Q.1", "1", "Abbreviated district"),
            ("Quận Tân Bình", "tan binh", "Named district"),
            ("Huyện Củ Chi", "cu chi", "Rural district"),
            ("Thị Xã Thuận An", "thuan an", "Town"),
        ]
    },
    
    'ward_level': {
        'description': 'Ward-Level Address Processing',
        'cases': [
            ("Phường Bến Nghé", "ben nghe", "Named ward"),
            ("P.Bến Nghé", "ben nghe", "Abbreviated ward"),
            ("Phường 12", "12", "Numbered ward"),
            ("Xã Tân Thông Hội", "tan thong hoi", "Commune"),
        ]
    },
    
    'messy_input': {
        'description': 'Messy Real-World Input',
        'cases': [
            ("357/28,Ng-T- Thuật,P1,Q3", None, "Missing spaces, hyphens"),
            ("TP.HCM™", "ho chi minh", "With trademark symbol"),
            ("Quận    1", "1", "Extra spaces"),
            ("P.BẾN NGHÉ!!!", "ben nghe", "Uppercase with punctuation"),
        ]
    },
}


FULL_ADDRESS_TESTS = [
    {
        'input': "TP.HCM, Quận 1, P.Bến Nghé",
        'expected': {
            'city': 'ho chi minh',
            'district': '1',
            'ward': 'ben nghe'
        },
        'description': "Standard format"
    },
    {
        'input': "Thành Phố Hồ Chí Minh, Quận Tân Bình, Phường 12",
        'expected': {
            'city': 'ho chi minh',
            'district': 'tan binh',
            'ward': '12'
        },
        'description': "Full form with diacritics"
    },
    {
        'input': "Hà Nội, Q.Ba Đình, P.Ngọc Hà",
        'expected': {
            'city': 'ha noi',
            'district': 'ba dinh',
            'ward': 'ngoc ha'
        },
        'description': "Mixed abbreviations"
    },
]


# ========================================================================
# TEST RUNNER
# ========================================================================

def run_integration_tests():
    """
    Run all integration tests
    """
    print("="*70)
    print("LAYER 1 + LAYER 2: INTEGRATION TESTS")
    print("="*70)
    
    normalizer = AddressNormalizer(data_dir="../data")
    
    total_passed = 0
    total_failed = 0
    
    # Test each level
    for suite_name, suite_config in INTEGRATION_TESTS.items():
        print(f"\n✅ {suite_config['description']}")
        print("-" * 70)
        
        level = suite_name.replace('_level', '').replace('_', ' ')
        if level == 'messy input':
            level = 'auto'
        
        for input_text, expected, description in suite_config['cases']:
            if expected is None:
                # Just test that it doesn't crash
                try:
                    result = normalizer.process(input_text, level=level)
                    print(f"✅ '{input_text[:30]:30}' → '{result[:30]:30}' | {description}")
                    total_passed += 1
                except Exception as e:
                    print(f"❌ '{input_text[:30]:30}' → ERROR: {e} | {description}")
                    total_failed += 1
            else:
                result = normalizer.process(input_text, level=level)
                passed = (result == expected)
                
                if passed:
                    print(f"✅ '{input_text[:30]:30}' → '{result[:30]:30}' | {description}")
                    total_passed += 1
                else:
                    print(f"❌ '{input_text[:30]:30}' → '{result[:30]:30}' | {description}")
                    print(f"   Expected: '{expected}'")
                    print(f"   Actual:   '{result}'")
                    total_failed += 1
    
    # Test full address processing
    print(f"\n✅ Full Address Processing")
    print("-" * 70)
    
    for test in FULL_ADDRESS_TESTS:
        result = normalizer.process_address(test['input'])
        expected = test['expected']
        
        passed = (result['components'] == expected)
        
        if passed:
            print(f"✅ {test['description']}")
            print(f"   Input:  {test['input']}")
            print(f"   Output: {result['components']}")
            total_passed += 1
        else:
            print(f"❌ {test['description']}")
            print(f"   Input:    {test['input']}")
            print(f"   Expected: {expected}")
            print(f"   Actual:   {result['components']}")
            total_failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("INTEGRATION TEST SUMMARY")
    print("="*70)
    
    total_tests = total_passed + total_failed
    percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nTotal: {total_passed}/{total_tests} passed ({percentage:.1f}%)")
    
    if total_failed > 0:
        print(f"⚠️  {total_failed} test(s) failed")
    else:
        print("✅ All tests passed!")
    
    print("="*70)
    
    return total_passed, total_failed


# ========================================================================
# DEMO EXAMPLES
# ========================================================================

def run_demo():
    """
    Interactive demo showing the pipeline in action
    """
    print("\n" + "="*70)
    print("INTEGRATION DEMO: Layer 1 + Layer 2 Pipeline")
    print("="*70)
    
    normalizer = AddressNormalizer(data_dir="../data")
    
    # Example 1: Step-by-step pipeline
    print("\n📍 Example 1: Step-by-step pipeline")
    print("-" * 70)
    
    raw = "TP.HCM, Quận 1, P.Bến Nghé"
    print(f"Raw input:  {raw}")
    
    # Layer 1 only
    normalized = normalizer.normalize_only(raw)
    print(f"Layer 1:    {normalized}")
    
    # Layer 1 + Layer 2 (full address)
    result = normalizer.process_address(raw)
    print(f"Layer 2:    {result['components']}")
    
    # Example 2: Messy real-world input
    print("\n📍 Example 2: Messy real-world input")
    print("-" * 70)
    
    messy = "357/28,Ng-T- Thuật,P.Bến Nghé,Q.1,TP.HCM™"
    print(f"Raw input:  {messy}")
    
    normalized = normalizer.normalize_only(messy)
    print(f"Layer 1:    {normalized}")
    
    # Example 3: Convenience functions
    print("\n📍 Example 3: Convenience functions")
    print("-" * 70)
    
    print(f"process_province('TP.HCM') → '{process_province('TP.HCM', data_dir='../data')}'")
    print(f"process_district('Quận 1') → '{process_district('Quận 1', data_dir='../data')}'")
    print(f"process_ward('P.Bến Nghé') → '{process_ward('P.Bến Nghé', data_dir='../data')}'")


if __name__ == "__main__":
    # Run integration tests
    passed, failed = run_integration_tests()
    
    # Run demo if all tests passed
    if failed == 0:
        run_demo()
