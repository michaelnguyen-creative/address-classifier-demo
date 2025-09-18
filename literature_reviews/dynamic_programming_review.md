# Dynamic Programming Applications in Text Processing: Literature Review

## Overview
This literature review examines dynamic programming (DP) algorithms and their applications in text processing, string matching, and natural language processing tasks relevant to address classification and OCR post-processing.

## 1. Theoretical Foundations of Dynamic Programming

### 1.1 Core Principles
**Reference**: Bellman (1957). *Dynamic Programming*

- **Optimal Substructure**: Optimal solution contains optimal solutions to subproblems
- **Overlapping Subproblems**: Recursive solution recomputes same subproblems
- **Memoization**: Store computed results to avoid redundant calculations
- **Bottom-up Construction**: Build solutions incrementally from smaller subproblems

### 1.2 DP Design Methodology
**Reference**: Cormen et al. (2009). *Introduction to Algorithms, 3rd Edition*

#### Design Steps:
1. **Characterize Structure**: Define optimal substructure property
2. **Define Recurrence**: Express solution in terms of subproblems
3. **Compute Bottom-up**: Fill DP table in appropriate order
4. **Construct Solution**: Trace back through DP table if needed

#### Time-Space Trade-offs:
- **Time Complexity**: Typically O(subproblems × time per subproblem)
- **Space Complexity**: Can often be optimized using rolling arrays
- **Practical Considerations**: Cache locality, memory access patterns

## 2. Classic String Processing DP Algorithms

### 2.1 Longest Common Subsequence (LCS)
**Reference**: Hunt & Szymanski (1977). "A fast algorithm for computing longest common subsequences"

#### Problem Definition:
- **Input**: Two strings X[1..m] and Y[1..n]
- **Output**: Length of longest subsequence common to both strings
- **Applications**: Diff algorithms, DNA sequence alignment, plagiarism detection

#### DP Formulation:
```
LCS[i][j] = {
    0                           if i = 0 or j = 0
    LCS[i-1][j-1] + 1          if X[i] = Y[j]
    max(LCS[i-1][j], LCS[i][j-1])  if X[i] ≠ Y[j]
}
```

#### Complexity Analysis:
- **Time**: O(m × n)
- **Space**: O(m × n), reducible to O(min(m,n)) for length-only computation
- **Practical Optimization**: Myers' O((m+n)D) algorithm for small edit distances

### 2.2 Edit Distance (Levenshtein Distance)
**Reference**: Levenshtein (1966). "Binary codes capable of correcting deletions, insertions, and reversals"

#### Problem Definition:
- **Operations**: Insert, delete, substitute characters
- **Goal**: Minimum operations to transform string A into string B
- **Applications**: Spell checking, OCR error correction, fuzzy string matching

#### DP Recurrence:
```
Edit[i][j] = {
    i                              if j = 0
    j                              if i = 0
    Edit[i-1][j-1]                if A[i] = B[j]
    1 + min(Edit[i-1][j],         // deletion
            Edit[i][j-1],         // insertion  
            Edit[i-1][j-1])       // substitution
}
```

#### Advanced Variants:
- **Weighted Edit Distance**: Different costs for operations
- **Damerau-Levenshtein**: Includes transposition operations
- **Jaro-Winkler**: Optimized for name matching applications

### 2.3 Longest Increasing Subsequence (LIS)
**Reference**: Patience sorting and Erdős–Szekeres theorem applications

#### Problem Definition:
- **Input**: Sequence of numbers A[1..n]
- **Output**: Length of longest strictly increasing subsequence
- **Applications**: Scheduling, box stacking, envelope problems

#### DP Formulation:
```
LIS[i] = 1 + max{LIS[j] : j < i and A[j] < A[i]}
```

#### Optimization to O(n log n):
- **Binary Search**: Maintain array of smallest tail elements
- **Patience Sorting**: Card game inspired algorithm
- **Applications**: Version control systems, sequence alignment

## 3. Advanced String Matching with DP

### 3.1 Approximate String Matching
**Reference**: Navarro & Raffinot (2002). *Flexible Pattern Matching in Strings*

#### k-Approximate Matching:
- **Problem**: Find all occurrences of pattern P in text T with at most k errors
- **DP Solution**: Extend edit distance to handle pattern matching
- **Applications**: Bioinformatics, information retrieval, spell checking

#### Optimized Algorithms:
- **Ukkonen's Cutoff**: Early termination when k errors exceeded
- **Myers' Bit-Parallel**: Use bit operations for small k values
- **Four Russians**: Speed up using lookup tables

