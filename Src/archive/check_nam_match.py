"""
Check ALL province abbreviations to find the exact match
"""

import json
from pathlib import Path
from archive.normalizer import build_province_abbreviations, normalize_text, NormalizationConfig

# Load provinces
with open("../Data/Provinces.json", encoding="utf-8") as f:
    provinces = json.load(f)

abbrevs = build_province_abbreviations(provinces)

# Test what happens during normalization
test_text = "nam từ liêm"
print(f"Input text: {test_text!r}")
print()

# Check step by step what gets replaced
print("Checking each abbreviation:")
for abbrev, full_name in sorted(abbrevs.items(), key=lambda x: len(x[0]), reverse=True):
    if abbrev in test_text:
        print(f"  MATCH: {abbrev!r} → {full_name!r}")
        replaced = test_text.replace(abbrev, full_name)
        print(f"    Result: {test_text!r} → {replaced!r}")
        print()

# Also check what the actual provinces with "Nam" are
print("\nProvinces containing 'Nam':")
for p in provinces:
    if 'Nam' in p['Name']:
        print(f"  {p['Name']}")
