## **BUSINESS SCOPE DEFINITION**

### **Primary Business Objectives**
1. **Competition Success** (Primary Goal)
   - Achieve >85% accuracy on private test dataset
   - Meet strict performance requirements (<0.1s max, <0.01s average)
   - Deliver working solution within 3-week timeline

2. **Academic Learning** (Secondary Goal)
   - Master advanced algorithms (Tries, Dynamic Programming, Connected Components)
   - Gain experience with Vietnamese text processing and OCR error handling
   - Develop teamwork and project management skills

3. **Real-World Impact** (Tertiary Goal)
   - Create reusable Vietnamese address processing system
   - Demonstrate algorithmic approach to NLP problems without ML libraries
   - Build foundation for production Vietnamese text processing

### **Business Value Proposition**
- **For Competition**: Sophisticated algorithmic solution leveraging domain expertise
- **For Academic Growth**: Deep understanding of data structures applied to real-world problem
- **For Career Development**: Portfolio project demonstrating systems thinking and implementation skills

### **Success Metrics & KPIs**
| Metric Type | Requirement | Target | Business Impact |
|-------------|-------------|---------|-----------------|
| **Performance** | ≤0.1s max | ≤0.01s avg | Hard constraint (zero score if failed) |
| **Accuracy** | ≥85% | ≥90% | Primary ranking factor |
| **Reliability** | 100% uptime | Graceful degradation | Quality differentiator |
| **Documentation** | Complete | Professional | Team evaluation component |

---

## **TECHNICAL SCOPE DEFINITION**

### **Core Technical Requirements**

#### **1. Input/Output Specifications**
```python
# INPUT: Raw OCR Vietnamese address text
input_examples = [
    "Xã Thịnh Sơn H. Đô Lương T. Nghệ An",     # Clean
    "Xa Thinh Son H. Do Luong T. Nghe An",     # Diacritics lost
    "X ThuanThanh H. Can Giuoc, Long An",      # Multiple OCR errors
]

# OUTPUT: Structured JSON with confidence
output_format = {
    "address_info": {
        "province": "Nghệ An",
        "district": "Đô Lương", 
        "ward": "Thịnh Sơn"
    },
    "confidence": 0.95,
    "processing_time": 0.008
}
```

#### **2. Algorithm Architecture**
```
Tiered Processing Pipeline:
├── Tier 1: Exact Lookup Tables (60% coverage, <1ms)
├── Tier 2: Hierarchical Trie Matching (30% coverage, <5ms)  
└── Tier 3: Fuzzy Fallback with Constraints (10% coverage, <10ms)

Core Components:
├── Vietnamese Text Normalizer (remove diacritics, spacing)
├── Administrative Pattern Parser (X./H./T. recognition)
├── Multi-level Trie Data Structure (province→district→ward)
├── Geographic Constraint Validator (business rules)
└── Edit Distance Fuzzy Matcher (OCR error tolerance)
```

#### **3. Key Data Structures**
- **Hierarchical Tries**: Efficient prefix matching with geographic constraints
- **Exact Lookup Tables**: O(1) performance for common patterns
- **Geographic Constraint Database**: Validate administrative hierarchy
- **Character Confusion Maps**: Handle systematic OCR errors

#### **4. Performance Engineering**
```python
# Critical Performance Requirements
HARD_CONSTRAINTS = {
    "max_time_per_request": 0.1,    # Automatic failure if exceeded
    "target_avg_time": 0.01,        # Competitive performance
    "initialization_time": 30.0,    # Startup constraint
    "memory_usage": "reasonable"    # Single-core i5 environment
}

# Optimization Strategies
OPTIMIZATION_TECHNIQUES = [
    "Aggressive preprocessing during initialization",
    "Exact lookup caching for common patterns", 
    "Early termination in edit distance algorithms",
    "Geographic constraint-based search space reduction",
    "String interning for memory efficiency"
]
```

### **Technical Constraints & Boundaries**

#### **What's INCLUDED in Scope:**
✅ **Algorithm Implementation**
- Vietnamese text normalization and preprocessing
- Pattern-based administrative segment extraction
- Hierarchical trie-based matching with geographic constraints
- Fuzzy string matching with edit distance algorithms
- Confidence scoring and partial result handling

