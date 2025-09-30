"""
Check actual district names in database
"""

import json
from pathlib import Path

# Load districts
with open("../Data/Districts.json", encoding="utf-8") as f:
    districts = json.load(f)

# Find Nam Từ Liêm
print("Searching for 'Nam Từ Liêm' in Districts.json:")
for d in districts:
    if 'Nam' in d['Name'] and 'Liêm' in d['Name']:
        print(f"  Found: {d['Name']!r} (Code: {d['Code']})")

print("\nSearching for 'Tân Bình' in Districts.json:")
for d in districts:
    if 'Tân Bình' in d['Name']:
        print(f"  Found: {d['Name']!r} (Code: {d['Code']})")
        
# Now let's test normalization on these
print("\n" + "="*70)
print("Testing normalization:")

from normalizer import NormalizationConfig, normalize_text

sample_provinces = [{'Name': 'Hồ Chí Minh'}, {'Name': 'Hà Nội'}]
config = NormalizationConfig(sample_provinces)

test_names = [
    "Quận Nam Từ Liêm",
    "Quận Tân Bình",
]

for name in test_names:
    normalized = normalize_text(name, config)
    print(f"  {name!r} → {normalized!r}")
