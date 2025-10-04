"""
Find the problematic abbreviations
"""

import json
from pathlib import Path
from archive.normalizer import build_province_abbreviations

# Load ALL provinces
with open("../Data/Provinces.json", encoding="utf-8") as f:
    provinces = json.load(f)

# Build abbreviations
abbrevs = build_province_abbreviations(provinces)

print("Searching for problematic abbreviations:")
print()

# Find abbreviations that match common district name parts
problem_patterns = ['nam', 'tan', 'binh', 'thanh']

for pattern in problem_patterns:
    print(f"Abbreviations matching '{pattern}':")
    for abbrev, full_name in sorted(abbrevs.items()):
        if pattern in abbrev:
            print(f"  {abbrev!r} → {full_name!r}")
    print()