### 3.2 Regular Expression Matching
**Reference**: Thompson (1968). "Programming techniques: Regular expression search algorithm"

#### DP Approach:
```python
def match_regex(text, pattern):
    m, n = len(text), len(pattern)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    
    # Base cases
    dp[0][0] = True
    for j in range(2, n + 1, 2):
        if pattern[j-1] == '*':
            dp[0][j] = dp[0][j-2]
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if pattern[j-1] == text[i-1] or pattern[j-1] == '.':
                dp[i][j] = dp[i-1][j-1]
            elif pattern[j-1] == '*':
                dp[i][j] = dp[i][j-2]  # Zero occurrences
                if pattern[j-2] == text[i-1] or pattern[j-2] == '.':
                    dp[i][j] = dp[i][j] or dp[i-1][j]  # One or more
    
    return dp[m][n]
```

#### Performance Characteristics:
- **Time**: O(m × n) for basic DP approach
- **Space**: O(m × n), optimizable to O(n)
- **Alternative**: NFA/DFA construction for repeated matching

### 3.3 Sequence Alignment Algorithms
**Reference**: Needleman & Wunsch (1970). "A general method applicable to the search for similarities in amino acid sequences"

#### Global Alignment:
- **Scoring**: Match/mismatch scores, gap penalties
- **Applications**: Bioinformatics, plagiarism detection, version control
- **Extensions**: Local alignment (Smith-Waterman), multiple sequence alignment

#### Affine Gap Penalties:
```
Recurrence with gap opening (d) and extension (e) penalties:
M[i][j] = max(M[i-1][j-1], X[i-1][j-1], Y[i-1][j-1]) + s(i,j)
X[i][j] = max(M[i-1][j] - d, X[i-1][j] - e)
Y[i][j] = max(M[i][j-1] - d, Y[i][j-1] - e)
```

## 4. DP in Natural Language Processing

### 4.1 Text Segmentation
**Reference**: Ponte & Croft (1997). "Text segmentation by topic"

#### Word Segmentation:
- **Problem**: Split continuous text into words (Chinese, Thai, Vietnamese)
- **DP Approach**: Minimize cost of segmentation using dictionary
- **Applications**: Asian language processing, compound word splitting

```python
def segment_text(text, dictionary):
    n = len(text)
    dp = [float('inf')] * (n + 1)
    dp[0] = 0
    
    for i in range(1, n + 1):
        for j in range(i):
            word = text[j:i]
            if word in dictionary:
                dp[i] = min(dp[i], dp[j] + cost(word))
    
    return dp[n]
```

#### Topic Segmentation:
- **Objective**: Split text into topically coherent segments
- **Metrics**: Lexical cohesion, semantic similarity
- **DP Formulation**: Minimize within-segment variance, maximize between-segment differences

### 4.2 Parsing and Grammar
**Reference**: Earley (1970). "An efficient context-free parsing algorithm"

#### CYK Algorithm (Context-Free Parsing):
- **Grammar**: Chomsky Normal Form
- **DP Table**: dp[i][j][A] = true if A can generate text[i:i+j]
- **Complexity**: O(n³|G|) where |G| is grammar size

#### Probabilistic Parsing:
- **Extension**: CYK with probabilities for ambiguous grammars
- **Applications**: Natural language parsing, RNA secondary structure
- **Viterbi Algorithm**: Find most probable parse tree

### 4.3 Machine Translation Alignment
**Reference**: Brown et al. (1993). "The mathematics of statistical machine translation"

#### Word Alignment:
- **IBM Models**: Statistical models for translation alignment
- **DP Approach**: Find optimal alignment between source and target sentences
- **Applications**: Translation memory, parallel corpus processing

#### Phrase-Based Alignment:
- **Segments**: Align phrases rather than individual words
- **Complexity**: Exponential in phrase length, requires pruning
- **Heuristics**: Beam search, approximate DP solutions

## 5. DP Optimizations and Practical Considerations

### 5.1 Space Optimization Techniques
**Reference**: Hirschberg (1975). "A linear space algorithm for computing maximal common subsequences"

#### Rolling Array Optimization:
```python
# Space-optimized LCS (length only)
def lcs_space_optimized(X, Y):
    m, n = len(X), len(Y)
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i-1] == Y[j-1]:
                curr[j] = prev[j-1] + 1
            else:
                curr[j] = max(prev[j], curr[j-1])
        prev, curr = curr, prev
    
    return prev[n]
```

