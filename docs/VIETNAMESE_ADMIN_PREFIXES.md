# Complete Vietnamese Administrative Prefixes & Hierarchy

**Purpose:** Reference document for Vietnamese address parsing and normalization.

**Last Updated:** October 2025

**Sources:** Official Vietnamese government administrative divisions, ISO 3166-2:VN, postal service documentation

---

## 📋 **Administrative Hierarchy Overview**

Vietnam has a **3-tier administrative structure**:

```
Level 1: Province/City (Cấp Tỉnh)
    ├── 63 provinces (Tỉnh)
    └── 6 centrally-governed cities (Thành phố trực thuộc trung ương)

Level 2: District (Cấp Huyện)
    ├── Urban districts (Quận)
    ├── Rural districts (Huyện)
    ├── Provincial cities (Thành phố thuộc tỉnh)
    └── Towns (Thị xã)

Level 3: Ward/Commune (Cấp Xã)
    ├── Wards (Phường) - urban areas
    ├── Communes (Xã) - rural areas
    └── Townships (Thị trấn) - small urban centers
```

---

## 🏙️ **Level 1: Provincial/City Level (Cấp Tỉnh)**

### **Thành phố trực thuộc trung ương** (Centrally-Governed City)

| Full Form | Common Abbreviations | English Translation |
|-----------|---------------------|---------------------|
| Thành phố trực thuộc trung ương | TP, TP., Tp, Tp. | Centrally-governed city |

**Usage:** Only 6 cities in Vietnam have this status:
- Hà Nội
- Hồ Chí Minh (TP.HCM)
- Đà Nẵng
- Hải Phòng
- Cần Thơ
- (Previously) Đà Lạt

**Examples:**
```
TP.HCM → Hồ Chí Minh
TP. Hà Nội → Hà Nội
Tp Đà Nẵng → Đà Nẵng
```

---

### **Tỉnh** (Province)

| Full Form | Common Abbreviations | English Translation |
|-----------|---------------------|---------------------|
| Tỉnh | T, T. | Province |

**Usage:** All other first-level administrative units (63 total)

**Examples:**
```
T. Bình Dương → Bình Dương
Tỉnh Lâm Đồng → Lâm Đồng
```

---

## 🏘️ **Level 2: District Level (Cấp Huyện)**

### **Quận** (Urban District)

| Full Form | Common Abbreviations | English Translation |
|-----------|---------------------|---------------------|
| Quận | Q, Q. | Urban district |

**Usage:** Districts within major cities (typically numbered or named)

**Examples:**
```
Q.1 → 1
Q. 3 → 3
Q. Bình Thạnh → Bình Thạnh
Quận Tân Bình → Tân Bình
```

**Note:** Urban districts are found in major cities like:
- Hồ Chí Minh City: Q.1, Q.2, ... Q.12, Bình Thạnh, Tân Bình, etc.
- Hà Nội: Ba Đình, Hoàn Kiếm, Đống Đa, etc.

---

### **Huyện** (Rural District)

| Full Form | Common Abbreviations | English Translation |
|-----------|---------------------|---------------------|
| Huyện | H, H. | Rural district |

**Usage:** Districts in less urbanized areas

**Examples:**
```
H. Củ Chi → Củ Chi
Huyện Nhà Bè → Nhà Bè
H. Bình Chánh → Bình Chánh
```

---

### **Thành phố** (Provincial City)

| Full Form | Common Abbreviations | English Translation |
|-----------|---------------------|---------------------|
| Thành phố (thuộc tỉnh) | TP, TP., Tp, Tp. | Provincial city |

**Usage:** Cities within provinces (second-tier cities)

**⚠️ CRITICAL:** This creates **ambiguity** with Level 1 cities!

**Examples:**
```
TP. Thủ Dầu Một (in Bình Dương province)
TP. Biên Hòa (in Đồng Nai province)
Tp Vũng Tàu (in Bà Rịa-Vũng Tàu province)
```

**Disambiguation Strategy:**
- Level 1: Only 6 cities (Hà Nội, HCM, Đà Nẵng, Hải Phòng, Cần Thơ, Đà Lạt)
- Level 2: All other "TP" references are provincial cities

---

### **Thị xã** (Town)

| Full Form | Common Abbreviations | English Translation |
|-----------|---------------------|---------------------|
| Thị xã | TX, TX., Tx, Tx. | Town |

