"""
Quick test script for the new smart search methods
"""

from address_database import AddressDatabase

print("="*70)
print("TESTING SMART SEARCH WITH PREFIX EXPANSION")
print("="*70)

# Initialize database
db = AddressDatabase(data_dir="../Data")

# Test province searches
province_tests = [
    ("ha noi", "Direct match"),
    ("hcm", "Alias match"),
    ("tp.hcm", "Prefix expansion"),
    ("TP HCM", "Case + prefix"),
    ("thanh pho ho chi minh", "Full form with prefix"),
    ("dn", "Ambiguous abbreviation"),
]

print("\n🔍 PROVINCE SEARCHES:")
print("-"*70)
for query, description in province_tests:
    result = db.search_province(query)
    status = "✅" if result else "❌"
    print(f"{status} '{query:30}' → {result:20} ({description})")

# Test district searches
district_tests = [
    ("nam tu liem", "Direct match"),
    ("q.1", "Prefix abbreviation"),
    ("q1", "Compact abbreviation"),
    ("quan 3", "Full form"),
    ("tan binh", "Duplicate name"),
]

print("\n🔍 DISTRICT SEARCHES:")
print("-"*70)
for query, description in district_tests:
    result = db.search_district(query)
    status = "✅" if result else "❌"
    print(f"{status} '{query:30}' → {result:20} ({description})")

# Test ward searches
ward_tests = [
    ("cau dien", "Direct match"),
    ("p.1", "Prefix abbreviation"),
    ("p1", "Compact abbreviation"),
    ("phuong 12", "Full form"),
]

print("\n🔍 WARD SEARCHES:")
print("-"*70)
for query, description in ward_tests:
    result = db.search_ward(query)
    status = "✅" if result else "❌"
    print(f"{status} '{query:30}' → {result:20} ({description})")

print("\n" + "="*70)
print("Test complete!")
print("="*70)
