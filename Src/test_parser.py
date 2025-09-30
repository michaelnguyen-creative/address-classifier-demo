"""
Test Parser Against Public Test Set
"""

import json
import time
import statistics
from pathlib import Path
from address_parser import AddressParser
from typing import Dict, List, Optional


class PerformanceMonitor:
    """Track and analyze performance metrics"""
    
    def __init__(self, requirements: Optional[Dict] = None):
        self.parse_times = []  # Individual parse latencies
        self.init_time = None   # Initialization duration
        self.total_time = None  # Total test suite duration
        
        # Default performance requirements (can be overridden)
        self.requirements = requirements or {
            'max_mean_ms': 10.0,      # Average parse time
            'max_p95_ms': 50.0,       # 95th percentile
            'max_p99_ms': 100.0,      # 99th percentile
            'min_throughput': 100.0,  # Addresses per second
        }
    
    def record_parse(self, duration: float):
        """Record a single parse operation time"""
        self.parse_times.append(duration)
    
    def compute_statistics(self) -> Dict:
        """Compute performance statistics"""
        if not self.parse_times:
            return {}
        
        sorted_times = sorted(self.parse_times)
        n = len(sorted_times)
        
        return {
            'count': n,
            'total_parse_time': sum(sorted_times),
            'mean': statistics.mean(sorted_times),
            'median': statistics.median(sorted_times),
            'min': min(sorted_times),
            'max': max(sorted_times),
            'stdev': statistics.stdev(sorted_times) if n > 1 else 0,
            'p95': sorted_times[int(n * 0.95)] if n > 0 else 0,
            'p99': sorted_times[int(n * 0.99)] if n > 0 else 0,
        }
    
    def throughput(self) -> float:
        """Calculate addresses per second"""
        if not self.parse_times or not self.total_time:
            return 0
        return len(self.parse_times) / self.total_time
    
    def check_requirements(self, stats: Dict) -> Dict:
        """Check if performance meets requirements"""
        checks = {
            'mean': (stats['mean'] * 1000, self.requirements['max_mean_ms'], 
                    stats['mean'] * 1000 <= self.requirements['max_mean_ms']),
            'p95': (stats['p95'] * 1000, self.requirements['max_p95_ms'],
                   stats['p95'] * 1000 <= self.requirements['max_p95_ms']),
            'p99': (stats['p99'] * 1000, self.requirements['max_p99_ms'],
                   stats['p99'] * 1000 <= self.requirements['max_p99_ms']),
            'throughput': (self.throughput(), self.requirements['min_throughput'],
                          self.throughput() >= self.requirements['min_throughput']),
        }
        return checks


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
    
    # Initialize performance monitor
    perf = PerformanceMonitor()
    
    # Load test data
    print(f"\nLoading test data from: {test_file}")
    test_cases = load_test_data(test_file)
    print(f"Loaded {len(test_cases)} test cases")
    
    # Initialize parser with timing
    print("\nInitializing parser...")
    init_start = time.perf_counter()
    parser = AddressParser(data_dir=data_dir)
    init_end = time.perf_counter()
    perf.init_time = init_end - init_start
    print(f"Initialization took: {perf.init_time:.3f} seconds")
    
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
        'failures': [],
        'slow_cases': []  # Track slowest parses
    }
    
    # Start total timing
    total_start = time.perf_counter()
    
    for i, test_case in enumerate(test_cases, 1):
        input_text = test_case['text']
        expected = test_case['result']
        
        # Parse with timing
        parse_start = time.perf_counter()
        parsed = parser.parse(input_text, debug=False)
        parse_end = time.perf_counter()
        parse_duration = parse_end - parse_start
        perf.record_parse(parse_duration)
        
        # Track slow cases (top 10)
        results['slow_cases'].append((parse_duration, i, input_text))
        results['slow_cases'].sort(reverse=True)
        results['slow_cases'] = results['slow_cases'][:10]
        
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
    
    # End total timing
    total_end = time.perf_counter()
    perf.total_time = total_end - total_start
    
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
    
    # Performance report
    stats = perf.compute_statistics()
    print(f"\n" + "="*70)
    print("PERFORMANCE METRICS")
    print("="*70)
    print(f"\nInitialization Time: {perf.init_time:.3f}s")
    print(f"Total Test Time:     {perf.total_time:.3f}s")
    print(f"Pure Parse Time:     {stats['total_parse_time']:.3f}s")
    print(f"\nThroughput:          {perf.throughput():.2f} addresses/sec")
    print(f"\nPer-Address Latency (milliseconds):")
    print(f"  Mean:   {stats['mean']*1000:7.3f} ms")
    print(f"  Median: {stats['median']*1000:7.3f} ms")
    print(f"  StdDev: {stats['stdev']*1000:7.3f} ms")
    print(f"  Min:    {stats['min']*1000:7.3f} ms")
    print(f"  Max:    {stats['max']*1000:7.3f} ms")
    print(f"  P95:    {stats['p95']*1000:7.3f} ms")
    print(f"  P99:    {stats['p99']*1000:7.3f} ms")
    
    # Performance requirements check
    checks = perf.check_requirements(stats)
    print(f"\n" + "="*70)
    print("PERFORMANCE REQUIREMENTS CHECK")
    print("="*70)
    all_passed = True
    for metric, (actual, threshold, passed) in checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        all_passed = all_passed and passed
        
        if metric == 'throughput':
            print(f"  {metric.upper():12s}: {actual:7.2f} >= {threshold:7.2f}  {status}")
        else:
            print(f"  {metric.upper():12s}: {actual:7.3f} <= {threshold:7.2f}  {status}")
    
    print(f"\nOverall: {'✓ ALL REQUIREMENTS MET' if all_passed else '✗ SOME REQUIREMENTS FAILED'}")
    
    # Show slowest cases
    if results['slow_cases']:
        print(f"\n" + "="*70)
        print("SLOWEST TEST CASES (Top 10)")
        print("="*70)
        for duration, idx, text in results['slow_cases']:
            print(f"\n[{idx}] {duration*1000:.3f} ms")
            print(f"  {text[:100]}{'...' if len(text) > 100 else ''}")
    
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