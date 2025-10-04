"""
Dynamic Abbreviation Builder for Vietnamese Administrative Entities

Builds abbreviation mappings from data files instead of hardcoding them.
This module generates the same kind of mappings that alias_generator.py creates,
but in reverse: abbreviation → full name(s)

Key Insight:
    - alias_generator.py: "Hồ Chí Minh" → ["ho chi minh", "hcm", ...]
    - abbreviation_builder.py: "hcm" → "ho chi minh"
    
Usage:
    builder = AbbreviationBuilder(data_dir="./data")
    builder.build_province_abbreviations()
    
    # Use the mappings
    full_name = builder.abbreviations['provinces'].get('hcm')
    # → "ho chi minh"
    
    # Check for ambiguity
    if 'dn' in builder.ambiguous['provinces']:
        candidates = builder.ambiguous['provinces']['dn']
        # → ['da nang', 'dong nai', 'dak nong']
"""

from typing import Dict, List, Set, Optional
from pathlib import Path
from collections import defaultdict
import json


# ========================================================================
# ABBREVIATION BUILDER
# ========================================================================

class AbbreviationBuilder:
    """
    Dynamically builds abbreviation mappings from data files
    
    Architecture:
        1. Read entity names from text files
        2. For each name, generate all possible abbreviations (using alias logic)
        3. Build reverse mapping: abbreviation → entity name
        4. Detect conflicts (same abbreviation → multiple entities)
    
    Attributes:
        abbreviations: Dict[level, Dict[abbrev, full_name]]
        ambiguous: Dict[level, Dict[abbrev, List[full_names]]]
        known_entities: Dict[level, Set[full_names]]
    """
    
    def __init__(self, data_dir: str):
        """
        Initialize builder with data directory
        
        Args:
            data_dir: Path to directory containing provinces.txt, districts.txt, ward.txt
        """
        self.data_dir = Path(data_dir)
        
        # Main mappings: level → (abbrev → full_name)
        self.abbreviations: Dict[str, Dict[str, str]] = {
            'provinces': {},
            'districts': {},
            'wards': {}
        }
        
        # Ambiguous mappings: level → (abbrev → [full_names])
        self.ambiguous: Dict[str, Dict[str, List[str]]] = {
            'provinces': {},
            'districts': {},
            'wards': {}
        }
        
        # Known entity sets for validation
        self.known_entities: Dict[str, Set[str]] = {
            'provinces': set(),
            'districts': set(),
            'wards': set()
        }
    
    def build_all(self):
        """
        Build abbreviation mappings for all levels
        
        Convenience method to build everything at once
        """
        self.build_province_abbreviations()
        self.build_district_abbreviations()
        self.build_ward_abbreviations()
    
    def build_province_abbreviations(self):
        """
        Build province abbreviation mappings from provinces.txt
        
        Process:
            1. Read provinces.txt
            2. Normalize each province name
            3. Generate initials (using same logic as alias_generator)
            4. Create reverse mapping
            5. Detect conflicts
        """
        self._build_abbreviations_for_level(
            level='provinces',
            filename='provinces.txt'
        )
    
    def build_district_abbreviations(self):
        """Build district abbreviation mappings from districts.txt"""
        self._build_abbreviations_for_level(
            level='districts',
            filename='districts.txt'
        )
    
    def build_ward_abbreviations(self):
        """Build ward abbreviation mappings from ward.txt or wards.txt"""
        # Try ward.txt first, then wards.txt
        for filename in ['ward.txt', 'wards.txt']:
            filepath = self.data_dir / filename
            if filepath.exists():
                self._build_abbreviations_for_level(
                    level='wards',
                    filename=filename
                )
                break
    
    def _build_abbreviations_for_level(self, level: str, filename: str):
        """
        Generic method to build abbreviations for any level
        
        Args:
            level: 'provinces', 'districts', or 'wards'
            filename: Name of the text file to read
        
        Algorithm:
            1. Read and normalize entity names
            2. For each entity, generate initials
            3. Build reverse mapping (initials → entity)
            4. Handle conflicts by creating ambiguous mappings
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            print(f"Warning: {filepath} not found, skipping {level}")
            return
        
        # Step 1: Read entities
        entities = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                entity = line.strip()
                if entity:
                    entities.append(entity)
        
        # Step 2: Normalize and build mappings
        # Import here to avoid circular dependency
        from archive.normalizer import normalize_text, NormalizationConfig
        
        # Create a minimal config (we don't need full province checking for this)
        config = NormalizationConfig(provinces=[])
        
        # Track: abbreviation → list of entities
        abbrev_to_entities: Dict[str, List[str]] = defaultdict(list)
        
        for entity in entities:
            # Normalize (this also removes admin prefixes)
            normalized = normalize_text(entity, config)
            
            # Store normalized entity
            self.known_entities[level].add(normalized)
            
            # Generate initials (using same logic as alias_generator)
            initials = self._generate_initials(normalized)
            
            # Build reverse mapping
            for abbrev in initials:
                abbrev_to_entities[abbrev].append(normalized)
        
        # Step 3: Separate unique vs ambiguous
        for abbrev, entity_list in abbrev_to_entities.items():
            if len(entity_list) == 1:
                # Unique abbreviation
                self.abbreviations[level][abbrev] = entity_list[0]
            else:
                # Ambiguous abbreviation
                self.ambiguous[level][abbrev] = entity_list
    
    def _generate_initials(self, normalized_name: str) -> List[str]:
        """
        Generate initial-based abbreviations for a normalized name
        
        This mirrors the logic in alias_generator.py but only returns
        the abbreviation variants (initials, dotted, etc.)
        
        Args:
            normalized_name: Already normalized entity name (e.g., "ho chi minh")
        
        Returns:
            List of abbreviations (e.g., ["hcm", "h.c.m", "hochiminh"])
        
        Examples:
            "ho chi minh" → ["hcm", "h.c.m", "hochiminh"]
            "ha noi" → ["hn", "h.n", "hanoi"]
            "1" → ["1"]  # single token, no initials
        """
        abbrevs = []
        
        tokens = normalized_name.split()
        num_tokens = len(tokens)
        
        # Edge case: empty
        if num_tokens == 0:
            return abbrevs
        
        # Single token: just return the token itself
        if num_tokens == 1:
            abbrevs.append(tokens[0])
            return abbrevs
        
        # Multi-token:
        # 1. Initials acronym: "hcm"
        initials = ''.join(t[0] for t in tokens)
        abbrevs.append(initials)
        
        # 2. Dotted initials: "h.c.m"
        dotted = '.'.join(t[0] for t in tokens)
        abbrevs.append(dotted)
        
        # 3. No-space compact: "hochiminh"
        no_space = ''.join(tokens)
        abbrevs.append(no_space)
        
        # Note: We DON'T add full normalized name here, because that's the value,
        # not the key. The full name is what we map TO, not FROM.
        
        return abbrevs
    
    def get_full_name(self, abbreviation: str, level: str) -> Optional[str]:
        """
        Get full name for an abbreviation at a given level
        
        Args:
            abbreviation: Short form (e.g., "hcm", "dn")
            level: 'provinces', 'districts', or 'wards'
        
        Returns:
            Full normalized name, or None if not found
            If ambiguous, returns the first candidate
        
        Examples:
            get_full_name("hcm", "provinces") → "ho chi minh"
            get_full_name("dn", "provinces") → "da nang" (first candidate)
        """
        # Check unique mappings first
        if abbreviation in self.abbreviations[level]:
            return self.abbreviations[level][abbreviation]
        
        # Check ambiguous mappings
        if abbreviation in self.ambiguous[level]:
            # Return first candidate (can be improved with priority logic)
            return self.ambiguous[level][abbreviation][0]
        
        return None
    
    def is_ambiguous(self, abbreviation: str, level: str) -> bool:
        """Check if an abbreviation is ambiguous at a given level"""
        return abbreviation in self.ambiguous[level]
    
    def get_all_candidates(self, abbreviation: str, level: str) -> List[str]:
        """
        Get all possible full names for an abbreviation
        
        Returns:
            List of full names (length 1 if unique, >1 if ambiguous)
        """
        if abbreviation in self.abbreviations[level]:
            return [self.abbreviations[level][abbreviation]]
        elif abbreviation in self.ambiguous[level]:
            return self.ambiguous[level][abbreviation]
        else:
            return []
    
    def export_to_json(self, output_path: str):
        """
        Export abbreviation mappings to JSON for inspection
        
        Args:
            output_path: Path to save JSON file
        """
        export_data = {
            'abbreviations': self.abbreviations,
            'ambiguous': self.ambiguous,
            'stats': {
                'provinces': {
                    'total_entities': len(self.known_entities['provinces']),
                    'unique_abbrevs': len(self.abbreviations['provinces']),
                    'ambiguous_abbrevs': len(self.ambiguous['provinces'])
                },
                'districts': {
                    'total_entities': len(self.known_entities['districts']),
                    'unique_abbrevs': len(self.abbreviations['districts']),
                    'ambiguous_abbrevs': len(self.ambiguous['districts'])
                },
                'wards': {
                    'total_entities': len(self.known_entities['wards']),
                    'unique_abbrevs': len(self.abbreviations['wards']),
                    'ambiguous_abbrevs': len(self.ambiguous['wards'])
                }
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Abbreviations exported to: {output_path}")


# ========================================================================
# TESTING
# ========================================================================

if __name__ == "__main__":
    print("="*70)
    print("ABBREVIATION BUILDER - TESTING")
    print("="*70)
    
    # Build abbreviations
    builder = AbbreviationBuilder(data_dir="../data")
    builder.build_all()
    
    # Display stats
    print("\n📊 STATISTICS:")
    print("-" * 70)
    
    for level in ['provinces', 'districts', 'wards']:
        total = len(builder.known_entities[level])
        unique = len(builder.abbreviations[level])
        ambiguous = len(builder.ambiguous[level])
        
        print(f"\n{level.upper()}:")
        print(f"  Total entities: {total}")
        print(f"  Unique abbreviations: {unique}")
        print(f"  Ambiguous abbreviations: {ambiguous}")
    
    # Test some lookups
    print("\n" + "="*70)
    print("🔍 LOOKUP TESTS:")
    print("="*70)
    
    test_cases = [
        ("hcm", "provinces"),
        ("hn", "provinces"),
        ("dn", "provinces"),  # Should be ambiguous
        ("ct", "provinces"),
        ("bd", "provinces"),  # Should be ambiguous
        ("bt", "districts"),  # Could be multiple districts
    ]
    
    for abbrev, level in test_cases:
        full_name = builder.get_full_name(abbrev, level)
        is_amb = builder.is_ambiguous(abbrev, level)
        candidates = builder.get_all_candidates(abbrev, level)
        
        status = "⚠️ AMBIGUOUS" if is_amb else "✅ UNIQUE"
        
        print(f"\n{status} '{abbrev}' ({level}):")
        print(f"  → Primary: {full_name}")
        if len(candidates) > 1:
            print(f"  → All candidates:")
            for c in candidates:
                print(f"      - {c}")
    
    # Export to JSON
    print("\n" + "="*70)
    builder.export_to_json("../abbreviations.json")
    print("="*70)
