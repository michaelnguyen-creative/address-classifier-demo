"""
Layer 1: Generic Text Normalization (Domain-Agnostic) - Version 2

DESIGN PRINCIPLES:
    1. Domain-agnostic: Works with any character mapping
    2. Single Responsibility: Only normalizes text
    3. No business logic: Doesn't know about prefixes, abbreviations, etc.
    4. Configurable: Support multiple normalization strategies

NEW FEATURES (v2):
    ✓ Unicode symbol removal (™, ®, ©, etc.)
    ✓ Smart punctuation: preserve ., comma, / by default
    ✓ Space-preserving dot removal in aggressive mode
    ✓ Configurable meaningful punctuation

USAGE:
    # Vietnamese normalization (preserve structure)
    normalizer = TextNormalizer(VIETNAMESE_CHAR_MAP)
    result = normalizer.normalize("TP.HCM")  # → "tp.hcm"
    
    # Aggressive mode (clean for matching)
    result = normalizer.normalize("TP.HCM", aggressive=True)  # → "tp hcm"
    
    # Custom normalization
    custom_map = {'ñ': 'n', 'ç': 'c'}
    normalizer = TextNormalizer(custom_map)
    result = normalizer.normalize("España")  # → "espana"
"""

import re
import string
import unicodedata
from typing import List, Dict, Optional, Set


# ========================================================================
# CONFIGURATION CONSTANTS
# ========================================================================

# Meaningful punctuation in Vietnamese addresses
# These preserve structure and should be kept in normal mode
MEANINGFUL_PUNCT = {'.', ',', '/'}


# ========================================================================
# VIETNAMESE CHARACTER MAPPING (Can be imported separately)
# ========================================================================

VIETNAMESE_CHAR_MAP = {
    # Lowercase vowels with tones
    'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
    'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
    'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    'đ': 'd',
    'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
    'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
    'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
    'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
    'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
    'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
    'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    # Uppercase
    'À': 'a', 'Á': 'a', 'Ả': 'a', 'Ã': 'a', 'Ạ': 'a',
    'Ă': 'a', 'Ằ': 'a', 'Ắ': 'a', 'Ẳ': 'a', 'Ẵ': 'a', 'Ặ': 'a',
    'Â': 'a', 'Ầ': 'a', 'Ấ': 'a', 'Ẩ': 'a', 'Ẫ': 'a', 'Ậ': 'a',
    'Đ': 'd',
    'È': 'e', 'É': 'e', 'Ẻ': 'e', 'Ẽ': 'e', 'Ẹ': 'e',
    'Ê': 'e', 'Ề': 'e', 'Ế': 'e', 'Ể': 'e', 'Ễ': 'e', 'Ệ': 'e',
    'Ì': 'i', 'Í': 'i', 'Ỉ': 'i', 'Ĩ': 'i', 'Ị': 'i',
    'Ò': 'o', 'Ó': 'o', 'Ỏ': 'o', 'Õ': 'o', 'Ọ': 'o',
    'Ô': 'o', 'Ồ': 'o', 'Ố': 'o', 'Ổ': 'o', 'Ỗ': 'o', 'Ộ': 'o',
    'Ơ': 'o', 'Ờ': 'o', 'Ớ': 'o', 'Ở': 'o', 'Ỡ': 'o', 'Ợ': 'o',
    'Ù': 'u', 'Ú': 'u', 'Ủ': 'u', 'Ũ': 'u', 'Ụ': 'u',
    'Ư': 'u', 'Ừ': 'u', 'Ứ': 'u', 'Ử': 'u', 'Ữ': 'u', 'Ự': 'u',
    'Ỳ': 'y', 'Ý': 'y', 'Ỷ': 'y', 'Ỹ': 'y', 'Ỵ': 'y',
}


# ========================================================================
# TEXT NORMALIZER CLASS (Layer 1) - IMPROVED VERSION
# ========================================================================

