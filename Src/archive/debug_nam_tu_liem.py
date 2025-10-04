"""
Debug normalization of 'Nam Từ Liêm'
"""

from archive.normalizer import NormalizationConfig, normalize_text

sample_provinces = [{'Name': 'Hồ Chí Minh'}, {'Name': 'Hà Nội'}]
config = NormalizationConfig(sample_provinces)

# Test the actual district name from JSON
district_name = "Nam Từ Liêm"

print(f"Input: {district_name!r}")
print()

# Step by step
text = district_name.lower()
print(f"After lowercase: {text!r}")

# Check province abbreviations
print("\nChecking province abbreviations:")
for abbrev, full_name in config.province_abbreviations.items():
    if abbrev in text:
        print(f"  Found abbreviation: {abbrev!r} → {full_name!r}")
        text_replaced = text.replace(abbrev, full_name)
        print(f"  After replacement: {text_replaced!r}")

# Now normalize fully
result = normalize_text(district_name, config)
print(f"\nFull normalize_text result: {result!r}")

# Test with 'Tân Bình' too
print("\n" + "="*70)
district_name2 = "Tân Bình"
print(f"Input: {district_name2!r}")
result2 = normalize_text(district_name2, config)
print(f"Full normalize_text result: {result2!r}")
