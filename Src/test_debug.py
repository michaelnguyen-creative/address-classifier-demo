import re

text = "P.1, Q.3, TP.Hồ Chí Minh"
text_lower = text.lower()

print(f"Input: {text}")
print(f"Lowercase: {text_lower}")
print()

# Test the province pattern
pattern = r'\btp\.?\s+([^,]+?)(?=\s*[,\n]|$)'
match = re.search(pattern, text_lower)

if match:
    print(f"✓ Pattern matched!")
    print(f"  Full match: '{match.group(0)}'")
    print(f"  Captured value: '{match.group(1)}'")
    print(f"  Position: {match.start()}-{match.end()}")
else:
    print(f"✗ Pattern did NOT match")
    print(f"  Testing why...")
    
    # Try simpler patterns
    if re.search(r'\btp\.?', text_lower):
        print(f"  ✓ Found 'tp.'")
    else:
        print(f"  ✗ No 'tp.' found")
    
    if re.search(r'\btp\.?\s', text_lower):
        print(f"  ✓ Found 'tp.' with space")
    else:
        print(f"  ✗ No space after 'tp.'")
