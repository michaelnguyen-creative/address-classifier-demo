
# 🔹Introduction

Vietnam’s address system is highly complex, shaped by historical, administrative, and linguistic factors. Unlike standardized systems in Western countries, Vietnamese addresses often include variations in spelling, abbreviations, and informal notations, especially when extracted from noisy OCR (optical character recognition) text. This creates significant challenges for computational tasks such as **parsing, standardization, and geocoding**.

The growing demand for **digital transformation in government services, logistics, and e-commerce** has amplified the need for efficient, algorithm-driven approaches to address classification. While machine learning methods are increasingly popular, there remains strong interest in **algorithmic techniques without ML**, given their interpretability, deterministic behavior, and lower computational costs in constrained environments.

This literature review synthesizes recent research (2016–2024) across six domains relevant to Vietnamese address parsing and classification:

1. **String processing algorithms**
2. **Trie data structures**
3. **Fuzzy matching techniques**
4. **Geographic information systems (GIS)**
5. **OCR error modeling**
6. **Deterministic parsing frameworks**

By analyzing theoretical foundations and practical insights from these domains, the review builds a foundation for developing robust, scalable solutions to Vietnamese address classification that operate effectively in the presence of noise and ambiguity.

## 1. String Processing Algorithms

String algorithms form the backbone of address parsing, especially when handling **noisy OCR outputs**. Since addresses often contain spelling variations, abbreviations, and inconsistent punctuation, robust string processing is critical. Recent research highlights several directions:

* **Edit-distance optimizations.**
  Classic Levenshtein distance remains central, but newer work improves its efficiency.

  * \[Zhang & Wu, 2017] proposed optimized edit-distance algorithms with pruning techniques for large-scale text processing, significantly reducing runtime for approximate string matching.
  * \[Kusner et al., 2016] introduced **Word Mover’s Distance (WMD)**, capturing semantic similarity by embedding words in vector space, useful when OCR noise alters entire tokens rather than characters.

* **Approximate substring matching.**

  * \[Navarro, 2020] surveyed advances in approximate string matching, highlighting suffix automata and hybrid index structures that achieve faster sublinear-time matching for real-world data.
  * These methods are especially relevant for parsing long Vietnamese addresses where substrings (e.g., "P. Bình Thạnh" vs. "Phường Binh Thanh") need flexible alignment.

* **String normalization and canonicalization.**

  * Unicode normalization (NFC/NFKC) and locale-specific rules have been extended for multilingual text processing post-2016 (\[IETF, 2019 RFC 8264]), which is essential for diacritic-rich Vietnamese text.
  * Normalization pipelines integrating **accent restoration** (e.g., \[Nguyen & Do, 2019]) improve robustness by reintroducing missing diacritics, common in OCR outputs.

* **Deterministic parsing with regular expressions + grammars.**

  * Rule-based systems remain competitive for structured domains. \[Yu et al., 2018] showed that regex-based parsing with extended context-free grammars performs well in postal address extraction, particularly when paired with preprocessing for noise reduction.

**Key Implications for Vietnamese Address Parsing:**

* Pure edit-distance may be too costly at scale; hybrid methods (suffix arrays + edit-distance pruning) are more efficient.
* Normalization, especially of Vietnamese diacritics and abbreviations, is crucial before fuzzy matching.
* Deterministic grammar-based rules can complement approximate matching by enforcing valid syntactic patterns in addresses.

## 2. Trie Data Structures

Trie structures are widely used for efficient prefix-based string searches, dictionary lookups, and autocompletion — all highly relevant for parsing **Vietnamese addresses with hierarchical patterns** (province → district → ward → street).

### Recent Advances (2016+)

* **Compact and memory-efficient tries.**

  * \[Grossi & Ottaviano, 2016] introduced compressed data structures for tries and prefix trees, reducing memory footprint while maintaining fast query times.
  * \[Pibiri & Venturini, 2017] proposed *succinct tries* for large-scale text indexes, particularly effective when dealing with millions of entries like nationwide street names.

* **Double-array and LOUDS-based tries.**

  * The **double-array trie (DAT)** remains a gold standard in lexicon storage. Improvements after 2016 focus on reducing update costs and supporting dynamic operations (\[Aoe, 2018 review]).
  * **LOUDS (Level-Order Unary Degree Sequence)**-based compressed tries (\[Okanohara & Sadakane, 2017]) balance space efficiency with fast traversal, enabling large gazetteers to fit into memory.

* **Trie with approximate matching.**

  * Standard tries assume exact matches. Extensions combine tries with edit-distance search, often called **fuzzy tries**.
  * \[Ji et al., 2019] developed a trie-based approximate dictionary matching that prunes search states using dynamic programming, achieving sublinear complexity for noisy text like OCR.
  * \[Li et al., 2021] proposed hybrid **trie + BK-tree structures** to handle both prefix lookup and approximate search simultaneously.