class TextNormalizer:
    """
    Generic text normalizer with improved Unicode and punctuation handling
    
    NEW FEATURES (v2):
        ✓ Unicode symbol removal (™, ®, ©, etc.)
        ✓ Smart punctuation: preserve ., comma, / by default
        ✓ Space-preserving dot removal in aggressive mode
        ✓ Configurable meaningful punctuation
    
    Normalization Pipeline:
        1. Remove special Unicode symbols
        2. Lowercase
        3. Apply character mapping (diacritics)
        4. Clean whitespace
        5. Handle punctuation (context-aware)
        6. Final cleanup
    
    Examples:
        # Normal mode (preserve structure)
        "Test™, TP.HCM/Q.1!" → "test, tp.hcm/q.1"
        
        # Aggressive mode (clean for matching)
        "Test™, TP.HCM/Q.1" → "test tp hcm q 1"
    """
    
    def __init__(
        self, 
        char_map: Optional[Dict[str, str]] = None,
        meaningful_punct: Optional[Set[str]] = None
    ):
        """
        Initialize normalizer
        
        Args:
            char_map: Character replacement mapping (e.g., Vietnamese diacritics)
                     If None, only lowercase/whitespace cleaning is performed
            meaningful_punct: Punctuation to preserve in normal mode
                            Default: {'.', ',', '/'}
        
        Design rationale:
            - char_map: Dependency injection for language flexibility
            - meaningful_punct: Domain-specific punctuation rules
        """
        self.char_map = char_map or {}
        self.meaningful_punct = meaningful_punct or MEANINGFUL_PUNCT.copy()
        
        # Pre-compute noise punctuation for efficiency
        self.noise_punct = set(string.punctuation) - self.meaningful_punct
        
        # Pre-compile regex patterns
        self._whitespace_pattern = re.compile(r'\s+')
    
    def normalize(self, text: str, aggressive: bool = False) -> str:
        """
        Normalize text using multi-stage pipeline
        
        Pipeline stages:
            1. Unicode symbol removal (NEW)
            2. Lowercase
            3. Character mapping (diacritics)
            4. Whitespace cleaning
            5. Punctuation handling (IMPROVED)
            6. Final cleanup
        
        Args:
            text: Raw input text
            aggressive: Remove ALL punctuation (replace with spaces)
        
        Returns:
            Normalized text
        
        Complexity:
            Time: O(n) where n = text length
            Space: O(n) for result
        
        Examples:
            # Normal mode
            normalize("Test™, TP.HCM!") → "test, tp.hcm"
            
            # Aggressive mode
            normalize("TP.HCM/Q.1", aggressive=True) → "tp hcm q 1"
        """
        if not text:
            return ""
        
        # Stage 1: Remove special Unicode symbols
        # WHY FIRST: Broadest filter, language-agnostic
        text = self._remove_special_symbols(text)
        
        # Stage 2: Lowercase
        # WHY HERE: After symbol removal, before language-specific processing
        text = text.lower()
        
        # Stage 3: Character mapping (language-specific diacritics)
        # WHY AFTER LOWERCASE: Simpler mapping (only need lowercase variants)
        if self.char_map:
            text = self._apply_char_map(text)
        
        # Stage 4: Intermediate whitespace cleanup
        # WHY HERE: Clean up before punctuation processing
        text = self._clean_whitespace(text)
        
        # Stage 5: Punctuation handling (context-aware)
        # WHY LAST: Context-dependent, needs clean text
        text = self._handle_punctuation(text, aggressive=aggressive)
        
        # Stage 6: Final whitespace cleanup
        # WHY: Remove extra spaces from punctuation replacement
        text = self._clean_whitespace(text)
        
        return text.strip()
    
    def normalize_aggressive(self, text: str) -> str:
        """
        Convenience method: Aggressive normalization
        
        Use when:
            - You need clean text for matching
            - Structure (dots/commas) no longer needed
            - Preparing for trie insertion
        
        Examples:
            "tp.hcm, quan 1" → "tp hcm quan 1"
        """
        return self.normalize(text, aggressive=True)
    
    def normalize_batch(
        self, 
        texts: List[str], 
        aggressive: bool = False
    ) -> List[str]:
        """
        Normalize multiple texts efficiently
        
        More efficient than loop because:
            - Single method call overhead
            - Potential for future parallelization
        """
        return [self.normalize(text, aggressive=aggressive) for text in texts]
    
    # ========================================================================
    # INTERNAL HELPER METHODS
    # ========================================================================
    
    def _remove_special_symbols(self, text: str) -> str:
        """
        Remove special Unicode symbols using category filtering
        
        Strategy:
            Keep only characters in these Unicode categories:
            - L (Letters): All alphabetic characters
            - N (Numbers): Digits 0-9
            - Z (Separators): Spaces, line breaks
            - P (Punctuation): Will filter later
        
        Removes:
            ™ (trademark), ® (registered), © (copyright)
            € (euro), £ (pound), ¥ (yen)
            ° (degree), ± (plus-minus), × (multiply)
            And any other special symbols
        
        Why Unicode categories?
            - General: Handles any Unicode symbol
            - Robust: Works with characters we haven't seen
            - Self-documenting: Clear semantic meaning
        
        Args:
            text: Input text
        
        Returns:
            Text with special symbols removed
        
        Examples:
            "Test™" → "Test"
            "50€" → "50"
            "©2024" → "2024"
        
        Complexity:
            Time: O(n) where n = text length
            Space: O(n) for result
        """
        allowed_categories = {'L', 'N', 'Z', 'P'}
        return ''.join(
            char for char in text
            if unicodedata.category(char)[0] in allowed_categories
        )
    
    def _apply_char_map(self, text: str) -> str:
        """
        Apply character mapping for diacritic removal
        
        Strategy:
            Character-by-character replacement
            Could optimize with str.translate() for large maps
        
        Why after lowercase?
            Only need to map lowercase variants
            Reduces char_map size by 50%
        """
        return ''.join(self.char_map.get(char, char) for char in text)
    
    def _clean_whitespace(self, text: str) -> str:
        """
        Clean and normalize whitespace
        
        Operations:
            - Replace multiple spaces with single space
            - Remove leading/trailing whitespace
            - Ensure space after commas (if commas are meaningful)
        """
        # First, collapse multiple spaces
        text = self._whitespace_pattern.sub(' ', text).strip()
        
        # Then, ensure space after meaningful punctuation
        if ',' in self.meaningful_punct:
            # Replace comma-no-space with comma-space
            text = re.sub(r',(?=\S)', ', ', text)
        
        if '/' in self.meaningful_punct:
            # Optionally: ensure space after slashes
            # text = re.sub(r'/(?=\S)', '/ ', text)
            pass
        
        return text
    
    def _handle_punctuation(self, text: str, aggressive: bool = False) -> str:
        """
        Handle punctuation based on mode (IMPROVED)
        
        Two modes:
        
        Normal mode (aggressive=False):
            - Remove noise punctuation (!, ?, ;, :, etc.)
            - Preserve meaningful punctuation (., comma, /)
            Result: "tp.hcm, quan 1!" → "tp.hcm, quan 1"
        
        Aggressive mode (aggressive=True):
            - Replace meaningful punctuation with SPACES
            - Then remove all remaining punctuation
            Result: "tp.hcm, quan 1" → "tp hcm  quan 1" → "tp hcm quan 1"
        
        Why replace with spaces in aggressive mode?
            Preserves word boundaries for downstream parsing:
            - "tp.hcm" → "tp hcm" (can detect "tp" prefix)
            - NOT "tphcm" (looks like one word)
        
        Args:
            text: Input text
            aggressive: Use aggressive mode
        
        Returns:
            Text with punctuation handled
        """
        if aggressive:
            # Step 1: Replace meaningful punctuation with spaces
            for punct in self.meaningful_punct:
                text = text.replace(punct, ' ')
            
            # Step 2: Remove ALL remaining punctuation
            text = text.translate(str.maketrans('', '', string.punctuation))
        else:
            # Normal mode:
            # Step 1: Replace hyphens with spaces (they're word separators)
            text = text.replace('-', ' ')
            
            # Step 2: Remove only noise punctuation (excluding hyphen, already handled)
            noise_without_hyphen = self.noise_punct - {'-'}
            text = text.translate(str.maketrans('', '', ''.join(noise_without_hyphen)))
        
        return text
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_config(self) -> Dict:
        """
        Get current normalizer configuration
        
        Useful for debugging and logging
        """
        return {
            'has_char_map': bool(self.char_map),
            'char_map_size': len(self.char_map),
            'meaningful_punct': list(self.meaningful_punct),
            'noise_punct_count': len(self.noise_punct),
        }


