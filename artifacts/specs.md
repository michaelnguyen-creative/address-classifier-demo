## 🎯 **What This Notebook Is Doing - A Conceptual Breakdown**

### **The Problem We're Solving**

Imagine you receive messy Vietnamese addresses from OCR (Optical Character Recognition) like:
- `"TT Tân Bình Huyện Yên Sơn, Tuyên Quang"` 
- `"357/28,Ng-T- Thuật,P1,Q3,TP.HồChíMinh."`

Your job: **Extract three pieces** → `province`, `district`, `ward`

---

### **How the Notebook Works**

**Step 1: Setup & Data Loading**
```python
# The notebook provides 3 reference data files:
self.province_path = 'list_province.txt'  # 63 provinces
self.district_path = 'list_district.txt'  # Hundreds of districts  
self.ward_path = 'list_ward.txt'         # Thousands of wards
```

**Step 2: Your Task - Implement `process()`**
```python
def process(self, s: str):
    # Input: Messy address string
    # Output: Clean dictionary
    return {
        "province": "",  # You extract this
        "district": "",  # You extract this
        "ward": ""       # You extract this
    }
```

**Step 3: Testing & Scoring**
The notebook:
1. Downloads test data (450 test cases)
2. Runs your `process()` on each test
3. Handles **normalization** (e.g., "Hoà Bình" = "Hòa Bình")
4. Scores you: 1 point per correct field
5. Max score: 450 tests × 3 fields = **1,350 points**

**Step 4: Output**
Creates an Excel file with:
- Summary sheet (score, time)
- Details sheet (each test result)

---

### **The Algorithm Challenge**

Think of this as a **hierarchical search problem**:

```
Vietnam (63 provinces)
  ├─ Province 1 (many districts)
  │   ├─ District 1 (many wards)
  │   │   ├─ Ward 1
  │   │   ├─ Ward 2
  │   │   └─ ...
  │   └─ District 2
  └─ Province 2
```

**Key Algorithmic Concepts:**

1. **String Matching** (easy → hard)
   - Exact match: `"Hà Nội"` finds `"Hà Nội"` ✓
   - Fuzzy match: `"Ha Noi"` finds `"Hà Nội"` ✓ 
   - Pattern match: `"TP.HCM"` finds `"Hồ Chí Minh"` ✓

2. **Hierarchical Constraints**
   - Province → District → Ward flows **downward**
   - `"Hà Đông"` (district) ONLY exists under `"Hà Nội"` (province)
   - Invalid: `"Hà Đông"` + `"Nghệ An"` ✗

3. **Data Structures**
   - **Trie** for prefix matching
   - **Hash tables** for exact lookups  
   - **Graphs** for geographic relationships

---

### **What You Need to Build**

**Phase 1: Text Normalization** (Foundation)
```python
# Before: "Ng-T- Thuật,P1,Q3,TP.HồChíMinh"
# After: "nguyen tu thuat p1 q3 tp ho chi minh"
```
- Remove accents (diacritics)
- Lowercase everything
- Handle abbreviations (`TP.` → `thanh pho`)

**Phase 2: Pattern Recognition** (Core Algorithm)
```python
# Identify administrative levels:
patterns = {
    'province': ['tỉnh', 'thành phố', 'tp.', 't.'],
    'district': ['quận', 'huyện', 'q.', 'h.'],  
    'ward': ['phường', 'xã', 'p.', 'x.']
}
```

**Phase 3: Matching Strategy** (Optimization)
```
Priority 1: Exact match (fast)
Priority 2: Pattern-based extraction (medium)
Priority 3: Fuzzy matching (slow, only if needed)
```

---

### **Performance Requirements**

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| **Speed** | <0.1s per address | 450 tests in <45s |
| **Accuracy** | >85% (1,148/1,350) | Passing grade |
| **Memory** | Efficient data structures | No memory errors |

---

### **Key Insight for Algorithm Design**

**Think "Search Space Reduction":**

```
🔴 BAD: Check ALL 63 provinces × ALL districts × ALL wards
        = Millions of comparisons per address

🟢 GOOD: 
   1. Find province first (63 options)
   2. Only check districts in THAT province (20-50 options)
   3. Only check wards in THAT district (10-100 options)
        = ~100-200 comparisons per address
```

This is the **hierarchical constraint** in action!

