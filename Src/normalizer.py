"""
Vietnamese Address Text Normalization - REFACTORED
Preserves type information while normalizing text
"""

import re
import string
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# ========================================================================
# DATA STRUCTURES
# ========================================================================

@dataclass
class TypeHint:
    """
    Metadata about detected entity type
    
    Simple structure: what was found, where, and how confident
    """
    entity_type: str  # 'province', 'district', 'ward'
    value: str        # normalized value
    confidence: float # 0.0 to 1.0
    
    def __repr__(self):
        return f"{self.entity_type}='{self.value}' ({self.confidence:.2f})"


@dataclass
class NormalizedAddress:
    """
    Normalization result: text + hints
    """
    text: str                        # normalized for matching
    hints: Dict[str, TypeHint]       # detected entity types
    tokens: List[str]                # split text
    
    def __repr__(self):
        return f"text='{self.text}' | hints={list(self.hints.values())}"


# ========================================================================
# VIETNAMESE CHARACTER MAPPING
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
# MARKER DETECTION
# ========================================================================

def detect_type_markers(text: str) -> Dict[str, TypeHint]:
    """
    Find administrative markers (P., Q., TP., etc.) in text
    
    Returns hints dict: {'ward': TypeHint(...), 'district': TypeHint(...)}
    
    Key improvement: Use greedy matching to capture full multi-word names
    
    Example:
        "P.1, Q.3, TP.Hồ Chí Minh" → {
            'ward': TypeHint('ward', '1', 0.95),
            'district': TypeHint('district', '3', 0.95),
            'province': TypeHint('province', 'ho chi minh', 0.90)
        }
    """
    hints = {}
    text_lower = text.lower()
    
    # Patterns ordered by specificity (most specific first)
    patterns = [
        # === Province (must come first to capture full names) ===
        (r'\btp\.?\s*([^,]+?)(?=\s*[,\n]|$)', 'province', 0.90),       # TP.Hồ Chí Minh (\s* = 0+ spaces)
        (r'\bthành\s+phố\s+([^,]+?)(?=\s*[,\n]|$)', 'province', 0.88), # Thành phố ...
        (r'\btỉnh\s+([^,]+?)(?=\s*[,\n]|$)', 'province', 0.88),        # Tỉnh ...
        
        # === District ===
        (r'\bq\.?\s*(\d+)\b', 'district', 0.95),                        # Q.3, Q3
        (r'\bquận\s+(\d+)\b', 'district', 0.90),                        # Quận 3
        (r'\bquận\s+([^,\d]+?)(?=\s*[,\n]|$)', 'district', 0.85),      # Quận Tân Bình
        (r'\bhuyện\s+([^,]+?)(?=\s*[,\n]|$)', 'district', 0.85),       # Huyện Củ Chi
        
        # === Ward (includes towns and communes at same hierarchical level) ===
        (r'\btt\.?\s*([^,]+?)(?=\s*[,\n]|$)', 'ward', 0.90),          # TT Tân Bình (town)
        (r'\bthị\s+trấn\s+([^,]+?)(?=\s*[,\n]|$)', 'ward', 0.88),     # Thị trấn ...
        (r'\bp\.?\s*(\d+)\b', 'ward', 0.95),                            # P.1, P1
        (r'\bphường\s+(\d+)\b', 'ward', 0.90),                          # Phường 1
        (r'\bphường\s+([^,\d]+?)(?=\s*[,\n]|$)', 'ward', 0.85),        # Phường Tân Bình
        (r'\bxã\s+([^,]+?)(?=\s*[,\n]|$)', 'ward', 0.85),              # Xã ...
    ]
    
    for pattern, entity_type, confidence in patterns:
        if entity_type in hints:
            continue  # Already found this type, skip
        
        match = re.search(pattern, text_lower)
        if match:
            value = match.group(1).strip()
            # Normalize the value
            normalized_value = normalize_text_simple(value)
            hints[entity_type] = TypeHint(entity_type, normalized_value, confidence)
    
    return hints


# ========================================================================
# CONFIGURATION (PRESERVED FROM ORIGINAL)
# ========================================================================

