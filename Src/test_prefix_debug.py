"""
Debug Step 5 - prefix stripping in detail
"""

from normalizer import NormalizationConfig
import re

# Create minimal config
sample_provinces = [{'Name': 'Hồ Chí Minh'}, {'Name': 'Hà Nội'}]
config = NormalizationConfig(sample_provinces)

# Start with the text after Step 3
text = "ho chi minh"
print(f"Input to Step 5: {text!r}")
print()

# Get normalized prefixes
normalized_prefixes = config.get_normalized_prefixes()
print(f"Number of normalized prefixes: {len(normalized_prefixes)}")
print("Normalized prefixes:")
for i, prefix in enumerate(normalized_prefixes):
    print(f"  [{i}] {prefix!r}")
print()

# Test each prefix
print("Testing prefix stripping:")
for prefix in normalized_prefixes:
    starts_with_space = text.startswith(prefix + ' ')
    if starts_with_space:
        print(f"  ✓ MATCH: {prefix!r} + space")
        print(f"    Would strip: {text!r} → {text[len(prefix) + 1:].strip()!r}")
        break
    else:
        # Check what the regex would do
        pattern = r'\b' + re.escape(prefix) + r'\s+(?=\w)'
        matches = list(re.finditer(pattern, text))
        if matches:
            print(f"  ✓ REGEX MATCH: pattern {pattern!r}")
            for match in matches:
                print(f"    Found at position {match.start()}-{match.end()}: {text[match.start():match.end()]!r}")
        
print()

# Now run the actual Step 5 logic
text_copy = text
print("Running Step 5 logic:")

# First loop
for prefix in normalized_prefixes:
    if text_copy.startswith(prefix + ' '):
        text_copy = text_copy[len(prefix) + 1:].strip()
        print(f"  After first loop: {text_copy!r}")
        break

# Second loop
print(f"  Before second loop: {text_copy!r}")
for prefix in normalized_prefixes:
    before = text_copy
    text_copy = re.sub(r'\b' + re.escape(prefix) + r'\s+(?=\w)', '', text_copy)
    if before != text_copy:
        print(f"  Regex for {prefix!r} changed: {before!r} → {text_copy!r}")

print()
print(f"Final result: {text_copy!r}")
