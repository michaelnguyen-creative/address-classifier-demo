Here’s a more fully-fleshed **Chapter 2: Literature Review** draft that explicitly addresses your Functional & Non-Functional Requirements, weaving in recent research (2016-2025). You’ll need to fill in some Vietnamese-specific datasets/gazetteers etc. and add more citations that you find in your domain, but this should give you a solid, structured backbone.

---

# Chapter 2: Literature Review

This chapter surveys the theoretical and practical literature relevant to building a Vietnamese address parser under the constraints defined in Section 2 (Functional & Non-Functional Requirements). The aim is to show what prior work supports each requirement, identify gaps, and guide design choices.

---

## 2.1 Overview of Key Challenges in Vietnamese Address Parsing

Vietnamese address parsing faces several unique challenges:

* **Complex diacritics**: Vietnamese orthography uses tone marks and modified vowels, which OCR often misrecognizes or omits.
* **Noise from OCR**: Besides diacritic loss, there are frequent spacing errors, character confusions (e.g. “o ↔ ô/ơ”, “a variants”, “l/1”, etc.).
* **Hierarchical administrative structure**: Vietnam’s provinces, districts, wards form a strict containment hierarchy. This can be exploited for validation and pruning.
* **Limited or inconsistent formatting**: Addresses may be missing components, use abbreviations, or have multiple kinds of noise.

Recent surveys confirm that these are still principal sources of error in Vietnamese document analysis & recognition (DAR). For example, *A Survey on Vietnamese Document Analysis and Recognition: Challenges and Future Directions* (2025) emphasizes diacritic/tone errors, segmentation issues, and lack of large annotated datasets. ([arXiv][1])

---

## 2.2 Functional Requirements: What Prior Art Offers

Below I map each core functional requirement to prior work, showing how the field supports what you need.

### FR-01: Parse unstructured Vietnamese address text into structured JSON

* Several works combine **fuzzy matching** with **gazetteer lookup** or **address standardization** for Vietnamese addresses. One example is *A Novel Conditional Random Fields Aided Fuzzy Matching in Vietnamese Address Standardization* (2020) which uses a CRF model in combination with fuzzy matching of candidate address components, reaching \~88% accuracy. Although this uses ML, the pipeline combining gazetteers + fuzzy matching gives insight into what structured parsing can achieve. ([ACM Digital Library][2])
* Tools like *vn\_address\_standardizer* (2023-2024, GitHub) offer practical, rule-based or hybrid pipelines for parsing addresses into structured components (province, district, ward), often emitting JSON-style outputs. (While not always formally published, they provide real evidence for feasibility.)

### FR-02: Handle multiple input formats and noise patterns

* The diacritic restoration literature includes *On the Use of Machine Translation-Based Approaches for Vietnamese Diacritic Restoration* (2017), which studies phrase-based and neural MT methods for adding missing diacritics. The work shows high accuracy (\~97.3%) for phrase-based methods, and slightly lower for neural ones, which suggests that even missing diacritics cases (a common noise pattern) are tractable. ([scholar.vnu.edu.vn][3])
* Surveys like the 2025 DAR survey note that spacing errors and character confusions remain major error modes in OCR for Vietnamese. They also point to post-OCR correction methods (e.g. LLM or transformer-based) as promising. ([arXiv][1])
* The *Reference-Based Post-OCR Processing with LLM for Diacritic Languages* (2024) addresses historical documents with multiple error types, using transformer/LLM-assisted correction to improve recognition under heavy noise. This suggests that for noisy input you can get much better accuracy if you include a correction/postprocess stage. ([arXiv][4])

### FR-03: Support hierarchical address validation (province → district → ward)

* Gazetteer-based systems and dictionaries are standard in address standardization. They rely on administrative boundaries. The hierarchical model is implicit in many parsing pipelines: you only accept matches if the ward belongs to the district, the district to the province.
* *CoCo-trie: Data-Aware Compression and Indexing of Strings* (2024) provides data structures for large dictionaries that support fast lookup, prefix, and range queries. While that paper is not about addresses per se, the dictionary functionality (fast membership, prefix search) is exactly what hierarchical validation depends on. ([ACM Digital Library][5])