def build_province_abbreviations(provinces: List[Dict]) -> Dict[str, str]:
    """Generate province abbreviations dynamically from database
    
    CRITICAL: Only generate SAFE abbreviations that won't collide with
    common district/ward names. Avoid short patterns that could match
    substring of unrelated words.
    
    Strategy:
    - Use TP/Thành phố prefix patterns (unambiguous)
    - Avoid generating bare 2-character abbreviations like 'na', 'tn'
    - Only use initials when ≥3 characters
    """
    abbrevs = {}
    
    for province in provinces:
        name = province['Name']
        name_lower = name.lower()
        tokens = name_lower.split()
        
        # Only generate initials if ≥3 characters (safe from collisions)
        if len(tokens) >= 2:
            initials = ''.join([t[0] for t in tokens])
            if len(initials) >= 3:
                abbrevs[initials] = name_lower
            
            # TP-prefixed versions (always safe)
            abbrevs[f'tp.{initials}'] = name_lower
            abbrevs[f'tp {initials}'] = name_lower
            abbrevs[f'tp. {initials}'] = name_lower
            abbrevs[f'tp{initials}'] = name_lower
        
        # REMOVED: The dangerous 2-token patterns that cause collisions
        # OLD: abbrevs[f'{tokens[0][0]}.{tokens[1]}'] = name_lower
        # This was creating 'n.an' → 'nghệ an', matching 'na' in 'nam'
        
        # Only add thành phố abbreviations (safe prefix)
        if 'thành phố' in name_lower:
            core_name = name_lower.replace('thành phố', '').strip()
            if core_name:
                abbrevs[f'tp.{core_name}'] = name_lower
                abbrevs[f'tp {core_name}'] = name_lower
                abbrevs[f'tp{core_name}'] = name_lower
    
    return abbrevs


def build_expansion_patterns() -> List[tuple]:
    """
    Expansion patterns for Vietnamese address normalization
    Only 3 levels: province/city, district, ward/commune
    Handles compact, spaced, dotted, and uppercase variations.
    
    CRITICAL FIX: Single-letter patterns (h, q, p, x) must be followed by:
    - A dot: "H." or "H. "
    - A space + digit: "H 3", "P 1"
    - A space + uppercase: "H Nam"
    
    This prevents matching words like "hồ", "quận", "phường", "xã" themselves.
    """
    return [
        # --- Province / City ---
        (r'\b(?:tp|t\.p)\.?\s+([a-zA-ZÀ-ỹ\d]+)', r'thành phố \1', 'TP → Thành phố'),
        (r'\bthanh\s*pho\s+([a-zA-ZÀ-ỹ\d]+)', r'thành phố \1', 'Thanh pho → Thành phố'),
        (r'\btinh[h]?\s+([a-zA-ZÀ-ỹ\d]+)', r'tỉnh \1', 'Tinh → Tỉnh'),

        # --- District ---
        # FIXED: Single 'q' only matches with dot OR space+capital/digit
        (r'\bq\.\s*([a-zA-ZÀ-ỹ\d]+)', r'quận \1', 'Q. → Quận'),
        (r'\bq\s+([A-ZÀ-Ỹ\d][a-zA-ZÀ-ỹ\d]*)', r'quận \1', 'Q Capital → Quận'),
        (r'\bquan\s+([a-zA-ZÀ-ỹ\d]+)', r'quận \1', 'Quan → Quận'),
        # FIXED: Single 'h' only matches with dot OR space+capital/digit
        (r'\bh\.\s*([a-zA-ZÀ-ỹ\d]+)', r'huyện \1', 'H. → Huyện'),
        (r'\bh\s+([A-ZÀ-Ỹ\d][a-zA-ZÀ-ỹ\d]*)', r'huyện \1', 'H Capital → Huyện'),
        (r'\bhuyen\s+([a-zA-ZÀ-ỹ\d]+)', r'huyện \1', 'Huyen → Huyện'),

        # --- Ward / Commune ---
        # FIXED: Single 'p' only matches with dot OR space+capital/digit
        (r'\bp\.\s*([a-zA-ZÀ-ỹ\d]+)', r'phường \1', 'P. → Phường'),
        (r'\bp\s+(\d+)', r'phường \1', 'P digit → Phường'),
        (r'\bphuong\s+([a-zA-ZÀ-ỹ\d]+)', r'phường \1', 'Phuong → Phường'),
        # FIXED: Single 'x' only matches with dot OR space+capital/digit
        (r'\bx\.\s*([a-zA-ZÀ-ỹ\d]+)', r'xã \1', 'X. → Xã'),
        (r'\bx\s+([A-ZÀ-Ỹ\d][a-zA-ZÀ-ỹ\d]*)', r'xã \1', 'X Capital → Xã'),
        (r'\bxa\s+([a-zA-ZÀ-ỹ\d]+)', r'xã \1', 'Xa → Xã'),
        (r'\btt\.?\s+([a-zA-ZÀ-ỹ\d]+)', r'thị trấn \1', 'TT → Thị trấn'),
        (r'\bthi\s+tran\s+([a-zA-ZÀ-ỹ\d]+)', r'thị trấn \1', 'Thi tran → Thị trấn'),
    ]



def build_admin_prefixes() -> List[str]:
    """Generate administrative prefixes"""
    return [
        'thị trấn', 'thị xã', 'thành phố',
        'tỉnh', 'huyện', 'quận',
        'phường', 'xã', 'thôn', 'ấp',
        'tt', 'tx', 'tp', 'h', 'q', 'p', 'x',
    ]