#### Hirschberg's Algorithm:
- **Divide-and-Conquer**: Split problem in half
- **Space**: O(min(m,n)) instead of O(m×n)
- **Time**: Still O(m×n) but with better constants

### 5.2 Parallel DP Algorithms
**Reference**: Valiant (1975). "Parallelism in comparison problems"

#### Anti-Diagonal Processing:
- **Observation**: Elements on same anti-diagonal can be computed in parallel
- **Implementation**: SIMD operations, GPU parallelization
- **Limitations**: Load balancing, memory bandwidth

#### Block-Based Parallelization:
- **Strategy**: Divide DP table into blocks, process dependencies
- **Challenges**: Load balancing, communication overhead
- **Applications**: Large-scale sequence alignment, distributed computing

### 5.3 Approximate DP Solutions
**Reference**: Landau & Vishkin (1989). "Fast parallel and serial approximate string matching"

#### Bounded Error DP:
- **Ukkonen's Algorithm**: Process only O(k×n) cells for k-approximate matching
- **Diagonal Band**: Limit computation to relevant diagonals
- **Applications**: Large-scale text search, real-time spell checking

#### Sampling and Sketching:
- **Random Sampling**: Approximate solutions using subset of data
- **Locality-Sensitive Hashing**: Fast approximate similarity search
- **Trade-offs**: Accuracy vs. speed, probabilistic guarantees

## 6. Applications to Address Processing

### 6.1 Address Standardization
**Reference**: Christen (2006). "A comparison of personal name matching techniques"

#### Fuzzy Address Matching:
```python
def match_address_components(ocr_text, standard_addresses):
    best_matches = []
    
    for address in standard_addresses:
        # Tokenize both addresses
        ocr_tokens = tokenize(ocr_text)
        std_tokens = tokenize(address)
        
        # Use LCS to find best alignment
        lcs_length = longest_common_subsequence(ocr_tokens, std_tokens)
        
        # Calculate similarity score
        similarity = 2 * lcs_length / (len(ocr_tokens) + len(std_tokens))
        
        if similarity > threshold:
            best_matches.append((address, similarity))
    
    return sorted(best_matches, key=lambda x: x[1], reverse=True)
```

#### Hierarchical Address Matching:
- **Strategy**: Match components at different geographic levels
- **DP Application**: Optimal alignment of address hierarchies
- **Error Handling**: OCR errors at different levels have different impacts

### 6.2 OCR Post-Processing
**Reference**: Kukich (1992). "Techniques for automatically correcting words in text"

#### Dictionary-Based Correction:
```python
def correct_ocr_text(ocr_word, dictionary, max_distance=2):
    candidates = []
    
    for dict_word in dictionary:
        if abs(len(ocr_word) - len(dict_word)) <= max_distance:
            distance = edit_distance(ocr_word, dict_word)
            if distance <= max_distance:
                candidates.append((dict_word, distance))
    
    # Return best candidates
    return sorted(candidates, key=lambda x: x[1])
```

#### Context-Aware Correction:
- **N-gram Models**: Use surrounding context for disambiguation
- **DP Integration**: Viterbi algorithm for sequence labeling
- **Performance**: Balance accuracy with real-time requirements

### 6.3 Template Matching
**Reference**: Template-based document analysis techniques

#### Flexible Template Matching:
- **Problem**: Match address fields against expected templates
- **DP Solution**: Allow for insertions, deletions, substitutions in template
- **Applications**: Form processing, structured document analysis

#### Multi-Template Alignment:
```python
def align_to_templates(text, templates):
    best_alignment = None
    best_score = float('-inf')
    
    for template in templates:
        # Use modified edit distance with template-specific costs
        alignment_cost = template_alignment_dp(text, template)
        confidence = calculate_confidence(alignment_cost, len(text), len(template))
        
        if confidence > best_score:
            best_score = confidence
            best_alignment = template
    
    return best_alignment, best_score
```

## 7. Performance Analysis and Benchmarking

### 7.1 Complexity Analysis

| Algorithm | Time | Space | Space-Optimized |
|-----------|------|-------|-----------------|
| LCS | O(mn) | O(mn) | O(min(m,n)) |
| Edit Distance | O(mn) | O(mn) | O(min(m,n)) |
| LIS | O(n²) | O(n) | O(n log n) optimized |
| Sequence Alignment | O(mn) | O(mn) | O(min(m,n)) |
| CYK Parsing | O(n³) | O(n²) | Problem-dependent |

### 7.2 Real-World Performance
**Reference**: Benchmark studies on string processing algorithms

