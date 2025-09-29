#!/usr/bin/env python3
"""
Interactive CLI for Vietnamese Address Database

Features:
- Search provinces, districts, wards
- Validate addresses
- Browse hierarchy
- Statistics and debugging
"""

import sys
from typing import Optional
from address_database import AddressDatabase, AddressMatch
from archive.address_parser import AddressParser


class AddressCLI:
    """Interactive command-line interface for address database"""
    
    def __init__(self):
        print("Loading address database...")
        self.db = AddressDatabase()
        self.parser = AddressParser(self.db)
        self.running = True
        
    def run(self):
        """Main CLI loop"""
        self.print_welcome()
        
        while self.running:
            try:
                command = input("\n> ").strip().lower()
                
                if not command:
                    continue
                
                self.handle_command(command)
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except EOFError:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def print_welcome(self):
        """Print welcome message and help"""
        print("\n" + "="*70)
        print("Vietnamese Address Database - Interactive CLI")
        print("="*70)
        print("\nType 'help' to see available commands")
        print("Type 'quit' to exit")
    
    def handle_command(self, command: str):
        """Route commands to appropriate handlers"""
        
        if command in ['quit', 'exit', 'q']:
            self.running = False
            print("Goodbye!")
            return
        
        if command in ['help', 'h', '?']:
            self.show_help()
            return
        
        if command in ['stats', 'statistics']:
            self.show_stats()
            return
        
        if command.startswith('province ') or command.startswith('p '):
            query = command.split(maxsplit=1)[1]
            self.search_province(query)
            return
        
        if command.startswith('district ') or command.startswith('d '):
            query = command.split(maxsplit=1)[1]
            self.search_district(query)
            return
        
        if command.startswith('ward ') or command.startswith('w '):
            query = command.split(maxsplit=1)[1]
            self.search_ward(query)
            return
        
        if command.startswith('full ') or command.startswith('f '):
            query = command.split(maxsplit=1)[1]
            self.full_address(query)
            return
        
        if command.startswith('list ') or command.startswith('l '):
            query = command.split(maxsplit=1)[1]
            self.list_children(query)
            return
        
        if command.startswith('validate ') or command.startswith('v '):
            self.validate_address()
            return
        
        if command == 'interactive' or command == 'i':
            self.interactive_search()
            return
        
        if command.startswith('parse ') or command.startswith('extract '):
            query = command.split(maxsplit=1)[1]
            self.parse_address(query)
            return
        
        if command == 'test' or command == 'tests':
            self.run_tests()
            return
        
        print(f"Unknown command: '{command}'")
        print("Type 'help' to see available commands")
    
    def show_help(self):
        """Display help information"""
        print("\n" + "="*70)
        print("AVAILABLE COMMANDS")
        print("="*70)
        
        commands = [
            ("help, h, ?", "Show this help message"),
            ("quit, exit, q", "Exit the program"),
            ("stats", "Show database statistics"),
            ("", ""),
            ("SEARCH COMMANDS:", ""),
            ("province <name>", "Search for a province"),
            ("  Aliases: p <name>", "  Example: province ha noi"),
            ("", ""),
            ("district <name>", "Search for a district"),
            ("  Aliases: d <name>", "  Example: district tan binh"),
            ("", ""),
            ("ward <name>", "Search for a ward"),
            ("  Aliases: w <name>", "  Example: ward cau dien"),
            ("", ""),
            ("full <ward>", "Get full address for a ward"),
            ("  Aliases: f <ward>", "  Example: full cau dien"),
            ("", ""),
            ("BROWSING COMMANDS:", ""),
            ("list <province>", "List all districts in province"),
            ("  Aliases: l <province>", "  Example: list ha noi"),
            ("", ""),
            ("list <province> / <district>", "List all wards in district"),
            ("  Example: list ha noi / nam tu liem", ""),
            ("", ""),
            ("VALIDATION:", ""),
            ("validate", "Interactive address validation"),
            ("  Aliases: v", "  Prompts for ward, district, province"),
            ("", ""),
            ("INTERACTIVE MODE:", ""),
            ("interactive", "Step-by-step address builder"),
            ("  Aliases: i", "  Guided selection of province -> district -> ward"),
            ("", ""),
            ("PARSING:", ""),
            ("parse <text>", "Parse unstructured address text"),
            ("  Aliases: extract", "  Example: parse cau dien nam tu liem ha noi"),
            ("", ""),
            ("test", "Run parser test suite"),
            ("  Aliases: tests", "  Tests various address formats"),
        ]
        
        for cmd, desc in commands:
            if cmd:
                print(f"  {cmd:30} {desc}")
            else:
                print()
    
    def show_stats(self):
        """Display database statistics"""
        stats = self.db.get_stats()
        
        print("\n" + "="*70)
        print("DATABASE STATISTICS")
        print("="*70)
        
        print(f"\nTotal Entities:")
        print(f"  Provinces: {stats['provinces']}")
        print(f"  Districts: {stats['districts']}")
        print(f"  Wards: {stats['wards']}")
        print(f"  Total: {stats['provinces'] + stats['districts'] + stats['wards']}")
        
        print(f"\nDuplicates:")
        print(f"  District names appearing in multiple provinces: {stats['duplicate_district_names']}")
        print(f"  Ward names appearing in multiple districts: {stats['duplicate_ward_names']}")
        
        print(f"\nAliases:")
        print(f"  Province aliases: {stats['province_aliases']}")
    
    def search_province(self, query: str):
        """Search for a province"""
        result = self.db.lookup_province(query)
        
        if result:
            print(f"\nFound: {result}")
            
            # Show districts count
            districts = self.db.get_districts_in_province(result)
            print(f"Contains {len(districts)} districts")
            print("\nTip: Use 'list <province>' to see all districts")
        else:
            print(f"\nProvince not found: '{query}'")
            print("\nTip: Try without diacritics (e.g., 'ha noi' instead of 'Hà Nội')")
            print("      Or use aliases: 'tp hcm', 'saigon', 'hn'")
    
    def search_district(self, query: str):
        """Search for a district"""
        results = self.db.lookup_district(query)
        
        if not results:
            print(f"\nDistrict not found: '{query}'")
            return
        
        print(f"\nFound {len(results)} match(es):")
        
        for district_name in results:
            # Find which provinces contain this district
            matches = self.db.get_full_address(district_name)
            if matches:
                # Get unique provinces (district might have same name in different provinces)
                provinces = set()
                for match in matches:
                    if match.district == district_name:
                        provinces.add(match.province)
                
                if provinces:
                    print(f"  - {district_name} in {', '.join(provinces)}")
                else:
                    print(f"  - {district_name}")
    
    def search_ward(self, query: str):
        """Search for a ward"""
        results = self.db.lookup_ward(query)
        
        if not results:
            print(f"\nWard not found: '{query}'")
            return
        
        print(f"\nFound {len(results)} match(es):")
        
        # Get full addresses for each match
        seen = set()
        for ward_name in results:
            matches = self.db.get_full_address(ward_name)
            for match in matches:
                key = (match.ward, match.district, match.province)
                if key not in seen:
                    print(f"  - {match.ward}, {match.district}, {match.province}")
                    seen.add(key)
    
    def full_address(self, query: str):
        """Get full address for a ward"""
        matches = self.db.get_full_address(query)
        
        if not matches:
            print(f"\nWard not found: '{query}'")
            return
        
        print(f"\nFound {len(matches)} location(s):")
        print()
        
        for i, match in enumerate(matches, 1):
            print(f"Location {i}:")
            print(f"  Ward:     {match.ward}")
            print(f"  District: {match.district}")
            print(f"  Province: {match.province}")
            print(f"  Codes:    {match.ward_code} / {match.district_code} / {match.province_code}")
            print()
    
    def list_children(self, query: str):
        """List districts in province or wards in district"""
        
        if '/' in query:
            # Format: "ha noi / nam tu liem"
            parts = [p.strip() for p in query.split('/')]
            if len(parts) != 2:
                print("\nInvalid format. Use: list <province> / <district>")
                return
            
            province_query, district_query = parts
            
            # Lookup province
            province = self.db.lookup_province(province_query)
            if not province:
                print(f"\nProvince not found: '{province_query}'")
                return
            
            # Lookup district
            districts = self.db.lookup_district(district_query, province_context=province)
            if not districts:
                print(f"\nDistrict not found: '{district_query}' in {province}")
                return
            
            district = districts[0]
            
            # Get wards
            wards = self.db.get_wards_in_district(province, district)
            
            print(f"\n{district}, {province} has {len(wards)} wards:")
            for i, ward in enumerate(wards, 1):
                print(f"  {i:2d}. {ward}")
        
        else:
            # Format: "ha noi" (list districts)
            province = self.db.lookup_province(query)
            if not province:
                print(f"\nProvince not found: '{query}'")
                return
            
            districts = self.db.get_districts_in_province(province)
            
            print(f"\n{province} has {len(districts)} districts:")
            for i, district in enumerate(districts, 1):
                print(f"  {i:2d}. {district}")
            
            print(f"\nTip: Use 'list {query} / <district>' to see wards in a district")
    
    def validate_address(self):
        """Interactive address validation"""
        print("\nAddress Validation")
        print("-" * 50)
        
        ward = input("Ward: ").strip()
        district = input("District: ").strip()
        province = input("Province: ").strip()
        
        if not (ward and district and province):
            print("\nAll fields required!")
            return
        
        print("\nValidating...")
        
        # Lookup each component
        prov_result = self.db.lookup_province(province)
        if not prov_result:
            print(f"  Province '{province}' not found")
            return
        
        dist_results = self.db.lookup_district(district, province_context=prov_result)
        if not dist_results:
            print(f"  District '{district}' not found in {prov_result}")
            return
        
        ward_results = self.db.lookup_ward(ward, district_context=dist_results[0])
        if not ward_results:
            print(f"  Ward '{ward}' not found in {dist_results[0]}")
            return
        
        # Validate hierarchy
        valid = self.db.validate_hierarchy(ward_results[0], dist_results[0], prov_result)
        
        print("\nResult:")
        if valid:
            print("  Status: VALID")
            print(f"  Official: {ward_results[0]}, {dist_results[0]}, {prov_result}")
        else:
            print("  Status: INVALID")
            print(f"  The ward '{ward_results[0]}' does not exist in")
            print(f"  {dist_results[0]}, {prov_result}")
    
    def interactive_search(self):
        """Interactive step-by-step address builder"""
        print("\nInteractive Address Builder")
        print("="*70)
        
        # Step 1: Select province
        print("\nStep 1: Select Province")
        print("-" * 50)
        province_query = input("Enter province name (or alias): ").strip()
        
        province = self.db.lookup_province(province_query)
        if not province:
            print(f"Province not found: '{province_query}'")
            return
        
        print(f"Selected: {province}")
        
        # Step 2: Select district
        districts = self.db.get_districts_in_province(province)
        print(f"\nStep 2: Select District ({len(districts)} available)")
        print("-" * 50)
        
        # Show first 10 districts
        print("First 10 districts:")
        for i, dist in enumerate(districts[:10], 1):
            print(f"  {i:2d}. {dist}")
        
        if len(districts) > 10:
            print(f"  ... and {len(districts) - 10} more")
        
        district_query = input("\nEnter district name: ").strip()
        
        matched_districts = self.db.lookup_district(district_query, province_context=province)
        if not matched_districts:
            print(f"District not found: '{district_query}' in {province}")
            return
        
        district = matched_districts[0]
        print(f"Selected: {district}")
        
        # Step 3: Select ward
        wards = self.db.get_wards_in_district(province, district)
        print(f"\nStep 3: Select Ward ({len(wards)} available)")
        print("-" * 50)
        
        # Show first 10 wards
        print("First 10 wards:")
        for i, w in enumerate(wards[:10], 1):
            print(f"  {i:2d}. {w}")
        
        if len(wards) > 10:
            print(f"  ... and {len(wards) - 10} more")
        
        ward_query = input("\nEnter ward name: ").strip()
        
        matched_wards = self.db.lookup_ward(ward_query, district_context=district)
        if not matched_wards:
            print(f"Ward not found: '{ward_query}' in {district}")
            return
        
        ward = matched_wards[0]
        
        # Final result
        print("\n" + "="*70)
        print("COMPLETE ADDRESS")
        print("="*70)
        print(f"\nWard:     {ward}")
        print(f"District: {district}")
        print(f"Province: {province}")
        
        # Get codes
        matches = self.db.get_full_address(ward)
        for match in matches:
            if match.district == district and match.province == province:
                print(f"\nCodes:")
                print(f"  Ward:     {match.ward_code}")
                print(f"  District: {match.district_code}")
                print(f"  Province: {match.province_code}")
                break
    
    def parse_address(self, text: str):
        """Parse unstructured address text"""
        print(f"\nParsing: '{text}'")
        print("-" * 70)
        
        result = self.parser.parse(text, debug=False)
        
        if result.province or result.district or result.ward:
            print("\n✓ Extracted Components:")
            if result.ward:
                print(f"  Ward:     {result.ward}")
            if result.district:
                print(f"  District: {result.district}")
            if result.province:
                print(f"  Province: {result.province}")
            
            print(f"\n  Confidence: {result.confidence:.2%}")
            print(f"  Valid:      {'Yes' if result.valid else 'No'}")
            
            if result.valid and result.ward and result.district and result.province:
                print(f"\n  Codes:")
                if result.ward_code:
                    print(f"    Ward:     {result.ward_code}")
                if result.district_code:
                    print(f"    District: {result.district_code}")
                if result.province_code:
                    print(f"    Province: {result.province_code}")
        else:
            print("\n✗ No address components found")
            print("  Tip: Make sure the text contains Vietnamese administrative names")
    
    def run_tests(self):
        """Run comprehensive parser tests"""
        test_cases = [
            ("Cau Dien, Nam Tu Liem, Ha Noi", "Full address"),
            ("Nam Tu Liem, Ha Noi", "Partial"),
            ("Ha Noi", "Province only"),
            ("Cau Dien", "Ward auto-resolve"),
            ("Tan Binh, tp hcm", "With alias"),
            ("Invalid text", "No match"),
        ]
        
        print("\n" + "="*70)
        print("ADDRESS PARSER TESTS")
        print("="*70)
        
        for i, (text, desc) in enumerate(test_cases, 1):
            print(f"\nTest {i}: {desc}")
            print(f"Input: '{text}'")
            result = self.parser.parse(text)
            parts = [p for p in [result.ward, result.district, result.province] if p]
            if parts:
                print(f"Result: {', '.join(parts)} ({result.confidence:.0%})")
            else:
                print("Result: No match")


def main():
    """Entry point"""
    try:
        cli = AddressCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
