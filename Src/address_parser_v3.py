"""
Address Parser - Three-Tier Matching System

Architecture:
    Tier 1: Trie Exact Match    O(m)      ~80% cases
    Tier 2: LCS Alignment       O(n×m)    ~15% cases
    Tier 3: Edit Distance       O(k×m)    ~5% cases

Algorithm:
- Try Trie first (fast path for clean addresses)
- Fallback to LCS (handles extra words, reordering)
- Fallback to Edit Distance (handles typos, OCR errors)
- Validate hierarchy at each level
- Return best result with confidence score
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# Import from our modules
from address_database import AddressDatabase
from archive.normalizer import normalize_text
from lcs_matcher import LCSMatcher
from edit_distance_matcher import EditDistanceMatcher  # NEW: Tier 3


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
    Three-tier address parser with intelligent fallback
    
    Usage:
        parser = AddressParser()
        result = parser.parse("ha nol")  # Typo: should be "ha noi"
        
        print(result.province)       # "Hà Nội"
        print(result.match_method)   # "edit_distance"
        print(result.confidence)     # 0.3
    """
    
    def __init__(self, data_dir: str = "../Data"):
        """
        Initialize parser with all three matching tiers
        
        Args:
            data_dir: Path to JSON data files
        """
        print("Initializing Address Parser...")
        
        # Build database (includes Tries)
        self.db = AddressDatabase(data_dir=data_dir)

        # Initialize all three matchers
        self.lcs_matcher = LCSMatcher(threshold=0.4)           # Tier 2
        self.edit_matcher = EditDistanceMatcher(max_distance=2)  # Tier 3
        
        print("✓ Parser ready (Trie + LCS + Edit Distance + validation)")
    
    # ========================================================================
    # MAIN PARSING INTERFACE
    # ========================================================================
    
    def parse(self, text: str, debug: bool = True) -> ParsedAddress:
        """
        Parse address with three-tier fallback
        
        Args:
            text: Raw address text
            debug: If True, include detailed debug information
        
        Returns:
            ParsedAddress with extracted components and metadata
        
        Flow:
            1. Try Trie exact match (Tier 1)
            2. Try LCS alignment (Tier 2)
            3. Try Edit Distance fuzzy match (Tier 3)
            4. Validate hierarchy at each level
            5. Return best valid result
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
        
        # ===== TIER 2: LCS ALIGNMENT =====
        if debug:
            print("\n[TIER 2] Falling back to LCS...")
        
        lcs_result = self._try_lcs_match(input_tokens, trie_result, debug)
        
        if self._is_valid_result(lcs_result, debug):
            if debug:
                print("✓ LCS match SUCCESS - returning result")
            lcs_result.match_method = "lcs"
            # Confidence based on how complete the result is
            lcs_result.confidence = 0.7 if lcs_result.ward else \
                                0.6 if lcs_result.district else 0.5
            return lcs_result
        
        if debug:
            print("✗ LCS match failed")
        
        # ===== TIER 3: EDIT DISTANCE FUZZY MATCH =====
        if debug:
            print("\n[TIER 3] Falling back to Edit Distance...")
        
        edit_result = self._try_edit_match(input_tokens, lcs_result, debug)
        
        if self._is_valid_result(edit_result, debug):
            if debug:
                print("✓ Edit Distance match SUCCESS - returning result")
            edit_result.match_method = "edit_distance"
            # Lower confidence for fuzzy matches
            edit_result.confidence = 0.5 if edit_result.ward else \
                                   0.4 if edit_result.district else 0.3
            return edit_result
        
        if debug:
            print("\n✗ All tiers failed - returning empty result")
        
        return ParsedAddress()
    
    # ========================================================================
    # TIER 1: TRIE MATCHING
    # ========================================================================
    
    def _try_trie_match(self, normalized_text: str, debug: bool = True) -> ParsedAddress:
        """
        Try Trie exact matching with hierarchical masking
        
        (Implementation unchanged from your existing code)
        """
        tokens = normalized_text.split()
        
        if debug:
            print(f"\n  Input tokens: {tokens}")
        
        # ===== STEP 1: Match Province =====
        province_matches = self.db.province_trie.search_in_text(normalized_text)
        province = self._select_best_match(province_matches)
        province_span = None
        
        if province and province_matches:
            for match in province_matches:
                if match[0] == province:
                    province_span = (match[1], match[2])
                    break
        
        if debug:
            print(f"\n  Province matches: {province_matches}")
            print(f"  Selected: {province} at {province_span}")
        
        # ===== STEP 2: Match District (with masking) =====
        if province_span:
            masked_tokens = tokens.copy()
            for i in range(province_span[0], province_span[1]):
                if i < len(masked_tokens):
                    masked_tokens[i] = "___"
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
        
        # Add codes
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
    
    # ========================================================================
    # TIER 2: LCS MATCHING
    # ========================================================================
    
    def _try_lcs_match(
        self, 
        input_tokens: List[str],
        trie_result: ParsedAddress,
        debug: bool = False
    ) -> ParsedAddress:
        """
        Try LCS matching with hierarchical constraints
        
        (Implementation unchanged from your existing code)
        """
        if debug:
            print("\n  Trying LCS matching...")
            print(f"  Trie gave us: P={trie_result.province}, "
                f"D={trie_result.district}, W={trie_result.ward}")
        
        # Start with what Trie found
        result = ParsedAddress(
            province=trie_result.province,
            district=trie_result.district,
            ward=trie_result.ward
        )

        # Clear invalid trie results before LCS
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
    # TIER 3: EDIT DISTANCE MATCHING (NEW!)
    # ========================================================================
    
    def _try_edit_match(
        self,
        input_tokens: List[str],
        lcs_result: ParsedAddress,
        debug: bool = False
    ) -> ParsedAddress:
        """
        Try Edit Distance fuzzy matching with hierarchical constraints
        
        Strategy:
        1. Start with what LCS found (may be partial or empty)
        2. Use Edit Distance to find matches with typos/OCR errors
        3. Constrain search based on what we already know
        
        Args:
            input_tokens: Tokenized input text
            lcs_result: Result from LCS matching (may be partial)
            debug: Print debug info
        
        Returns:
            ParsedAddress with Edit Distance matches filled in
        
        Handles:
        - Character-level typos ("ha nol" → "ha noi")
        - OCR errors ("dihn cong" → "dinh cong")
        - Transpositions ("cauv dien" → "cau dien")
        """
        if debug:
            print("\n  Trying Edit Distance matching...")
            print(f"  LCS gave us: P={lcs_result.province}, "
                f"D={lcs_result.district}, W={lcs_result.ward}")
        
        # Start with what LCS found
        result = ParsedAddress(
            province=lcs_result.province,
            district=lcs_result.district,
            ward=lcs_result.ward
        )
        
        # Clear invalid LCS results before Edit Distance
        if result.ward and not lcs_result.ward_code:
            if debug:
                print(f"  Clearing invalid LCS ward: '{result.ward}'")
            result.ward = None
        
        if result.district and not lcs_result.district_code:
            if debug:
                print(f"  Clearing invalid LCS district: '{result.district}'")
            result.district = None
        
        # ===== CASE 1: No province found → Search all levels =====
        if not result.province:
            if debug:
                print("  Case 1: No province → searching all levels with Edit Distance")
            
            # Search province
            province_match = self.edit_matcher.find_best_match(
                input_tokens,
                self.db.province_candidates,
                "province"
            )
            
            if province_match:
                result.province = province_match.entity_name
                if debug:
                    print(f"    Province Edit: {result.province} "
                        f"(distance={province_match.edit_distance}, "
                        f"score={province_match.normalized_score:.2f})")
            
            # If we found province, search district
            if result.province:
                district_candidates = self.db.get_districts_in_province(result.province)
                district_match = self.edit_matcher.find_best_match(
                    input_tokens,
                    district_candidates,
                    "district"
                )
                
                if district_match:
                    result.district = district_match.entity_name
                    if debug:
                        print(f"    District Edit: {result.district} "
                            f"(distance={district_match.edit_distance})")
            
            # If we have province + district, search ward
            if result.province and result.district:
                ward_candidates = self.db.get_wards_in_district(
                    result.district,
                    result.province
                )
                ward_match = self.edit_matcher.find_best_match(
                    input_tokens,
                    ward_candidates,
                    "ward"
                )
                
                if ward_match:
                    result.ward = ward_match.entity_name
                    if debug:
                        print(f"    Ward Edit: {result.ward} "
                            f"(distance={ward_match.edit_distance})")
        
        # ===== CASE 2: Has province but no district → Search district/ward =====
        elif result.province and not result.district:
            if debug:
                print(f"  Case 2: Has province '{result.province}' → "
                    f"searching district/ward with Edit Distance")
            
            # Search district within province
            district_candidates = self.db.get_districts_in_province(result.province)
            district_match = self.edit_matcher.find_best_match(
                input_tokens,
                district_candidates,
                "district"
            )
            
            if district_match:
                result.district = district_match.entity_name
                if debug:
                    print(f"    District Edit: {result.district} "
                        f"(distance={district_match.edit_distance})")
                
                # Search ward within district
                ward_candidates = self.db.get_wards_in_district(
                    result.district,
                    result.province
                )
                ward_match = self.edit_matcher.find_best_match(
                    input_tokens,
                    ward_candidates,
                    "ward"
                )
                
                if ward_match:
                    result.ward = ward_match.entity_name
                    if debug:
                        print(f"    Ward Edit: {result.ward} "
                            f"(distance={ward_match.edit_distance})")
        
        # ===== CASE 3: Has province + district but no ward → Search ward only =====
        elif result.province and result.district and not result.ward:
            if debug:
                print(f"  Case 3: Has province + district → searching ward only with Edit Distance")
            
            ward_candidates = self.db.get_wards_in_district(
                result.district,
                result.province
            )
            ward_match = self.edit_matcher.find_best_match(
                input_tokens,
                ward_candidates,
                "ward"
            )
            
            if ward_match:
                result.ward = ward_match.entity_name
                if debug:
                    print(f"    Ward Edit: {result.ward} "
                        f"(distance={ward_match.edit_distance})")
        
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
    # HELPER METHODS
    # ========================================================================
    
    def _select_best_match(self, matches: List[tuple]) -> Optional[str]:
        """Select best match from candidates (longest + rightmost)"""
        if not matches:
            return None
        
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
        """Find district code that belongs to given province"""
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
        """Find ward code that belongs to given district and province"""
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
        Check if parse result is valid (graceful degradation)
        """
        if not result or not result.province:
            if debug:
                print("  ✗ Invalid: No province found")
            return False
        
        if not result.province_code:
            if debug:
                print(f"  ✗ Invalid: Province '{result.province}' not found in database")
            return False
        
        # Clear invalid district
        if result.district and not result.district_code:
            if debug:
                print(f"  ⚠ Warning: District '{result.district}' not in province '{result.province}' - clearing")
            result.district = None
            result.district_code = None
        
        # Clear invalid ward
        if result.ward and not result.ward_code:
            if debug:
                print(f"  ⚠ Warning: Ward '{result.ward}' not in district '{result.district}' - clearing")
            result.ward = None
            result.ward_code = None
        
        result.valid = True
        
        if debug:
            print(f"  ✓ Valid result (Province: {result.province}, "
                f"District: {result.district or 'N/A'}, "
                f"Ward: {result.ward or 'N/A'})")
        
        return True