### FR-04: Return confidence scores for classifications

* Post-OCR and correction works often compute some score of likelihood: number of corrections, edit distance, whether diacritics were restored, language model probabilities, or whether the match was unique vs ambiguous. The 2024 LLM-based post-OCR work provides graded scoring for diacritic restoration vs baseline model. ([arXiv][4])
* The address standardization work with CRFs + fuzzy matching often outputs probabilities or scores associated with candidate matches. Though these are ML methods, the idea of re-ranking candidates is useful for a rule-based pipeline (e.g., weighted penalty scoring). ([ACM Digital Library][2])

### FR-05: Handle missing or incomplete address components gracefully

* Many works observe that inputs may lack ward or even district information; parsers often have to produce partial parses. For example, post-OCR pipelines yield partial text where necessary; address standardization systems have mechanisms to fall back when matching fails at ward level but succeeds at district or province.
* The DAR survey points out that real input often lacks consistent format; systems that succeed do so because they are robust to such cases. ([arXiv][1])

---

## 2.3 Non-Functional Requirements: Performance, Accuracy, Constraints

Now turning to how the literature supports what you need under your non-functional constraints.

### 2.3.1 Performance Requirements (NFR-01 to NFR-04)

* **Data structures**: *CoCo-trie* (2022-2024) is state of the art in compressing and indexing large static string dictionaries. It achieves favorable space/time trade-offs, which is promising for large gazetteer storage with fast lookups. ([learned.di.unipi.it][6])
* **Blockwise compression + Patricia trie hybrid indexing**: In *Engineering a Textbook Approach to Index Massive String Dictionaries* (SPIRE 2023), authors show that with such hybrid techniques one can index billions of strings with very low in-memory footprint, and still answer membership/lexicographic queries efficiently. That suggests that lookup + validation (FR-03) can be made very fast. ([SpringerLink][7])
* **Diacritic restoration speed**: The 2017 study (MT-based) shows phrase-based methods reach high accuracy, and neural ones are faster – this suggests that for preprocess steps (normalization / diacritic recovery) latency can be acceptable. ([scholar.vnu.edu.vn][3])
* **Post-OCR correction**: The 2024 transformer / LLM-assisted correction methods are heavier, but many use offline precomputation or batch correction. If limited to small texts (addresses), the overhead may be manageable. The 2024 LLM-based work reports improvements and shows that computational cost is nontrivial, but optimization may be possible. ([arXiv][4])

These support your aim for **average ≤ 0.01 s** and **max ≤ 0.1 s**, provided:

1. You use efficient data structures (compressed tries etc.),
2. Limit fuzzy matching or correction to when needed (fast path vs correction path),
3. Preload / precompute heavy data (gazetteers, dictionaries, normalization maps) during initialization (NFR-04).

### 2.3.2 Accuracy Requirements (NFR-05 to NFR-07)

* Empirical address standardization work (e.g. CRF + fuzzy matching) achieves \~88% accuracy. ([ACM Digital Library][2])
* Diacritic restoration studies report very high accuracy (phrase-based \~97.3%, neural slightly lower but improving). ([scholar.vnu.edu.vn][3])
* DAR survey (2025) notes that when inputs are clean and domain is restricted (address-like text), accuracy can be higher; with noise, accuracy drops but partial methods and correction narrow the gap. ([arXiv][1])

Thus >85% is reasonable as a target if you include correction and validation, and detect/handle difficult cases.

### 2.3.3 Technical Constraints (NFR-08 to NFR-11)

* Many of the algorithms and data structures surveyed (tries, Patricia-tries, compressed dictionaries) are implementable in pure Python (or with minimal extension). CoCo-trie etc. are research implementations often in C/C++ but the concepts carry over.
* Methods like edit distance, normalization, diacritic restoration (non-ML or small neural components) can run offline / offline-like and do not require Internet or external resources beyond initial datasets.
* The LLM-based work does need more computation, but can be used as post-processing offline or cached for common cases to meet CPU constraints.

### 2.3.4 Maintainability, Modular Design (NFR-12 to NFR-14)

