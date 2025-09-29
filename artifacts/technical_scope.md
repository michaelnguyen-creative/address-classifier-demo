## 🎯 **Technical Requirements Analysis: Vietnamese Address Classifier**
- Audience: Technical

### **🔧 System Architecture & Algorithm Design**

**Core Challenge**: Multi-class hierarchical classification with noisy input under extreme performance constraints.

```
Input Pipeline: OCR Text → Normalization → Pattern Extraction → Hierarchical Matching → Structured Output
```

### **📋 Functional Requirements Breakdown**

| ID | Requirement | Algorithmic Implications |
|----|-------------|--------------------------|
| **FR-01** | Parse Vietnamese text → JSON structure | Text parsing + structured data mapping |
| **FR-02** | Handle multiple noise patterns | Robust normalization pipeline required |
| **FR-03** | Hierarchical validation (P→D→W) | Geographic constraint graph traversal |
| **FR-04** | Confidence scoring | Probabilistic matching + uncertainty quantification |
| **FR-05** | Graceful degradation | Fallback algorithms + partial result handling |

### **⚡ Performance Requirements (Critical Path)**

| Metric | Hard Limit | Target | Algorithmic Strategy |
|--------|------------|--------|----------------------|
| **Max Time** for 1/1M requests | 0.1s | 0.01s | Tiered processing: exact → pattern → fuzzy |
| **Avg Time** | 0.01s | 0.005s | Precomputed lookups + early termination |
| **Memory** | Reasonable | Minimal | Embedded data structures, no external files |
| **Accuracy** | 85% | 90%+ | Vietnamese-specific domain optimization |

### **🏗️ Algorithm Strategy & Data Structures**

**Phase 1 Algorithms (Days 1-7):**
- **Text Normalization**: Unicode normalization + Vietnamese diacritic handling
- **Pattern Matching**: Regex-based administrative prefix detection  
- **Exact Lookup**: Hash tables for O(1) perfect matches
- **Basic Validation**: Province→District→Ward hierarchy checks

**Phase 2 Algorithms (Days 8-14):**
- **Fuzzy Matching**: Edit distance with Vietnamese-optimized costs
- **Trie Structures**: Prefix trees for O(k) substring matching
- **Performance Optimization**: Caching + early termination strategies

**Phase 3 Algorithms (Days 15-21):**
- **Advanced Heuristics**: Geographic proximity + administrative consistency
- **Competition Optimization**: Single-file deployment + embedded data

### **🎯 Technical Constraints & Design Decisions**

**Language & Libraries:**
- **Python only** (no C extensions for compatibility)
- **No ML/NLP libraries** (scikit-learn, spaCy prohibited)
- **Standard library + basic packages only**

**Data Structures Required:**
- **Province Database**: 63 entries with name variants
- **District Database**: ~700 entries with province relationships  
- **Ward Database**: ~11,000 entries with district relationships
- **Lookup Tables**: Precomputed exact matches for performance

### **🔍 Algorithm Complexity Analysis**

**Time Complexity Goals:**
- **Exact Match**: O(1) via hash lookup
- **Pattern Match**: O(n) where n = input length
- **Fuzzy Match**: O(k×m) where k = candidate count, m = string length
- **Overall System**: O(n) average case with tiered fallbacks

**Space Complexity:**
- **Embedded Data**: O(1) - preloaded at startup
- **Processing Memory**: O(n) - proportional to input size
- **Total Memory**: < 100MB for single-core i5 environment

