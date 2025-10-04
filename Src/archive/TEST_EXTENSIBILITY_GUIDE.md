# Test Extensibility Guide

## ✅ What Changed?

The tests in `normalizer_v2.py` have been refactored from **inline test cases** to a **data-driven architecture**.

---

## 🎯 Key Improvements

### Before (Inline Tests)
```python
# Hard to extend - tests mixed with logic
test_cases = [
    ("TP.HCM", "tp.hcm", "Keep dots"),
    # Adding more requires finding this exact location
]

for input_text, expected, description in test_cases:
    result = normalize_text(input_text)
    status = "✅" if result == expected else "❌"
    print(f"{status} '{input_text}' → '{result}' | {description}")
```

### After (Data-Driven)
```python
# Easy to extend - tests separated from execution logic
TEST_SUITES = {
    'basic_normalization': {
        'function': normalize_text,
        'description': 'Basic normalization tests',
        'cases': [
            ("TP.HCM", "tp.hcm", "Keep dots"),
            # ✅ ADD MORE HERE - just append tuples!
        ]
    },
    # ✅ ADD NEW SUITES HERE - just add dictionary entries!
}

# Reusable test runner (never needs modification)
def run_test_suite(suite_name, suite_config):
    # ... runs all cases automatically
```

---

## 📋 How to Add Tests

### Method 1: Add to Existing Suite (Easiest)

**Location**: `normalizer_v2.py` → `TEST_SUITES` dictionary

```python
TEST_SUITES = {
    'basic_normalization': {
        'cases': [
            # Existing tests...
            ("TP.HCM", "tp.hcm", "Keep dots for Layer 2"),
            
            # ✅ ADD YOUR TEST HERE (just one line!):
            ("Huyện Bình Chánh", "huyen binh chanh", "District with tones"),
            ("Xã Tân Thông Hội", "xa tan thong hoi", "Commune name"),
        ]
    }
}
```

**That's it!** Run `python normalizer_v2.py` and your tests execute automatically.

---

### Method 2: Create New Test Suite

```python
TEST_SUITES = {
    # Existing suites...
    
    # ✅ ADD NEW SUITE HERE:
    'my_custom_tests': {
        'function': normalize_text,  # Or normalize_text_aggressive
        'description': 'My Custom Test Suite',
        'cases': [
            ("Custom Input 1", "expected 1", "Description 1"),
            ("Custom Input 2", "expected 2", "Description 2"),
            # Add as many as you want!
        ]
    }
}
```

---

## 🔧 Test Structure Explained

Each test suite has this structure:

```python
{
    'function': <function_to_test>,      # What to test
    'description': <suite_description>,  # Human-readable name
    'cases': [                           # List of test cases
        (input, expected, description),  # Each test is a 3-tuple
        # ...
    ]
}
```

Each test case is a tuple:
- **Position 0**: Input string to test
- **Position 1**: Expected output
- **Position 2**: Human-readable description

---

## 📊 What You Get Automatically

When you run tests, you automatically get:

### 1. Individual Test Results
```
✅ 'TP.HCM                        ' → 'tp.hcm                        ' | Keep dots for Layer 2
❌ 'Bad Input                     ' → 'wrong output                  ' | Should fail
   Expected: 'correct output'
   Actual:   'wrong output'
```

### 2. Suite-Level Statistics
```
Test Suite Results:
----------------------------------------------------------------------
✅ basic_normalization        |   6/  6 passed (100.0%)
⚠️  aggressive_normalization   |   3/  4 passed ( 75.0%)
✅ edge_cases                 |   5/  5 passed (100.0%)
```

### 3. Overall Summary
```
======================================================================
OVERALL: 14/15 tests passed (93.3%)

⚠️  1 test(s) failed:
  Suite: aggressive_normalization
    - Should handle special case
      Input:    'Bad Input'
      Expected: 'correct output'
      Actual:   'wrong output'
```

---

## 💡 Advanced: Testing Multiple Functions

You can test different functions in different suites:

```python
TEST_SUITES = {
    'basic_tests': {
        'function': normalize_text,  # Tests this function
        'cases': [...]
    },
    
    'aggressive_tests': {
        'function': normalize_text_aggressive,  # Tests different function
        'cases': [...]
    },
}
```

---

## 🚀 Example Workflow

1. **Identify what to test**: "I want to test Đà Nẵng normalization"

2. **Choose a suite**: Use `unicode_handling` (already exists)

3. **Add your test**:
```python
TEST_SUITES['unicode_handling']['cases'].append(
    ("Đà Nẵng", "da nang", "City with multiple diacritics")
)
```

4. **Run tests**:
```bash
cd src/
python normalizer_v2.py
```

5. **See results**:
```
✅ 'Đà Nẵng                     ' → 'da nang                      ' | City with multiple diacritics
```

**Done!** 🎉

---

## 📈 Scaling Benefits

### Small scale (10 tests)
- Both approaches work fine

### Medium scale (50+ tests)
- Data-driven approach: Easy to manage
- Inline approach: Becomes unwieldy

### Large scale (100+ tests)
- Data-driven approach: Still manageable, group by suites
- Inline approach: Nearly impossible to maintain

---

## 🎓 Key Concepts

### Separation of Concerns
- **Test Data** (in TEST_SUITES): What to test
- **Test Logic** (in run_test_suite): How to test
- **Test Reporting** (in print_test_summary): How to report results

### DRY Principle (Don't Repeat Yourself)
- Write test runner **once**
- Reuse for **all** test suites
- Add tests by adding **data only**

### Extensibility
- Adding tests = Adding data
- No code modification needed
- No breaking existing tests

---

## ✅ Quick Reference

| Task | How to Do It |
|------|-------------|
| Add test to existing suite | Append tuple to `cases` list |
| Create new test suite | Add new key to `TEST_SUITES` |
| Test different function | Set `'function'` field |
| Change suite description | Modify `'description'` field |
| Run all tests | `python normalizer_v2.py` |

---

**Bottom line**: Adding a test is now as simple as adding one line to a list! 🎯
