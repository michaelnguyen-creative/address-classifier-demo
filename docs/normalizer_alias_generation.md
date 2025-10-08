# Normal vs. Aggressive normalizer for alias generation

## **Concept 1: Understanding What Each Mode Produces**

Let me trace through concrete examples:Great! Now let's see what aliases would be generated from each:Interesting! Now let me analyze what happens during actual **matching**:Perfect! Now let me create a comprehensive trade-off analysis:

---

## **Concept 2: Trade-Off Analysis**Now let me show you the **critical decision matrix**:---

## **Concept 3: My Strong Recommendation**

**Use AGGRESSIVE mode for alias generation** ✅

**Here's why:**

### **1. Robustness to Input Variations**
```python
User types any of:
- "TP.HCM"
- "TP HCM"  
- "TPHCM"
- "tp.hcm"

All normalize to: "tp hcm"
All match aliases: {"tp hcm", "tphcm", "th", ...}
```

### **2. Tokenization Alignment**
```python
# Aggressive mode already gives you tokens:
"tp hcm" → ["tp", "hcm"]  # Clean split

# Normal mode needs extra processing:
"tp.hcm" → ["tp.hcm"]     # Single token!
           → split on dots → ["tp", "hcm"]  # Extra work
```

### **3. Consistency Guarantee**
```python
# BOTH must use aggressive:
db_aliases = generate_aliases("Hồ Chí Minh", aggressive=True)
parser_input = normalizer.normalize("TP.HCM", aggressive=True)
# → "tp hcm" matches alias "tp hcm" ✅
```

### **4. Real-World Address Messiness**
```python
# Vietnamese addresses are often messy:
"357/28,Ng-T- Thuật,P1,Q3,TP.HồChíMinh."

# Aggressive handles this:
→ "357 28 ng t thuat p1 q3 tp ho chi minh"
# Everything is cleanly tokenized!
```

---

## **Concept 4: Implementation Strategy**

Here's the refactoring plan:

```python
# 1. Update alias_generator.py
def generate_aliases(original_name: str, normalizer: TextNormalizer) -> Set[str]:
    # Use AGGRESSIVE mode
    base_name = normalizer.normalize(original_name, aggressive=True)
    # ... generate aliases from clean base

# 2. Update address_database.py
self.normalizer = TextNormalizer()  # Vietnamese by default

# When building tries:
aliases = generate_aliases(name, self.normalizer)

# 3. Update address_parser.py  
normalized = self.db.normalizer.normalize(text, aggressive=True)
```

---

**Final Answer:** Use **AGGRESSIVE MODE** for alias generation because:
1. ✅ Handles messy input
2. ✅ Consistent tokenization
3. ✅ Simpler matching logic
4. ✅ Just ensure parser ALSO uses aggressive mode