* In tools like vn\_address\_standardizer and similar address normalization pipelines, there is separation of concerns: data (gazetteer), normalization (diacritics, spacing, abbreviation), matching & validation, error reporting.
* Parameterization: Many systems have configurable thresholds (edit distance bound, confidence weights), abbreviation lists, alias tables.
* Logging & error metrics: DAR surveys and correction works stress the importance of collecting statistics (error types, correction rates, times) both for research and production debugging. ([arXiv][1])

---

## 2.4 Data Structures & Algorithms: Deep Dive

To deliver on both functional and non-functional requirements, the following algorithmic tools/designs are especially relevant. These are from recent literature and are likely to form your backbone.

### 2.4.1 Compressed Tries / String Dictionary Structures

* **CoCo-trie**: A data-aware compression + collapsed trie structure. Compresses subtries of arbitrary depth into succinctly encoded macro-nodes to reduce space while allowing efficient membership, prefix, predecessor, rank queries. Useful for storing gazetteers of provinces/districts/wards. ([ACM Digital Library][5])
* **Patricia tries / Radix trees**: Well-known compressed versions of tries: collapse chains of nodes with single children, reducing depth and memory. These appear in many indexing data structures.
* **Hybrid blockwise compression + trie for massive dictionaries**: As in SPIRE 2023, where large sorted dictionaries are stored compressed in blocks, while a smaller trie index built over first entries in each block supports fast lookup. Good when gazetteer is huge. ([SpringerLink][7])

### 2.4.2 Diacritic Restoration & Normalization

* The 2017 MT-based study comparing phrase-based & neural MT for restoring missing Vietnamese diacritics. Demonstrates high performance, but neural methods are still catching up in some metrics of error type. ([scholar.vnu.edu.vn][3])
* More recent work (2024) in post-OCR / LLM-assisted correction of historical Vietnamese text (for diacritic and other error types) shows that heavy noise can be corrected with modest supervision or correction references. ([arXiv][4])

### 2.4.3 Fuzzy Matching & Re-Ranking

* Fuzzy matching (bounded edit distance, approximate string search) is essential when noise exists. Works that combine fuzzy candidate generation + re-ranking (e.g., CRF aided fuzzy matching) perform well for Vietnamese address standardization. ([ACM Digital Library][2])
* Post-OCR correction works also implicitly do fuzzy matching (spell correction etc.) as part of restoring diacritics or correcting misrecognized characters.

---

## 2.5 Gaps & Lessons Learned

From the surveyed literature, here are the gaps and implications you should watch out for:

1. **Trade-off between speed and correction complexity**
   Heavy correction (diacritic restoration, LLM post-OCR) improves accuracy but at cost of latency and possibly memory. For NFR constraints, heavy correction must be applied selectively (fast paths vs fallback paths).

2. **Limited datasets / domain mismatch**
   Many works show high accuracy on clean or semi-clean text. Noisy or historical documents often underperform. For address parsing, domain of input (OCR engine, document type) matters a lot. You’ll need to collect / test on data similar to your target input.

3. **Rule-based vs ML-based approach constraints**
   You have technical constraints forbidding ML/NLP libraries. That rules out many recent works or parts (e.g., neural diacritic restoration, large transformer models). But many ML-based works give insight into what rule-based systems must approximate or emulate.

4. **Confidence estimation often implicit**
   Many papers don’t define standard ways to compute confidence in purely rule-based systems. You’ll need to explicitly design a confidence scoring model (e.g. weighted by edit distances, number of corrections, whether match is unique, etc.)

5. **Handling missing/incomplete components less often fully addressed**
   While many works mention fallback for missing components, fewer systematically evaluate “partial outputs” or error codes. This is an area where your system may need to contribute.

---

## 2.6 Design Implications: What the Literature Suggests for Your System

Based on the surveyed work, here are suggestions / best practices for your system:

