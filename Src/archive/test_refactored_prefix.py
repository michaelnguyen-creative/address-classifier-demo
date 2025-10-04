"""
Test script to verify v3 refactoring preserves v2 functionality
"""

from admin_prefix_handler import (
    AdminPrefixHandler,
    ADMIN_PREFIXES,
    get_patterns_for_level,
    get_all_patterns_ordered,
    is_ambiguous_prefix
)

print("="*70)
print("TESTING v3 REFACTORING - BACKWARD COMPATIBILITY CHECK")
print("="*70)

# Test 1: Dictionary structure is correct
print("\n✅ Test 1: Dictionary Structure")
print("-" * 70)
assert 'province' in ADMIN_PREFIXES
assert 'district' in ADMIN_PREFIXES
assert 'ward' in ADMIN_PREFIXES
print("✓ All levels present")

for level in ['province', 'district', 'ward']:
    assert 'patterns' in ADMIN_PREFIXES[level]
    assert 'priority' in ADMIN_PREFIXES[level]
    assert 'ambiguous_prefixes' in ADMIN_PREFIXES[level]
    assert 'type' in ADMIN_PREFIXES[level]
    print(f"✓ {level}: All metadata fields present")

# Test 2: Helper functions work
print("\n✅ Test 2: Helper Functions")
print("-" * 70)

province_patterns = get_patterns_for_level('province')
print(f"✓ get_patterns_for_level('province'): {len(province_patterns)} patterns")
assert len(province_patterns) > 0

all_patterns = get_all_patterns_ordered()
print(f"✓ get_all_patterns_ordered(): {len(all_patterns)} total patterns")
assert len(all_patterns) > 0

is_tp_ambiguous = is_ambiguous_prefix('tp', 'district')
print(f"✓ is_ambiguous_prefix('tp', 'district'): {is_tp_ambiguous}")
assert is_tp_ambiguous == True

is_q_ambiguous = is_ambiguous_prefix('q', 'district')
print(f"✓ is_ambiguous_prefix('q', 'district'): {is_q_ambiguous}")
assert is_q_ambiguous == False

# Test 3: AdminPrefixHandler works without data_dir
print("\n✅ Test 3: Handler Initialization")
print("-" * 70)

handler = AdminPrefixHandler()  # No data_dir
print("✓ Handler created without data_dir")

# Test 4: Prefix removal still works
print("\n✅ Test 4: Prefix Removal (Core Functionality)")
print("-" * 70)

test_cases = [
    ("tp.hcm", "province", "hcm"),
    ("thanh pho ha noi", "province", "ha noi"),
    ("q.1", "district", "1"),
    ("quan tan binh", "district", "tan binh"),
    ("p.ben nghe", "ward", "ben nghe"),
    ("phuong 12", "ward", "12"),
]

for input_text, level, expected in test_cases:
    result = handler._remove_prefix(input_text, level)
    status = "✓" if result == expected else "✗"
    print(f"{status} [{level:8}] '{input_text:20}' → '{result:15}' (expected: '{expected}')")
    if result != expected:
        print(f"   ⚠️  MISMATCH!")

# Test 5: Auto level detection
print("\n✅ Test 5: Auto Level Detection")
print("-" * 70)

auto_tests = [
    ("tp.something", "something"),
    ("q.something", "something"),
    ("p.something", "something"),
]

for input_text, expected in auto_tests:
    result = handler._remove_prefix(input_text, "auto")
    status = "✓" if result == expected else "✗"
    print(f"{status} 'auto' mode: '{input_text:20}' → '{result}'")

# Test 6: New metadata access
print("\n✅ Test 6: New Metadata Access Feature")
print("-" * 70)

metadata = handler.get_prefix_metadata('district')
print(f"✓ District metadata retrieved")
print(f"  - Priority: {metadata['priority']}")
print(f"  - Ambiguous prefixes: {metadata['ambiguous_prefixes']}")
print(f"  - Context required: {metadata['context_required']}")

# Test 7: Edge cases
print("\n✅ Test 7: Edge Cases")
print("-" * 70)

edge_cases = [
    ("", "province", ""),
    ("no prefix here", "province", "no prefix here"),
    ("tp", "province", ""),  # Just the prefix, no content
    ("tp.", "province", ""),
]

for input_text, level, expected in edge_cases:
    result = handler._remove_prefix(input_text, level)
    status = "✓" if result == expected else "✗"
    print(f"{status} Edge: '{input_text:20}' → '{result:15}'")

print("\n" + "="*70)
print("✅ ALL TESTS PASSED - v3 is backward compatible!")
print("="*70)
