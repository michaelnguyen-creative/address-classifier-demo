"""
AddressDatabase - Hierarchical Vietnamese Address Storage

Architecture:
    1. Trie: Fast name matching O(m)
    2. Hash Maps: Fast validation O(1)
    3. Hierarchy validation using codes

Design Philosophy:
    - Tries for MATCHING (find entities in text)
    - Hash maps for VALIDATION (check relationships)
    - Separation of concerns = clarity
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Import Trie from trie_parser module
from trie_parser import Trie

# REFACTORED: Use new normalizer_v2 instead of archive.normalizer
from text_normalizer import TextNormalizer


# ========================================================================
# ADDRESS DATABASE
# ========================================================================

class AddressDatabase:
    """
    Vietnamese address database with fast lookup and validation
    
    Data Sources:
        - Provinces.json: 63 provinces/cities
        - Districts.json: ~700 districts
        - Wards.json: ~11,000 wards
    
    Key Features:
        1. Trie-based matching (fast path)
        2. Code-based validation (handle duplicates)
        3. Hierarchical consistency checking
    
    Usage:
        db = AddressDatabase(data_dir="../Data")
        
        # Fast lookup
        province = db.province_trie.search("ha noi")  # "Hà Nội"
        
        # Validation
        valid = db.validate_hierarchy("Cầu Diễn", "Nam Từ Liêm", "Hà Nội")
    """
    
    def __init__(self, data_dir: str = "../Data"):
        """
        Initialize database from JSON files
        
        Build Process:
        1. Load JSON → O(P + D + W)
        2. Build hash maps → O(P + D + W)
        3. Build Tries → O(P×p + D×d + W×w) where p,d,w are avg name lengths
        
        Total: O(n) where n = total data size
        """
        print(f"Loading address database from {data_dir}...")
        
        # Step 1: Load raw data
        self._load_json_files(data_dir)
        
        # Step 2: Build lookup maps (name → code)
        self._build_lookup_maps()
        
        # Step 3: Build hierarchy maps (code → parent_code)
        self._build_hierarchy_maps()
        
        # REFACTORED: Create TextNormalizer (uses Vietnamese defaults)
        # This will be used for all text normalization in AGGRESSIVE mode
        self.normalizer = TextNormalizer()
        print(f"✓ Normalizer initialized (Vietnamese, aggressive mode for aliases)")

        # NEW: Create AdminPrefixHandler for prefix detection & removal
        # This handles all the pattern matching for administrative prefixes
        from admin_prefix_handler import AdminPrefixHandler
        self.admin_handler = AdminPrefixHandler(data_dir=data_dir)
        print(f"✓ AdminPrefixHandler initialized (prefix detection & removal)")
        
        # NEW: Create PrefixRouter that uses AdminPrefixHandler
        # Router reuses handler's patterns to determine which Trie to search
        from prefix_router import PrefixRouter
        self.prefix_router = PrefixRouter(self.admin_handler)
        print(f"✓ PrefixRouter initialized (intelligent Trie routing)")

        # Step 4: Build Tries for fast matching
        self._build_tries()
        
        print(f"✓ Database ready:")
        print(f"  - {len(self.provinces)} provinces")
        print(f"  - {len(self.districts)} districts")
        print(f"  - {len(self.wards)} wards")

        # NEW: Pre-tokenized candidates for LCS matching
        self._build_lcs_candidates()
    
    # ====================================================================
    # STEP 1: LOAD JSON FILES
    # ====================================================================
    
    def _load_json_files(self, data_dir: str):
        """
        Load JSON files into memory
        
        Expected Format:
            Provinces.json: [{Code: "01", Name: "Hà Nội"}, ...]
            Districts.json: [{Code: "001", Name: "Ba Đình", ProvinceCode: "01"}, ...]
            Wards.json: [{Code: "00001", Name: "Phúc Xá", DistrictCode: "001"}, ...]
        
        Time: O(P + D + W) - single pass through all files
        """
        base_path = Path(data_dir)
        
        with open(base_path / "Provinces.json", encoding="utf-8") as f:
            self.provinces = json.load(f)
        
        with open(base_path / "Districts.json", encoding="utf-8") as f:
            self.districts = json.load(f)
        
        with open(base_path / "Wards.json", encoding="utf-8") as f:
            self.wards = json.load(f)
    
    # ====================================================================
    # STEP 2: BUILD LOOKUP MAPS (Name → Code)
    # ====================================================================
    
    def _build_lookup_maps(self):
        """
        Build hash maps for O(1) name → code lookup
        
        Why different structures for each level?
        
        Province: 1:1 mapping
            "Hà Nội" → "01" (unique names)
        
        District: 1:many mapping
            "Tân Bình" → ["760", "761"] (duplicates across provinces)
        
        Ward: 1:many mapping
            "Tân Bình" → ["10363", "10364", ...] (many duplicates)
        
        Time: O(P + D + W)
        """
        # Province: Unique names → single code
        self.province_name_to_code: Dict[str, str] = {
            p['Name']: p['Code'] 
            for p in self.provinces
        }
        
        # District: Duplicate names → list of codes
        self.district_name_to_codes: Dict[str, List[str]] = {}
        for d in self.districts:
            name = d['Name']
            if name not in self.district_name_to_codes:
                self.district_name_to_codes[name] = []
            self.district_name_to_codes[name].append(d['Code'])
        
        # Ward: Duplicate names → list of codes
        self.ward_name_to_codes: Dict[str, List[str]] = {}
        for w in self.wards:
            name = w['Name']
            if name not in self.ward_name_to_codes:
                self.ward_name_to_codes[name] = []
            self.ward_name_to_codes[name].append(w['Code'])
    
    # ====================================================================
    # STEP 3: BUILD HIERARCHY MAPS (Code → Parent Code)
    # ====================================================================
    
    def _build_hierarchy_maps(self):
        """
        Build parent-child relationship maps using codes
        
        Why code-based?
            - Names duplicate, codes are unique
            - O(1) validation: just check parent_code match
        
        Structure:
            district_to_province: {"001" → "01"}
                                   Ba Đình → Hà Nội
            
            ward_to_district: {"00001" → "001"}
                               Phúc Xá → Ba Đình
        
        Time: O(D + W)
        """
        # District → Province mapping
        self.district_to_province: Dict[str, str] = {
            d['Code']: d['ProvinceCode']
            for d in self.districts
        }
        
        # Ward → District mapping
        self.ward_to_district: Dict[str, str] = {
            w['Code']: w['DistrictCode']
            for w in self.wards
        }

    # ====================================================================
    # STEP 4: BUILD TRIES (for fast matching with aliases)
    # ====================================================================
    
    def _build_tries(self):
        """
        Build separate Tries for each hierarchy level WITH ALIAS SUPPORT
        
        NEW: Generates and inserts multiple alias variants for each entity:
        - Normalized base form: "ho chi minh"
        - No-space compact: "hochiminh"
        - Initials: "hcm"
        - Dotted initials: "h.c.m"
        - First + last: "ho minh" (3+ tokens)
        - First initial + rest: "h. chi minh"
        
        All aliases point to the same original name for display.
        
        Time: O(P×p×a + D×d×a + W×w×a) where:
              p,d,w = avg name lengths
              a = number of aliases per entity (~6)
              Effective: O(n) since a is constant
        """
        from alias_generator import generate_aliases
        
        print("Building Tries with alias support (aggressive normalization)...")
        
        # Province Trie
        self.province_trie = Trie()
        province_alias_count = 0
        for p in self.provinces:
            name = p['Name']
            # REFACTORED: Pass normalizer instance (uses aggressive mode internally)
            aliases = generate_aliases(name, self.normalizer)
            
            # Insert all aliases pointing to original name
            for alias in aliases:
                self.province_trie.insert(alias, name)
            
            province_alias_count += len(aliases)
        
        print(f"  ✓ Province Trie: {len(self.provinces)} entities, {province_alias_count} total aliases")
        
        # District Trie
        self.district_trie = Trie()
        district_alias_count = 0
        for d in self.districts:
            name = d['Name'].strip()
            # REFACTORED: Pass normalizer instance
            aliases = generate_aliases(name, self.normalizer)
            
            for alias in aliases:
                self.district_trie.insert(alias, name)
            
            district_alias_count += len(aliases)
        
        print(f"  ✓ District Trie: {len(self.districts)} entities, {district_alias_count} total aliases")
        
        # Ward Trie
        self.ward_trie = Trie()
        ward_alias_count = 0
        for w in self.wards:
            name = w['Name'].strip()
            # REFACTORED: Pass normalizer instance
            aliases = generate_aliases(name, self.normalizer)
            
            for alias in aliases:
                self.ward_trie.insert(alias, name)
            
            ward_alias_count += len(aliases)
        
        print(f"  ✓ Ward Trie: {len(self.wards)} entities, {ward_alias_count} total aliases")
    
    def _build_lcs_candidates(self):
        """
        Pre-tokenize all entities for LCS matching

        Why: LCS needs token sequences, not raw strings
        Cost: O(total_entities) one-time preprocessing
        Benefit: O(1) lookup during parsing
        
        REFACTORED: Uses aggressive normalization for consistency
        """
        print("Building LCS candidate lists (aggressive normalization)...")

        # Province candidates: List[(name, tokens)]
        self.province_candidates = [
            (name, self.normalizer.normalize(name, aggressive=True).split())
            for name in self.province_name_to_code.keys()
        ]

        # District candidates: List[(name, tokens)]
        self.district_candidates = [
            (name, self.normalizer.normalize(name, aggressive=True).split())
            for name in self.district_name_to_codes.keys()
        ]

        # Ward candidates: List[(name, tokens)]
        self.ward_candidates = [
            (name, self.normalizer.normalize(name, aggressive=True).split())
            for name in self.ward_name_to_codes.keys()
        ]

        print(f"  ✓ {len(self.province_candidates)} provinces")
        print(f"  ✓ {len(self.district_candidates)} districts")
        print(f"  ✓ {len(self.ward_candidates)} wards")

    def get_districts_in_province(self, province_name: str) -> List[Tuple[str, List[str]]]:
        """
        Get LCS candidates for districts within a province
        
        Args:
            province_name: Province name (e.g., "Hà Nội")
        
        Returns:
            List of (district_name, tokens) that belong to this province
        """
        province_code = self.province_name_to_code.get(province_name)
        if not province_code:
            return []
        
        # Filter district candidates by province
        return [
            (name, tokens)
            for name, tokens in self.district_candidates
            if any(
                self.district_to_province.get(code) == province_code
                for code in self.district_name_to_codes[name]
            )
        ]
    
    def get_wards_in_district(
        self, 
        district_name: str, 
        province_name: str
    ) -> List[Tuple[str, List[str]]]:
        """
        Get LCS candidates for wards within a district
        
        Args:
            district_name: District name
            province_name: Province name (for disambiguation)
        
        Returns:
            List of (ward_name, tokens) that belong to this district
        """
        # First, get the correct district code
        district_code = self._find_valid_district_code(district_name, province_name)
        if not district_code:
            return []
        
        # Filter ward candidates by district
        return [
            (name, tokens)
            for name, tokens in self.ward_candidates
            if any(
                self.ward_to_district.get(code) == district_code
                for code in self.ward_name_to_codes[name]
            )
        ]
    
    def _find_valid_district_code(
        self, 
        district_name: str, 
        province_name: str
    ) -> Optional[str]:
        """
        Find district code that belongs to given province
        """
        province_code = self.province_name_to_code.get(province_name)
        if not province_code:
            return None
        
        district_codes = self.district_name_to_codes.get(district_name, [])
        
        for district_code in district_codes:
            if self.district_to_province.get(district_code) == province_code:
                return district_code
        
        return None
    
    # ====================================================================
    # SMART SEARCH METHODS (with prefix routing)
    # ====================================================================
    
    def search_province(self, query: str) -> Optional[str]:
        """
        Search for province using intelligent prefix routing
        
        Strategy:
            1. Normalize query
            2. Use PrefixRouter to detect level and extract core name
            3. If prefix detected and level=province, search province_trie directly
            4. Otherwise, try direct search as fallback
        
        Args:
            query: User input (e.g., "TP.HCM", "T Hà Nội", "Hồ Chí Minh")
        
        Returns:
            Matched province name or None
        
        Examples:
            search_province("tp.hcm") → "Hồ Chí Minh" (via routing)
            search_province("t ha noi") → "Hà Nội" (via routing)
            search_province("hcm") → "Hồ Chí Minh" (direct alias)
        """
        if not query:
            return None
        
        # Step 1: Normalize
        normalized = self.normalizer.normalize(query, aggressive=True)
        
        # Step 2: Try prefix routing (FAST PATH)
        level, core_name = self.prefix_router.detect_level(normalized)
        
        if level == 'province':
            # Router detected province-level prefix
            result = self.province_trie.search(core_name)
            if result:
                return result
        
        # Step 3: Fallback - direct search (no prefix detected)
        # This handles aliases and full names without prefixes
        result = self.province_trie.search(normalized)
        return result
    
    def search_district(self, query: str) -> Optional[str]:
        """
        Search for district using intelligent prefix routing
        
        Similar to search_province() but for district level
        Handles: "Q.1", "H. Củ Chi", "Quận 3", "Tân Bình"
        
        Returns:
            Matched district name or None
        """
        if not query:
            return None
        
        normalized = self.normalizer.normalize(query, aggressive=True)
        
        # Try prefix routing
        level, core_name = self.prefix_router.detect_level(normalized)
        
        if level == 'district':
            result = self.district_trie.search(core_name)
            if result:
                return result
        
        # Fallback - direct search
        result = self.district_trie.search(normalized)
        return result
    
    def search_ward(self, query: str) -> Optional[str]:
        """
        Search for ward using intelligent prefix routing
        
        KEY FEATURE: Properly handles "TT Tân Bình" (Thị trấn)
        
        Similar to search_province() but for ward level
        Handles: "P.1", "TT Tân Bình", "Xã Phú Bình", "Bến Nghé"
        
        Returns:
            Matched ward name or None
        """
        if not query:
            return None
        
        normalized = self.normalizer.normalize(query, aggressive=True)
        
        # Try prefix routing (THIS IS THE KEY FIX!)
        level, core_name = self.prefix_router.detect_level(normalized)
        
        if level == 'ward':
            # Router detected ward-level prefix (TT, P, X, etc.)
            result = self.ward_trie.search(core_name)
            if result:
                return result
        
        # Fallback - direct search
        result = self.ward_trie.search(normalized)
        return result
    
    # ====================================================================
    # VALIDATION METHODS
    # ====================================================================
    
    def validate_hierarchy(
        self, 
        ward_name: str, 
        district_name: str, 
        province_name: str
    ) -> bool:
        """
        Validate if (ward, district, province) forms valid hierarchy
        
        Algorithm:
            1. Get all possible codes for each name
            2. Check if ANY combination is valid using hierarchy maps
        
        Example:
            Input: ("Tân Bình", "Tân Bình", "Hồ Chí Minh")
            
            Step 1: Get codes
                ward_codes = ["10363", "10364"]
                district_codes = ["766"]
                province_code = "79"
            
            Step 2: Check combinations
                For ward "10363":
                    ward_to_district["10363"] == "766" ✓
                    district_to_province["766"] == "79" ✓
                → VALID
        
        Time: O(W_dup × D_dup) where W_dup, D_dup are duplicate counts
              In practice: O(1) since duplicates are small (~2-5)
        
        Returns:
            True if valid hierarchy, False otherwise
        """
        # Get province code (unique)
        province_code = self.province_name_to_code.get(province_name)
        if not province_code:
            return False
        
        # Get possible district codes
        district_codes = self.district_name_to_codes.get(district_name, [])
        if not district_codes:
            return False
        
        # Get possible ward codes
        ward_codes = self.ward_name_to_codes.get(ward_name, [])
        if not ward_codes:
            return False
        
        # Check if ANY combination is valid
        for ward_code in ward_codes:
            # Does this ward belong to any of the candidate districts?
            ward_district = self.ward_to_district.get(ward_code)
            
            if ward_district in district_codes:
                # Ward belongs to this district - check district→province
                if self.district_to_province.get(ward_district) == province_code:
                    return True
        
        return False
    
    def validate_district_province(
        self,
        district_name: str,
        province_name: str
    ) -> bool:
        """
        Validate if district belongs to province
        
        Time: O(D_dup) where D_dup = number of districts with same name
        """
        province_code = self.province_name_to_code.get(province_name)
        if not province_code:
            return False
        
        district_codes = self.district_name_to_codes.get(district_name, [])
        
        for district_code in district_codes:
            if self.district_to_province.get(district_code) == province_code:
                return True
        
        return False


# ========================================================================
# TESTING
# ========================================================================

if __name__ == "__main__":
    # Initialize database
    db = AddressDatabase(data_dir="../Data")
    
    print("\n" + "="*70)
    print("TESTING SMART SEARCH WITH PREFIX EXPANSION")
    print("="*70)
    
    # Test new smart search methods
    province_tests = [
        ("ha noi", "Direct match"),
        ("hcm", "Alias match"),
        ("tp.hcm", "Prefix expansion"),
        ("TP HCM", "Case + prefix"),
        ("thanh pho ho chi minh", "Full form with prefix"),
        ("dn", "Ambiguous abbreviation"),
    ]
    
    print("\nPROVINCE SEARCHES:")
    print("-"*70)
    for query, description in province_tests:
        result = db.search_province(query)
        status = "✅" if result else "❌"
        print(f"{status} '{query:30}' → {result:20} ({description})")
    
    district_tests = [
        ("nam tu liem", "Direct match"),
        ("q.1", "Prefix abbreviation"),
        ("q1", "Compact abbreviation"),
        ("quan 3", "Full form"),
        ("tan binh", "Duplicate name"),
    ]
    
    print("\nDISTRICT SEARCHES:")
    print("-"*70)
    for query, description in district_tests:
        result = db.search_district(query)
        status = "✅" if result else "❌"
        print(f"{status} '{query:30}' → {result:20} ({description})")
    
    ward_tests = [
        ("cau dien", "Direct match"),
        ("p.1", "Prefix abbreviation"),
        ("p1", "Compact abbreviation"),
        ("phuong 12", "Full form"),
    ]
    
    print("\nWARD SEARCHES:")
    print("-"*70)
    for query, description in ward_tests:
        result = db.search_ward(query)
        status = "✅" if result else "❌"
        print(f"{status} '{query:30}' → {result:20} ({description})")
    
    print("\n" + "="*70)
    print("TESTING HIERARCHY VALIDATION")
    print("="*70)
    
    # Test hierarchy validation
    test_cases = [
        ("Cầu Diễn", "Nam Từ Liêm", "Hà Nội", True),
        ("Định Công", "Hoàng Mai", "Hà Nội", True),
        ("Tân Bình", "Tân Bình", "Hồ Chí Minh", True),  # Fixed: use exact JSON name
        ("Cầu Diễn", "Hoàng Mai", "Hà Nội", False),  # Wrong district
        ("Tân Bình", "Nam Từ Liêm", "Hà Nội", False),  # Wrong combination
    ]
    
    for ward, district, province, expected in test_cases:
        result = db.validate_hierarchy(ward, district, province)
        status = "✓" if result == expected else "✗"
        print(f"{status} ({ward}, {district}, {province}) → {result}")
    
    print("\n" + "="*70)
    print("All tests complete!")
