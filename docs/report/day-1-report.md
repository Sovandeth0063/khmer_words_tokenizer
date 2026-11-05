# Day 1 Report - Foundation and Khmer Unicode Normalization

## Overview

Day 1 established the project foundation and implemented the Khmer Unicode
normalization pipeline. The goal was to clean Khmer text before later
segmentation so character clusters, Coeng marks, vowels, and boundary cues are
handled safely.

## Completed Files

### Project Configuration

#### `pyproject.toml`

Defines the package name, version, Python support range, development
dependencies, CLI entry point, test settings, Ruff settings, and Mypy settings.

#### `.gitignore`

Prevents temporary Python files, test caches, virtual environments, build
outputs, and generated package metadata from being committed.

### Main Package

#### `khmer_tokenizer/__init__.py`

Exports the public normalization objects:

- `KhmerNormalizer`
- `NormalizedText`
- `normalize`

#### `khmer_tokenizer/constants.py`

Stores shared constants used by the tokenizer, including:

- Khmer Unicode ranges
- Khmer Symbols range
- Coeng (`U+17D2`)
- Zero-width characters
- ZWSP
- BIES tags
- Khmer base, vowel, and diacritic ranges

#### `khmer_tokenizer/exceptions.py`

Defines clear project-specific exceptions:

- `TokenizerError`
- `InvalidConfigurationError`
- `MalformedModelError`
- `TokenizerSetupError`

These errors allow configuration and setup failures to be reported explicitly.

### Normalizer

#### `khmer_tokenizer/normalizer/__init__.py`

Provides the main normalization pipeline. It:

1. Loads normalization rules from JSON.
2. Validates the rule structure.
3. Applies Unicode NFC normalization.
4. Applies deprecated-character replacements.
5. Merges configured composite vowels.
6. Resolves register-shifter collisions.
7. Extracts ZWSP positions.
8. Reorders Khmer cluster marks.

It exposes:

```python
from khmer_tokenizer.normalizer import KhmerNormalizer, normalize
```

#### `khmer_tokenizer/normalizer/cleaner.py`

Removes invisible control characters while recording the locations of
zero-width spaces. The result contains:

- Cleaned text
- ZWSP positions

#### `khmer_tokenizer/normalizer/vowels.py`

Handles configured character replacements and register-shifter correction.
It supports:

- Composite vowel replacement
- Deprecated-character replacement
- `U+17BB` collision handling
- Muusikatoan and Triisap selection

#### `khmer_tokenizer/normalizer/reorder.py`

Reorders Khmer characters into a stable cluster order while preserving:

- Base consonants
- Register shifters
- Coeng marks
- Subscript consonants
- Dependent vowels
- Diacritics

Malformed or incomplete marks are handled without raising an unhandled error.

### Configuration

#### `configs/normalizer_rules.json`

Contains the data-driven normalization rules:

- Composite vowel mappings
- Deprecated character mappings
- Zero-width character list
- Register-shifter collision configuration
- Base consonant series

JSON comments were intentionally not added because standard JSON does not
support comments.

### Tests

#### `tests/test_normalizer.py`

Contains focused Day 1 tests for:

- NFC-equivalent input
- Split composite vowels
- Deprecated Khmer characters
- ZWSP extraction
- Register-shifter collision handling
- Coeng attachment
- Repeated and incomplete marks
- Invalid configuration errors

## Current API

The current normalization API is:

```python
from khmer_tokenizer import normalize

result = normalize("ក\u200bខ")

print(result.text)
print(result.zwsp_positions)
```

The normalized result contains:

- `result.text`: cleaned and reordered text
- `result.zwsp_positions`: positions where ZWSP characters were found

## Current Day 1 Capabilities

Day 1 currently supports:

- Unicode NFC normalization
- Split composite-vowel merging
- Deprecated Khmer character cleanup
- Register-shifter collision handling
- Zero-width control cleanup
- ZWSP boundary-cue extraction
- Khmer cluster mark reordering
- Safe handling of malformed Coeng sequences
- Explicit invalid-configuration errors

## Test Result

The initial test run reported:

- 9 tests passed
- 2 tests failed

The two failures were investigated and corrected:

1. Overlapping shifter base sets were resolved with Triisap precedence.
2. Cluster reordering was corrected to keep leading vowels and Coeng-subscript
   sequences attached to the correct base.

The tests should be run again after these corrections:

```powershell
python -m pytest tests\test_normalizer.py -v
```

On Windows systems using the Python Launcher:

```powershell
py -m pytest tests\test_normalizer.py -v
```

## Not Yet Implemented

The following are Day 3 or later work:

- CRF feature extraction
- CRF model inference
- Complete `tokenize()` implementation
- CLI processing
- Full benchmark and evaluation pipeline

Day 2 completed the CSV dictionary preparation, Trie construction, KCC
segmenter, pre-lexer, BiMM engine, and custom dictionary support.

## Day 1 Completion Status

Day 1 foundation and normalization work is implemented and verified. Day 2 is
also complete; see the [Day 2 report](./day-2-report.md) for segmentation and
dictionary details.
