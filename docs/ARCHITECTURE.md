"""
==========================================================================
VIETNAMESE ADDRESS NORMALIZATION - ARCHITECTURE SUMMARY
==========================================================================

COMPLETED MODULES:
==================

1. text_normalizer.py (Layer 1)
   - Generic text normalization (domain-agnostic)
   - Vietnamese defaults built-in
   - Two modes: normal (preserve structure) vs aggressive (remove all punctuation)
   - Smart punctuation handling, Unicode symbol removal

2. admin_prefix_handler.py (Layer 2)
   - Vietnamese-specific admin prefix detection and removal
   - Abbreviation expansion (TP.HCM → ho chi minh)
   - Works with provinces.txt, districts.txt, wards.txt data files

3. normalizer_v2.py (Layer 1 + Layer 2 Integration)
   - Unified pipeline: AddressNormalizer class
   - Convenience functions: process_province(), process_district(), process_ward()
   - Full address parsing: process_full_address()

4. test_normalizer_integration.py
   - Integration tests for the complete pipeline
   - Demos showing layer-by-layer processing


PIPELINE FLOW:
==============

Input: "TP.HCM, Quận 1, P.Bến Nghé"
   ↓
Layer 1 (text_normalizer.py): Normalize text
   → "tp.hcm, quan 1, p.ben nghe"
   ↓
Layer 2 (admin_prefix_handler.py): Expand prefixes
   → "ho chi minh", "1", "ben nghe"
   ↓
Output: Clean entity names
   → {'city': 'ho chi minh', 'district': '1', 'ward': 'ben nghe'}


USAGE EXAMPLES:
===============

# Option 1: Full pipeline (most common)
from normalizer_v2 import AddressNormalizer

normalizer = AddressNormalizer(data_dir="../data")
result = normalizer.process("TP.HCM", level='province')
# → "ho chi minh"

# Option 2: Full address parsing
from normalizer_v2 import process_full_address

result = process_full_address("TP.HCM, Quận 1, P.Bến Nghé", data_dir="../data")
# → {'city': 'ho chi minh', 'district': '1', 'ward': 'ben nghe'}

# Option 3: Layer-by-layer control
normalizer = AddressNormalizer(data_dir="../data")
normalized = normalizer.normalize_only("TP.HCM")  # Layer 1 only
expanded = normalizer.expand_only("tp.hcm", 'province')  # Layer 2 only

# Option 4: Convenience functions
from normalizer_v2 import process_province, process_district, process_ward

city = process_province("TP.HCM", data_dir="../data")  # → "ho chi minh"
district = process_district("Quận 1", data_dir="../data")  # → "1"
ward = process_ward("P.Bến Nghé", data_dir="../data")  # → "ben nghe"


SEPARATE SYSTEMS (NOT PART OF NORMALIZER):
==========================================

Layer 3: Alias Generation
   - NOT part of the normalizer pipeline
   - Belongs to the trie database module
   - Takes clean entity names and generates search aliases
   - Example: "ho chi minh" → ["ho chi minh", "hcm", "saigon", ...]

Flow:
   Clean names (from normalizer)
      ↓
   Alias Generator (separate module)
      ↓
   Multiple search keys
      ↓
   Trie database insertion


KEY DESIGN PRINCIPLES:
=====================

1. Separation of Concerns
   - Each layer has a single responsibility
   - Layers don't know about each other
   - Can be used independently or combined

2. Smart Defaults
   - TextNormalizer() works with Vietnamese by default
   - No configuration needed for 99% of use cases
   - Easy to customize when needed

3. Two-Mode Normalization
   - Normal mode: Preserve structure for parsing (Layer 2 needs dots)
   - Aggressive mode: Remove all punctuation for matching (trie search)

4. Clear Boundaries
   - Normalization pipeline (Layer 1 + 2) is complete
   - Alias generation is a separate concern
   - Trie operations are a separate concern


TESTING:
========

Run Layer 1 tests:
  python text_normalizer.py

Run Layer 1 integration tests:
  python normalizer_v2.py

Run Layer 1 + Layer 2 integration tests:
  python test_normalizer_integration.py


NEXT STEPS (SEPARATE MODULES):
==============================

1. Alias Generator
   - Generate search aliases from clean entity names
   - Handle abbreviations, nicknames, variations
   - Example: "ho chi minh" → ["ho chi minh", "hcm", "saigon"]

2. Trie Database
   - Insert aliases into trie structure
   - Fast prefix-based search
   - Fuzzy matching capabilities

3. Address Classifier
   - Use normalized data for classification
   - Level detection (province/district/ward)
   - Confidence scoring
"""
