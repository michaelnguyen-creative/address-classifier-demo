# Vietnamese Address Classifier - Technical Specification

## 1. System Architecture

### 1.1 High-Level Design

```
Input Text → Normalizer → Pattern Parser → Hierarchical Matcher → Output JSON
                ↓              ↓                    ↓
           Preprocessing    Segmentation      Multi-level Tries
                ↓              ↓                    ↓
           Exact Lookup → Fuzzy Fallback → Geographic Validation
```

### 1.2 Component Overview

| Component | Purpose | Performance Target |
|-----------|---------|-------------------|
| **Normalizer** | Text cleanup, diacritic removal | < 1ms |
| **Pattern Parser** | Administrative prefix detection | < 2ms |
| **Hierarchical Matcher** | Multi-level trie matching | < 5ms |
| **Fuzzy Fallback** | Edit distance matching | < 10ms (rare) |
| **Geographic Validator** | Consistency checking | < 1ms |

## 2. Data Structures

### 2.1 Multi-Level Trie Architecture

```python
class AddressTrie:
    """
    Hierarchical trie structure optimized for Vietnamese addresses
    """
    def __init__(self):
        self.provinces = TrieNode()  # Root level
        self.districts = {}          # province_id -> TrieNode
        self.wards = {}             # district_id -> TrieNode
        
    # Key operations: O(|query|) for exact, O(|query| * k) for fuzzy
```

**Design Rationale:**
- **Search space reduction**: Only search wards within identified district
- **Memory efficiency**: Shared prefixes compressed in trie structure
- **Performance**: Hierarchical constraints eliminate impossible combinations

### 2.2 Exact Lookup Tables

```python
class ExactLookup:
    """
    Preprocessed exact match tables for common variations
    """
    def __init__(self):
        # Normalized string -> (province, district, ward)
        self.complete_addresses = {}     # Full address strings
        self.province_variants = {}      # Province name variations  
        self.district_variants = {}      # District name variations
        self.ward_variants = {}         # Ward name variations
```

**Key Features:**
- **Aggressive normalization**: Remove diacritics, spaces, punctuation
- **Variation generation**: Common OCR errors, abbreviations
- **O(1) lookup time**: Hash table performance for exact matches

### 2.3 Geographic Constraint Database

```python
class GeographicDB:
    """
    Hierarchical relationships and validation rules
    """
    def __init__(self):
        self.province_to_districts = {}  # province_id -> [district_ids]
        self.district_to_wards = {}     # district_id -> [ward_ids]
        self.ward_to_district = {}      # ward_id -> district_id
        self.district_to_province = {}  # district_id -> province_id
```

## 3. Core Algorithms

### 3.1 Text Normalization Pipeline

```python
def normalize_text(text: str) -> str:
    """
    Multi-stage normalization for consistent processing
    Time Complexity: O(|text|)
    """
    # Stage 1: Unicode normalization (NFC)
    text = unicodedata.normalize('NFC', text)
    
    # Stage 2: Diacritic removal
    text = remove_diacritics(text)  # á→a, ô→o, ư→u
    
    # Stage 3: Case normalization  
    text = text.lower()
    
    # Stage 4: Punctuation/whitespace cleanup
    text = re.sub(r'[.,\-\s]+', ' ', text).strip()
    
    return text
```

**Performance Considerations:**
- **Precompiled regex**: Pattern compilation cached
- **Unicode handling**: Efficient diacritic mapping table
- **Memory reuse**: In-place string operations where possible

### 3.2 Pattern-Based Segmentation

```python
def parse_administrative_patterns(text: str) -> List[Tuple[str, str]]:
    """
    Extract administrative segments using pattern matching
    Time Complexity: O(|text|)
    """
    patterns = {
        'province': r'(?:t\.|tinh|tp\.|thanh\s+pho)\s*([^,]+)',
        'district': r'(?:h\.|huyen|q\.|quan|tx\.|thi\s+xa)\s*([^,]+)', 
        'ward': r'(?:x\.|xa|p\.|phuong|tt\.|thi\s+tran)\s*([^,]+)'
    }
    
    segments = []
    for level, pattern in patterns.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        segments.extend([(level, match.group(1).strip()) for match in matches])
    
    return segments
```

