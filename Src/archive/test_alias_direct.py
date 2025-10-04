"""
Test generate_aliases directly with district names
"""

from archive.normalizer import NormalizationConfig
from alias_generator import generate_aliases

# Create config
sample_provinces = [{'Name': 'Hồ Chí Minh'}, {'Name': 'Hà Nội'}]
config = NormalizationConfig(sample_provinces)

# Test the problematic district names
test_cases = [
    "Nam Từ Liêm",
    "Tân Bình",
]

for name in test_cases:
    print(f"\nTesting: {name!r}")
    aliases = generate_aliases(name, config)
    print(f"Generated {len(aliases)} aliases:")
    for alias in sorted(aliases):
        print(f"  - {alias!r}")
