"""
Address Parser - Multi-Tier Matching System

Architecture:
    Tier 1: Trie Exact Match    O(m)      ~80% cases
    Tier 2: LCS Alignment       O(n×m)    ~15% cases
    Tier 3: Edit Distance       O(k×m)    ~5% cases (future)

Algorithm:
- Try Trie first (fast path)
- Fallback to LCS if Trie fails
- Validate hierarchy at each level
- Return best result with confidence score
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field

# Import from our modules
from address_database import AddressDatabase
from trie_parser import normalize_text, Trie


@dataclass
class ParsedAddress:
    """Result of address parsing with metadata"""
    ward: Optional[str] = None
    district: Optional[str] = None
    province: Optional[str] = None
    
    ward_code: Optional[str] = None
    district_code: Optional[str] = None
    province_code: Optional[str] = None
    
    confidence: float = 0.0
    valid: bool = False
    match_method: str = "none"  # "trie", "lcs", "edit_distance", or "none"
    
    # Debug info
    debug_info: Dict = field(default_factory=dict)


class AddressParser:
    """
    Multi-tier address parser with intelligent fallback
    
    Usage:
        parser = AddressParser()
        result = parser.parse("123 Nguyen Van Linh, Cau Dien, Nam Tu Liem, Ha Noi")
        
        print(result.ward)          # "Cầu Diễn"
        print(result.match_method)  # "trie"
        print(result.confidence)    # 1.0
    """
    
    def __init__(self, data_dir: str = "../Data"):
        """
        Initialize parser with all matching tiers
        
        Args:
            data_dir: Path to JSON data files
        """
        print("Initializing Address Parser...")
        
        # Build database (includes Tries)
        self.db = AddressDatabase(data_dir=data_dir)
        
        print("✓ Parser ready (Trie + validation)")
    
    # ========================================================================
    # MAIN PARSING INTERFACE
    # ========================================================================
    
    def parse(self, text: str, debug: bool = False) -> ParsedAddress:
        """
        Parse address with multi-tier fallback
        
        Args:
            text: Raw address text
            debug: If True, include detailed debug information
        
        Returns:
            ParsedAddress with extracted components and metadata
        
        Flow:
            1. Try Trie exact match
            2. Validate hierarchy
            3. Return best result
        """
        if not text or not text.strip():
            return ParsedAddress()
        
        normalized = normalize_text(text)
        input_tokens = normalized.split()
        
        if debug:
            print(f"\n{'='*70}")
            print(f"PARSING: {text}")
            print(f"Normalized: {normalized}")
            print(f"Tokens: {input_tokens}")
            print(f"{'='*70}")
        
        # ===== TIER 1: TRIE EXACT MATCH =====
        if debug:
            print("\n[TIER 1] Trying Trie exact match...")
        
        trie_result = self._try_trie_match(normalized, debug)
        
        if self._is_valid_result(trie_result, debug):
            if debug:
                print("✓ Trie match SUCCESS - returning result")
            trie_result.match_method = "trie"
            trie_result.confidence = 1.0  # Exact match
            return trie_result
        
        if debug:
            print("✗ Trie match failed")
        
        # ===== TIER 2: LCS ALIGNMENT (FUTURE) =====
        # TODO: Implement LCS fallback for fuzzy matching
        
        # ===== TIER 3: EDIT DISTANCE (FUTURE) =====
        # TODO: Implement edit distance for typos
        
        if debug:
            print("\n✗ All tiers failed - returning empty result")
        
        return ParsedAddress()
    
    # ========================================================================
    # TIER 1: TRIE MATCHING
    # ========================================================================
    
    def _try_trie_match(self, normalized_text: str, debug: bool = False) -> ParsedAddress:
        """
        Try Trie exact matching
        
        Args:
            normalized_text: Normalized input text
            debug: Print debug info
        
        Returns:
            ParsedAddress (may be invalid if no match)
        
        Algorithm:
            1. Search in all 3 tries (province, district, ward)
            2. Get matches with position information
            3. Select best match from each tier
            4. Look up codes for validation
        """
        # Search in all three tries
        province_matches = self.db.province_trie.search_in_text(normalized_text)
        district_matches = self.db.district_trie.search_in_text(normalized_text)
        ward_matches = self.db.ward_trie.search_in_text(normalized_text)
        
        if debug:
            print(f"\n  Trie Matches:")
            print(f"    Provinces: {province_matches}")
            print(f"    Districts: {district_matches}")
            print(f"    Wards: {ward_matches}")
        
        # Select best match from each (longest + rightmost)
        province = self._select_best_match(province_matches)
        district = self._select_best_match(district_matches)
        ward = self._select_best_match(ward_matches)
        
        # Build result
        result = ParsedAddress(
            province=province,
            district=district,
            ward=ward
        )
        
        # Add codes if we have matches
        if result.province:
            result.province_code = self.db.province_name_to_code.get(result.province)
        
        if result.district and result.province:
            # Get district codes that belong to this province
            result.district_code = self._find_valid_district_code(
                result.district, 
                result.province
            )
        
        if result.ward and result.district and result.province:
            # Get ward code that belongs to this district
            result.ward_code = self._find_valid_ward_code(
                result.ward,
                result.district,
                result.province
            )
        
        if debug:
            print(f"\n  Extracted:")
            print(f"    Province: {result.province} ({result.province_code})")
            print(f"    District: {result.district} ({result.district_code})")
            print(f"    Ward: {result.ward} ({result.ward_code})")
        
        return result
    
    def _select_best_match(self, matches: List[tuple]) -> Optional[str]:
        """
        Select best match from candidates
        
        Strategy:
        1. Prefer longest match (most specific)
        2. Break ties with rightmost position
        
        Args:
            matches: List of (value, start_pos, end_pos)
        
        Returns:
            Best matching value or None
        """
        if not matches:
            return None
        
        # Sort by: length DESC, then end position DESC
        sorted_matches = sorted(
            matches,
            key=lambda x: (len(x[0]), x[2]),
            reverse=True
        )
        
        return sorted_matches[0][0]
    
    def _find_valid_district_code(
        self, 
        district_name: str, 
        province_name: str
    ) -> Optional[str]:
        """
        Find district code that belongs to given province
        
        Handles duplicate district names by filtering by province
        
        Returns:
            District code or None
        """
        province_code = self.db.province_name_to_code.get(province_name)
        if not province_code:
            return None
        
        district_codes = self.db.district_name_to_codes.get(district_name, [])
        
        for district_code in district_codes:
            if self.db.district_to_province.get(district_code) == province_code:
                return district_code
        
        return None
    
    def _find_valid_ward_code(
        self,
        ward_name: str,
        district_name: str,
        province_name: str
    ) -> Optional[str]:
        """
        Find ward code that belongs to given district and province
        
        Handles duplicate ward names by filtering by district
        
        Returns:
            Ward code or None
        """
        # Get district code first
        district_code = self._find_valid_district_code(district_name, province_name)
        if not district_code:
            return None
        
        ward_codes = self.db.ward_name_to_codes.get(ward_name, [])
        
        for ward_code in ward_codes:
            if self.db.ward_to_district.get(ward_code) == district_code:
                return ward_code
        
        return None
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    
    def _is_valid_result(self, result: ParsedAddress, debug: bool = False) -> bool:
        """
        Check if parse result is valid
        
        Valid if:
        1. Has at least province
        2. Hierarchy is consistent (codes match)
        
        Args:
            result: ParsedAddress to validate
            debug: Print validation details
        
        Returns:
            True if valid, False otherwise
        """
        if not result or not result.province:
            if debug:
                print("  ✗ Invalid: No province found")
            return False
        
        # If we have codes, hierarchy is already validated
        # (codes are only assigned if hierarchy is valid)
        
        # Additional check: If we have district, must have valid code
        if result.district and not result.district_code:
            if debug:
                print(f"  ✗ Invalid: District '{result.district}' not in province '{result.province}'")
            return False
        
        # If we have ward, must have valid code
        if result.ward and not result.ward_code:
            if debug:
                print(f"  ✗ Invalid: Ward '{result.ward}' not in district '{result.district}'")
            return False
        
        result.valid = True
        if debug:
            print(f"  ✓ Valid result")
        
        return True


# ========================================================================
# CONVENIENCE FUNCTIONS
# ========================================================================

def parse_address(text: str, data_dir: str = "../Data") -> Dict[str, Optional[str]]:
    """
    Simple interface for address parsing
    
    Args:
        text: Address text
        data_dir: Path to data files
    
    Returns:
        Dict with province, district, ward, confidence, method keys
    """
    parser = AddressParser(data_dir=data_dir)
    result = parser.parse(text)
    
    return {
        "province": result.province,
        "district": result.district,
        "ward": result.ward,
        "confidence": result.confidence,
        "valid": result.valid,
        "method": result.match_method
    }


# ========================================================================
# TESTING
# ========================================================================

if __name__ == "__main__":
    print("="*70)
    print("ADDRESS PARSER - TEST SUITE")
    print("="*70)
    
    # Initialize parser (this builds the database)
    parser = AddressParser(data_dir="../Data")
    
    # Test cases covering various scenarios
    test_cases = [
        # Clean, well-formatted addresses
        "Cầu Diễn, Nam Từ Liêm, Hà Nội",
        "Định Công, Hoàng Mai, Hà Nội",
        
        # Without diacritics
        "Cau Dien, Nam Tu Liem, Ha Noi",
        
        # Duplicate names (needs hierarchy validation)
        "Tân Bình, Tân Bình, Hồ Chí Minh",
        
        # Partial addresses
        "Hà Nội",
        "Nam Từ Liêm, Hà Nội",
        
        # Edge cases
        "Ha Noi",
        "HCM",
    ]
    
    print("\n")
    for i, text in enumerate(test_cases, 1):
        print(f"[TEST {i}] '{text}'")
        print("-" * 70)
        
        result = parser.parse(text, debug=False)
        
        print(f"  Province:   {result.province or 'N/A'}")
        print(f"  District:   {result.district or 'N/A'}")
        print(f"  Ward:       {result.ward or 'N/A'}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Method:     {result.match_method}")
        print(f"  Valid:      {result.valid}")
        print()
    
    print("="*70)
    print("All tests complete!")
    print("="*70)