**Algorithm Properties:**
- **Order independent**: Handles T.X.H. or H.T.X. patterns
- **Abbreviation robust**: Supports both full and abbreviated forms
- **Noise tolerant**: Flexible whitespace/punctuation handling

### 3.3 Hierarchical Trie Matching

```python
def hierarchical_match(segments: List[Tuple[str, str]]) -> Optional[AddressResult]:
    """
    Multi-level trie matching with geographic validation
    Time Complexity: O(Σ|segment|) for exact, O(Σ|segment| * k) for fuzzy
    """
    # Phase 1: Exact matching at each level
    province = self.match_province_exact(segments)
    if not province:
        return None
        
    # Phase 2: District matching within province constraints
    districts = self.get_districts_in_province(province.id)
    district = self.match_district_exact(segments, districts)
    if not district:
        district = self.match_district_fuzzy(segments, districts, max_edits=2)
        
    # Phase 3: Ward matching within district constraints  
    if district:
        wards = self.get_wards_in_district(district.id)
        ward = self.match_ward_exact(segments, wards)
        if not ward:
            ward = self.match_ward_fuzzy(segments, wards, max_edits=2)
    
    return AddressResult(province, district, ward, confidence_score)
```

### 3.4 Edit Distance with Early Termination

```python
def bounded_edit_distance(s1: str, s2: str, max_edits: int) -> int:
    """
    Wagner-Fischer algorithm with early termination optimization
    Time Complexity: O(min(|s1| * |s2|, |s1| * max_edits))
    """
    if abs(len(s1) - len(s2)) > max_edits:
        return max_edits + 1  # Early termination
        
    # Use optimized DP with diagonal constraint
    prev_row = list(range(len(s2) + 1))
    
    for i in range(1, len(s1) + 1):
        curr_row = [i]
        min_in_row = i
        
        for j in range(1, len(s2) + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            curr_row.append(min(
                prev_row[j] + 1,      # deletion
                curr_row[j-1] + 1,    # insertion  
                prev_row[j-1] + cost  # substitution
            ))
            min_in_row = min(min_in_row, curr_row[j])
            
        # Early termination if all values exceed threshold
        if min_in_row > max_edits:
            return max_edits + 1
            
        prev_row = curr_row
    
    return prev_row[len(s2)]
```

## 4. Performance Optimizations

### 4.1 Preprocessing Strategy

```python
class AddressClassifier:
    def __init__(self, data_path: str):
        """
        Aggressive preprocessing during initialization
        Initialization time: < 30 seconds
        """
        start_time = time.time()
        
        # Load raw data
        self.raw_data = self.load_data(data_path)
        
        # Build exact lookup tables (5-10 seconds)
        self.exact_tables = self.build_exact_lookups()
        
        # Build hierarchical tries (10-15 seconds) 
        self.tries = self.build_hierarchical_tries()
        
        # Build geographic constraints (2-3 seconds)
        self.geo_db = self.build_geographic_database()
        
        # Precompile regex patterns (< 1 second)
        self.patterns = self.compile_patterns()
        
        print(f"Initialization completed in {time.time() - start_time:.2f}s")
```

### 4.2 Tiered Processing Strategy

```python
def classify_address(self, text: str) -> dict:
    """
    Tiered processing: exact → pattern → fuzzy fallback
    Target: < 0.01s average, < 0.1s maximum
    """
    start_time = time.perf_counter()
    
    # Tier 1: Exact lookup (< 1ms, ~60% of cases)
    normalized = self.normalize_text(text)
    if normalized in self.exact_tables.complete_addresses:
        result = self.exact_tables.complete_addresses[normalized]
        return self.format_result(result, time.perf_counter() - start_time)
    
    # Tier 2: Pattern + exact matching (< 5ms, ~30% of cases)
    segments = self.parse_patterns(text)
    if segments:
        result = self.hierarchical_exact_match(segments)
        if result and result.confidence > 0.8:
            return self.format_result(result, time.perf_counter() - start_time)
    
    # Tier 3: Fuzzy fallback (< 10ms, ~10% of cases)
    result = self.fuzzy_match_with_constraints(text, max_edits=2)
    return self.format_result(result, time.perf_counter() - start_time)
```

### 4.3 Memory Optimization Techniques