| Requirement                            | Design Implications / Recommendations                                                                                                                                                                                                                |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FR-01 / FR-03                          | Use a **gazetteer** (static list of provinces, districts, wards) stored in a compressed trie or similar; leverage prefix lookup, exact match, fuzzy match of candidate components.                                                                   |
| FR-02                                  | Early normalization: remove or canonicalize diacritics (if missing), consistent spacing, abbreviation expansion; optionally light correction (edit distance) when noise is moderate.                                                                 |
| FR-04                                  | Build a deterministic scoring model using penalties: missing diacritic, distance in fuzzy match, ambiguity (multiple matching ward/district), depth of match. Also possibly producing a baseline score (e.g., exact match) plus penalty adjustments. |
| FR-05                                  | Fallback logic: if ward fails, still output district + province; if district fails, output province; mark missing/unreliable parts via confidence or error codes. Don’t fail outright.                                                               |
| NFR-01 / NFR-02 (Performance)          | Optimize the common case: exact match on normalized input (fast trie lookup), avoid fuzzy matching unless necessary; preload data; use efficient data structures (compressed trie, Patricia trie); avoid heavy dynamic computation per request.      |
| NFR-04 (Initialization)                | Data structure loading (gazetteer, normalization maps) must be fast; precompute abbreviation tables, mapping dictionaries, etc. Possibly serialize the built data structure for reuse.                                                               |
| NFR-05 (Accuracy)                      | Use noise modeling (e.g. assume certain probabilities for missing diacritics, spacing errors) to inform fuzzy matching; test on noisy real data; measure both component‐level and address‐level accuracy.                                            |
| NFR-08 / NFR-09 / NFR-11 (Constraints) | Implement all in Python; avoid external ML/NLP libraries. For fuzzy matching / edit distance, you can use pure Python or write small efficient modules; data structures likely need to be memory efficient so choose compact representations.        |
| Maintainability                        | Modularize: separation among normalization, matching, validation, scoring; configuration files for thresholds; comprehensive unit tests; error logging with failure modes.                                                                           |

---

## 2.7 Summary

The literature indicates that building a Vietnamese address parsing system satisfying your Functional & Non-Functional Requirements is **feasible**, provided careful algorithmic design. Key enablers:

* Compressed trie / Patricia / CoCo-trie for efficient gazetteer storage and lookup
* Preprocessing including normalization and diacritic restoration
* Fuzzy matching with bounded error + hierarchical validation
* Confidence scoring via penalty models, correction counts, ambiguity detection
* Graceful handling of missing components

At the same time, the literature also shows where you must be cautious: dataset mismatch, speed vs correction complexity, limited examination of partial results and error codings in prior work. These will inform your evaluation design and testing.

---

If you like, I can also produce a **bibliography** for all the cited papers (in appropriate style), plus suggestions of datasets you might use to benchmark. Would that be helpful?

[1]: https://arxiv.org/abs/2506.05061?utm_source=chatgpt.com "A Survey on Vietnamese Document Analysis and Recognition: Challenges and Future Directions"
[2]: https://dl.acm.org/doi/abs/10.1145/3368926.3369687?utm_source=chatgpt.com "A Novel Conditional Random Fields Aided Fuzzy Matching in Vietnamese Address Standardization | Proceedings of the 10th International Symposium on Information and Communication Technology"
[3]: https://scholar.vnu.edu.vn/entities/publication/3bbb155a-e203-4d46-916a-610cb98f2d50?utm_source=chatgpt.com "On the use of machine translation-based approaches for Vietnamese diacritic restoration"
[4]: https://web3.arxiv.org/abs/2410.13305?utm_source=chatgpt.com "[2410.13305] Reference-Based Post-OCR Processing with LLM for Diacritic Languages"
[5]: https://dl.acm.org/doi/10.1016/j.is.2023.102316?utm_source=chatgpt.com "CoCo-trie: : Data-aware compression and indexing of strings: Information Systems: Vol 120, No C"
[6]: https://learned.di.unipi.it/publication/compressed-string-dictionaries-via-data-aware-subtrie-compaction/?utm_source=chatgpt.com "Compressed string dictionaries via data-aware subtrie compaction | Multicriteria Learned Data Structures"
[7]: https://link.springer.com/chapter/10.1007/978-3-031-43980-3_16?utm_source=chatgpt.com "Engineering a Textbook Approach to Index Massive String Dictionaries | SpringerLink"