# ========================================================================
# CONVENIENCE FUNCTIONS (Backward compatibility)
# ========================================================================

# Create default Vietnamese normalizer with new config
_default_vietnamese_normalizer = TextNormalizer(
    char_map=VIETNAMESE_CHAR_MAP,
    meaningful_punct={'.', ',', '/'}
)


def normalize_text(text: str) -> str:
    """
    Convenience function: Vietnamese text normalization (preserve structure)
    
    Backward compatible with existing code.
    
    Args:
        text: Raw Vietnamese text
    
    Returns:
        Normalized text with structure preserved
    
    Examples:
        normalize_text("TP.HCM") → "tp.hcm"
        normalize_text("Quận 1") → "quan 1"
    """
    return _default_vietnamese_normalizer.normalize(text, aggressive=False)


def normalize_text_aggressive(text: str) -> str:
    """
    Convenience function: Aggressive Vietnamese normalization
    
    Backward compatible with existing code.
    
    Args:
        text: Raw Vietnamese text
    
    Returns:
        Normalized text with all punctuation removed
    
    Examples:
        normalize_text_aggressive("tp.hcm") → "tp hcm"
        normalize_text_aggressive("q.1") → "q 1"
    """
    return _default_vietnamese_normalizer.normalize_aggressive(text)


