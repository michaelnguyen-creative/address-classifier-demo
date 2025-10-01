"""
Edit Distance Matcher for Vietnamese Addresses (Tier 3)
========================================================

Purpose: Handle typos and OCR errors that exact match (Tier 1) and 
         LCS alignment (Tier 2) cannot handle.

Algorithm: Bounded Edit Distance (Ukkonen's algorithm)
- Computes minimum edit operations (insert/delete/substitute)
- Early termination when distance exceeds threshold
- Diagonal band optimization for O(k×m) time complexity

Use Cases:
- "ha nol" → "ha noi" (typo: l↔i)
- "nam tu leam" → "nam tu liem" (typo: a↔i)
- "dihn cong" → "dinh cong" (transposition)
- "cauv dien" → "cau dien" (extra character)

Time Complexity: O(k × m) per candidate where k=threshold, m=length
Space Complexity: O(m) - two rows only
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass


# ========================================================================
# CORE ALGORITHM: BOUNDED EDIT DISTANCE
# ========================================================================

def bounded_edit_distance(s: str, t: str, max_k: int = 2) -> int:
    """
    Compute edit distance with early termination if distance > max_k
    
    Algorithm: Ukkonen's bounded edit distance (diagonal band DP)
    
    Key Optimizations:
    1. Length-based pruning: Skip if |len(s) - len(t)| > k
    2. Diagonal band: Only compute cells where |i-j| ≤ k
    3. Early termination: Stop if min(row) > k
    4. Space optimization: Only keep 2 rows instead of full table
    
    Time: O(k × min(n, m)) where n=len(s), m=len(t), k=max_k
    Space: O(m) - only two rows
    
    Args:
        s: Source string
        t: Target string
        max_k: Maximum distance threshold
    
    Returns:
        Edit distance if ≤ max_k, otherwise max_k+1
    
    Examples:
        >>> bounded_edit_distance("ha nol", "ha noi", 2)
        1
        >>> bounded_edit_distance("cat", "bat", 2)
        1
        >>> bounded_edit_distance("random", "ha noi", 2)
        3  # Exceeds threshold
    
    DP Recurrence:
        if s[i] == t[j]:
            dp[i][j] = dp[i-1][j-1]
        else:
            dp[i][j] = 1 + min(
                dp[i-1][j-1],  # substitute
                dp[i-1][j],    # delete from s
                dp[i][j-1]     # insert into s
            )
    """
    n, m = len(s), len(t)
    
    # ========================================
    # OPTIMIZATION 1: Length-based pruning
    # ========================================
    # If lengths differ by more than k, distance must exceed k
    # Reasoning: Need at least |n-m| insertions or deletions
    if abs(n - m) > max_k:
        return max_k + 1
    
    # ========================================
    # OPTIMIZATION 2: Space optimization
    # ========================================
    # Only keep two rows: previous and current
    # Each cell dp[i][j] only depends on:
    # - dp[i-1][j-1], dp[i-1][j] (previous row)
    # - dp[i][j-1] (current row, left cell)
    
    # Initialize first row: distance from empty string to t[0:j]
    # prev[j] = j for j in [0, min(m, max_k)]
    prev = list(range(min(m, max_k) + 1))
    
    # Pad with max_k+1 for indices beyond band width
    if m > max_k:
        prev.extend([max_k + 1] * (m - max_k))
    
    curr = [0] * (m + 1)
    
    # ========================================
    # MAIN DP LOOP
    # ========================================
    for i in range(1, n + 1):
        # Base case: distance from s[0:i] to empty string
        curr[0] = i
        
        # ========================================
        # OPTIMIZATION 3: Diagonal band computation
        # ========================================
        # Only compute cells where |i - j| ≤ max_k
        # Cells outside this band have distance > k by triangle inequality
        start = max(1, i - max_k)
        end = min(m, i + max_k)
        
        min_in_row = float('inf')  # Track minimum for early termination
        
        for j in range(start, end + 1):
            if s[i-1] == t[j-1]:
                # Characters match - no edit needed
                curr[j] = prev[j-1]
            else:
                # Characters differ - pick cheapest operation
                substitute = prev[j-1] if j > 0 else float('inf')
                delete = prev[j] if j <= m else float('inf')
                insert = curr[j-1] if j > 0 else float('inf')
                
                curr[j] = 1 + min(substitute, delete, insert)
            
            # Track minimum value in this row
            min_in_row = min(min_in_row, curr[j])
        
        # ========================================
        # OPTIMIZATION 4: Early termination
        # ========================================
        # If all cells in current row exceed threshold, we can stop
        # Future rows will only have equal or larger values
        if min_in_row > max_k:
            return max_k + 1
        
        # Swap rows for next iteration
        prev, curr = curr, prev
    
    return prev[m]


# ========================================================================
# MATCHER CLASS
# ========================================================================

@dataclass
class EditDistanceMatch:
    """
    Result from edit distance matching
    
    Attributes:
        entity_name: Official name of matched entity
        entity_type: "province", "district", or "ward"
        edit_distance: Number of edits needed (lower is better)
        normalized_score: Similarity score in [0, 1] (higher is better)
    """
    entity_name: str
    entity_type: str
    edit_distance: int
    normalized_score: float


class EditDistanceMatcher:
    """
    Fuzzy matching using bounded edit distance (Tier 3)
    
    Strategy:
    1. For each candidate, compute edit distance to input
    2. Keep matches where distance ≤ max_distance
    3. Return best match (minimum distance)
    4. Break ties by preferring shorter candidates
    
    Time Complexity: O(num_candidates × k × m)
        where k = max_distance, m = average candidate length
    
    Example Usage:
        matcher = EditDistanceMatcher(max_distance=2)
        
        candidates = [
            ("Hà Nội", ["ha", "noi"]),
            ("Hà Nam", ["ha", "nam"])
        ]
        
        match = matcher.find_best_match(
            ["ha", "nol"],  # Input with typo
            candidates,
            "province"
        )
        
        print(match.entity_name)  # "Hà Nội"
        print(match.edit_distance)  # 1
    """
    
    def __init__(self, max_distance: int = 2):
        """
        Initialize edit distance matcher
        
        Args:
            max_distance: Maximum acceptable edit distance
                         Typical values: 1-2 for short addresses
        """
        self.max_distance = max_distance
    
    def find_best_match(self,
                       input_tokens: List[str],
                       candidates: List[Tuple[str, List[str]]],
                       entity_type: str) -> Optional[EditDistanceMatch]:
        """
        Find best matching candidate using edit distance
        
        Args:
            input_tokens: Tokens from user input (normalized)
            candidates: List of (entity_name, entity_tokens) tuples
            entity_type: "province", "district", or "ward"
        
        Returns:
            Best EditDistanceMatch if distance ≤ max_distance, else None
        
        Strategy:
        - Join tokens into single string for comparison
        - This handles tokenization errors better than token-by-token
        - Example: "hano i" vs "ha noi" → detects space error
        
        Time: O(num_candidates × k × m)
        """
        best_match = None
        best_distance = float('inf')
        
        # Join input tokens into single phrase
        input_phrase = " ".join(input_tokens)
        
        for entity_name, entity_tokens in candidates:
            # Join candidate tokens
            candidate_phrase = " ".join(entity_tokens)
            
            # Compute edit distance
            distance = bounded_edit_distance(
                input_phrase,
                candidate_phrase,
                self.max_distance
            )
            
            # Check if this is the best match so far
            if distance <= self.max_distance and distance < best_distance:
                best_distance = distance
                
                # Compute normalized similarity score
                max_len = max(len(input_phrase), len(candidate_phrase))
                normalized_score = 1.0 - (distance / max_len) if max_len > 0 else 0.0
                
                best_match = EditDistanceMatch(
                    entity_name=entity_name,
                    entity_type=entity_type,
                    edit_distance=distance,
                    normalized_score=normalized_score
                )
        
        return best_match


# ========================================================================
# TESTING
# ========================================================================

if __name__ == "__main__":
    print("="*70)
    print("EDIT DISTANCE MATCHER - BASIC TESTS")
    print("="*70)
    
    # Test 1: Basic edit distance
    print("\n[TEST 1] Bounded Edit Distance")
    print("-" * 50)
    
    test_cases = [
        ("cat", "bat", 2, 1),
        ("ha noi", "ha nol", 2, 1),
        ("test", "test", 2, 0),
        ("abc", "xyz", 2, 3),
    ]
    
    for s, t, max_k, expected in test_cases:
        result = bounded_edit_distance(s, t, max_k)
        status = "✓" if result == expected else "✗"
        print(f"  {status} edit('{s}', '{t}', k={max_k}) = {result} (expected {expected})")
    
    # Test 2: Matcher class
    print("\n[TEST 2] EditDistanceMatcher")
    print("-" * 50)
    
    matcher = EditDistanceMatcher(max_distance=2)
    
    candidates = [
        ("Hà Nội", ["ha", "noi"]),
        ("Hà Nam", ["ha", "nam"]),
        ("Hải Phòng", ["hai", "phong"])
    ]
    
    # Test with typo
    input_tokens = ["ha", "nol"]
    match = matcher.find_best_match(input_tokens, candidates, "province")
    
    if match:
        print(f"  Input: {input_tokens}")
        print(f"  Best match: {match.entity_name}")
        print(f"  Edit distance: {match.edit_distance}")
        print(f"  Score: {match.normalized_score:.3f}")
        print(f"  Status: {'✓ PASS' if match.entity_name == 'Hà Nội' else '✗ FAIL'}")
    else:
        print(f"  Status: ✗ FAIL (no match found)")
    
    print("\n" + "="*70)
    print("Basic tests complete! Run test_edit_distance.py for comprehensive tests.")
    print("="*70)