**Usage:** Semi-urban administrative units, typically smaller than cities

**Examples:**
```
TX. Thuận An → Thuận An
Thị xã Tân Uyên → Tân Uyên
TX. Dĩ An → Dĩ An
```

---

## 🏡 **Level 3: Ward/Commune Level (Cấp Xã)**

### **Phường** (Ward)

| Full Form | Common Abbreviations | English Translation |
|-----------|---------------------|---------------------|
| Phường | P, P. | Ward |

**Usage:** Urban subdivisions within districts

**Examples:**
```
P. Tân Định → Tân Định
Phường Bến Nghé → Bến Nghé
P.12 → 12
P. Nguyễn Thái Bình → Nguyễn Thái Bình
```

**Note:** Wards are numbered in some cities (P.1, P.2) or named.

---

### **Xã** (Commune)

| Full Form | Common Abbreviations | English Translation |
|-----------|---------------------|---------------------|
| Xã | X, X. | Commune |

**Usage:** Rural subdivisions

**Examples:**
```
X. Phú Mỹ Hưng → Phú Mỹ Hưng
Xã Tân Thông Hội → Tân Thông Hội
X. Lê Minh Xuân → Lê Minh Xuân
```

---

### **Thị trấn** (Township)

| Full Form | Common Abbreviations | English Translation |
|-----------|---------------------|---------------------|
| Thị trấn | TT, TT., Tt, Tt. | Township/Townlet |

**Usage:** Small urban centers within rural districts (capitals of rural districts)

**Examples:**
```
TT. Củ Chi → Củ Chi
Thị trấn Hóc Môn → Hóc Môn
TT. Tân Túc → Tân Túc
```

---

## 🛣️ **Additional Address Elements (Non-Administrative)**

These appear in addresses but are **not administrative divisions**:

### **Street/Road Terms**

| Term | Abbreviations | English | Region | Notes |
|------|--------------|---------|--------|-------|
| **Đường** | Đ, Đ., D, D. | Street/Road | Nationwide | "D" used when no Vietnamese keyboard |
| **Phố** | - | Street | Northern Vietnam | More common in Hanoi |
| **Ngõ** | - | Alley/Lane | Northern Vietnam | Smaller than đường |
| **Hẻm** | - | Alley | Southern Vietnam | Used in HCM City area |

### **Other Terms**

| Term | Abbreviations | English | Usage |
|------|--------------|---------|-------|
| **Khu phố** | KP, KP. | Neighborhood | Subdivision within ward |
| **Ấp** | - | Hamlet | Rural subdivision (unofficial 4th tier) |
| **Thôn** | - | Village | Rural subdivision (unofficial 4th tier) |
| **Tổ dân phố** | - | Residential group | Urban subdivision (unofficial 4th tier) |

---

## ⚠️ **Critical Ambiguities**

### **1. "TP" Ambiguity**

**Problem:** "TP" can mean two different things:

```
Context: Province level
"TP.HCM" → Thành phố Hồ Chí Minh (Level 1 city)

Context: District level (within a province)
"TP. Thủ Dầu Một" → Provincial city in Bình Dương (Level 2)
```

**Resolution Strategy:**
- Maintain a list of 6 Level 1 cities
- All other "TP" references are Level 2 provincial cities

---

### **2. Province Code Ambiguities**

**Problem:** Some abbreviations map to multiple provinces:

```
"DN" → Could be:
    - Đà Nẵng (city code: DN, DA)
    - Đồng Nai (province code: DN, DON)
    - Đắk Nông (province code: DN, DNO)

"HCM" or "HCMC" → 
    - Hồ Chí Minh City (unambiguous)

"HP" →
    - Hải Phòng (city)
    - Hòa Bình (province - but usually HB)
```

**Resolution Strategy:**
- Use context from surrounding text
- Prioritize major cities (Đà Nẵng over Đồng Nai for "DN")
- Maintain comprehensive mapping with confidence scores

---

### **3. "Đ" vs "D" Ambiguity**

**Problem:** "D" could be:

```
"D" → Đường (street prefix)
"D" → Đà (part of place name like "Đà Nẵng")
"D" → ASCII representation of "Đ" (no Vietnamese keyboard)
```

**Resolution Strategy:**
- Check position in address (prefix vs. part of name)
- Use context clues (followed by street name vs. city name)

