# Data Granularity Levels in Tree Structures: A Specialized Guide

## Overview

This guide explores **granularity levels** for organizing data in tree structures, with emphasis on **text processing, address classification, and hierarchical data systems**.
Granularity directly impacts **performance, memory, and semantic precision**.

---

## 1. Granularity Fundamentals

### 1.1 Definition

Granularity = the **size of the unit** stored at each node.

It affects:

* **Alphabet size** → how many children a node can have
* **Tree depth** → how many steps from root to leaf
* **Memory usage** → space needed per unit
* **Query performance** → time for search/match

---

### 1.2 Spectrum of Granularity

Think of parsing like zoom levels on a map:

```
Character ─► Token ─► Word ─► Phrase ─► Sentence
   ↑          ↑        ↑       ↑         ↑
 Finest   Domain-    Natural  Compound   Too coarse
 detail   specific   units    units      for addresses
```

* **Fine-grained** → deep, detailed, high sharing (but many nodes)
* **Coarse-grained** → shallow, fewer nodes, less sharing

#### Character-Level

***Summary***: Catches OCR noise (e.g., `Binh` vs. `Bình`), but tries are deep & heavy

* **Strengths:** Extremely robust against OCR noise; any string can be represented.
* **Weaknesses:** Deep tries, larger memory footprint, slower lookups.
* **Use Cases:** Noisy text recovery; fuzzy matching at finest resolution.

#### Token-Level

***Summary***: Domain-aware atomic units that preserve semantic meaning within specific contexts

* **Strengths:** High semantic awareness; balanced depth vs. meaning; efficient for structured data.
* **Weaknesses:** Requires domain-specific tokenization; preprocessing overhead.
* **Use Cases:** Code completion, mathematical expressions, structured data parsing.

#### Word-Level

***Summary***: Natural fit for addresses, efficient, tokens align with real units (*Phường*, *Quận*)

* **Strengths:** Natural unit for addresses; balances efficiency and robustness.
* **Weaknesses:** Vulnerable to tokenization errors; requires clean segmentation.
* **Use Cases:** Default granularity for Vietnamese addresses.

#### Phrase-Level

***Summary***: Groups multi-word names (*Bình Thạnh*), avoids fragmentation

* **Strengths:** Captures hierarchical components (e.g., *“Phường Bình Thạnh”*). Reduces ambiguity in multi-word administrative names.
* **Weaknesses:** Larger index size; requires normalization.
* **Use Cases:** Parsing common address templates, especially in Vietnamese hierarchy.

#### Sentence-Level

***Summary***: Not relevant for address parsing & classification use cases; addresses are not full sentences

* **Strengths:** Suitable for long free-form text.
* **Weaknesses:** Overkill for structured addresses; adds parsing overhead.
* **Use Cases:** Rare; fallback for unstructured descriptions.

**Best practice:** 👉 Use **word-level** as default, **character-level** as fallback, and **phrase-level** for compound names.

---

### 1.3 Trade-offs

| Granularity | Strengths                         | Weaknesses                   | When to Use                           |
| ----------- | --------------------------------- | ---------------------------- | ------------------------------------- |
| Character   | Robust to OCR & typos             | Deep tries, slower, more RAM | As fallback when tokens are corrupted |
| Token       | Domain semantic awareness         | Requires preprocessing       | Code, math, structured data           |
| Word        | Natural for Vietnamese addresses  | Sensitive to OCR noise       | Default parsing unit                  |
| Phrase      | Handles multi-token wards, cities | Needs curated phrase lists   | Compound names (e.g., “Bình Thạnh”)   |
| Sentence    | None (too coarse)                 | Not useful for addresses     | Rarely / never                        |

---

## 2. Detailed Granularity Levels

### 2.1 Character-Level

#### Example Structure

```
Strings: ["CAT", "CAR", "CARD", "DOG"]

         root
        /    \
       C      D
       |      |
       A      O
      / \      |
     T   R     G
     ●   |     ●
         D
         ●
```

#### Properties

| Property      | Value       | Impact                    |
| ------------- | ----------- | ------------------------- |
| Alphabet Size | 26–256      | Small branching           |
| Tree Depth    | Word length | Can be very deep          |
| Sharing       | Maximum     | Great for prefix matching |
| Memory        | Many nodes  | High overhead             |

**Best for**: spell checking, DNA sequences, autocomplete.
**Weakness**: long traversals, no semantic grouping.

---

### 2.2 Token-Level

Tokens = **atomic units** that carry semantic meaning depending on a domain

* **Code**: keywords, operators, identifiers
* **Math**: numbers, variables, operators
* **Data**: fields, values

**Key Insight**: Unlike characters (too fine) or words (language-specific), tokens are **domain-aware semantic units**.

***Tokenization Strategies***

**Programming Languages:**
```
"for i in range(10):" → ["for", "i", "in", "range", "(", "10", ")", ":"]
```

**Mathematical Expressions:**
```
"sin(x^2 + 1)" → ["sin", "(", "x", "^", "2", "+", "1", ")"]
```

**Structured Data (JSON):**
```
'{"name": "value"}' → ["{", "name", ":", "value", "}"]
```

***Example Structure (Code Snippets)***

```
Code patterns: ["for i in range", "for item in list", "if condition"]

         root
          |
        "for"
          |
       [branch]
       /      \
     "i"     "item"
      |        |
     "in"     "in"
      |        |
   "range"   "list"
      ●        ●

(separate branch)
    "if" → "condition" ●
```

