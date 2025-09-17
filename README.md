# Vietnamese Address Classifier

## Competition Project: Vietnamese Address Classification

A high-performance algorithmic system for parsing noisy OCR-extracted Vietnamese addresses into structured components without using machine learning or NLP libraries.

### 🎯 Project Overview

- **Challenge**: Parse Vietnamese address text from OCR into structured province/district/ward components
- **Constraints**: No ML/NLP libraries, <0.1s max processing time, >85% accuracy target  
- **Duration**: 3 weeks development timeline
- **Team**: 3-5 members with solo foundation approach

### 🚀 Quick Start

```bash
# Clone and setup
git clone <repository_url>
cd address-classifier-demo
pip install -r requirements.txt

# Run the classifier
python run_classifier.py --input "Xã Thịnh Sơn H. Đô Lương T. Nghệ An"
```

### 📊 Performance Targets

| Metric | Requirement | Target | Status |
|--------|-------------|---------|---------|
| **Max Time** | ≤0.1s | ≤0.01s | 🔄 In Progress |
| **Accuracy** | >85% | >90% | 🔄 In Progress |
| **Coverage** | All cases | Graceful degradation | 🔄 In Progress |

### 🏗️ Architecture

```
Input Text → Normalizer → Pattern Parser → Hierarchical Matcher → Output JSON
                ↓              ↓                    ↓
           Vietnamese      Administrative      Multi-level Tries
           Text Cleanup    Prefix Detection    + Geographic Rules
```

### 📁 Project Structure

```
address-classifier-demo/
├── src/                    # Core implementation
├── data/                   # Training data and references
├── tests/                  # Comprehensive test suite
├── docs/                   # Project documentation
├── scripts/               # Development utilities
└── submission/            # Competition submission files
```

### 🎯 Development Phases

#### Phase 1: POC (Days 1-7) - "Prove It Works"
- ✅ Basic Vietnamese text normalization
- ✅ Pattern-based administrative segment extraction  
- ✅ Geographic constraint database
- ✅ Simple exact matching system
- **Target**: >70% accuracy, <0.05s processing

#### Phase 2: MVP (Days 8-14) - "Meet Requirements"  
- 🔄 Performance optimization and caching
- 🔄 Advanced fuzzy matching with constraints
- 🔄 Team integration and specialization
- **Target**: >85% accuracy, <0.01s average

#### Phase 3: Production (Days 15-21) - "Exceed & Win"
- 🔄 Competitive advantage optimizations
- 🔄 Comprehensive testing and validation
- 🔄 Professional documentation package
- **Target**: >90% accuracy, <0.005s average

### 🔧 Key Features

- **Vietnamese-Optimized**: Deep domain knowledge of Vietnamese administrative hierarchy
- **Performance-First**: Tiered processing (exact → pattern → fuzzy) for optimal speed
- **OCR-Robust**: Specialized handling of Vietnamese OCR error patterns
- **Geographic-Aware**: Hierarchical validation using province→district→ward constraints

### 📚 Documentation

- [📋 Requirements Document](docs/01_requirements.md)
- [🗂️ Phased Development Roadmap](docs/phased_development_roadmap.md)  
- [🏗️ Project Structure & Implementation Plan](docs/project_structure.md)
- [🇻🇳 Vietnamese Address Domain Knowledge](docs/vietnamese_address_domain.md)
- [📈 Business Analysis & Algorithm Insights](docs/business_analysis_guide.md)

### 🎮 Getting Started with Development

#### Day 1: Environment Setup
```bash
# Set up development environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Load and analyze training data
python scripts/analyze_data.py
```

#### Day 2: Text Normalization
```bash
# Implement Vietnamese text normalizer
python -m pytest tests/test_normalizer.py -v
```

### 🏆 Competitive Advantages

1. **Domain Expertise**: Deep Vietnamese address system knowledge vs generic approaches
2. **Performance**: 2-10x faster through hierarchical constraints and tiered processing  
3. **Accuracy**: Vietnamese-specific error patterns and geographic validation
4. **Robustness**: Comprehensive business rules and graceful degradation

### 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Performance testing
python scripts/benchmark.py

# Accuracy validation  
python scripts/validate_accuracy.py
```

### 🚀 Submission

Final submission will be a single optimized Python file with embedded data structures, meeting all competition requirements with significant safety margins.

### 🤝 Team Coordination

- **Solo Foundation (Days 1-11)**: Build complete working prototype
- **Team Integration (Days 12-21)**: Specialist roles for optimization, testing, documentation
- **Quality Gates**: Daily checkpoints with go/no-go decisions

### 📈 Progress Tracking

- **Technical KPIs**: Accuracy progression, performance optimization, test coverage
- **Business KPIs**: Team coordination, documentation quality, competitive positioning  
- **Risk Management**: Early warning indicators with mitigation strategies

---

**Status**: 🚀 Ready to Start Development  
**Next Milestone**: Day 7 - POC Validation (>70% accuracy, <0.05s processing)  
**Team**: Currently solo development, team integration planned for Day 12