#### Typical Performance (1000 character strings):
- **Edit Distance**: 1-10 milliseconds
- **LCS**: 2-15 milliseconds  
- **Approximate Matching**: 0.1-1 milliseconds (with optimizations)
- **Template Alignment**: 5-50 milliseconds (depends on template complexity)

#### Scaling Characteristics:
- **Linear Scaling**: Well-suited for parallel processing
- **Memory Bound**: Performance often limited by memory bandwidth
- **Cache Effects**: Significant impact on real-world performance

### 7.3 Optimization Guidelines
**Reference**: Best practices from competitive programming and industrial applications

#### Implementation Optimizations:
1. **Data Layout**: Use cache-friendly array layouts
2. **SIMD Instructions**: Vectorize inner loops where possible
3. **Early Termination**: Use bounds to terminate unpromising branches
4. **Precomputation**: Cache frequently used values

#### Algorithm Selection:
1. **String Length**: Different algorithms optimal for different input sizes
2. **Error Tolerance**: Approximate algorithms for high-error scenarios
3. **Repeated Queries**: Preprocessing may amortize costs
4. **Memory Constraints**: Space-time trade-offs based on available RAM

## 8. Advanced Topics and Research Directions

### 8.1 Machine Learning Integration
**Reference**: Recent advances in neural string processing

#### Neural Edit Distance:
- **Learned Costs**: Train neural networks to learn operation costs
- **Context-Aware**: Consider surrounding context in edit operations
- **Applications**: Personalized spell correction, domain-specific matching

#### Differentiable DP:
- **Soft Alignments**: Differentiable approximations to hard alignments
- **End-to-End Training**: Integrate DP into neural network training
- **Applications**: Neural machine translation, structured prediction

### 8.2 Quantum Dynamic Programming
**Reference**: Theoretical quantum computing approaches

#### Quantum Speedups:
- **Grover's Algorithm**: Quadratic speedup for certain DP problems
- **Quantum Walk**: Alternative formulations for path-counting problems
- **Limitations**: Current quantum hardware constraints

#### Practical Considerations:
- **Noise Tolerance**: Quantum error correction requirements
- **Problem Size**: Limited qubit availability
- **Classical Preprocessing**: Hybrid quantum-classical approaches

### 8.3 Streaming and Online DP
**Reference**: Algorithms for processing data streams

#### Online Edit Distance:
- **Streaming Input**: Process characters as they arrive
- **Approximate Maintenance**: Maintain approximate edit distance
- **Applications**: Real-time spell checking, live transcription

#### Sliding Window DP:
- **Fixed Window**: Maintain DP solution over sliding window
- **Memory Management**: Efficient data structure maintenance
- **Applications**: Real-time pattern matching, network monitoring

## 9. Implementation Guidelines for Address Classification

### 9.1 Algorithm Selection for Vietnamese Addresses

#### Primary Recommendations:
1. **Edit Distance**: For handling OCR errors in place names
2. **LCS**: For partial address matching and completion
3. **Template Matching**: For structured address field extraction
4. **Fuzzy String Matching**: Combined approach for robustness

#### Implementation Strategy:
```python
class AddressClassifier:
    def __init__(self, address_database):
        self.provinces = self.build_trie(address_database['provinces'])
        self.districts = self.build_hierarchical_trie(address_database['districts'])
        self.wards = self.build_hierarchical_trie(address_database['wards'])
        
    def classify_address(self, ocr_text, max_edit_distance=2):
        tokens = self.tokenize_vietnamese(ocr_text)
        
        # Try exact matching first
        result = self.exact_match(tokens)
        if result.confidence > 0.8:
            return result
        
        # Fall back to fuzzy matching
        return self.fuzzy_match_dp(tokens, max_edit_distance)
    
    def fuzzy_match_dp(self, tokens, max_distance):
        candidates = []
        
        # Match against province names
        for province in self.provinces:
            distance = self.edit_distance_with_early_termination(
                ' '.join(tokens), province, max_distance
            )
            if distance <= max_distance:
                candidates.append(('province', province, distance))
        
        # Continue with district and ward matching...
        return self.select_best_candidates(candidates)
```

### 9.2 Performance Optimization for Real-Time Processing

#### Preprocessing Optimizations:
1. **Trie Integration**: Combine DP with trie-based exact matching
2. **Index Structure**: Build inverted index for fast candidate retrieval
3. **Caching**: LRU cache for frequently queried addresses
4. **Parallel Processing**: Multi-threaded processing for multiple addresses