✅ **Data Structures**
- Multi-level trie implementation for hierarchical addresses
- Hash tables for exact lookups and caching
- Geographic relationship mapping (province→district→ward)
- OCR error pattern recognition and correction

✅ **Performance Optimization**
- Tiered processing (exact→pattern→fuzzy)
- Early termination algorithms
- Memory-efficient data structure design
- Comprehensive benchmarking and profiling

#### **What's EXCLUDED from Scope:**
❌ **Prohibited Technologies**
- Machine learning libraries (scikit-learn, spaCy, etc.)
- NLP frameworks and pre-trained models
- External API calls or internet dependency
- Database systems (must use in-memory structures)

❌ **Out-of-Scope Features**
- OCR preprocessing (input is already extracted text)
- Address geocoding or mapping integration
- Real-time learning or model updates
- Multi-language support beyond Vietnamese

### **Architecture Decision Records**

#### **ADR-001: Hierarchical Trie vs Flat Hash Tables**
- **Decision**: Use hierarchical tries with geographic constraints
- **Rationale**: Province→district→ward hierarchy reduces search space by 98%+
- **Trade-offs**: Higher complexity vs superior performance and accuracy

#### **ADR-002: Tiered Processing Strategy**
- **Decision**: Exact lookups → Pattern matching → Fuzzy fallback
- **Rationale**: Optimize for common cases (60%+ exact matches) while handling edge cases
- **Trade-offs**: Implementation complexity vs predictable performance

#### **ADR-003: Vietnamese-Specific Optimizations**
- **Decision**: Deep Vietnamese domain knowledge integration
- **Rationale**: Generic string matching insufficient for OCR noise + administrative patterns
- **Trade-offs**: Language-specific code vs competitive accuracy advantage

---

## **DEVELOPMENT SCOPE & TIMELINE**

### **3-Week Development Phases**

#### **Week 1: Foundation (Solo Development)**
- Core data structures and algorithms
- Text normalization and pattern recognition
- Basic matching with exact lookups
- Performance monitoring framework
- **Milestone**: >70% accuracy, <0.05s processing

#### **Week 2: Optimization (Solo → Team Transition)**  
- Hierarchical trie implementation
- Fuzzy matching with constraints
- Performance optimization
- Team integration preparation
- **Milestone**: >85% accuracy, <0.01s processing

#### **Week 3: Polish (Team Collaboration)**
- Edge case handling and robustness
- Comprehensive testing and validation
- Documentation and submission preparation
- Final performance tuning
- **Milestone**: Competition-ready solution with documentation

### **Risk Management & Contingency Plans**

#### **Technical Risks**
1. **Performance Bottleneck**: Implement fallback algorithms with simpler approaches
2. **Accuracy Plateau**: Use ensemble methods or parameter optimization
3. **Integration Complexity**: Strong solo foundation minimizes coordination risk

#### **Mitigation Strategies**
- **Performance Safety Net**: Simple exact-matching backup if optimization fails
- **Accuracy Validation**: Continuous testing against development dataset
- **Team Coordination**: Clear module boundaries and comprehensive documentation

---

## **DELIVERABLES & SUCCESS CRITERIA**

### **Technical Deliverables**
1. **Core Implementation**: Single-file Python classifier meeting all requirements
2. **Performance Reports**: Timing analysis and accuracy validation
3. **Test Suite**: Comprehensive unit and integration tests
4. **Documentation**: Technical specification and user guide

### **Business Deliverables**
1. **Competition Submission**: Optimized solution ready for evaluation
2. **Team Report**: Individual contributions and methodology
3. **Project Portfolio**: Professional documentation for academic/career use
4. **Knowledge Transfer**: Reusable Vietnamese text processing expertise

### **Final Success Definition**
**Minimum Success**: Meet all competition requirements (>85% accuracy, <0.1s processing)
**Target Success**: Competitive performance with professional implementation (>90% accuracy, <0.01s processing)
**Exceptional Success**: Top-tier solution with potential for real-world deployment

