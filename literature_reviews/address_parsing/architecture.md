

Multi-Stage Pipeline

A practical pipeline looks like this:

```
[Input OCR Text]
       │
       ▼
 [Normalization]
   - Unicode (NFC/NFKC)
   - Diacritics restored
   - Abbreviations expanded
       │
       ▼
 [Trie Matching]
   - Word-level (main)
   - Phrase-level (compound units)
   - Character-level (fallback)
       │
       ▼
 [Fuzzy Matching]
   - Edit distance pruning
   - Substring alignment
       │
       ▼
 [Validation]
   - Gazetteer / admin DB
   - Ensure only valid units
```

This sequential design ensures **speed first**, then **robustness**, then **final accuracy check**.