```python
# String interning for repeated address components
from sys import intern

class OptimizedAddressStorage:
    def __init__(self):
        # Use interned strings to reduce memory footprint
        self.provinces = {intern(name): id for name, id in province_data}
        self.districts = {intern(name): id for name, id in district_data}
        self.wards = {intern(name): id for name, id in ward_data}
        
        # Use slots for data classes
        @dataclass
        class AddressComponent:
            __slots__ = ['name', 'id', 'normalized']
            name: str
            id: int  
            normalized: str
```

## 5. Error Handling & Edge Cases

### 5.1 Input Validation

```python
def validate_input(self, text: str) -> Tuple[bool, str]:
    """Input validation with early error detection"""
    if not text or not text.strip():
        return False, "Empty input"
        
    if len(text) > 1000:  # Sanity check
        return False, "Input too long"
        
    if not re.search(r'[a-zA-ZÀ-ỹ]', text):  # Must contain letters
        return False, "No valid text found"
        
    return True, "Valid"
```

### 5.2 Graceful Degradation

```python
def handle_partial_matches(self, province=None, district=None, ward=None) -> dict:
    """
    Return best partial result when complete classification fails
    """
    confidence = 0.0
    if province:
        confidence += 0.4
    if district:  
        confidence += 0.3
    if ward:
        confidence += 0.3
        
    return {
        "address_info": {
            "province": province.name if province else None,
            "district": district.name if district else None,
            "ward": ward.name if ward else None
        },
        "confidence": confidence,
        "status": "partial_match"
    }
```

## 6. Testing Strategy

### 6.1 Unit Testing Framework

```python
# Test categories:
class TestAddressClassifier(unittest.TestCase):
    def test_normalization_pipeline(self):
        """Test text normalization accuracy and performance"""
        pass
        
    def test_pattern_extraction(self):
        """Test administrative pattern recognition"""
        pass
        
    def test_trie_operations(self):
        """Test trie insertion, search, fuzzy matching"""
        pass
        
    def test_performance_constraints(self):
        """Verify timing requirements on test data"""
        pass
```

### 6.2 Performance Benchmarking

```python
def benchmark_performance(self, test_cases: List[str]) -> dict:
    """
    Comprehensive performance analysis
    """
    times = []
    for text in test_cases:
        start = time.perf_counter()
        result = self.classify_address(text)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        
        # Fail fast if any request exceeds hard limit
        assert elapsed < 0.1, f"Request exceeded 0.1s limit: {elapsed:.4f}s"
    
    return {
        "avg_time": np.mean(times),
        "max_time": np.max(times), 
        "95th_percentile": np.percentile(times, 95),
        "within_limits": all(t < 0.1 for t in times)
    }
```

## 7. Configuration Management

### 7.1 Parameter Configuration

```python
# config.yaml
performance:
  max_processing_time: 0.1      # Hard limit (seconds)
  target_avg_time: 0.01         # Performance target
  
matching:
  max_edit_distance: 2          # Fuzzy matching threshold
  confidence_threshold: 0.8     # Minimum confidence for acceptance
  
normalization:
  remove_diacritics: true
  normalize_whitespace: true
  lowercase: true
```

### 7.2 Logging Configuration

```python
import logging

# Performance monitoring
logger = logging.getLogger('address_classifier')
logger.setLevel(logging.INFO)

def log_performance(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        
        if elapsed > 0.05:  # Log slow requests
            logger.warning(f"Slow request: {elapsed:.4f}s")
            
        return result
    return wrapper
```

## 8. Deployment Considerations

### 8.1 System Requirements
- **Python**: 3.8+
- **Memory**: ~500MB for data structures
- **CPU**: Single-core i5 or equivalent
- **Storage**: ~100MB for preprocessed data

### 8.2 Performance Monitoring

```python
class PerformanceMonitor:
    def __init__(self):
        self.request_times = deque(maxlen=1000)  # Recent request history
        self.slow_requests = []
        
    def record_request(self, elapsed_time: float):
        self.request_times.append(elapsed_time)
        if elapsed_time > 0.05:
            self.slow_requests.append(elapsed_time)
            
    def get_stats(self) -> dict:
        return {
            "avg_time": np.mean(self.request_times),
            "max_time": np.max(self.request_times),
            "slow_request_count": len(self.slow_requests)
        }
```

---

**Document Version**: 1.0  
**Last Updated**: [Current Date]  
**Status**: Draft - Ready for Implementation