class NormalizationConfig:
    """Dynamic normalization configuration"""
    
    def __init__(self, provinces: List[Dict]):
        self.province_abbreviations = build_province_abbreviations(provinces)
        self.expansion_patterns = build_expansion_patterns()
        self.admin_prefixes = build_admin_prefixes()
        self._normalized_prefixes = None
    
    def get_normalized_prefixes(self) -> List[str]:
        if self._normalized_prefixes is None:
            self._normalized_prefixes = [
                apply_char_map(prefix) 
                for prefix in self.admin_prefixes
            ]
        return self._normalized_prefixes


# ========================================================================
# CORE FUNCTIONS
# ========================================================================

def apply_char_map(text: str) -> str:
    """Map Vietnamese characters to ASCII"""
    result = []
    for char in text.lower():
        result.append(VIETNAMESE_CHAR_MAP.get(char, char))
    return ''.join(result)


def normalize_text_simple(text: str) -> str:
    """
    Simple normalization: lowercase, remove diacritics, clean punctuation
    Used for normalizing hint values
    """
    text = text.lower()
    
    # Map diacritics
    result = []
    for char in text:
        result.append(VIETNAMESE_CHAR_MAP.get(char, char))
    text = ''.join(result)
    
    # Remove punctuation except hyphens
    text = text.translate(str.maketrans('', '', string.punctuation.replace('-', '')))
    
    # Clean whitespace
    return ' '.join(text.split())


def normalize_text(text: str, config: NormalizationConfig) -> str:
    """
    BACKWARD COMPATIBLE: Original normalize_text function
    
    Use this when you just need normalized text without metadata
    
    Args:
        text: Input text
        config: NormalizationConfig instance
    
    Returns:
        Normalized text string
    """
    # Step 1: Lowercase
    text = text.lower()
    
    # Step 2: Expand abbreviations
    for abbrev, full_name in config.province_abbreviations.items():
        text = text.replace(abbrev, full_name)
    
    for pattern, replacement, _ in config.expansion_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Step 3: Map Vietnamese diacritics
    result = []
    for char in text:
        result.append(VIETNAMESE_CHAR_MAP.get(char, char))
    text = ''.join(result)
    
    # Step 4: Convert delimiters to spaces FIRST
    # This prevents token fusion: "P1,Q3" → "P1 Q3" not "P1Q3"
    for delimiter in ',./;:':
        text = text.replace(delimiter, ' ')

    # Then remove other punctuation except hyphens
    punctuation_to_remove = string.punctuation.replace('-', '')
    text = text.translate(str.maketrans('', '', punctuation_to_remove))
    
    # Step 5: Strip administrative prefixes (FIXED: only strip if followed by space)
    normalized_prefixes = config.get_normalized_prefixes()
    
    # Only strip prefixes when followed by whitespace
    for prefix in normalized_prefixes:
        if text.startswith(prefix + ' '):
            text = text[len(prefix) + 1:].strip()  # +1 to also remove the space
            break  # Only strip once at the beginning
    
    # Also remove prefixes mid-text
    for prefix in normalized_prefixes:
        text = re.sub(r'\b' + re.escape(prefix) + r'\s+(?=\w)', '', text)
    
    # Step 6: Clean whitespace
    text = text.strip()
    text = ' '.join(text.split())
    
    return text


def normalize_with_metadata(
    text: str,
    config: NormalizationConfig
) -> NormalizedAddress:
    """
    Main function: normalize text + extract type hints
    
    Algorithm:
    1. Detect markers in raw text → hints dict
    2. Apply full normalization → normalized text
    3. Return both
    
    Example:
        Input: "P.1, Q.3, TP.HCM"
        Output: NormalizedAddress(
            text="1 3 ho chi minh",
            hints={'ward': TypeHint('ward', '1', 0.95), ...},
            tokens=["1", "3", "ho", "chi", "minh"]
        )
    """
    # Step 1: Extract hints before normalization destroys them
    hints = detect_type_markers(text)
    
    # Step 2: Normalize text (use existing function)
    normalized_text = normalize_text(text, config)
    
    # Step 3: Tokenize
    tokens = normalized_text.split()
    
    return NormalizedAddress(
        text=normalized_text,
        hints=hints,
        tokens=tokens
    )


# ========================================================================
# EXAMPLE USAGE
# ========================================================================

if __name__ == "__main__":
    # Create config
    sample_provinces = [
        {'Name': 'Hồ Chí Minh'},
        {'Name': 'Hà Nội'},
    ]
    config = NormalizationConfig(sample_provinces)
    
    # Test
    test_cases = [
        "P.1, Q.3, TP.Hồ Chí Minh",
        "357/28, P.1, Q.3, TP.HCM",
        "TT Tân Bình, Huyện Củ Chi",
        "Phường Tân Bình, Quận 10, Hà Nội",
    ]
    
    print("="*70)
    print("IMPROVED NORMALIZER TEST")
    print("="*70)
    
    for test in test_cases:
        print(f"\nInput:  {test}")
        result = normalize_with_metadata(test, config)
        print(f"Output: {result}")
        
        # Show detailed hints
        for entity_type, hint in result.hints.items():
            print(f"  {entity_type:10s}: '{hint.value}' (confidence={hint.confidence})")
