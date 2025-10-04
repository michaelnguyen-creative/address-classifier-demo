"""
Debug script to trace exactly what normalize_text is doing
"""

from archive.normalizer import normalize_text, NormalizationConfig, VIETNAMESE_CHAR_MAP

# Create minimal config
sample_provinces = [{'Name': 'Hồ Chí Minh'}, {'Name': 'Hà Nội'}]
config = NormalizationConfig(sample_provinces)

test_text = "Hồ Chí Minh"
print(f"Original: {test_text!r}")
print(f"Length: {len(test_text)}")
print()

# Step 1: Lowercase
step1 = test_text.lower()
print(f"Step 1 (lowercase): {step1!r}")
print(f"Length: {len(step1)}")
print("Characters:")
for i, char in enumerate(step1):
    print(f"  [{i}] '{char}' U+{ord(char):04X}")
print()

# Step 3: Apply character map (skipping step 2 expansion)
result = []
for i, char in enumerate(step1):
    mapped = VIETNAMESE_CHAR_MAP.get(char, char)
    result.append(mapped)
    if mapped != char:
        print(f"  [{i}] '{char}' → '{mapped}' ✓ MAPPED")
    else:
        print(f"  [{i}] '{char}' → '{mapped}' (unchanged)")

step3 = ''.join(result)
print()
print(f"Step 3 (after char map): {step3!r}")
print(f"Length: {len(step3)}")
print()

# Now run the full normalize_text
full_result = normalize_text(test_text, config)
print(f"Full normalize_text result: {full_result!r}")