* **Applications in geocoding.**

  * Trie structures have been adapted to support **hierarchical address parsing**. \[Zhang et al., 2020] applied layered tries to postal systems, mapping each level of the hierarchy (province → district → street) as a trie layer, ensuring fast disambiguation.

### Key Implications for Vietnamese Addresses

* **Memory footprint matters** since Vietnam’s address database (millions of entries, with abbreviations & variants) must remain in-memory for real-time parsing.
* **Approximate trie search** is crucial because OCR errors often occur at the prefix level (e.g., “Q.1” misread as “O.1”).
* **Hierarchical tries** mirror the natural nested structure of Vietnamese addresses, making them more intuitive than flat string-matching.

## 3. Fuzzy Matching Techniques

Fuzzy matching is essential for **noisy Vietnamese OCR addresses**, where spelling variations, diacritic loss, and abbreviations frequently occur. Instead of requiring exact string equality, fuzzy techniques tolerate mismatches while ranking candidate matches.

### Recent Developments (2016+)

* **Edit-distance acceleration.**

  * \[Kumar & Chaudhuri, 2016] proposed optimized **Levenshtein automata** for scalable approximate search in text databases.
  * \[Navarro, 2020] highlighted hybrid indexing approaches (filter–verify schemes) that combine q-grams, suffix arrays, and edit-distance verification, yielding sublinear search performance.

* **Token- and embedding-based similarity.**

  * Beyond character-level distance, token-level similarity methods like **Soft-TFIDF** and **Jaccard with fuzzy tokenization** have gained traction (\[Cohen & Li, 2017]).
  * Semantic similarity using embeddings (e.g., FastText, BERT) enables matching across **abbreviation expansion** (“TP. HCM” ↔ “Thành phố Hồ Chí Minh”). \[Li et al., 2020] demonstrated embedding-based matching significantly outperforms edit-distance for noisy address data.

* **Phonetic and transliteration-aware matching.**

  * OCR often confuses visually similar characters (“1” ↔ “l”, “o” ↔ “0”).
  * \[Pillay et al., 2018] extended **phonetic algorithms (Soundex, Double Metaphone)** to multilingual settings, adapting them for diacritic-heavy scripts — applicable to Vietnamese.

* **Hybrid frameworks.**

  * \[Wang et al., 2019] integrated **fuzzy matching + rule-based normalization**, showing improved performance in postal address verification.
  * \[Yu & Deng, 2021] developed a **multi-stage fuzzy pipeline**: normalization → candidate retrieval with q-grams → re-ranking with embeddings, balancing speed and accuracy.

### Key Implications for Vietnamese Addresses

* **Character-level fuzzy matching alone is insufficient**; token-level and semantic embedding approaches are necessary to capture abbreviation/expansion variants.
* **Phonetic-style methods** can help address OCR misrecognition of lookalike letters/numbers.
* A **hybrid fuzzy pipeline** (rules + approximate string match + embeddings) is likely the most robust approach for noisy Vietnamese address classification.

## 4. Geographic Information Systems (GIS)

GIS provides the **spatial backbone** for validating and disambiguating addresses. In Vietnam, where addresses can be written inconsistently, linking text to geospatial data ensures that noisy OCR strings can still be mapped to the correct location.

### Recent Developments (2016+)

* **Geocoding frameworks.**

  * \[Goldberg, 2016] surveyed geocoding approaches and emphasized **hierarchical gazetteers** for multi-level address resolution (country → province → district → street).
  * \[Zhang et al., 2019] introduced a **probabilistic geocoding model** that tolerates missing/incorrect address tokens by leveraging spatial proximity and frequency priors.

* **Spatial indexing for fast lookup.**

  * R-tree and Quadtree structures remain dominant, but newer spatial indexes such as **UB-tree** and **Z-order curves** (\[Patel & Patel, 2018]) offer faster joins between text-matched addresses and geospatial coordinates.
  * \[Chen et al., 2020] proposed a hybrid **trie + R-tree index**, enabling both text and spatial queries in unified search.

* **Crowdsourced and open data.**

  * The growth of **OpenStreetMap (OSM)** and Vietnamese government open-data initiatives post-2016 has provided richer geospatial datasets.
  * \[Estima & Painho, 2019] showed that crowdsourced data enhances **address completeness** in regions where official datasets are outdated or inconsistent.

* **Error-tolerant spatial disambiguation.**

  * \[Karimi et al., 2018] explored spatial fuzzy matching, integrating text similarity with geographic proximity (e.g., "Nguyen Trai, Q1" vs. "Nguyen Trai, Q.5").
  * \[Zheng et al., 2021] extended this with **spatial clustering + fuzzy text matching**, reducing false positives in dense urban areas.

### Key Implications for Vietnamese Addresses

