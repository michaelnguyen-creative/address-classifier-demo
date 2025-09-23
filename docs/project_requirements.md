# Vietnamese Address Classifier - Requirements Document

## 1. Project Overview

### 1.1 Problem Statement
Develop an algorithmic system to parse noisy OCR-extracted Vietnamese addresses into structured components (province/tỉnh, district/huyện, ward/xã) without using machine learning or NLP libraries.

### 1.2 Context
- **Source**: Advanced Algorithms course project
- **Duration**: 3 weeks
- **Team Size**: 3-5 members (working solo initially)
- **Data Source**: OCR text from Vietnamese ID documents

## 2. Functional Requirements

### 2.1 Core Functionality
- **FR-01**: Parse unstructured Vietnamese address text into structured JSON format
- **FR-02**: Handle multiple input formats and noise patterns
- **FR-03**: Support hierarchical address validation (province → district → ward)
- **FR-04**: Return confidence scores for classifications
- **FR-05**: Handle missing or incomplete address components gracefully

### 2.2 Input/Output Specifications

#### Input Format
```
Raw OCR text strings with various noise patterns:
- "Xã Thịnh Sơn H. Đô Lương T. Nghệ An" (clean)
- "Xa Thịnh Sơn H. Đô Lương T. Nghệ An" (missing diacritics)
- "Thuận Thành, HCần Giuộc, Tlong An" (spacing errors)
- "X ThuanThanh H. Can Giuoc, Long An" (multiple errors)
```

#### Output Format
```json
{
    "address_info": {
        "province": "Nghệ An",
        "district": "Đô Lương", 
        "ward": "Thịnh Sơn"
    },
    "confidence": 0.95,
    "processing_time": 0.008
}
```

### 2.3 Error Handling
- **FR-06**: Return partial results when complete classification impossible
- **FR-07**: Provide error codes for different failure modes
- **FR-08**: Log processing statistics for debugging

## 3. Non-Functional Requirements

### 3.1 Performance Requirements (CRITICAL)
- **NFR-01**: **Maximum processing time**: ≤ 0.1 seconds per request (HARD LIMIT)
- **NFR-02**: **Average processing time**: ≤ 0.01 seconds per request
- **NFR-03**: **Memory usage**: Reasonable for single-core i5 environment
- **NFR-04**: **Initialization time**: < 30 seconds for loading data structures

### 3.2 Accuracy Requirements
- **NFR-05**: **Target accuracy**: > 85% on development set
- **NFR-06**: **Graceful degradation**: Partial matches when perfect match impossible
- **NFR-07**: **Consistency**: Same input always produces same output

### 3.3 Technical Constraints
- **NFR-08**: **Language**: Python only
- **NFR-09**: **Libraries**: No ML/NLP libraries (scikit-learn, spaCy, etc.)
- **NFR-10**: **Runtime**: Offline execution (no internet access)
- **NFR-11**: **Platform**: Single-core i5 CPU, no GPU

### 3.4 Maintainability Requirements
- **NFR-12**: **Code quality**: Clean, documented, testable code
- **NFR-13**: **Modularity**: Separable components for easy team development
- **NFR-14**: **Configuration**: Easy parameter tuning without code changes

## 4. Data Requirements

### 4.1 Training Data
- **1000 labeled samples** in JSON format
- Supporting reference lists: provinces, districts, wards
- Geographic hierarchy relationships

### 4.2 Test Data
- **Public test**: 20% weight in final scoring
- **Private test**: 80% weight in final scoring  
- **Free test**: 1 submission allowed

### 4.3 Data Quality Assumptions
- OCR noise patterns are representative of real-world Vietnamese ID documents
- Geographic data is complete and up-to-date
- Hierarchical relationships are accurate

## 5. Success Criteria

### 5.1 Primary Success Metrics
1. **Performance compliance**: All requests complete within time limits
2. **Accuracy threshold**: > 85% correct classifications on private test
3. **System reliability**: No crashes or timeouts during evaluation

### 5.2 Secondary Success Metrics
1. **Code quality**: Clean, maintainable implementation
2. **Team coordination**: Successful collaboration and task delegation
3. **Documentation**: Complete project artifacts and technical documentation

## 6. Risk Assessment

### 6.1 High Risk
- **Performance bottlenecks**: Exceeding 0.1s limit results in zero score
- **Algorithm complexity**: Fuzzy matching may be too slow
- **Data preprocessing**: Incorrect normalization reduces accuracy

### 6.2 Medium Risk  
- **OCR noise patterns**: Development data may not represent test data
- **Geographic data gaps**: Missing ward/district combinations
- **Team coordination**: Solo development then delegation challenges

### 6.3 Mitigation Strategies
- **Performance**: Implement tiered matching (exact → pattern → fuzzy)
- **Testing**: Extensive timing benchmarks throughout development
- **Validation**: Cross-validation on development data
- **Fallback**: Simple exact matching as performance safety net

## 7. Acceptance Criteria

### 7.1 Technical Acceptance
- [ ] All functional requirements implemented
- [ ] Performance requirements verified with benchmarks
- [ ] Code passes quality checks (linting, testing)
- [ ] System handles edge cases gracefully

### 7.2 Business Acceptance  
- [ ] Accuracy meets threshold on validation set
- [ ] Processing time consistently under limits
- [ ] Output format matches specification exactly
- [ ] Error handling provides meaningful feedback

## 8. Deliverables

### 8.1 Code Deliverables
- **Core classifier module** with main processing logic
- **Data preprocessing utilities** for normalization and loading
- **Performance benchmarking scripts** 
- **Unit tests** for all major components
- **Integration script** for final submission format

### 8.2 Documentation Deliverables
- **Technical specification** (algorithms and data structures)
- **User manual** (how to run the system)
- **Performance analysis** (timing and accuracy reports)
- **Team contribution log** (individual responsibilities)

### 8.3 Data Deliverables
- **Preprocessed data structures** (tries, lookup tables)
- **Configuration files** (parameters, mappings)
- **Test datasets** (validation splits, edge cases)

---

**Document Version**: 1.0  
**Last Updated**: [Current Date]  
**Status**: Draft - Ready for Technical Specification