# ========================================================================
# TEST DATA (Easily Extensible)
# ========================================================================

TEST_CASES = {
    # Test Suite 1: Basic Vietnamese Normalization
    'vietnamese_basic': {
        'description': 'Vietnamese Normalization (Structure Preserved)',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'meaningful_punct': {'.', ',', '/'}
        },
        'cases': [
            {
                'input': "TP.HCM",
                'expected': "tp.hcm",
                'description': "Keep dots for Layer 2"
            },
            {
                'input': "Quận 1",
                'expected': "quan 1",
                'description': "Remove diacritics"
            },
            {
                'input': "Phường Bến Nghé",
                'expected': "phuong ben nghe",
                'description': "Full normalization"
            },
            {
                'input': "THÀNH PHỐ HỒ CHÍ MINH",
                'expected': "thanh pho ho chi minh",
                'description': "Uppercase + diacritics"
            },
            {
                'input': "  Multiple   Spaces  ",
                'expected': "multiple spaces",
                'description': "Whitespace cleaning"
            },
            {
                'input': "P.Tân Định",
                'expected': "p.tan dinh",
                'description': "Ward with prefix"
            },
        ]
    },
    
    # Test Suite 2: Aggressive Normalization (UPDATED)
    'aggressive_mode': {
        'description': 'Aggressive Normalization (Punctuation → Spaces)',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'meaningful_punct': {'.', ',', '/'}
        },
        'cases': [
            {
                'input': "tp.hcm",
                'expected': "tp hcm",
                'description': "Dots → spaces",
                'aggressive': True
            },
            {
                'input': "q.1",
                'expected': "q 1",
                'description': "Dots before numbers",
                'aggressive': True
            },
            {
                'input': "p.ben nghe",
                'expected': "p ben nghe",
                'description': "Dots in names",
                'aggressive': True
            },
            {
                'input': "hello, world!",
                'expected': "hello world",
                'description': "Commas and exclamation",
                'aggressive': True
            },
        ]
    },
    
    # Test Suite 3: Domain-Agnostic Mode
    'domain_agnostic': {
        'description': 'Domain-Agnostic Mode (No Character Map)',
        'normalizer_config': {
            'char_map': None,
            'meaningful_punct': {'.', ',', '/'}
        },
        'cases': [
            {
                'input': "HELLO WORLD",
                'expected': "hello world",
                'description': "Just lowercase"
            },
            {
                'input': "Multiple   Spaces",
                'expected': "multiple spaces",
                'description': "Whitespace cleaning"
            },
            {
                'input': "No.Dots.Removed",
                'expected': "no.dots.removed",
                'description': "Dots preserved"
            },
        ]
    },
    
    # Test Suite 4: Edge Cases (UPDATED)
    'edge_cases': {
        'description': 'Edge Cases and Special Scenarios',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'meaningful_punct': {'.', ',', '/'}
        },
        'cases': [
            {
                'input': "",
                'expected': "",
                'description': "Empty string"
            },
            {
                'input': "   ",
                'expected': "",
                'description': "Only whitespace"
            },
            {
                'input': "123",
                'expected': "123",
                'description': "Numbers only"
            },
            {
                'input': "!!!",
                'expected': "",
                'description': "Punctuation only (removed)"
            },
            {
                'input': "a",
                'expected': "a",
                'description': "Single character"
            },
            {
                'input': "TP.HCM, Quận 1, P.Bến Nghé",
                'expected': "tp.hcm, quan 1, p.ben nghe",
                'description': "Full address with commas"
            },
        ]
    },
    
    # Test Suite 5: Unicode and Special Characters (UPDATED)
    'unicode_handling': {
        'description': 'Unicode and Special Character Handling',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'meaningful_punct': {'.', ',', '/'}
        },
        'cases': [
            {
                'input': "Đường Nguyễn Huệ",
                'expected': "duong nguyen hue",
                'description': "Vietnamese Đ character"
            },
            {
                'input': "Café",
                'expected': "cafe",
                'description': "French accent (é)"
            },
            {
                'input': "Test™",
                'expected': "test",
                'description': "Trademark symbol removal"
            },
        ]
    },
    
    # Test Suite 6: Unicode Symbol Handling (NEW)
    'unicode_symbols': {
        'description': 'Unicode Symbol Removal',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'meaningful_punct': {'.', ',', '/'}
        },
        'cases': [
            {
                'input': "Test™",
                'expected': "test",
                'description': "Trademark symbol"
            },
            {
                'input': "Product®",
                'expected': "product",
                'description': "Registered symbol"
            },
            {
                'input': "©2024 Company",
                'expected': "2024 company",
                'description': "Copyright symbol"
            },
            {
                'input': "Price: 50€",
                'expected': "price 50",
                'description': "Euro symbol (with colon removal)"
            },
            {
                'input': "25°C",
                'expected': "25c",
                'description': "Degree symbol"
            },
            {
                'input': "±5%",
                'expected': "5",
                'description': "Plus-minus and percent"
            },
        ]
    },
    
    # Test Suite 7: Punctuation Preservation (NEW)
    'punctuation_preservation': {
        'description': 'Meaningful Punctuation Preservation',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'meaningful_punct': {'.', ',', '/'}
        },
        'cases': [
            {
                'input': "TP.HCM, Quận 1",
                'expected': "tp.hcm, quan 1",
                'description': "Keep dots and commas"
            },
            {
                'input': "Địa chỉ: 123/45 Đường ABC",
                'expected': "dia chi 123/45 duong abc",
                'description': "Keep slashes, remove colons"
            },
            {
                'input': "Hello, World!",
                'expected': "hello, world",
                'description': "Keep comma, remove exclamation"
            },
            {
                'input': "Q.1, P.Tân Định",
                'expected': "q.1, p.tan dinh",
                'description': "Multiple meaningful punctuation"
            },
        ]
    },
    
    # Test Suite 8: Aggressive Mode - Space Preservation (NEW)
    'aggressive_space_preservation': {
        'description': 'Aggressive Mode: Punctuation → Spaces',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'meaningful_punct': {'.', ',', '/'}
        },
        'cases': [
            {
                'input': "tp.hcm",
                'expected': "tp hcm",
                'description': "Dot becomes space (aggressive)",
                'aggressive': True
            },
            {
                'input': "q.1",
                'expected': "q 1",
                'description': "Dot before number (aggressive)",
                'aggressive': True
            },
            {
                'input': "123/45",
                'expected': "123 45",
                'description': "Slash becomes space (aggressive)",
                'aggressive': True
            },
            {
                'input': "a,b,c",
                'expected': "a b c",
                'description': "Commas become spaces (aggressive)",
                'aggressive': True
            },
            {
                'input': "tp.hcm/quan.1",
                'expected': "tp hcm quan 1",
                'description': "Multiple punctuation (aggressive)",
                'aggressive': True
            },
            {
                'input': "357/28,Ng-T- Thuật,P1,Q3",
                'expected': "357/28, ng t thuat, p1, q3",
                'description': "Missing spaces after commas"
            },
        ]
    },
}


