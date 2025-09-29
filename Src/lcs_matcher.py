"""
LCS-Based Matcher for Vietnamese Addresses
===========================================

Purpose: Handle cases where exact trie matching fails due to:
- Extra words in input (street names, house numbers)
- Token reordering
- Missing punctuation/separators

Algorithm: Longest Common Subsequence (LCS) Dynamic Programming
Time Complexity: O(n × m) where n = input length, m = candidate length
Space Complexity: O(n × m) for DP table

From literature: "LCS provides optimal alignment of hierarchical address components"
"""

from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass


@dataclass
class LCSMatch:
    """Represents a match found via LCS alignment"""
    entity_name: str        # Official name of matched entity
    entity_type: str        # "province", "district", or "ward"
    similarity_score: float # 0.0 to 1.0
    lcs_length: int        # Length of longest common subsequence


class LCSMatcher:
    """
    Token-based LCS matching for address components
    
    Strategy:
    1. Compute LCS between input tokens and candidate tokens
    2. Score by: 2 * LCS_length / (len(input) + len(candidate))
    3. Return matches above threshold
    """
    
    def __init__(self, threshold: float = 0.4):
        """
        Initialize LCS matcher
        
        Args:
            threshold: Minimum similarity score to accept (0.0 to 1.0)
                      Default 0.4 balances precision vs recall
        """
        self.threshold = threshold
    
    # ========================================================================
    # CORE LCS ALGORITHM
    # ========================================================================
    
    def compute_lcs_length(self, seq1: List[str], seq2: List[str]) -> int:
        """
        Compute length of longest common subsequence
        
        Args:
            seq1: First sequence of tokens
            seq2: Second sequence of tokens
        
        Returns:
            Length of LCS
        
        Time: O(n × m)
        Space: O(n × m)
        
        Example:
            seq1 = ["ha", "noi", "nam", "tu", "liem"]
            seq2 = ["nam", "tu", "liem"]
            returns 3
        """
        n, m = len(seq1), len(seq2)
        
        # DP table: dp[i][j] = LCS length for seq1[0:i] and seq2[0:j]
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        
        # Fill table using recurrence relation
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if seq1[i-1] == seq2[j-1]:
                    # Match found - extend sequence
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    # No match - take max of skipping either token
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[n][m]
    
    def compute_lcs_similarity(self, input_tokens: List[str], 
                              candidate_tokens: List[str]) -> float:
        """
        Compute similarity score based on LCS
        
        Formula: 2 × LCS_length / (len(input) + len(candidate))
        
        Rationale:
        - Ranges from 0.0 (no common tokens) to 1.0 (identical)
        - Favors candidates with high overlap relative to their length
        - Factor of 2 normalizes to [0,1] range
        
        Args:
            input_tokens: Tokens from user input
            candidate_tokens: Tokens from candidate entity name
        
        Returns:
            Similarity score between 0.0 and 1.0
        
        Examples:
            input = ["cau", "dien", "ha", "noi"]
            candidate = ["cau", "dien"]
            → LCS = 2, score = 2×2/(4+2) = 0.67
            
            input = ["random", "words"]
            candidate = ["cau", "dien"]
            → LCS = 0, score = 0
        """
        if not input_tokens or not candidate_tokens:
            return 0.0
        
        lcs_len = self.compute_lcs_length(input_tokens, candidate_tokens)
        
        # Similarity formula
        total_len = len(input_tokens) + len(candidate_tokens)
        similarity = (2 * lcs_len) / total_len
        
        return similarity
    
    # ========================================================================
    # MATCHING INTERFACE
    # ========================================================================
    
    def find_best_match(self, 
                        input_tokens: List[str], 
                        candidates: List[Tuple[str, List[str]]],
                        entity_type: str) -> Optional[LCSMatch]:
        """
        Find best matching candidate using LCS
        
        Args:
            input_tokens: Tokens from user input
            candidates: List of (entity_name, entity_tokens) tuples
            entity_type: "province", "district", or "ward"
        
        Returns:
            Best LCSMatch if score >= threshold, None otherwise
        
        Time: O(k × n × m) where k = number of candidates
        
        Example:
            input_tokens = ["cau", "dien", "nam", "tu", "liem", "ha", "noi"]
            candidates = [
                ("Nam Từ Liêm", ["nam", "tu", "liem"]),
                ("Cầu Giấy", ["cau", "giay"])
            ]
            → Returns LCSMatch for "Nam Từ Liêm" (score ~0.67)
        """
        best_match = None
        best_score = 0.0
        
        for entity_name, entity_tokens in candidates:
            score = self.compute_lcs_similarity(input_tokens, entity_tokens)
            
            if score > best_score and score >= self.threshold:
                best_score = score
                lcs_len = self.compute_lcs_length(input_tokens, entity_tokens)
                
                best_match = LCSMatch(
                    entity_name=entity_name,
                    entity_type=entity_type,
                    similarity_score=score,
                    lcs_length=lcs_len
                )
        
        return best_match
    
    def find_all_matches(self,
                        input_tokens: List[str],
                        candidates_dict: Dict[str, List[Tuple[str, List[str]]]]) -> Dict[str, Optional[LCSMatch]]:
        """
        Find best matches across all entity types
        
        Args:
            input_tokens: Tokens from user input
            candidates_dict: Dict mapping entity_type → list of (name, tokens)
                           e.g., {"province": [...], "district": [...]}
        
        Returns:
            Dict mapping entity_type → best LCSMatch (or None)
        
        Example:
            input_tokens = ["cau", "dien", "nam", "tu", "liem", "ha", "noi"]
            candidates_dict = {
                "province": [("Hà Nội", ["ha", "noi"])],
                "district": [("Nam Từ Liêm", ["nam", "tu", "liem"])],
                "ward": [("Cầu Diễn", ["cau", "dien"])]
            }
            → Returns matches for all three levels
        """
        results = {}
        
        for entity_type, candidates in candidates_dict.items():
            best_match = self.find_best_match(
                input_tokens, 
                candidates, 
                entity_type
            )
            results[entity_type] = best_match
        
        return results