---

## 📊 **Common Abbreviation Patterns**

### **Province/City Codes (ISO-style)**

| Province/City | Official Name | Common Codes |
|--------------|---------------|--------------|
| Hồ Chí Minh | Thành phố Hồ Chí Minh | HCM, HCMC, SG (Saigon) |
| Hà Nội | Thành phố Hà Nội | HN, HA |
| Đà Nẵng | Thành phố Đà Nẵng | DN, DA, DAD |
| Hải Phòng | Thành phố Hải Phòng | HP, HAI |
| Cần Thơ | Thành phố Cần Thơ | CT, CTO |
| Bình Dương | Tỉnh Bình Dương | BD, BDU |
| Đồng Nai | Tỉnh Đồng Nai | DN, DON |
| Lâm Đồng | Tỉnh Lâm Đồng | LD, LDO |

**Note:** These codes are used in postal systems, vehicle registration, but NOT standardized across all systems.

---

## 🎯 **Parsing Strategy Recommendations**

### **1. Prefix Identification**

```python
# Order matters! Check longer patterns first
PREFIX_PATTERNS = [
    # Full forms (longest first)
    'Thành phố trực thuộc trung ương',
    'Thành phố',
    'Tỉnh',
    'Quận',
    'Huyện', 
    'Thị xã',
    'Phường',
    'Xã',
    'Thị trấn',
    'Đường',
    
    # Abbreviated forms (with dots)
    'TP.',
    'TX.',
    'TT.',
    'Q.',
    'H.',
    'P.',
    'X.',
    'Đ.',
    'D.',
    'T.',
    
    # Abbreviated forms (without dots)
    'TP',
    'TX',
    'TT',
    'Tp',
    'Tx',
    'Tt',
]
```

### **2. Context-Aware Processing**

```python
def extract_admin_entity(text, level):
    """
    Extract administrative entity name based on hierarchical level
    
    Args:
        text: Input text (e.g., "TP.HCM")
        level: 'province', 'district', or 'ward'
    
    Returns:
        Core entity name with prefix removed
    """
    # Use level-specific prefix list
    # Apply appropriate expansion rules
    # Return normalized entity name
```

### **3. Known Entity Validation**

```python
# Validate against database of known entities
KNOWN_PROVINCES = {'Hà Nội', 'Hồ Chí Minh', ...}
KNOWN_DISTRICTS = {'Quận 1', 'Quận 2', 'Ba Đình', ...}
KNOWN_WARDS = {'Phường 1', 'Bến Nghé', ...}

# Cross-reference extracted names with database
```

---

## 📝 **Real-World Address Examples**

### **Example 1: Ho Chi Minh City Address**

```
Input:
123 Nguyễn Huệ, P. Bến Nghé, Q.1, TP.HCM

Parsing:
├── Street: "123 Nguyễn Huệ"
├── Ward: "P. Bến Nghé" → Extract: "Bến Nghé"
├── District: "Q.1" → Extract: "1"
└── City: "TP.HCM" → Extract: "Hồ Chí Minh"

Normalized:
{
    "street": "123 nguyen hue",
    "ward": "ben nghe",
    "district": "1",
    "province": "ho chi minh"
}
```

### **Example 2: Hanoi Address**

```
Input:
45 Phố Huế, P. Ngô Thì Nhậm, Q. Hai Bà Trưng, Hà Nội

Parsing:
├── Street: "45 Phố Huế"
├── Ward: "P. Ngô Thì Nhậm" → Extract: "Ngô Thì Nhậm"
├── District: "Q. Hai Bà Trưng" → Extract: "Hai Bà Trưng"
└── City: "Hà Nội" → Extract: "Hà Nội"

Normalized:
{
    "street": "45 pho hue",
    "ward": "ngo thi nham",
    "district": "hai ba trung",
    "province": "ha noi"
}
```

### **Example 3: Provincial Address**

```
Input:
Số 7, TT. Củ Chi, H. Củ Chi, TP.HCM

Parsing:
├── Street: "Số 7"
├── Township: "TT. Củ Chi" → Extract: "Củ Chi"
├── District: "H. Củ Chi" → Extract: "Củ Chi"
└── City: "TP.HCM" → Extract: "Hồ Chí Minh"

Normalized:
{
    "street": "so 7",
    "ward": "cu chi",
    "district": "cu chi", 
    "province": "ho chi minh"
}
```