# ========================================================================
# TEST BATCH DATA (For performance testing)
# ========================================================================

BATCH_TEST_DATA = {
    'sample_addresses': {
        'description': 'Batch processing of addresses',
        'normalizer_config': {
            'char_map': VIETNAMESE_CHAR_MAP,
            'meaningful_punct': {'.', ',', '/'}
        },
        'batch_input': [
            "TP.HCM",
            "Quận 1",
            "Phường Bến Nghé",
            "Hà Nội",
            "THÀNH PHỐ ĐÀ NẴNG"
        ],
        'expected_output': [
            "tp.hcm",
            "quan 1",
            "phuong ben nghe",
            "ha noi",
            "thanh pho da nang"
        ]
    },
}


# ========================================================================
# REUSABLE TEST RUNNER FUNCTIONS (UPDATED)
# ========================================================================

def run_test_suite(suite_name: str, suite_config: dict) -> dict:
    """
    Run a single test suite and return results
    
    UPDATED: Now handles test cases with 'aggressive' flag
    
    Args:
        suite_name: Name of the test suite
        suite_config: Configuration dictionary containing:
            - description: Suite description
            - normalizer_config: Config for TextNormalizer
            - cases: List of test cases
    
    Returns:
        Dictionary with test results and statistics
    """
    print(f"\
✅ {suite_config['description']}")
    print("-" * 70)
    
    # Create normalizer with suite config
    normalizer = TextNormalizer(**suite_config['normalizer_config'])
    
    results = {
        'suite_name': suite_name,
        'total': 0,
        'passed': 0,
        'failed': 0,
        'failures': []
    }
    
    # Run each test case
    for case in suite_config['cases']:
        results['total'] += 1
        
        # Check if test specifies aggressive mode
        aggressive = case.get('aggressive', False)
        
        # Execute test
        actual = normalizer.normalize(case['input'], aggressive=aggressive)
        expected = case['expected']
        passed = (actual == expected)
        
        # Update statistics
        if passed:
            results['passed'] += 1
            status = "✅"
        else:
            results['failed'] += 1
            status = "❌"
            results['failures'].append({
                'input': case['input'],
                'expected': expected,
                'actual': actual,
                'description': case['description'],
                'aggressive': aggressive
            })
        
        # Print result with mode indicator
        mode_indicator = " [AGG]" if aggressive else ""
        print(f"{status} '{case['input'][:30]:30}' → '{actual[:30]:30}' | {case['description']}{mode_indicator}")
        
        if not passed:
            print(f"   Expected: '{expected}'")
            print(f"   Actual:   '{actual}'")
    
    return results