# ========================================================================
# HELPER FUNCTIONS
# ========================================================================

def prepare_candidate_tokens(entity_name: str, 
                            normalize_fn) -> List[str]:
    """
    Prepare candidate tokens from entity name
    
    Args:
        entity_name: Original entity name (e.g., "Nam Từ Liêm")
        normalize_fn: Function to normalize text
    
    Returns:
        List of normalized tokens
    """
    normalized = normalize_fn(entity_name)
    return normalized.split()


# ========================================================================
# TESTING & EXAMPLES
# ========================================================================

if __name__ == "__main__":
    print("="*70)
    print("LCS MATCHER - UNIT TESTS")
    print("="*70)
    
    matcher = LCSMatcher(threshold=0.4)
    
    # Test 1: Basic LCS computation
    print("\n[TEST 1] LCS Length Computation")
    print("-" * 50)
    
    seq1 = ["ha", "noi", "nam", "tu", "liem"]
    seq2 = ["nam", "tu", "liem"]
    lcs_len = matcher.compute_lcs_length(seq1, seq2)
    print(f"  seq1: {seq1}")
    print(f"  seq2: {seq2}")
    print(f"  LCS length: {lcs_len}")
    print(f"  Expected: 3")
    print(f"  Status: {'✓ PASS' if lcs_len == 3 else '✗ FAIL'}")
    
    # Test 2: Similarity score
    print("\n[TEST 2] Similarity Score Computation")
    print("-" * 50)
    
    input_tokens = ["cau", "dien", "ha", "noi"]
    candidate_tokens = ["cau", "dien"]
    score = matcher.compute_lcs_similarity(input_tokens, candidate_tokens)
    expected_score = 2 * 2 / (4 + 2)  # = 0.6667
    print(f"  input: {input_tokens}")
    print(f"  candidate: {candidate_tokens}")
    print(f"  Score: {score:.4f}")
    print(f"  Expected: {expected_score:.4f}")
    print(f"  Status: {'✓ PASS' if abs(score - expected_score) < 0.01 else '✗ FAIL'}")
    
    # Test 3: Find best match
    print("\n[TEST 3] Best Match Selection")
    print("-" * 50)
    
    input_tokens = ["cau", "dien", "nam", "tu", "liem", "ha", "noi"]
    candidates = [
        ("Nam Từ Liêm", ["nam", "tu", "liem"]),
        ("Cầu Giấy", ["cau", "giay"]),
        ("Hà Nội", ["ha", "noi"])
    ]
    
    best = matcher.find_best_match(input_tokens, candidates, "district")
    
    print(f"  Input: {input_tokens}")
    print(f"  Candidates: {[c[0] for c in candidates]}")
    
    if best:
        print(f"\n  Best Match:")
        print(f"    Name: {best.entity_name}")
        print(f"    Type: {best.entity_type}")
        print(f"    Score: {best.similarity_score:.4f}")
        print(f"    LCS Length: {best.lcs_length}")
        print(f"  Status: {'✓ PASS' if best.entity_name == 'Nam Từ Liêm' else '✗ FAIL'}")
    else:
        print(f"  Status: ✗ FAIL (no match found)")
    
    # Test 4: No match below threshold
    print("\n[TEST 4] Threshold Filtering")
    print("-" * 50)
    
    input_tokens = ["completely", "different", "words"]
    best = matcher.find_best_match(input_tokens, candidates, "district")
    
    print(f"  Input: {input_tokens}")
    print(f"  Candidates: {[c[0] for c in candidates]}")
    print(f"  Best Match: {best}")
    print(f"  Status: {'✓ PASS' if best is None else '✗ FAIL'}")
    
    print("\n" + "="*70)
    print("All tests complete!")
    print("="*70)