***Domain-Specific Alphabets***

| Domain | Token Types | Alphabet Size | Example Tokens |
|--------|-------------|---------------|----------------|
| **Programming** | keywords, operators, identifiers | 50-200 | `for`, `if`, `+`, `variable_name` |
| **Mathematics** | numbers, variables, functions, operators | 30-100 | `sin`, `x`, `+`, `3.14` |
| **Data Formats** | keys, values, structural elements | 20-50 | `{`, `}`, `"key"`, `value` |
| **SQL** | keywords, functions, identifiers | 100-300 | `SELECT`, `FROM`, `table_name` |

***Comparison vs Character & Word-Level***

| Aspect             | Character-Level  | **Token-Level**        | Word-Level             |
| ------------------ | ---------------- | ---------------------- | ---------------------- |
| Depth              | Word length      | Token count (shorter)  | Word count (shortest)  |
| Semantic awareness | None             | **High (domain-specific)** | High (natural language) |
| Preprocessing      | None             | **Tokenization required** | Language-dependent     |
| Robustness         | Highest          | **Medium**             | Lowest                 |
| Memory efficiency  | Low              | **Balanced**           | High                   |

**Best for**: programming code completion, mathematical expression parsing, structured data processing, domain-specific languages.

---

### 2.3 Word-Level

***Example (Vietnamese Addresses)***

```
["Hà Nội", "Thành phố Hồ Chí Minh", "Hà Nội Hoàn Kiếm"]

              root
             /    \
          "Hà"   "Thành"
           |       |
         "Nội"   "phố"
           ●       |
                  "Hồ"
                   |
                  "Chí"
                   |
                 "Minh"
                   ●
```

**Why effective?**

* Captures **semantic units**
* Balanced tree depth
* Ideal for NLP & addresses

---

### 2.4 Phrase-Level

Captures common **multi-word concepts** (e.g., “New York City”).

```
["New York City", "San Francisco", "Los Angeles County"]

       root
      /   |    \
 "New York" "San" "Los Angeles"
     |       |        |
   "City" "Francisco" "County"
     ●       ●          ●
```

Reduces depth, keeps semantic meaning intact.

---

### 2.5 Sentence-Level

Useful for **templates, responses, classification**.

```
["Thank you for your order", 
 "Your order has been shipped", 
 "Payment received"]

        root
     /    |     \
"Thank you" "Your order" "Payment"
     |         |            |
 "for your" "has been"   "received"
 "order"    "shipped"
   ●           ●
```

---

### 2.6 Document-Level

Entire document stored as a unit.

* Very shallow
* Used for **document indexing, categorization, retrieval**

---

## 3. Selection Framework

### 3.1 Decision Matrix

| Use Case               | Optimal Granularity | Notes                |
| ---------------------- | ------------------- | -------------------- |
| Spell check            | Character           | Typos/prefixes       |
| DNA                    | Character           | Small alphabet       |
| Code completion        | Token               | Language-specific    |
| Math expressions       | Token               | Operator/function aware |
| SQL query parsing      | Token               | Keyword recognition  |
| Address classification | Word                | Natural boundaries   |
| Common phrases         | Phrase              | Compact, semantic    |
| Templates              | Sentence            | Pattern-based        |
| Document management    | Document            | High-level retrieval |

---

## 4. Performance Insights

| Granularity | Tree Depth | Memory   | Semantic Awareness | Best Use       |
| ----------- | ---------- | -------- | ------------------ | -------------- |
| Character   | Long       | High     | None               | Typos, DNA     |
| Token       | Medium     | Moderate | Domain-specific    | Code, math     |
| Word        | Short      | Balanced | High               | NLP, addresses |
| Phrase      | Very Short | Low      | High               | Common phrases |
| Sentence    | Very Short | Low      | Very high          | Templates      |
| Document    | Minimal    | Low      | Highest            | Indexing       |

---

## 5. Domain Applications

**Address Classification (Vietnamese Context)**

* **Primary granularity**: **Word-level**
* **Fallback**: Character-level (handles OCR noise, typos)
* **Architecture**: Multi-level trie (province → district → ward → street)
* **Enhancements**: fuzzy matching, normalization, caching

**Recommendations**
- ✅ Use **word-level trie** as backbone. 
- ✅ Add **phrase-level nodes** for common compounds. 
- ✅ Enable **character-level fallback** for noisy OCR. 
- ✅ Normalize aggressively (diacritics, abbreviations).  
- ✅ Adopt a **multi-stage pipeline**:  

```
Trie → Fuzzy → Gazetteer
```

**Pitfalls to avoid**

* Over-engineering granularity
* Premature optimization
* Ignoring memory cost
* Hard-coding one granularity only

📌 **Bottom Line:** 

Vietnamese addresses are **structured but noisy**. A **hybrid granularity design** (word + phrase + character fallback), embedded in a **multi-stage deterministic pipeline**, provides the best balance of speed, robustness, and accuracy.

---

## References

* Morrison, D. R. (1968). PATRICIA: Practical Algorithm to Retrieve Information Coded in Alphanumeric. *JACM*.
* Askitis, N., & Sinha, R. (2007). HAT-trie: A cache-conscious trie-based data structure. *Australasian Computer Science Conf.*
* ACM Computing Surveys (2019). Performance optimization techniques for string processing.
* Vietnamese Language Processing Guidelines. *Vietnam National Standards*.
* Recent work (2016–2023): adaptive tries, compressed data structures, and hybrid text indexing approaches.