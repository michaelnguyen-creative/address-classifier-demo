"""
Vietnamese Address Database - Optimized Hierarchical Lookup System

Key Improvements:
- O(1) lookups for all operations (was O(n) for many queries)
- Memory-efficient duplicate handling with context
- Comprehensive bidirectional indexing
- Full ward-to-province traversal support
"""

import json
import unicodedata
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class AddressMatch:
    """Represents a matched administrative entity with full context"""
    ward: Optional[str] = None
    district: Optional[str] = None
    province: Optional[str] = None
    ward_code: Optional[str] = None
    district_code: Optional[str] = None
    province_code: Optional[str] = None


class AddressDatabase:
    """
    Optimized Vietnamese address database with O(1) lookups
    
    Structure:
        Provinces (63) → Districts (696) → Wards (10,047)
    
    Performance Guarantees:
        - All name lookups: O(1) average case
        - Hierarchy traversal: O(1) per level
        - Memory: O(P + D + W) with minimal duplication
    """
    
    def __init__(self, data_dir: str = "../Data"):
        """Initialize and build optimized indexes"""
        
        # === Raw Data Storage ===
        self.provinces: List[dict] = []
        self.districts: List[dict] = []
        self.wards: List[dict] = []
        
        # === Normalized Name → Original Name(s) ===
        self.province_map: Dict[str, str] = {}
        self.district_map: Dict[str, str | List[Tuple[str, str]]] = {}  # name or [(name, prov_code)]
        self.ward_map: Dict[str, str | List[Tuple[str, str]]] = {}      # name or [(name, dist_code)]
        
        # === Bidirectional Code Lookups (O(1)) ===
        self.province_by_code: Dict[str, dict] = {}
        self.district_by_code: Dict[str, dict] = {}
        self.ward_by_code: Dict[str, dict] = {}
        
        # === NEW: Name → Code Reverse Lookups ===
        self.province_name_to_code: Dict[str, str] = {}
        self.district_name_to_codes: Dict[str, List[str]] = {}  # Can have duplicates
        self.ward_name_to_codes: Dict[str, List[str]] = {}      # Can have duplicates
        
        # === Hierarchy (Parent → Children) ===
        self.hierarchy: Dict[str, Dict[str, List[str]]] = {}  # prov → {dist → [ward_names]}
        
        # === Reverse Hierarchy (Child → Parent) ===
        self.district_to_province: Dict[str, str] = {}
        self.ward_to_district: Dict[str, str] = {}
        
        # === Aliases ===
        self.province_aliases: Dict[str, str] = {}
        
        # === Build Everything ===
        self._load_json_files(data_dir)
        self._build_code_lookups()
        self._build_name_lookups()
        self._build_hierarchy()
        self._add_aliases()
        
        print(f"✅ Database initialized")
        print(f"   {len(self.provinces)} provinces, {len(self.districts)} districts, {len(self.wards)} wards")
    
    # ========================================================================
    # CORE INDEXING - All O(P + D + W) one-time cost
    # ========================================================================
    
    def _load_json_files(self, data_dir: str):
        """Load JSON files - O(P + D + W)"""
        base_path = Path(data_dir)
        
        with open(base_path / "Provinces.json", encoding="utf-8") as f:
            self.provinces = json.load(f)
        
        with open(base_path / "Districts.json", encoding="utf-8") as f:
            self.districts = json.load(f)
        
        with open(base_path / "Wards.json", encoding="utf-8") as f:
            self.wards = json.load(f)
    
    def _normalize(self, text: str) -> str:
        """
        Normalize Vietnamese text - O(n)
        
        Removes diacritics, lowercases, cleans whitespace
        """
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        return ' '.join(text.lower().split())
    
    def _build_code_lookups(self):
        """Build code-based indexes - O(P + D + W)"""
        
        for prov in self.provinces:
            self.province_by_code[prov["Code"]] = prov
            self.province_name_to_code[prov["Name"]] = prov["Code"]
        
        for dist in self.districts:
            self.district_by_code[dist["Code"]] = dist
            self.district_to_province[dist["Code"]] = dist["ProvinceCode"]
            
            # Handle duplicate district names
            if dist["Name"] not in self.district_name_to_codes:
                self.district_name_to_codes[dist["Name"]] = []
            self.district_name_to_codes[dist["Name"]].append(dist["Code"])
        
        for ward in self.wards:
            self.ward_by_code[ward["Code"]] = ward
            self.ward_to_district[ward["Code"]] = ward["DistrictCode"]
            
            # Handle duplicate ward names
            if ward["Name"] not in self.ward_name_to_codes:
                self.ward_name_to_codes[ward["Name"]] = []
            self.ward_name_to_codes[ward["Name"]].append(ward["Code"])
    
    def _build_name_lookups(self):
        """Build normalized name indexes - O(P + D + W)"""
        
        # Provinces (always unique)
        for prov in self.provinces:
            normalized = self._normalize(prov["Name"])
            self.province_map[normalized] = prov["Name"]
        
        # Districts (store with province context for duplicates)
        for dist in self.districts:
            normalized = self._normalize(dist["Name"])
            
            if normalized not in self.district_map:
                # First occurrence - store as string
                self.district_map[normalized] = dist["Name"]
            else:
                # Duplicate detected - upgrade to list with context
                if isinstance(self.district_map[normalized], str):
                    # Convert first entry
                    first_name = self.district_map[normalized]
                    first_code = self.district_name_to_codes[first_name][0]
                    first_prov = self.district_to_province[first_code]
                    self.district_map[normalized] = [(first_name, first_prov)]
                
                # Add new entry with context
                self.district_map[normalized].append((dist["Name"], dist["ProvinceCode"]))
        
        # Wards (store with district context for duplicates)
        for ward in self.wards:
            normalized = self._normalize(ward["Name"])
            
            if normalized not in self.ward_map:
                self.ward_map[normalized] = ward["Name"]
            else:
                if isinstance(self.ward_map[normalized], str):
                    first_name = self.ward_map[normalized]
                    first_code = self.ward_name_to_codes[first_name][0]
                    first_dist = self.ward_to_district[first_code]
                    self.ward_map[normalized] = [(first_name, first_dist)]
                
                self.ward_map[normalized].append((ward["Name"], ward["DistrictCode"]))
    
    def _build_hierarchy(self):
        """Build parent-child relationships - O(P + D + W)"""
        
        # Initialize province containers
        for prov in self.provinces:
            self.hierarchy[prov["Code"]] = {}
        
        # Add districts to provinces
        for dist in self.districts:
            prov_code = dist["ProvinceCode"]
            if prov_code in self.hierarchy:
                self.hierarchy[prov_code][dist["Code"]] = []
        
        # Add wards to districts
        for ward in self.wards:
            dist_code = ward["DistrictCode"]
            if dist_code in self.district_to_province:
                prov_code = self.district_to_province[dist_code]
                if prov_code in self.hierarchy and dist_code in self.hierarchy[prov_code]:
                    self.hierarchy[prov_code][dist_code].append(ward["Name"])
    
    def _add_aliases(self):
        """Add common province aliases"""
        
        hcm_variants = [
            "tp hcm", "tphcm", "tp. hcm", "tp.hcm",
            "tp ho chi minh", "thanh pho ho chi minh",
            "sai gon", "saigon", "sg", "hcmc"
        ]
        for variant in hcm_variants:
            self.province_aliases[self._normalize(variant)] = "Hồ Chí Minh"
        
        hanoi_variants = ["ha noi", "hn", "thanh pho ha noi", "hanoi"]
        for variant in hanoi_variants:
            self.province_aliases[self._normalize(variant)] = "Hà Nội"
        
        self.province_aliases.update({
            "da nang": "Đà Nẵng",
            "can tho": "Cần Thơ",
            "hai phong": "Hải Phòng",
        })
    
    # ========================================================================
    # PUBLIC API - All O(1) lookups
    # ========================================================================
    
    def lookup_province(self, query: str) -> Optional[str]:
        """
        Lookup province by name or alias - O(1)
        
        Args:
            query: Province name, alias, or normalized form
        
        Returns:
            Official province name, or None
        """
        normalized = self._normalize(query)
        
        # Check aliases first
        if normalized in self.province_aliases:
            return self.province_aliases[normalized]
        
        # Check normalized map
        return self.province_map.get(normalized)
    
    def lookup_district(self, query: str, province_context: Optional[str] = None) -> List[str]:
        """
        Lookup district by name - O(1)
        
        Args:
            query: District name
            province_context: Optional province to disambiguate
        
        Returns:
            List of matching district names (may be multiple if duplicates exist)
        """
        normalized = self._normalize(query)
        
        if normalized not in self.district_map:
            return []
        
        result = self.district_map[normalized]
        
        # Single match (no duplicates)
        if isinstance(result, str):
            return [result]
        
        # Multiple matches - filter by province if provided
        if province_context:
            prov_code = self.province_name_to_code.get(province_context)
            if prov_code:
                return [name for name, prov in result if prov == prov_code]
        
        # Return all matches
        return [name for name, _ in result]
    
    def lookup_ward(self, query: str, district_context: Optional[str] = None) -> List[str]:
        """
        Lookup ward by name - O(1)
        
        Args:
            query: Ward name
            district_context: Optional district to disambiguate
        
        Returns:
            List of matching ward names
        """
        normalized = self._normalize(query)
        
        if normalized not in self.ward_map:
            return []
        
        result = self.ward_map[normalized]
        
        if isinstance(result, str):
            return [result]
        
        # Filter by district if provided
        if district_context:
            dist_codes = self.district_name_to_codes.get(district_context, [])
            return [name for name, dist_code in result if dist_code in dist_codes]
        
        return [name for name, _ in result]
    
    def get_full_address(self, ward_name: str) -> List[AddressMatch]:
        """
        Get all possible full addresses for a ward - O(k) where k = matches
        
        Args:
            ward_name: Ward name to look up
        
        Returns:
            List of AddressMatch objects with full hierarchy
        """
        results = []
        
        # Get all ward codes for this name
        ward_codes = self.ward_name_to_codes.get(ward_name, [])
        
        for ward_code in ward_codes:
            ward_obj = self.ward_by_code[ward_code]
            dist_code = self.ward_to_district[ward_code]
            dist_obj = self.district_by_code[dist_code]
            prov_code = self.district_to_province[dist_code]
            prov_obj = self.province_by_code[prov_code]
            
            results.append(AddressMatch(
                ward=ward_obj["Name"],
                district=dist_obj["Name"],
                province=prov_obj["Name"],
                ward_code=ward_code,
                district_code=dist_code,
                province_code=prov_code
            ))
        
        return results
    
    def get_districts_in_province(self, province_name: str) -> List[str]:
        """Get all districts in a province - O(k) where k = num districts"""
        prov_code = self.province_name_to_code.get(province_name)
        if not prov_code or prov_code not in self.hierarchy:
            return []
        
        district_codes = self.hierarchy[prov_code].keys()
        return sorted([self.district_by_code[code]["Name"] for code in district_codes])
    
    def get_wards_in_district(self, province_name: str, district_name: str) -> List[str]:
        """Get all wards in a district - O(k) where k = num wards"""
        prov_code = self.province_name_to_code.get(province_name)
        if not prov_code:
            return []
        
        # Find district code in this province
        dist_codes = self.district_name_to_codes.get(district_name, [])
        dist_code = None
        for code in dist_codes:
            if self.district_to_province[code] == prov_code:
                dist_code = code
                break
        
        if not dist_code:
            return []
        
        if prov_code in self.hierarchy and dist_code in self.hierarchy[prov_code]:
            return sorted(self.hierarchy[prov_code][dist_code])
        
        return []
    
    def validate_hierarchy(self, ward: str, district: str, province: str) -> bool:
        """
        Check if ward belongs to district in province - O(1)
        
        Returns:
            True if hierarchy is valid
        """
        # Get codes
        prov_code = self.province_name_to_code.get(province)
        if not prov_code:
            return False
        
        # Find matching district in this province
        dist_codes = self.district_name_to_codes.get(district, [])
        dist_code = None
        for code in dist_codes:
            if self.district_to_province[code] == prov_code:
                dist_code = code
                break
        
        if not dist_code:
            return False
        
        # Check if ward exists in this district
        ward_codes = self.ward_name_to_codes.get(ward, [])
        for ward_code in ward_codes:
            if self.ward_to_district[ward_code] == dist_code:
                return True
        
        return False
    
    # ========================================================================
    # DEBUGGING & STATS
    # ========================================================================
    
    def get_stats(self) -> dict:
        """Get database statistics"""
        
        # Count duplicates
        dup_districts = sum(1 for v in self.district_map.values() if isinstance(v, list))
        dup_wards = sum(1 for v in self.ward_map.values() if isinstance(v, list))
        
        return {
            "provinces": len(self.provinces),
            "districts": len(self.districts),
            "wards": len(self.wards),
            "duplicate_district_names": dup_districts,
            "duplicate_ward_names": dup_wards,
            "province_aliases": len(self.province_aliases),
        }
    
    def debug_info(self):
        """Print comprehensive debug information"""
        stats = self.get_stats()
        
        print("\n" + "="*70)
        print("OPTIMIZED ADDRESS DATABASE")
        print("="*70)
        
        print(f"\n📊 Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print(f"\n🔍 Sample Lookups:")
        print(f"   Province 'ha noi' → {self.lookup_province('ha noi')}")
        print(f"   District 'tan binh' → {self.lookup_district('tan binh')}")
        
        print(f"\n🏙️ Sample Full Address:")
        matches = self.get_full_address("Cầu Diễn")
        if matches:
            match = matches[0]
            print(f"   {match.ward}, {match.district}, {match.province}")
        
        print("\n" + "="*70 + "\n")


# ========================================================================
# USAGE EXAMPLES
# ========================================================================

if __name__ == "__main__":
    db = AddressDatabase()
    
    db.debug_info()
    
    # Test O(1) lookups
    print("TEST: O(1) Province Lookup")
    print("-" * 50)
    for query in ["Hà Nội", "tp hcm", "saigon"]:
        result = db.lookup_province(query)
        print(f"  '{query}' → {result}")
    
    # Test full address resolution
    print("\nTEST: Full Address Resolution")
    print("-" * 50)
    ward = "Cầu Diễn"
    matches = db.get_full_address(ward)
    print(f"  Ward '{ward}' found in {len(matches)} location(s):")
    for match in matches:
        print(f"    → {match.ward}, {match.district}, {match.province}")
    
    # Test hierarchy validation
    print("\nTEST: Hierarchy Validation")
    print("-" * 50)
    test_cases = [
        ("Cầu Diễn", "Nam Từ Liêm", "Hà Nội", True),
        ("Cầu Diễn", "Tân Bình", "Hồ Chí Minh", False),
    ]
    for ward, district, province, expected in test_cases:
        valid = db.validate_hierarchy(ward, district, province)
        status = "✓" if valid == expected else "✗"
        print(f"  {status} {ward} in {district}, {province}: {valid}")
