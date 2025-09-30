"""
Vietnamese Address Text Normalization
Dynamic configuration based on address database
"""

import re
import string
from typing import Dict, List

# ========================================================================
# VIETNAMESE CHARACTER MAPPING
# ========================================================================

# Vietnamese character mapping
# Critical: Đ/đ (U+0110/U+0111) are distinct characters, not base D with diacritic
VIETNAMESE_CHAR_MAP = {
    # Lowercase vowels with tones
    'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
    'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
    'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    'đ': 'd',  # D with stroke - CRITICAL
    'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
    'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
    'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
    'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
    'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
    'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
    'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    # Uppercase vowels with tones
    'À': 'a', 'Á': 'a', 'Ả': 'a', 'Ã': 'a', 'Ạ': 'a',
    'Ă': 'a', 'Ằ': 'a', 'Ắ': 'a', 'Ẳ': 'a', 'Ẵ': 'a', 'Ặ': 'a',
    'Â': 'a', 'Ầ': 'a', 'Ấ': 'a', 'Ẩ': 'a', 'Ẫ': 'a', 'Ậ': 'a',
    'Đ': 'd',  # D with stroke - CRITICAL
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
# DYNAMIC CONFIGURATION GENERATION
# ========================================================================

def build_province_abbreviations(provinces: List[Dict]) -> Dict[str, str]:
    """
    Generate province abbreviations dynamically from database
    
    Strategy:
    1. Extract initials (e.g., "Hồ Chí Minh" → "hcm")
    2. Generate TP. variants for city names
    3. Generate T. variants for two-word names
    
    Args:
        provinces: List of province dicts with 'Name' field
    
    Returns:
        Dict mapping abbreviation -> full name (lowercase)
    """
    abbrevs = {}
    
    for province in provinces:
        name = province['Name']
        name_lower = name.lower()
        
        tokens = name_lower.split()
        
        if len(tokens) >= 2:
            # Generate initials: "Hồ Chí Minh" → "hcm"
            initials = ''.join([t[0] for t in tokens])
            abbrevs[initials] = name_lower
            
            # TP. prefix variations (for cities)
            abbrevs[f'tp.{initials}'] = name_lower
            abbrevs[f'tp {initials}'] = name_lower
            abbrevs[f'tp. {initials}'] = name_lower
            abbrevs[f'tp{initials}'] = name_lower
        
        # Two-word abbreviation: "Tiền Giang" → "t.giang"
        if len(tokens) == 2:
            abbrevs[f'{tokens[0][0]}.{tokens[1]}'] = name_lower
            abbrevs[f'{tokens[0][0]} {tokens[1]}'] = name_lower
        
        # Handle "Thành phố X" pattern
        if 'thành phố' in name_lower:
            core_name = name_lower.replace('thành phố', '').strip()
            if core_name:
                abbrevs[f'tp.{core_name}'] = name_lower
                abbrevs[f'tp {core_name}'] = name_lower
                abbrevs[f'tp{core_name}'] = name_lower
    
    return abbrevs


def build_expansion_patterns() -> List[tuple]:
    """
    Generate standard expansion patterns
    
    Universal patterns independent of data
    
    Returns:
        List of (pattern, replacement, description) tuples
    """
    return [
        # Numeric administrative units
        (r'\bp\.?\s*(\d+)\b', r'phường \1', 'P.X → Phường X'),
        (r'\bq\.?\s*(\d+)\b', r'quận \1', 'Q.X → Quận X'),
        (r'\bx\.?\s*(\d+)\b', r'xã \1', 'X.X → Xã X'),
        
        # Street name abbreviations
        (r'\bng\.\s*', r'nguyễn ', 'Ng. → Nguyễn'),
        (r'\bng-', r'nguyễn ', 'Ng- → Nguyễn'),
        (r'\bd\.\s*', r'đường ', 'D. → Đường'),
        (r'\blt\.\s*', r'lê thánh ', 'Lt. → Lê Thánh'),
        (r'\btr\.\s*', r'trần ', 'Tr. → Trần'),
    ]


def build_admin_prefixes() -> List[str]:
    """
    Generate administrative prefixes
    
    Standard Vietnamese administrative terms
    
    Returns:
        List of prefix strings (with diacritics)
    """
    return [
        # Full forms
        'thị trấn', 'thị xã', 'thành phố',
        'tỉnh', 'huyện', 'quận',
        'phường', 'xã', 'thôn', 'ấp',
        # Abbreviations
        'tt', 'tx', 'tp', 'h', 'q', 'p', 'x',
    ]


# ========================================================================
# CONFIGURATION CLASS
# ========================================================================

class NormalizationConfig:
    """
    Dynamic normalization configuration
    Builds from address database at initialization
    """
    
    def __init__(self, provinces: List[Dict]):
        """
        Initialize configuration from database
        
        Args:
            provinces: List of province dictionaries with 'Name' field
        """
        self.province_abbreviations = build_province_abbreviations(provinces)
        self.expansion_patterns = build_expansion_patterns()
        self.admin_prefixes = build_admin_prefixes()
        
        # Cache for performance
        self._normalized_prefixes = None
    
    def get_normalized_prefixes(self) -> List[str]:
        """Get normalized prefixes (cached)"""
        if self._normalized_prefixes is None:
            self._normalized_prefixes = [
                apply_char_map(prefix) 
                for prefix in self.admin_prefixes
            ]
        return self._normalized_prefixes


# ========================================================================
# NORMALIZATION FUNCTIONS
# ========================================================================

def normalize_text(text: str, config: NormalizationConfig) -> str:
    """
    Normalize Vietnamese address text for matching
    
    Algorithm:
    1. Lowercase
    2. Expand abbreviations (dynamic)
    3. Map Vietnamese diacritics
    4. Remove punctuation (except hyphens)
    5. Strip administrative prefixes (dynamic)
    6. Clean whitespace
    
    Time: O(n) where n = len(text)
    
    Args:
        text: Input text
        config: NormalizationConfig instance
    
    Returns:
        Normalized text
    
    Examples:
        "Hà Nội" → "ha noi"
        "TP.HCM" → "ho chi minh"
        "TT Tân Bình" → "tan binh"
        "P.1, Q.3" → "phuong 1 quan 3"
    """
    # Step 1: Lowercase
    text = text.lower()
    
    # Step 2: Expand abbreviations
    text = expand_abbreviations(text, config)
    
    # Step 3: Map Vietnamese diacritics
    result = []
    for char in text:
        result.append(VIETNAMESE_CHAR_MAP.get(char, char))
    text = ''.join(result)
    
    # Step 4: Remove punctuation (except hyphens)
    punctuation_to_remove = string.punctuation.replace('-', '')
    text = text.translate(str.maketrans('', '', punctuation_to_remove))
    
    # Step 5: Strip administrative prefixes
    text = strip_admin_prefixes(text, config)
    
    # Step 6: Clean whitespace
    text = text.strip()
    text = ' '.join(text.split())
    
    return text


def expand_abbreviations(text: str, config: NormalizationConfig) -> str:
    """Expand abbreviations using dynamic config"""
    # Province abbreviations
    for abbrev, full_name in config.province_abbreviations.items():
        text = text.replace(abbrev, full_name)
    
    # Regex patterns
    for pattern, replacement, _ in config.expansion_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def strip_admin_prefixes(text: str, config: NormalizationConfig) -> str:
    """Remove administrative prefixes using dynamic config"""
    normalized_prefixes = config.get_normalized_prefixes()
    
    # Strip from beginning
    for prefix in normalized_prefixes:
        if text.startswith(prefix + ' '):
            text = text[len(prefix):].strip()
        elif text.startswith(prefix):
            text = text[len(prefix):].strip()
    
    # Strip from word boundaries
    for prefix in normalized_prefixes:
        text = re.sub(r'\b' + re.escape(prefix) + r'\s+(?=\w)', '', text)
    
    return text.strip()


def apply_char_map(text: str) -> str:
    """Apply Vietnamese character mapping"""
    result = []
    for char in text.lower():
        result.append(VIETNAMESE_CHAR_MAP.get(char, char))
    return ''.join(result)