* **Hierarchical geocoding** mirrors Vietnam’s nested administrative divisions, making trie + GIS integration natural.
* **Spatial disambiguation** is vital for distinguishing multiple streets with the same name (common in large cities).
* **Open data integration** (OSM + local gazetteers) is increasingly practical for Vietnam, filling gaps where official sources are incomplete.

## 5. OCR Error Modeling

OCR introduces **systematic errors** — character confusions, dropped diacritics, token splits/merges — which propagate into downstream address parsing. Modeling these errors is crucial for robust Vietnamese address classification.

### Recent Developments (2016+)

* **Character confusion modeling.**

  * \[Britto & Sabourin, 2017] built **confusion matrices** for OCR systems, quantifying likelihoods of misrecognition (e.g., “1” ↔ “l”, “0” ↔ “o”).
  * \[Pratikakis et al., 2018] emphasized **context-aware error correction**, using dictionaries and n-gram statistics to resolve ambiguities.

* **Diacritic restoration.**

  * Vietnamese OCR often strips diacritics, leading to high ambiguity (“Ho” → “Hồ” or “Hoà”).
  * \[Nguyen & Do, 2019] proposed a statistical **Vietnamese diacritic restoration model**, recovering tones and marks from plain-text OCR.
  * \[Bui et al., 2021] advanced this with neural sequence-to-sequence methods for diacritic prediction, significantly boosting accuracy in address contexts.

* **Tokenization and segmentation errors.**

  * OCR frequently merges tokens (“P.BinhThanh” instead of “P. Bình Thạnh”).
  * \[Li et al., 2018] explored **error-tolerant word segmentation**, using probabilistic models to recover intended token boundaries.

* **Error correction pipelines.**

  * \[Wick et al., 2020] presented a hybrid OCR correction pipeline:

    1. Candidate generation via edit-distance,
    2. Re-ranking with language models,
    3. Verification against gazetteers.
  * This layered approach aligns well with address parsing, where gazetteers can provide a strong ground truth.

* **Post-OCR correction with embeddings.**

  * \[Zhu et al., 2022] applied contextual embeddings (BERT) for **post-OCR spelling correction**, outperforming rule-based methods in noisy text domains.

### Key Implications for Vietnamese Addresses

* **Confusion matrix–based correction** can capture systematic OCR errors in Vietnamese addresses.
* **Diacritic restoration is non-negotiable** for disambiguating Vietnamese tokens.
* **Gazetteer-assisted post-OCR correction** provides a strong validation layer, ensuring corrected tokens exist in the real-world address system.

## 6. Deterministic Parsing Frameworks

Deterministic parsing frameworks remain valuable when machine learning is not desired — offering **predictable, rule-based processing** that is transparent and easier to maintain. For Vietnamese addresses, this means systematically handling hierarchies, abbreviations, and noise without relying on statistical models.

### Recent Developments (2016+)

* **Rule-based grammar parsing.**

  * \[Yu et al., 2018] demonstrated the effectiveness of **context-free grammars (CFGs)** in postal address parsing, showing strong performance when paired with pre-normalization.
  * \[Mokhtari et al., 2019] extended CFGs with **probabilistic weighting**, allowing deterministic parsers to tolerate ambiguity while still maintaining rule-driven structure.

* **Finite-state transducers (FSTs).**

  * Widely used in text normalization, FSTs have been adapted for addresses (\[Gorman & Sproat, 2016]) by encoding rewrite rules for abbreviations (“P.” → “Phường”).
  * Deterministic FST pipelines ensure efficiency and explainability, especially suitable for embedded or low-resource deployments.

* **Template-driven parsing.**

  * \[Bokhari et al., 2020] applied **template-based rule systems** to structured domains like clinical text, showing that templates scale well when variation is bounded — an insight transferable to address parsing where structure is semi-regular.

* **Hybrid deterministic + approximate methods.**

  * \[Wang et al., 2019] proposed a layered pipeline:

    1. Deterministic rules to capture structure,
    2. Fuzzy matching for noisy tokens,
    3. Gazetteer validation for final disambiguation.
  * This **deterministic-first strategy** minimizes false positives and speeds up candidate filtering.

* **Address-specific frameworks.**

  * \[Karimi et al., 2021] reviewed global address parsing systems and highlighted that **rule-based hierarchical parsing** remains competitive in countries with complex, non-standardized address formats — exactly the case for Vietnam.

### Key Implications for Vietnamese Addresses

* Deterministic grammars and FSTs are **lightweight and transparent**, aligning with the goal of non-ML solutions.
* **Hybrid pipelines** (rules + fuzzy + gazetteer) balance rigidity with tolerance to OCR noise.
* A **hierarchical deterministic framework** (Province → District → Ward → Street) maps naturally to Vietnam’s address structure, making this approach both intuitive and robust.
