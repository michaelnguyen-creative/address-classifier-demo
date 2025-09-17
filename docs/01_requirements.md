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
- **NFR-13**: