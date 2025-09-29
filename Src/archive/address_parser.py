"""
Address Parser - Extract structured addresses from messy text

Algorithm: Contextual Hierarchical Matching
- Token-based sliding window for candidate extraction
- Hierarchical validation for disambiguation
- Scoring system for best match selection
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from address_database import AddressDatabase


@dataclass
class Candidate:
    """Represents a potential entity match in text"""
    entity_type: str  # "province", "district", or "ward"
    name: str         # Official name
    normalized: str   # Normalized form that matched
    start_token: int  # Position in token array
    end_token: int    # Position in token array (exclusive)
    codes: List[str] = field(default_factory=list)  # Possible codes for this entity


@dataclass
class ParsedAddress:
    """Result of address parsing with confidence score"""
    ward: Optional[str] = None
    district: Optional[str] = None
    province: Optional[str] = None
    
    ward_code: Optional[str] = None
    district_code: Optional[str] = None
    province_code: Optional[str] = None
    
    confidence: float = 0.0
    valid: bool = False
    
    # Debugging info
    all_candidates: List[Candidate] = field(default_factory=list)
    


class AddressParser:
    """
    Parse unstructured address text into structured components
    
    Algorithm Phases:
    1. Tokenization & Normalization
    2. Candidate Extraction (sliding window)
    3. Hierarchical Validation
    4. Scoring & Selection
    """
    
    def __init__(self, db: AddressDatabase):
        self.db = db
        self.max_window_size = 6  # Max tokens in an admin name
    
    def parse(self, text: str, debug: bool = False) -> ParsedAddress:
        """
        Parse address text into structured components
        
        Args:
            text: Raw address text (e.g., "Cau Dien, Nam Tu Liem, Ha Noi")
            debug: If True, include all candidates in result
        
        Returns:
            ParsedAddress object with extracted components
        
        Time Complexity: O(n × k) where n=tokens, k=window_size (constant)
        """
        # Phase 1: Tokenization
        normalized = self.db._normalize(text)
        tokens = normalized.split()
        
        if not tokens:
            return ParsedAddress()
        
        # Phase 2: Extract candidates using sliding window
        candidates = self._extract_candidates(tokens)
        
        if not candidates:
            return ParsedAddress(all_candidates=candidates if debug else [])
        
        # Phase 3: Find best valid combination
        best_match = self._find_best_match(candidates, tokens)
        
        if debug:
            best_match.all_candidates = candidates
        
        return best_match
    
    def _extract_candidates(self, tokens: List[str]) -> List[Candidate]:
        """
        Extract all possible entity matches using sliding window
        
        Algorithm:
        - For each window size (1 to max_window_size)
        - For each starting position
        - Try to match the token sequence against all entity types
        
        Time: O(n × k × 3) where 3 = number of entity types
        """
        candidates = []
        n = len(tokens)
        
        # Try all window sizes
        for window_size in range(1, min(self.max_window_size + 1, n + 1)):
            # Try all starting positions
            for start in range(n - window_size + 1):
                end = start + window_size
                
                # Extract candidate string
                candidate_tokens = tokens[start:end]
                candidate_str = " ".join(candidate_tokens)
                
                # Try matching as province
                province = self.db.lookup_province(candidate_str)
                if province:
                    prov_code = self.db.province_name_to_code.get(province)
                    candidates.append(Candidate(
                        entity_type="province",
                        name=province,
                        normalized=candidate_str,
                        start_token=start,
                        end_token=end,
                        codes=[prov_code] if prov_code else []
                    ))
                
                # Try matching as district
                districts = self.db.lookup_district(candidate_str)
                for district in districts:
                    dist_codes = self.db.district_name_to_codes.get(district, [])
                    candidates.append(Candidate(
                        entity_type="district",
                        name=district,
                        normalized=candidate_str,
                        start_token=start,
                        end_token=end,
                        codes=dist_codes
                    ))
                
                # Try matching as ward
                wards = self.db.lookup_ward(candidate_str)
                for ward in wards:
                    ward_codes = self.db.ward_name_to_codes.get(ward, [])
                    candidates.append(Candidate(
                        entity_type="ward",
                        name=ward,
                        normalized=candidate_str,
                        start_token=start,
                        end_token=end,
                        codes=ward_codes
                    ))
        
        return candidates
    
    def _find_best_match(self, candidates: List[Candidate], tokens: List[str]) -> ParsedAddress:
        """
        Find the best valid combination of candidates
        
        Strategy:
        1. Group candidates by type
        2. Try all combinations of (province, district, ward)
        3. Validate hierarchy for each combination
        4. Score valid combinations
        5. Return highest scoring
        
        Time: O(P × D × W) where P,D,W = candidates of each type
        Typical: O(1 × 2 × 3) = O(6) very fast
        """
        # Group by entity type
        provinces = [c for c in candidates if c.entity_type == "province"]
        districts = [c for c in candidates if c.entity_type == "district"]
        wards = [c for c in candidates if c.entity_type == "ward"]
        
        best_result = ParsedAddress()
        best_score = 0.0
        
        # Try all combinations
        # Start with most specific (ward) to least specific (province)
        
        # Case 1: Have all three levels
        for ward in wards:
            for district in districts:
                for province in provinces:
                    result = self._validate_combination(
                        ward, district, province, tokens
                    )
                    if result and result.confidence > best_score:
                        best_score = result.confidence
                        best_result = result
        
        # Case 2: Only district + province
        if best_score == 0.0:
            for district in districts:
                for province in provinces:
                    result = self._validate_combination(
                        None, district, province, tokens
                    )
                    if result and result.confidence > best_score:
                        best_score = result.confidence
                        best_result = result
        
        # Case 3: Only province
        if best_score == 0.0:
            for province in provinces:
                result = self._validate_combination(
                    None, None, province, tokens
                )
                if result and result.confidence > best_score:
                    best_score = result.confidence
                    best_result = result
        
        # Case 4: Only ward (resolve full address)
        if best_score == 0.0 and wards:
            for ward in wards:
                # Get full address for this ward
                matches = self.db.get_full_address(ward.name)
                if matches:
                    match = matches[0]  # Take first if multiple
                    result = ParsedAddress(
                        ward=match.ward,
                        district=match.district,
                        province=match.province,
                        ward_code=match.ward_code,
                        district_code=match.district_code,
                        province_code=match.province_code,
                        confidence=0.5,  # Lower confidence (only ward provided)
                        valid=True
                    )
                    if result.confidence > best_score:
                        best_score = result.confidence
                        best_result = result
        
        return best_result
    
    def _validate_combination(
        self,
        ward: Optional[Candidate],
        district: Optional[Candidate],
        province: Optional[Candidate],
        tokens: List[str]
    ) -> Optional[ParsedAddress]:
        """
        Validate a combination of candidates and compute confidence score
        
        Scoring:
        - Hierarchical consistency: 50%
        - Positional order: 30%
        - Completeness: 20%
        
        Returns None if invalid
        """
        if not province:
            return None
        
        # Check for overlapping tokens (can't be the same text)
        positions = []
        if ward:
            positions.append((ward.start_token, ward.end_token))
        if district:
            positions.append((district.start_token, district.end_token))
        if province:
            positions.append((province.start_token, province.end_token))
        
        # Check overlaps
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                start1, end1 = positions[i]
                start2, end2 = positions[j]
                # Overlap if: start1 < end2 AND start2 < end1
                if start1 < end2 and start2 < end1:
                    return None  # Overlapping candidates
        
        # Validate hierarchy if we have district
        if district:
            # Find which district code belongs to this province
            prov_code = province.codes[0] if province.codes else None
            if not prov_code:
                return None
            
            valid_dist_code = None
            for dist_code in district.codes:
                if self.db.district_to_province.get(dist_code) == prov_code:
                    valid_dist_code = dist_code
                    break
            
            if not valid_dist_code:
                return None  # District not in this province
            
            # If we have ward, validate it belongs to district
            if ward:
                valid_ward_code = None
                for ward_code in ward.codes:
                    if self.db.ward_to_district.get(ward_code) == valid_dist_code:
                        valid_ward_code = ward_code
                        break
                
                if not valid_ward_code:
                    return None  # Ward not in this district
                
                # Valid combination - compute score
                score = self._compute_score(ward, district, province, tokens)
                
                return ParsedAddress(
                    ward=ward.name,
                    district=district.name,
                    province=province.name,
                    ward_code=valid_ward_code,
                    district_code=valid_dist_code,
                    province_code=prov_code,
                    confidence=score,
                    valid=True
                )
            else:
                # Only district + province
                score = self._compute_score(None, district, province, tokens)
                
                return ParsedAddress(
                    district=district.name,
                    province=province.name,
                    district_code=valid_dist_code,
                    province_code=prov_code,
                    confidence=score,
                    valid=True
                )
        else:
            # Only province
            prov_code = province.codes[0] if province.codes else None
            score = self._compute_score(None, None, province, tokens)
            
            return ParsedAddress(
                province=province.name,
                province_code=prov_code,
                confidence=score,
                valid=True
            )
    
    def _compute_score(
        self,
        ward: Optional[Candidate],
        district: Optional[Candidate],
        province: Optional[Candidate],
        tokens: List[str]
    ) -> float:
        """
        Compute confidence score for a valid combination
        
        Components:
        1. Hierarchical consistency (50%): All parts validated
        2. Positional order (30%): Ward < District < Province in text
        3. Completeness (20%): More components = higher score
        """
        score = 0.0
        
        # Component 1: Hierarchical consistency (always 100% if we reach here)
        score += 0.5
        
        # Component 2: Positional order
        positions = []
        if ward:
            positions.append(("ward", ward.start_token))
        if district:
            positions.append(("district", district.start_token))
        if province:
            positions.append(("province", province.start_token))
        
        # Sort by position
        positions.sort(key=lambda x: x[1])
        
        # Check if order is ward -> district -> province
        expected_order = ["ward", "district", "province"]
        actual_order = [p[0] for p in positions]
        
        # Count how many are in correct relative order
        if len(actual_order) >= 2:
            correct_pairs = 0
            total_pairs = len(actual_order) - 1
            
            for i in range(len(actual_order) - 1):
                type1 = actual_order[i]
                type2 = actual_order[i + 1]
                
                idx1 = expected_order.index(type1)
                idx2 = expected_order.index(type2)
                
                if idx1 < idx2:
                    correct_pairs += 1
            
            order_score = correct_pairs / total_pairs
            score += 0.3 * order_score
        else:
            score += 0.3  # Single entity, no order to check
        
        # Component 3: Completeness
        num_components = sum([ward is not None, district is not None, province is not None])
        completeness = num_components / 3.0
        score += 0.2 * completeness
        
        return score


# ========================================================================
# CONVENIENCE FUNCTIONS
# ========================================================================

def parse_address(text: str, db: AddressDatabase) -> Dict[str, Optional[str]]:
    """
    Simple interface for address parsing
    
    Args:
        text: Address text
        db: AddressDatabase instance
    
    Returns:
        Dict with province, district, ward keys
    """
    parser = AddressParser(db)
    result = parser.parse(text)
    
    return {
        "province": result.province,
        "district": result.district,
        "ward": result.ward,
        "confidence": result.confidence,
        "valid": result.valid
    }


# ========================================================================
# TESTING
# ========================================================================

if __name__ == "__main__":
    print("Loading database...")
    db = AddressDatabase()
    parser = AddressParser(db)
    
    # Test cases
    test_cases = [
        "Cau Dien, Nam Tu Liem, Ha Noi",
        "Phuong Cau Dien, Quan Nam Tu Liem, TP Ha Noi",
        "Nam Tu Liem, Ha Noi",
        "Ha Noi",
        "Tan Binh, HCM",
        "Quan 1, Saigon",
        "Invalid garbage text here",
        "Cau Dien",  # Just ward
        "ha noi nam tu liem cau dien",  # No separators
    ]
    
    print("\n" + "="*70)
    print("ADDRESS PARSING TESTS")
    print("="*70)
    
    for text in test_cases:
        print(f"\nInput: '{text}'")
        result = parser.parse(text, debug=False)
        
        print(f"  Province: {result.province}")
        print(f"  District: {result.district}")
        print(f"  Ward:     {result.ward}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Valid:    {result.valid}")