def run_batch_test(test_name: str, test_config: dict) -> dict:
    """
    Run a batch processing test
    
    Args:
        test_name: Name of the batch test
        test_config: Configuration dictionary
    
    Returns:
        Test results
    """
    print(f"\
✅ {test_config['description']}")
    print("-" * 70)
    
    normalizer = TextNormalizer(**test_config['normalizer_config'])
    
    # Execute batch
    actual_output = normalizer.normalize_batch(test_config['batch_input'])
    expected_output = test_config['expected_output']
    
    # Check results
    passed = (actual_output == expected_output)
    
    print(f"Input ({len(test_config['batch_input'])} items):")
    for item in test_config['batch_input']:
        print(f"  - {item}")
    
    print(f"\
Output:")
    for item in actual_output:
        print(f"  - {item}")
    
    if passed:
        print("\n✅ Batch test PASSED")
    else:
        print("\n❌ Batch test FAILED")
        print(f"Expected: {expected_output}")
        print(f"Actual:   {actual_output}")
    
    return {
        'test_name': test_name,
        'passed': passed,
        'input_count': len(test_config['batch_input'])
    }


def run_convenience_function_tests() -> dict:
    """
    Test convenience functions for backward compatibility
    """
    print("\n✅ Backward Compatibility (Convenience Functions)")
    print("-" * 70)
    
    test_input = "TP.HCM"
    
    result1 = normalize_text(test_input)
    result2 = normalize_text_aggressive(test_input)
    
    print(f"normalize_text('{test_input}') → '{result1}'")
    print(f"normalize_text_aggressive('{test_input}') → '{result2}'")
    
    # Verify expected behavior
    expected_normal = "tp.hcm"
    expected_aggressive = "tp hcm"
    
    passed = (result1 == expected_normal and result2 == expected_aggressive)
    
    return {
        'passed': passed,
        'test_count': 2
    }


