"""
Test Parser Against Public Test Set
"""

import json
from pathlib import Path
from address_parser import AddressParser
from typing import Dict, List


def load_test_data(filepath: str) -> List[Dict]:
    """Load test cases from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def compare_results(expected: Dict, actual: Dict) -> Dict[str, bool]:
    """
    Compare expected vs actual results
    
    Returns:
        Dict with boolean flags for each component match
    """
    return {
        'province_match': expected.get('province') == actual.get('province'),
        'district_match': expected.get('district') == actual.get('district'),
        'ward_match': expected.get('ward') == actual.get('ward'),
        'full_match': (
            expected.get('province') == actual.get('province') and
            expected.get('district') == actual.get('district') and
            expected.get('ward') == actual.get('ward')
        )
    }


def run_tests(test_file: str, data_dir: str = "../Data"):
    """
    Run parser against test set and compute metrics
    
    Args:
        test_file: Path to public.json test file
        data_dir: Path to address database
    """
    print("="*70)
    print("PARSER VALIDATION AGAINST PUBLIC TEST SET")
    print("="*70)
    
    # Load test data
    print(f"\nLoading test data from: {test_file}")
    test_cases = load_test_data(test_file)
    print(f"Loaded {len(test_cases)} test cases")
    
    # Initialize parser
    print("\nInitializing parser...")
    parser = AddressParser(data_dir=data_dir)
    
    # Run tests
    print("\nRunning tests...\n")
    
    results = {
        'total': len(test_cases),
        'full_match': 0,
        'province_match': 0,
        'district_match': 0,
        'ward_match': 0,
        'province_only': 0,
        'province_district': 0,
        'failures': []
    }
    
    for i, test_case in enumerate(test_cases, 1):
        input_text = test_case['text']
        expected = test_case['result']
        
        # Parse
        parsed = parser.parse(input_text, debug=False)
        actual = {
            'province': parsed.province,
            'district': parsed.district,
            'ward': parsed.ward
        }
        
        # Compare
        comparison = compare_results(expected, actual)
        
        # Update metrics
        if comparison['full_match']:
            results['full_match'] += 1
        if comparison['province_match']:
            results['province_match'] += 1
        if comparison['district_match']:
            results['district_match'] += 1
        if comparison['ward_match']:
            results['ward_match'] += 1
        
        # Track partial matches
        if parsed.province and not parsed.district:
            results['province_only'] += 1
        elif parsed.province and parsed.district and not parsed.ward:
            results['province_district'] += 1
        
        # Track failures for analysis
        if not comparison['full_match']:
            results['failures'].append({
                'index': i,
                'input': input_text,
                'expected': expected,
                'actual': actual,
                'method': parsed.match_method,
                'confidence': parsed.confidence
            })
        
        # Progress indicator
        if i % 100 == 0:
            print(f"  Processed {i}/{len(test_cases)} cases...")
    
    # Print results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    total = results['total']
    print(f"\nTotal test cases: {total}")
    print(f"\nAccuracy Metrics:")
    print(f"  Full Match (P+D+W):  {results['full_match']:4d} / {total} "
          f"({results['full_match']/total*100:.2f}%)")
    print(f"  Province Correct:    {results['province_match']:4d} / {total} "
          f"({results['province_match']/total*100:.2f}%)")
    print(f"  District Correct:    {results['district_match']:4d} / {total} "
          f"({results['district_match']/total*100:.2f}%)")
    print(f"  Ward Correct:        {results['ward_match']:4d} / {total} "
          f"({results['ward_match']/total*100:.2f}%)")
    
    print(f"\nPartial Match Breakdown:")
    print(f"  Province only:       {results['province_only']:4d}")
    print(f"  Province + District: {results['province_district']:4d}")
    
    # Show first 10 failures
    if results['failures']:
        print(f"\n" + "="*70)
        print(f"SAMPLE FAILURES (first 10 of {len(results['failures'])})")
        print("="*70)
        
        for failure in results['failures'][:10]:
            print(f"\n[{failure['index']}] Input: {failure['input']}")
            print(f"  Expected: P={failure['expected'].get('province')}, "
                  f"D={failure['expected'].get('district')}, "
                  f"W={failure['expected'].get('ward')}")
            print(f"  Got:      P={failure['actual'].get('province')}, "
                  f"D={failure['actual'].get('district')}, "
                  f"W={failure['actual'].get('ward')}")
            print(f"  Method: {failure['method']}, Confidence: {failure['confidence']:.2f}")
    
    print("\n" + "="*70)
    
    return results


if __name__ == "__main__":
    # Adjust paths as needed
    test_file = "../Tests/public.json"  # Adjust to your path
    data_dir = "../Data"
    
    results = run_tests(test_file, data_dir)