#### Memory Management:
```python
class OptimizedDP:
    def __init__(self, max_string_length=100):
        # Pre-allocate DP tables to avoid repeated allocation
        self.dp_table = [[0] * max_string_length for _ in range(max_string_length)]
        self.trace_table = [[0] * max_string_length for _ in range(max_string_length)]
    
    def edit_distance_reusable(self, s1, s2):
        m, n = len(s1), len(s2)
        
        # Reuse pre-allocated table
        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0:
                    self.dp_table[i][j] = j
                elif j == 0:
                    self.dp_table[i][j] = i
                elif s1[i-1] == s2[j-1]:
                    self.dp_table[i][j] = self.dp_table[i-1][j-1]
                else:
                    self.dp_table[i][j] = 1 + min(
                        self.dp_table[i-1][j],     # deletion
                        self.dp_table[i][j-1],     # insertion
                        self.dp_table[i-1][j-1]    # substitution
                    )
        
        return self.dp_table[m][n]
```

### 9.3 Quality Assurance and Testing

#### Test Case Generation:
1. **Synthetic Errors**: Generate OCR-like errors programmatically
2. **Real OCR Data**: Test on actual OCR output from Vietnamese documents
3. **Edge Cases**: Handle empty strings, very long addresses, special characters
4. **Performance Regression**: Automated benchmarking

#### Evaluation Metrics:
- **Accuracy**: Percentage of correctly classified addresses
- **Precision/Recall**: For each geographic level (province, district, ward)
- **Response Time**: 95th percentile latency under load
- **Memory Usage**: Peak memory consumption during processing

## 10. Conclusion and Future Work

### 10.1 Key Insights
1. **DP Versatility**: Dynamic programming provides robust solutions for various text processing challenges
2. **Optimization Critical**: Real-world performance requires careful optimization
3. **Domain Adaptation**: Vietnamese address processing benefits from language-specific optimizations
4. **Hybrid Approaches**: Combining exact and approximate matching yields best results

### 10.2 Research Directions
1. **Neural-DP Integration**: Combine deep learning with classical DP algorithms
2. **Multilingual Support**: Extend techniques to other Southeast Asian languages
3. **Real-Time Adaptation**: Online learning for improving address databases
4. **Hardware Acceleration**: GPU and FPGA implementations for high-throughput processing

## References

1. Bellman, R. (1957). *Dynamic Programming*. Princeton University Press.

2. Brown, P. F., Pietra, V. J. D., Pietra, S. A. D., & Mercer, R. L. (1993). The mathematics of statistical machine translation: Parameter estimation. *Computational linguistics*, 19(2), 263-311.

3. Christen, P. (2006). A comparison of personal name matching techniques and practical issues. *Technical Report TR-CS-06-02*, Australian National University.

4. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to algorithms*. MIT press.

5. Earley, J. (1970). An efficient context-free parsing algorithm. *Communications of the ACM*, 13(2), 94-102.

6. Hirschberg, D. S. (1975). A linear space algorithm for computing maximal common subsequences. *Communications of the ACM*, 18(6), 341-343.

7. Hunt, J. W., & Szymanski, T. G. (1977). A fast algorithm for computing longest common subsequences. *Communications of the ACM*, 20(5), 350-353.

8. Kukich, K. (1992). Techniques for automatically correcting words in text. *ACM Computing Surveys*, 24(4), 377-439.

9. Landau, G. M., & Vishkin, U. (1989). Fast parallel and serial approximate string matching. *Journal of algorithms*, 10(2), 157-169.

10. Levenshtein, V. I. (1966). Binary codes capable of correcting deletions, insertions, and reversals. *Soviet physics doklady*, 10(8), 707-710.

11. Navarro, G., & Raffinot, M. (2002). *Flexible pattern matching in strings: practical on-line search algorithms for texts and biological sequences*. Cambridge University Press.

12. Needleman, S. B., & Wunsch, C. D. (1970). A general method applicable to the search for similarities in the amino acid sequences of two proteins. *Journal of molecular biology*, 48(3), 443-453.

13. Ponte, J. M., & Croft, W. B. (1997). Text segmentation by topic. *Proceedings of the first European conference on research and advanced technology for digital libraries*, 113-125.

14. Thompson, K. (1968). Programming techniques: Regular expression search algorithm. *Communications of the ACM*, 11(6), 419-422.

15. Valiant, L. G. (1975). Parallelism in comparison problems. *SIAM Journal on Computing*, 4(3), 348-355.