### **Example 4: Rural Address**

```
Input:
Ấp 3, X. Tân Thông Hội, H. Củ Chi, TP.HCM

Parsing:
├── Hamlet: "Ấp 3" (unofficial subdivision)
├── Commune: "X. Tân Thông Hội" → Extract: "Tân Thông Hội"
├── District: "H. Củ Chi" → Extract: "Củ Chi"
└── City: "TP.HCM" → Extract: "Hồ Chí Minh"

Normalized:
{
    "ward": "tan thong hoi",
    "district": "cu chi",
    "province": "ho chi minh"
}
```

---

## 🔍 **Edge Cases & Special Situations**

### **1. Abbreviated Informal Writing**

People often use ultra-short forms in casual communication:

```
"Q1" instead of "Q.1" or "Quận 1"
"P12" instead of "P.12" or "Phường 12"
"HCMC" instead of "TP.HCM"
"CMT8" instead of "Cách Mạng Tháng 8" (street name)
```

### **2. Mixed Formats**

```
"Q. 1" (space after dot)
"Q.1" (no space)
"Q1" (no dot, no space)
"Quận 1" (full form)
```

All refer to the same district.

### **3. Historical Names**

Some places have old names still in use:

```
"Sài Gòn" → "Hồ Chí Minh" (old name for HCMC)
"Gia Định" → Old province that became HCMC
```

### **4. Merged/Split Administrative Units**

Administrative boundaries change over time. Recent changes (2020s):
- Thủ Đức became a city-level district (from 3 districts)
- Various rural districts upgraded to towns
- Some provinces merged (check Wikipedia for recent changes)

---

## 📚 **References & Data Sources**

### **Official Sources**
1. **General Statistics Office of Vietnam** - https://www.gso.gov.vn/
2. **Vietnam Postal Corporation** - https://www.vnpost.vn/
3. **ISO 3166-2:VN** - International standard for subdivision codes
4. **Decision 124/2004/QĐ-TTg** - Administrative unit coding system

### **Useful Resources**
1. Vietnamese Wikipedia - Administrative divisions
2. OpenStreetMap Vietnam - Community-maintained geographic data
3. GADM Database - Global administrative areas dataset

### **For Developers**
1. Vietnam Provinces API - Community-maintained province/district/ward data
2. Address validation services (Smarty, PostGrid)
3. Vietnam postal code database

---

## 🛠️ **Implementation Notes**

### **For Address Parser Development**

1. **Priority Order:**
   - Match against known full names first
   - Then try prefix + name patterns
   - Finally attempt fuzzy matching

2. **Normalization Pipeline:**
   ```
   Raw Input → Remove Diacritics → Remove Prefixes → 
   Expand Abbreviations → Fuzzy Match → Validate
   ```

3. **Database Structure:**
   ```sql
   provinces (id, name, code, aliases)
   districts (id, name, code, province_id, aliases)
   wards (id, name, code, district_id, aliases)
   ```

4. **Alias Table:**
   Store all possible variations for each entity:
   ```
   Entity: "Hồ Chí Minh"
   Aliases: ["TP.HCM", "TPHCM", "HCM", "HCMC", "Sài Gòn", "Saigon"]
   ```

---

## ✅ **Validation Checklist**

When implementing prefix handling:

- [ ] Handle both dotted (TP.) and non-dotted (TP) forms
- [ ] Handle both uppercase and lowercase
- [ ] Handle full forms and abbreviations
- [ ] Disambiguate "TP" based on context (Level 1 vs Level 2)
- [ ] Handle province code ambiguities (DN, HP, etc.)
- [ ] Preserve original entity names for display
- [ ] Return normalized forms for matching
- [ ] Handle missing or malformed prefixes gracefully
- [ ] Validate extracted entities against database
- [ ] Support hierarchical validation (ward must belong to district)

---

## 📊 **Statistics (As of 2024)**

- **Level 1:** 63 provinces + 6 centrally-governed cities = **69 units**
- **Level 2:** ~700 districts (quận, huyện, thành phố, thị xã)
- **Level 3:** ~10,500 wards/communes (phường, xã, thị trấn)

**Total addressable administrative units:** ~11,269

---

**Document Version:** 1.0  
**Created:** October 2025  
**For:** Vietnamese Address Parser - Administrative Prefix Handler Module
