"""
Debug why district lookups are failing
"""

from address_database import AddressDatabase

# Initialize database
db = AddressDatabase(data_dir="../Data")

print("\n" + "="*70)
print("DEBUGGING DISTRICT LOOKUP FAILURES")
print("="*70)

# Test cases that failed
test_cases = [
    ("nam tu liem", "Nam Từ Liêm"),
    ("tan binh", "Tân Bình"),
]

for search_term, expected_name in test_cases:
    print(f"\nSearching for: '{search_term}'")
    print(f"Expected: {expected_name}")
    
    # Try direct search
    result = db.district_trie.search(search_term)
    print(f"Trie search result: {result}")
    
    # Check if the expected name exists in the database
    if expected_name in db.district_name_to_codes:
        print(f"✓ '{expected_name}' exists in district database")
        print(f"  Codes: {db.district_name_to_codes[expected_name]}")
        
        # Check what aliases were generated
        from alias_generator import generate_aliases
        aliases = generate_aliases(expected_name, db.norm_config)
        print(f"  Generated aliases: {sorted(aliases)}")
        
        # Check if our search term is in the aliases
        if search_term in aliases:
            print(f"  ✓ '{search_term}' IS in the generated aliases")
        else:
            print(f"  ✗ '{search_term}' NOT in the generated aliases")
            print(f"  Closest matches: {[a for a in aliases if search_term in a or a in search_term]}")
    else:
        print(f"✗ '{expected_name}' NOT found in district database")
        print(f"  Available districts with similar names:")
        for name in db.district_name_to_codes.keys():
            if "nam" in name.lower() and "liem" in name.lower():
                print(f"    - {name}")
            if "tan" in name.lower() and "binh" in name.lower():
                print(f"    - {name}")
