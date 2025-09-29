"""
Quick test of the fixed normalization
"""

import sys
sys.path.insert(0, 'C:/Users/luannvm/ClaudeManaged/address-classifier-demo/Src')

from trie_parser import normalize_text

print("Testing Fixed Normalization:")
print("="*50)

critical_tests = [
    ("Đà Nẵng", "da nang"),
    ("Định Công", "dinh cong"),
    ("Đồng Nai", "dong nai"),
    ("Hoàng Mai", "hoang mai"),
]

all_passed = True
for input_text, expected in critical_tests:
    result = normalize_text(input_text)
    passed = result == expected
    all_passed = all_passed and passed
    status = "✓" if passed else "✗"
    print(f"{status} '{input_text}' → '{result}'")
    if not passed:
        print(f"   Expected: '{expected}'")

print("="*50)
if all_passed:
    print("SUCCESS: All critical tests passed!")
else:
    print("FAILURE: Some tests failed")