def print_summary(all_results: list, batch_results: list, convenience_result: dict):
    """
    Print comprehensive test summary with statistics
    
    Args:
        all_results: List of test suite results
        batch_results: List of batch test results
        convenience_result: Result from convenience function tests
    """
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    # Calculate totals
    total_tests = sum(r['total'] for r in all_results)
    total_passed = sum(r['passed'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)
    
    # Add batch and convenience tests
    batch_passed = sum(1 for r in batch_results if r['passed'])
    total_tests += len(batch_results) + convenience_result['test_count']
    total_passed += batch_passed + (convenience_result['test_count'] if convenience_result['passed'] else 0)
    
    # Print suite-by-suite results
    print("\nTest Suite Results:")
    print("-" * 70)
    for result in all_results:
        percentage = (result['passed'] / result['total'] * 100) if result['total'] > 0 else 0
        status = "✅" if result['failed'] == 0 else "⚠️"
        print(f"{status} {result['suite_name']:30} | {result['passed']:3}/{result['total']:3} passed ({percentage:5.1f}%)")
    
    # Print batch test results
    if batch_results:
        print(f"\n{'✅' if batch_passed == len(batch_results) else '⚠️'} Batch Tests: {batch_passed}/{len(batch_results)} passed")
    
    # Print convenience function results
    status = "✅" if convenience_result['passed'] else "❌"
    print(f"{status} Convenience Functions: {'PASSED' if convenience_result['passed'] else 'FAILED'}")
    
    # Overall summary
    print("\n" + "="*70)
    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"OVERALL: {total_passed}/{total_tests} tests passed ({overall_percentage:.1f}%)")
    
    if total_failed > 0:
        print(f"\n⚠️  {total_failed} test(s) failed:")
        for result in all_results:
            if result['failures']:
                print(f"\n  Suite: {result['suite_name']}")
                for failure in result['failures']:
                    print(f"    - {failure['description']}")
                    print(f"      Input:    '{failure['input']}'")
                    print(f"      Expected: '{failure['expected']}'")
                    print(f"      Actual:   '{failure['actual']}'")
    else:
        print("✅ All tests passed!")
    
    print("="*70)


# ========================================================================
# MAIN TEST EXECUTION
# ========================================================================

if __name__ == "__main__":
    print("="*70)
    print("LAYER 1: TEXT NORMALIZER V2 - IMPROVED TEST SUITE")
    print("="*70)
    
    # Run all test suites
    all_results = []
    for suite_name, suite_config in TEST_CASES.items():
        result = run_test_suite(suite_name, suite_config)
        all_results.append(result)
    
    # Run batch tests
    batch_results = []
    for test_name, test_config in BATCH_TEST_DATA.items():
        result = run_batch_test(test_name, test_config)
        batch_results.append(result)
    
    # Run convenience function tests
    convenience_result = run_convenience_function_tests()
    
    # Print summary
    print_summary(all_results, batch_results, convenience_result)
    
    # Print key improvements
    print("\n" + "="*70)
    print("KEY IMPROVEMENTS IN V2:")
    print("="*70)
    print("""
1. ✓ Unicode Symbol Removal:
   - Handles ™, ®, ©, €, °, and other special symbols
   - Uses Unicode category filtering (robust and general)
   
2. ✓ Smart Punctuation:
   - Preserves meaningful punctuation (., comma, /) by default
   - Removes noise punctuation (!, ?, ;, :, etc.)
   
3. ✓ Space-Preserving Aggressive Mode:
   - "tp.hcm" → "tp hcm" (NOT "tphcm")
   - Preserves word boundaries for Layer 2 parsing
   
4. ✓ Configurable:
   - Can customize meaningful punctuation per domain
   - Works with any character mapping
   
5. ✓ Backward Compatible:
   - Convenience functions work as before
   - Existing code requires no changes
    """)
    
    print("\n✅ Test suite completed!")
    print("\n" + "="*70)
    print("READY FOR LAYER 2: Admin Prefix Handler")
    print("="*70)
