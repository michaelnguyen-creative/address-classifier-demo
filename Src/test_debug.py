"""
Debug script to investigate the Tân Bình validation issue
"""

from address_database import AddressDatabase

# Initialize database
db = AddressDatabase(data_dir="../Data")

print("="*70)
print("INVESTIGATING: Tân Bình validation failure")
print("="*70)

# Step 1: Check what province names exist
print("\n[Step 1] All province names containing 'Hồ Chí Minh':")
for p in db.provinces:
    if "chí minh" in p['Name'].lower():
        print(f"  - '{p['Name']}' (Code: {p['Code']})")

# Step 2: Try exact lookup
test_province_names = [
    "Thành phố Hồ Chí Minh",
    "Hồ Chí Minh",
    "TP. Hồ Chí Minh",
    "Thành Phố Hồ Chí Minh"  # Capital P
]

print("\n[Step 2] Testing province_name_to_code lookup:")
for name in test_province_names:
    code = db.province_name_to_code.get(name)
    print(f"  '{name}' → {code}")

# Step 3: Check Tân Bình ward codes
print("\n[Step 3] All 'Tân Bình' ward codes:")
ward_codes = db.ward_name_to_codes.get("Tân Bình", [])
print(f"  Found {len(ward_codes)} wards named 'Tân Bình'")

for ward_code in ward_codes[:5]:  # Show first 5
    district_code = db.ward_to_district.get(ward_code)
    province_code = db.district_to_province.get(district_code)
    
    # Get names
    district = next((d['Name'] for d in db.districts if d['Code'] == district_code), "?")
    province = next((p['Name'] for p in db.provinces if p['Code'] == province_code), "?")
    
    print(f"  Ward {ward_code} → District {district} ({district_code}) → Province {province} ({province_code})")

# Step 4: Check Tân Bình district codes
print("\n[Step 4] All 'Tân Bình' district codes:")
district_codes = db.district_name_to_codes.get("Tân Bình", [])
print(f"  Found {len(district_codes)} districts named 'Tân Bình'")

for district_code in district_codes:
    province_code = db.district_to_province.get(district_code)
    province = next((p['Name'] for p in db.provinces if p['Code'] == province_code), "?")
    print(f"  District {district_code} → Province {province} ({province_code})")

print("\n" + "="*70)
print("DIAGNOSIS COMPLETE")
print("="*70)
