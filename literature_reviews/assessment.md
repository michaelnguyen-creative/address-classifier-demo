# **Assessment: Theoretical Foundations for Vietnamese Address Classification**

## **Core Algorithmic Concepts for Implementation**

Before diving into code, let's build understanding of the **three key algorithmic pillars** your system needs:

### **1. The Hierarchical Matching Problem**

**Intuition**: Vietnamese addresses follow a strict hierarchy: `Province → District → Ward`. Think of this like a **decision tree** where each level constrains the next.

**Key insight**: Why is this powerful algorithmically?
- If you identify "Long An" as province, you only need to search ~15 districts instead of 700+ nationwide
- This creates **O(log n) lookup** instead of O(n) linear search

**Question for you**: Looking at your config, you mention "hierarchical_matching: true" - can you think of why exact matching should be tried *before* fuzzy matching in each level?

### **2. The Text Normalization Challenge**

**Problem**: OCR gives you messy input like "Thịnh Sơn H. Đô Lương T. Nghệ An"

**Strategy**: Multi-stage cleaning pipeline:
```
Raw OCR → Diacritic Normalization → Abbreviation Expansion → Token Extraction
```

**Core question**: What's the trade-off between aggressive normalization (risk losing information) vs. conservative normalization (risk missing matches)?

### **3. The Speed vs. Accuracy Balance**

Your constraint is brutal: **<0.1s hard limit**, ideally <0.01s average.

**Algorithmic strategy** (from your docs):
```
Tier 1: Exact Hash Lookup    → O(1) for common cases
Tier 2: Pattern Recognition  → O(k) for structured patterns  
Tier 3: Fuzzy Matching       → O(n*m) for edge cases
```

**Critical insight**: Most addresses should resolve in Tier 1/2. Tier 3 is your safety net.