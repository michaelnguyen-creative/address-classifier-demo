"""
Debug ALL steps of normalize_text
"""

from normalizer import NormalizationConfig, VIETNAMESE_CHAR_MAP
import re
import string

# Create config
sample_provinces = [{'Name': 'Hồ Chí Minh'}, {'Name': 'Hà Nội'}]
config = NormalizationConfig(sample_provinces)

text = "Hồ Chí Minh"
print(f"INPUT: {text!r}\n")

# Step 1: Lowercase
text = text.lower()
print(f"Step 1 (lowercase): {text!r}")

# Step 2: Expand abbreviations
print("\nStep 2 (expand abbreviations):")
print(f"  Before: {text!r}")

# Province abbreviations
for abbrev, full_name in config.province_abbreviations.items():
    if abbrev in text:
        print(f"    Checking abbrev {abbrev!r} → {full_name!r}")
        old_text = text
        text = text.replace(abbrev, full_name)
        if old_text != text:
            print(f"    ✓ REPLACED: {old_text!r} → {text!r}")

# Expansion patterns
for pattern, replacement, desc in config.expansion_patterns:
    old_text = text
    text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    if old_text != text:
        print(f"    ✓ Pattern {desc}: {old_text!r} → {text!r}")

print(f"  After: {text!r}")

# Step 3: Map Vietnamese diacritics
print("\nStep 3 (map diacritics):")
print(f"  Before: {text!r}")
result = []
for char in text:
    result.append(VIETNAMESE_CHAR_MAP.get(char, char))
text = ''.join(result)
print(f"  After: {text!r}")

# Step 4: Remove punctuation
print("\nStep 4 (remove punctuation):")
print(f"  Before: {text!r}")
punctuation_to_remove = string.punctuation.replace('-', '')
text = text.translate(str.maketrans('', '', punctuation_to_remove))
print(f"  After: {text!r}")

# Step 5: Strip administrative prefixes
print("\nStep 5 (strip admin prefixes):")
print(f"  Before: {text!r}")
normalized_prefixes = config.get_normalized_prefixes()

# First loop
for prefix in normalized_prefixes:
    if text.startswith(prefix + ' '):
        old_text = text
        text = text[len(prefix) + 1:].strip()
        print(f"  ✓ Stripped prefix {prefix!r}: {old_text!r} → {text!r}")
        break

# Second loop
for prefix in normalized_prefixes:
    old_text = text
    text = re.sub(r'\b' + re.escape(prefix) + r'\s+(?=\w)', '', text)
    if old_text != text:
        print(f"  ✓ Regex stripped {prefix!r}: {old_text!r} → {text!r}")

print(f"  After: {text!r}")

# Step 6: Clean whitespace
print("\nStep 6 (clean whitespace):")
print(f"  Before: {text!r}")
text = text.strip()
text = ' '.join(text.split())
print(f"  After: {text!r}")

print(f"\nFINAL OUTPUT: {text!r}")
