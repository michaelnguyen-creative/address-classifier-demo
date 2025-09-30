"""
Test with full province list like AddressDatabase does
"""

import json
from pathlib import Path
from normalizer import NormalizationConfig
from alias_generator import generate_aliases

# Load ALL provinces like AddressDatabase does
with open("../Data/Provinces.json", encoding="utf-8") as f:
    provinces = json.load(f)

# Create config with full province list
config = NormalizationConfig(provinces)

print(f"Loaded {len(provinces)} provinces")
print(f"Generated {len(config.province_abbreviations)} province abbreviations")
print()

# Check if 'nam' or 'tan' are in the abbreviations
print("Checking for problematic abbreviations:")
for abbrev, full_name in sorted(config.province_abbreviations.items()):
    if abbrev in ['nam', 'tan', 'n', 't']:
        print(f"  {abbrev!r} → {full_name!r}")

print("\n" + "="*70)
print("Now testing district name normalization with FULL config:")

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
