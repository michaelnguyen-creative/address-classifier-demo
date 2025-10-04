"""Quick validation of edit_distance_matcher.py"""
import sys
sys.path.append('.')

from edit_distance_matcher import bounded_edit_distance

# Test the core algorithm
print("Testing bounded_edit_distance()...")

test_cases = [
    ("cat", "bat", 2, 1),
    ("ha noi", "ha nol", 2, 1),
    ("test", "test", 2, 0),
]

all_pass = True
for s, t, k, expected in test_cases:
    result = bounded_edit_distance(s, t, k)
    status = "✓" if result == expected else "✗"
    if result != expected:
        all_pass = False
    print(f"  {status} edit('{s}', '{t}', k={k}) = {result} (expected {expected})")

if all_pass:
    print("\n✅ Core algorithm works! Ready to run full test suite.")
    print("Run: python test_edit_distance.py")
else:
    print("\n❌ Some tests failed. Check implementation.")