# ========================================================================
# TESTING
# ========================================================================

if __name__ == "__main__":
    print("="*70)
    print("THREE-TIER ADDRESS PARSER - TEST SUITE")
    print("="*70)
    
    parser = AddressParser(data_dir="../Data")
    
    # Test cases for all three tiers
    test_cases = [
        # Tier 1: Clean addresses (should use Trie)
        ("Cầu Diễn, Nam Từ Liêm, Hà Nội", "trie"),
        
        # Tier 2: Extra words (should use LCS)
        ("123 Nguyen Van Linh, Cau Dien, Nam Tu Liem, Ha Noi", "lcs"),
        
        # Tier 3: Typos (should use Edit Distance)
        ("ha nol", "edit_distance"),  # typo: nol → noi
        ("nam tu leam", "edit_distance"),  # typo: leam → liem
        ("dihn cong", "edit_distance"),  # transposition
    ]
    
    print("\n")
    for i, (text, expected_method) in enumerate(test_cases, 1):
        print(f"[TEST {i}] '{text}'")
        print(f"Expected method: {expected_method}")
        print("-" * 70)
        
        result = parser.parse(text, debug=True)
        
        print(f"\n  Result:")
        print(f"  Province:   {result.province or 'N/A'}")
        print(f"  District:   {result.district or 'N/A'}")
        print(f"  Ward:       {result.ward or 'N/A'}")
        print(f"  Method:     {result.match_method}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Status:     {'✓ PASS' if result.match_method == expected_method else '✗ FAIL'}")
        print()
    
    print("="*70)
    print("Test complete!")
    print("="*70)
