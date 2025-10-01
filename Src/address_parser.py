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

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# Import from our modules
from address_database import AddressDatabase
from normalizer import normalize_text
from lcs_matcher import LCSMatcher  # NEW import


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

        # NEW: Initialize LCS matcher
        self.lcs_matcher = LCSMatcher(threshold=0.4)
        
        print("✓ Parser ready (Trie + LCS + validation)")
    
    # ========================================================================
    # MAIN PARSING INTERFACE
    # ========================================================================
    
    def parse(self, text: str, debug: bool = True) -> ParsedAddress:
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
        
        normalized = normalize_text(text, self.db.norm_config)
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
        
        # ===== TIER 2: LCS ALIGNMENT =====  # ← NEW!
        if debug:
            print("\n[TIER 2] Falling back to LCS...")
        
        lcs_result = self._try_lcs_match(input_tokens, trie_result, debug)
        
        if self._is_valid_result(lcs_result, debug):
            lcs_result.match_method = "lcs"
            # Confidence based on how complete the result is
            lcs_result.confidence = 0.7 if lcs_result.ward else \
                                0.6 if lcs_result.district else 0.5
            return lcs_result
        
        if debug:
            print("\n✗ All tiers failed - returning empty result")
        
        return ParsedAddress()
    
    # ========================================================================
    # TIER 1: TRIE MATCHING
    # ========================================================================
    
    def _try_trie_match(self, normalized_text: str, debug: bool = True) -> ParsedAddress:
        """
        Try Trie exact matching with hierarchical masking
        
        Strategy:
        1. Match province first
        2. Mask province tokens, then match district
        3. Mask district tokens, then match ward
        4. Validate hierarchy using codes
        
        This prevents the same substring (e.g., "Tuyên Quang") from being
        matched as both province AND district.
        
        Args:
            normalized_text: Normalized input text
            debug: Print debug info
        
        Returns:
            ParsedAddress (may be invalid if no match)
        
        Time: O(m) where m = len(text), single pass per tier
        """
        tokens = normalized_text.split()
        
        if debug:
            print(f"\n  Input tokens: {tokens}")
        
        # ===== STEP 1: Match Province =====
        province_matches = self.db.province_trie.search_in_text(normalized_text)
        province = self._select_best_match(province_matches)
        province_span = None  # (start, end) token indices
        
        if province and province_matches:
            # Find the span of the selected province match
            for match in province_matches:
                if match[0] == province:
                    province_span = (match[1], match[2])  # (start_pos, end_pos)
                    break
        
        if debug:
            print(f"\n  Province matches: {province_matches}")
            print(f"  Selected: {province} at {province_span}")
        
        # ===== STEP 2: Match District (with masking) =====
        if province_span:
            # Mask province tokens to prevent re-matching
            masked_tokens = tokens.copy()
            for i in range(province_span[0], province_span[1]):
                if i < len(masked_tokens):
                    masked_tokens[i] = "___"  # Unmatchable placeholder
            
            district_search_text = " ".join(masked_tokens)
        else:
            district_search_text = normalized_text
        
        district_matches = self.db.district_trie.search_in_text(district_search_text)
        district = self._select_best_match(district_matches)
        district_span = None
        
        if district and district_matches:
            for match in district_matches:
                if match[0] == district:
                    district_span = (match[1], match[2])
                    break
        
        if debug:
            print(f"\n  District search text: {district_search_text}")
            print(f"  District matches: {district_matches}")
            print(f"  Selected: {district} at {district_span}")
        
        # ===== STEP 3: Match Ward (with masking) =====
        if province_span or district_span:
            # Mask both province and district tokens
            masked_tokens = tokens.copy()
            
            if province_span:
                for i in range(province_span[0], province_span[1]):
                    if i < len(masked_tokens):
                        masked_tokens[i] = "___"
            
            if district_span:
                for i in range(district_span[0], district_span[1]):
                    if i < len(masked_tokens):
                        masked_tokens[i] = "___"
            
            ward_search_text = " ".join(masked_tokens)
        else:
            ward_search_text = normalized_text
        
        ward_matches = self.db.ward_trie.search_in_text(ward_search_text)
        ward = self._select_best_match(ward_matches)
        
        if debug:
            print(f"\n  Ward search text: {ward_search_text}")
            print(f"  Ward matches: {ward_matches}")
            print(f"  Selected: {ward}")
        
        # ===== STEP 4: Build Result & Validate Hierarchy =====
        result = ParsedAddress(
            province=province,
            district=district,
            ward=ward
        )
        
        # Add codes if we have matches
        if result.province:
            result.province_code = self.db.province_name_to_code.get(result.province)
        
        if result.district and result.province:
            result.district_code = self._find_valid_district_code(
                result.district, 
                result.province
            )
        
        if result.ward and result.district and result.province:
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
            key=lambda x: (x[2] - x[1], x[2]),
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
    
    def _is_valid_result(self, result: ParsedAddress, debug: bool = True) -> bool:
        """
        Check if parse result is valid
        
        NEW STRATEGY: Graceful degradation
        - Accept partial matches (province only, province+district, etc.)
        - Clear invalid components but keep valid ones
        
        Valid if: Has at least province with valid hierarchy
        """
        if not result or not result.province:
            if debug:
                print("  ✗ Invalid: No province found")
            return False
        
        # Province is required and must be valid
        if not result.province_code:
            if debug:
                print(f"  ✗ Invalid: Province '{result.province}' not found in database")
            return False
        
        # If we have a district, it must be valid - otherwise CLEAR it
        if result.district and not result.district_code:
            if debug:
                print(f"  ⚠ Warning: District '{result.district}' not in province '{result.province}' - clearing")
            result.district = None
            result.district_code = None
        
        # If we have a ward, it must be valid - otherwise CLEAR it
        if result.ward and not result.ward_code:
            if debug:
                print(f"  ⚠ Warning: Ward '{result.ward}' not in district '{result.district}' - clearing")
            result.ward = None
            result.ward_code = None
        
        # At this point, whatever remains is valid
        result.valid = True
        
        if debug:
            print(f"  ✓ Valid result (Province: {result.province}, "
                f"District: {result.district or 'N/A'}, "
                f"Ward: {result.ward or 'N/A'})")
        
        return True
    
    def _try_lcs_match(
        self, 
        input_tokens: List[str],
        trie_result: ParsedAddress,
        debug: bool = False
    ) -> ParsedAddress:
        """
        Try LCS matching with hierarchical constraints
        
        Strategy:
        1. Determine what Trie found (province/district/ward)
        2. Use LCS to fill in missing pieces
        3. Constrain search based on what we already know
        
        Args:
            input_tokens: Tokenized input text
            trie_result: Result from Trie matching (may be partial)
            debug: Print debug info
        
        Returns:
            ParsedAddress with LCS matches filled in
        """
        if debug:
            print("\n[TIER 2] Trying LCS matching...")
            print(f"  Trie gave us: P={trie_result.province}, "
                f"D={trie_result.district}, W={trie_result.ward}")
        
        # Start with what Trie found
        result = ParsedAddress(
            province=trie_result.province,
            district=trie_result.district,
            ward=trie_result.ward
        )

        # NEW: Clear invalid trie results before LCS
        # (Don't let bad Trie matches pollute LCS)
        if result.ward and not trie_result.ward_code:
            if debug:
                print(f"  Clearing invalid Trie ward: '{result.ward}'")
            result.ward = None
        
        if result.district and not trie_result.district_code:
            if debug:
                print(f"  Clearing invalid Trie district: '{result.district}'")
            result.district = None
        
        # ===== CASE 1: No province found → Search all levels =====
        if not result.province:
            if debug:
                print("  Case 1: No province → searching all levels")
            
            # Search province
            province_match = self.lcs_matcher.find_best_match(
                input_tokens,
                self.db.province_candidates,
                "province"
            )
            
            if province_match:
                result.province = province_match.entity_name
                if debug:
                    print(f"    Province LCS: {result.province} "
                        f"(score={province_match.similarity_score:.2f})")
            
            # If we found province via LCS, now search district constrained
            if result.province:
                district_candidates = self.db.get_districts_in_province(result.province)
                district_match = self.lcs_matcher.find_best_match(
                    input_tokens,
                    district_candidates,
                    "district"
                )
                
                if district_match:
                    result.district = district_match.entity_name
                    if debug:
                        print(f"    District LCS: {result.district} "
                            f"(score={district_match.similarity_score:.2f})")
            
            # If we have province + district, search ward
            if result.province and result.district:
                ward_candidates = self.db.get_wards_in_district(
                    result.district,
                    result.province
                )
                ward_match = self.lcs_matcher.find_best_match(
                    input_tokens,
                    ward_candidates,
                    "ward"
                )
                
                if ward_match:
                    result.ward = ward_match.entity_name
                    if debug:
                        print(f"    Ward LCS: {result.ward} "
                            f"(score={ward_match.similarity_score:.2f})")
        
        # ===== CASE 2: Has province but no district → Search district/ward =====
        elif result.province and not result.district:
            if debug:
                print(f"  Case 2: Has province '{result.province}' → "
                    f"searching district/ward")
            
            # Search district within province
            district_candidates = self.db.get_districts_in_province(result.province)
            district_match = self.lcs_matcher.find_best_match(
                input_tokens,
                district_candidates,
                "district"
            )
            
            if district_match:
                result.district = district_match.entity_name
                if debug:
                    print(f"    District LCS: {result.district} "
                        f"(score={district_match.similarity_score:.2f})")
                
                # Now search ward within district
                ward_candidates = self.db.get_wards_in_district(
                    result.district,
                    result.province
                )
                ward_match = self.lcs_matcher.find_best_match(
                    input_tokens,
                    ward_candidates,
                    "ward"
                )
                
                if ward_match:
                    result.ward = ward_match.entity_name
                    if debug:
                        print(f"    Ward LCS: {result.ward} "
                            f"(score={ward_match.similarity_score:.2f})")
        
        # ===== CASE 3: Has province + district but no ward → Search ward only =====
        elif result.province and result.district and not result.ward:
            if debug:
                print(f"  Case 3: Has province + district → searching ward only")
            
            ward_candidates = self.db.get_wards_in_district(
                result.district,
                result.province
            )
            ward_match = self.lcs_matcher.find_best_match(
                input_tokens,
                ward_candidates,
                "ward"
            )
            
            if ward_match:
                result.ward = ward_match.entity_name
                if debug:
                    print(f"    Ward LCS: {result.ward} "
                        f"(score={ward_match.similarity_score:.2f})")
        
        # ===== Add codes for validation =====
        if result.province:
            result.province_code = self.db.province_name_to_code.get(result.province)
        
        if result.district and result.province:
            result.district_code = self._find_valid_district_code(
                result.district,
                result.province
            )
        
        if result.ward and result.district and result.province:
            result.ward_code = self._find_valid_ward_code(
                result.ward,
                result.district,
                result.province
            )
        
        return result


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

        # new cases
        "TT Tân Bình Huyện Yên Sơn, Tuyên Quang",
        " ,H Krông Năng,Đắk Lắk",
        "Liên Minh,,TỉnhThái Nguyên",
        "XMiền Đồi,LaZc Sơn,"
        ",H Bắc Son,TỉnhLạng Son",
        "357/28,Ng-T- Thuật,P1,Q3,TP.HồChíMinh.",
        "284DBis Ng Văn Giáo, P3, Mỹ Tho, T.Giang.",
        "Nà Làng Phú Bình, Chiêm Hoá, Tuyên Quang",
        "59/12 Ng-B-Khiêm, Đa Kao Quận 1, TP. Hồ Chí Minh"
    ]
    
    print("\n")
    for i, text in enumerate(test_cases, 1):
        print(f"[TEST {i}] '{text}'")
        print("-" * 70)
        
        result = parser.parse(text, debug=True)
        
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
