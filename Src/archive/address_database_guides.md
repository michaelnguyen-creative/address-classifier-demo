# **AddressDatabase Usage Guide**

Complete tutorial for working with the Vietnamese Address Database system.

---

## **Table of Contents**

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Basic Usage](#basic-usage)
4. [Advanced Queries](#advanced-queries)
5. [Common Patterns](#common-patterns)
6. [Performance Notes](#performance-notes)
7. [Troubleshooting](#troubleshooting)

---

## **Quick Start**

### **Installation**

```python
# No external dependencies - uses Python stdlib only
from address_database import AddressDatabase

# Initialize (takes ~15ms)
db = AddressDatabase(data_dir="../Data")
```

### **First Query**

```python
# Lookup a province
province = db.lookup_province("ha noi")
print(province)  # "Hà Nội"

# Get districts in a province
districts = db.get_districts_in_province("Hà Nội")
print(f"Found {len(districts)} districts")  # 30 districts
```

---

## **Core Concepts**

### **The Three-Level Hierarchy**

```
Province (Tỉnh/Thành phố)
    ├── District (Quận/Huyện)
    │       ├── Ward (Phường/Xã)
    │       ├── Ward
    │       └── Ward
    └── District
            └── ...
```

**Example:**
```
Hà Nội (Province)
    └── Nam Từ Liêm (District)
            ├── Cầu Diễn (Ward)
            ├── Xuân Phương (Ward)
            └── ...
```

### **Normalization**

All queries are **normalized** automatically:
- Removes diacritics: `Hà Nội` → `ha noi`
- Lowercases: `HA NOI` → `ha noi`
- Cleans whitespace: `ha  noi` → `ha noi`

You don't need to normalize manually - just pass the text as-is.

---

## **Basic Usage**

### **1. Province Lookups**

```python
# Standard names
db.lookup_province("Hà Nội")        # "Hà Nội"
db.lookup_province("Hồ Chí Minh")   # "Hồ Chí Minh"

# Without diacritics (automatic normalization)
db.lookup_province("ha noi")        # "Hà Nội"
db.lookup_province("ho chi minh")   # "Hồ Chí Minh"

# Aliases
db.lookup_province("tp hcm")        # "Hồ Chí Minh"
db.lookup_province("saigon")        # "Hồ Chí Minh"
db.lookup_province("sg")            # "Hồ Chí Minh"
db.lookup_province("hn")            # "Hà Nội"

# Unknown province
db.lookup_province("fake city")     # None
```

### **2. District Lookups**

```python
# Unique district name
districts = db.lookup_district("Nam Tu Liem")
print(districts)  # ["Nam Từ Liêm"]

# Duplicate district name (exists in multiple provinces)
districts = db.lookup_district("Tan Binh")
print(districts)  # ["Tân Bình", "Tân Bình"]  # Multiple matches!

# Disambiguate with province context
districts = db.lookup_district("Tan Binh", province_context="Hồ Chí Minh")
print(districts)  # ["Tân Bình"]  # Only the one in HCM
```

### **3. Ward Lookups**

```python
# Unique ward
wards = db.lookup_ward("Cau Dien")
print(wards)  # ["Cầu Diễn"]

# Ward with duplicate name
wards = db.lookup_ward("Phuong 1")
print(wards)  # Multiple "Phường 1" across different districts

# Disambiguate with district context
wards = db.lookup_ward("Phuong 1", district_context="Quận 1")
print(wards)  # ["Phường 1"]  # Only in Quận 1
```

---

## **Advanced Queries**

### **1. Full Address Resolution**

Get complete address hierarchy for a ward:

```python
matches = db.get_full_address("Cầu Diễn")

for match in matches:
    print(f"Ward: {match.ward}")
    print(f"District: {match.district}")
    print(f"Province: {match.province}")
    print(f"Codes: {match.ward_code}, {match.district_code}, {match.province_code}")
    print()

# Output:
# Ward: Cầu Diễn
# District: Nam Từ Liêm
# Province: Hà Nội
# Codes: 00001, 019, 01
```

**Use case:** When you have a ward name and need to know which province/district it belongs to.

### **2. List All Children**

```python
# Get all districts in a province
districts = db.get_districts_in_province("Hà Nội")
print(f"Hanoi has {len(districts)} districts")
for dist in districts[:5]:  # First 5
    print(f"  - {dist}")

# Output:
# Hanoi has 30 districts
#   - Ba Đình
#   - Cầu Giấy
#   - Đống Đa
#   - Hai Bà Trưng
#   - Hoàn Kiếm

# Get all wards in a district
wards = db.get_wards_in_district("Hà Nội", "Nam Từ Liêm")
print(f"Nam Từ Liêm has {len(wards)} wards")
for ward in wards[:5]:  # First 5
    print(f"  - {ward}")

# Output:
# Nam Từ Liêm has 10 wards
#   - Cầu Diễn
#   - Mỹ Đình 1
#   - Mỹ Đình 2
#   - Phú Đô
#   - Phương Canh
```

### **3. Hierarchy Validation**

Check if an address combination is valid:

```python
# Valid address
valid = db.validate_hierarchy(
    ward="Cầu Diễn",
    district="Nam Từ Liêm",
    province="Hà Nội"
)
print(valid)  # True

# Invalid address (ward not in that district)
valid = db.validate_hierarchy(
    ward="Cầu Diễn",
    district="Tân Bình",
    province="Hồ Chí Minh"
)
print(valid)  # False
```

**Use case:** Validate user input before saving to database.

---

## **Common Patterns**

### **Pattern 1: Address Autocomplete**

```python
def autocomplete_district(user_input: str, province: str) -> List[str]:
    """
    Suggest districts as user types
    """
    # Get all districts in province
    all_districts = db.get_districts_in_province(province)
    
    # Filter by user input (case-insensitive)
    normalized_input = db._normalize(user_input)
    matches = [
        d for d in all_districts 
        if normalized_input in db._normalize(d)
    ]
    
    return matches[:10]  # Limit to 10 suggestions

# Example
suggestions = autocomplete_district("nam", "Hà Nội")
print(suggestions)  # ["Nam Từ Liêm"]
```

### **Pattern 2: Address Parser**

```python
def parse_address(text: str) -> dict:
    """
    Extract province, district, ward from free text
    """
    normalized = db._normalize(text)
    tokens = normalized.split()
    
    result = {
        "province": None,
        "district": None,
        "ward": None
    }
    
    # Try to find province
    for i in range(len(tokens)):
        for j in range(i + 1, min(i + 4, len(tokens) + 1)):
            candidate = " ".join(tokens[i:j])
            province = db.lookup_province(candidate)
            if province:
                result["province"] = province
                break
    
    # Similar logic for district and ward...
    
    return result

# Example
address = parse_address("Cau Dien, Nam Tu Liem, Ha Noi")
print(address)
# {"province": "Hà Nội", "district": "Nam Từ Liêm", "ward": "Cầu Diễn"}
```

### **Pattern 3: Address Normalization**

```python
def normalize_address(ward: str, district: str, province: str) -> dict:
    """
    Convert user input to official names
    """
    # Lookup each component
    official_province = db.lookup_province(province)
    official_districts = db.lookup_district(district, province_context=official_province)
    official_wards = db.lookup_ward(ward, district_context=official_districts[0] if official_districts else None)
    
    if not (official_province and official_districts and official_wards):
        raise ValueError("Invalid address")
    
    # Validate hierarchy
    valid = db.validate_hierarchy(
        official_wards[0],
        official_districts[0],
        official_province
    )
    
    if not valid:
        raise ValueError("Address components don't match hierarchy")
    
    return {
        "province": official_province,
        "district": official_districts[0],
        "ward": official_wards[0]
    }

# Example
normalized = normalize_address("cau dien", "nam tu liem", "ha noi")
print(normalized)
# {"province": "Hà Nội", "district": "Nam Từ Liêm", "ward": "Cầu Diễn"}
```

### **Pattern 4: Batch Processing**

```python
def process_addresses(address_list: List[str]) -> List[dict]:
    """
    Process multiple addresses efficiently
    """
    results = []
    
    for addr in address_list:
        try:
            parsed = parse_address(addr)
            
            # Validate
            if parsed["province"] and parsed["district"] and parsed["ward"]:
                valid = db.validate_hierarchy(
                    parsed["ward"],
                    parsed["district"],
                    parsed["province"]
                )
                parsed["valid"] = valid
            else:
                parsed["valid"] = False
            
            results.append(parsed)
        except Exception as e:
            results.append({"error": str(e)})
    
    return results

# Example
addresses = [
    "Cau Dien, Nam Tu Liem, Ha Noi",
    "Tan Binh, HCM",
    "Invalid address here"
]

results = process_addresses(addresses)
for r in results:
    print(r)
```

---

## **Performance Notes**

### **Time Complexity**

| Operation | Complexity | Typical Time |
|-----------|------------|--------------|
| `lookup_province()` | O(1) | ~100 ns |
| `lookup_district()` | O(1) | ~100 ns |
| `lookup_ward()` | O(1) | ~100 ns |
| `get_full_address()` | O(k) | ~1 μs |
| `validate_hierarchy()` | O(1) | ~200 ns |
| `get_districts_in_province()` | O(k) | ~10 μs |

Where k = number of matches (usually 1-3)

### **Memory Usage**

- **Database size:** ~5-6 MB in memory
- **Build time:** ~15-20 ms
- **Recommendation:** Initialize once at startup, reuse across requests

### **Best Practices**

```python
# Good: Initialize once (singleton pattern)
class AddressService:
    _db = None
    
    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls._db = AddressDatabase()
        return cls._db

# Use it
db = AddressService.get_db()

# Bad: Don't initialize per request
def handle_request():
    db = AddressDatabase()  # Wastes 15ms per request!
    # ...
```

---

## **Troubleshooting**

### **Issue: Province not found**

```python
result = db.lookup_province("Hanoi")  # Returns None
```

**Solution:** Use Vietnamese name or known alias:
```python
result = db.lookup_province("Ha Noi")  # Works
result = db.lookup_province("hn")      # Works (alias)
```

### **Issue: Multiple matches for district**

```python
districts = db.lookup_district("Tan Binh")
# Returns: ["Tân Bình", "Tân Bình"]  # Which one?
```

**Solution:** Provide province context:
```python
districts = db.lookup_district("Tan Binh", province_context="Hồ Chí Minh")
# Returns: ["Tân Bình"]  # Unambiguous
```

### **Issue: FileNotFoundError**

```python
db = AddressDatabase(data_dir="Data")
# FileNotFoundError: [Errno 2] No such file or directory
```

**Solution:** Check relative path from your script location:
```python
# If running from Src/ and Data/ is at parent level:
db = AddressDatabase(data_dir="../Data")

# Or use absolute path:
from pathlib import Path
data_path = Path(__file__).parent.parent / "Data"
db = AddressDatabase(data_dir=str(data_path))
```

### **Issue: Validation fails unexpectedly**

```python
valid = db.validate_hierarchy("Cau Dien", "Nam Tu Liem", "Ha Noi")
# Returns: False (expected True)
```

**Debug:**
```python
# Check each component exists
province = db.lookup_province("Ha Noi")
print(f"Province: {province}")

districts = db.lookup_district("Nam Tu Liem", province_context=province)
print(f"Districts: {districts}")

wards = db.lookup_ward("Cau Dien", district_context=districts[0] if districts else None)
print(f"Wards: {wards}")

# Use exact names from lookups
valid = db.validate_hierarchy(wards[0], districts[0], province)
print(f"Valid: {valid}")
```

---

## **API Reference Summary**

```python
# Lookups (all O(1))
db.lookup_province(query: str) -> Optional[str]
db.lookup_district(query: str, province_context: Optional[str]) -> List[str]
db.lookup_ward(query: str, district_context: Optional[str]) -> List[str]

# Hierarchy queries
db.get_full_address(ward_name: str) -> List[AddressMatch]
db.get_districts_in_province(province_name: str) -> List[str]
db.get_wards_in_district(province_name: str, district_name: str) -> List[str]
db.validate_hierarchy(ward: str, district: str, province: str) -> bool

# Statistics
db.get_stats() -> dict
db.debug_info() -> None
```
