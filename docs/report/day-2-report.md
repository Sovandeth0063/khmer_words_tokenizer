# Day 2 Report - Lexer, KCC, Trie, and BiMM

## Overview

Day 2 implemented the deterministic segmentation foundation for the Khmer
tokenizer. The project can now split Khmer text into safe Khmer Character
Clusters (KCCs), preserve non-Khmer spans, load dictionary words, and perform
Bi-Directional Maximal Matching (BiMM).

## Completed Files

### Segmentation

#### `khmer_tokenizer/segmenter/kcc.py`

Splits Khmer text into Khmer Character Clusters. It keeps these parts together:

- Base consonants
- Register shifters
- Coeng marks
- Subscript consonants
- Dependent vowels
- Diacritics

It also handles incomplete and repeated Coeng marks without crashing.

#### `khmer_tokenizer/segmenter/lexer.py`

Splits input into typed spans:

- Khmer text
- Passthrough text
- Whitespace
- Punctuation

It recognizes and preserves URLs, email addresses, Latin words, Arabic
numbers, decimals, and Khmer numerals before Khmer segmentation.

#### `khmer_tokenizer/segmenter/__init__.py`

Exports the segmentation helpers:

- `LexSpan`
- `lex`
- `segment_kcc`

### Dictionary Model

#### `khmer_tokenizer/models/trie.py`

Implements a prefix Trie for dictionary matching. It supports:

- Adding words
- Removing words
- Longest KCC matching
- Loading newline-separated word lists
- Loading `word,pos` CSV files
- Loading custom dictionary files
- Checking whether a word exists

The POS column is ignored for tokenization because the tokenizer only needs the
word column.

#### `khmer_tokenizer/models/bimm.py`

Implements Bi-Directional Maximal Matching:

- Forward maximal matching
- Backward maximal matching
- Fewer-token conflict resolution
- Unknown singleton tie-breaking
- Custom dictionary loading
- `add_word()` and `remove_word()`
- Mixed Khmer and non-Khmer tokenization

#### `khmer_tokenizer/models/__init__.py`

Exports:

- `Trie`
- `BiMMTokenizer`

### Dictionary Preparation

#### `scripts/prepare_dictionary.py`

Converts the raw Khmer dictionary CSV into a clean newline-separated word list.
It:

- Reads the `word` column
- Removes empty words
- Removes duplicate words
- Sorts the output
- Writes the Trie source file

The source dictionary is:

```text
data/raw/khmer_dictionary.csv
```

The generated Trie word list is:

```text
data/dictionaries/chuon_nath_dict.txt
```

The current generated dictionary contains 101,134 unique words.

### Tests

#### `tests/test_kcc.py`

Tests:

- Khmer cluster segmentation
- Coeng and subscript preservation
- No dangling Coeng marks
- Malformed mark safety

#### `tests/test_bimm.py`

Tests:

- Trie longest matching
- Custom word insertion and removal
- CSV dictionary loading
- Custom dictionary file loading
- Preservation of URLs, numbers, and Latin text

## Current Usage

Prepare the dictionary:

```powershell
py scripts\prepare_dictionary.py `
  --input data\raw\khmer_dictionary.csv `
  --output data\dictionaries\chuon_nath_dict.txt
```

Use the BiMM tokenizer:

```python
from khmer_tokenizer.models import BiMMTokenizer, Trie

trie = Trie.from_file("data/dictionaries/chuon_nath_dict.txt")
tokenizer = BiMMTokenizer(trie)
tokens = tokenizer.tokenize("ប្រទេសកម្ពុជា")
```

Add a custom word:

```python
tokenizer.add_word("ពាក្យផ្ទាល់ខ្លួន")
```

## Test Result

The Day 1 and Day 2 focused test suite passed:

```text
20 passed
```

Ruff also passed for the Day 2 implementation:

```text
All checks passed!
```

Run the tests again with:

```powershell
py -m pytest tests\test_normalizer.py tests\test_kcc.py tests\test_bimm.py -v
```

## Current Day 2 Capabilities

Day 2 currently supports:

- Safe Khmer Character Cluster segmentation
- Mixed-script pre-lexing
- URL and email preservation
- Number and decimal preservation
- Khmer numeral preservation
- Trie dictionary matching
- CSV dictionary loading
- Custom dictionary words
- BiMM segmentation
- Deterministic matching conflict resolution

## Known Limitation

BiMM follows the dictionary-first rule and selects the segmentation with fewer
tokens. If the dictionary contains a compound entry such as
`ប្រទេសកម្ពុជា`, BiMM may return it as one token. The CRF engine planned for Day
3 will provide more precise lexical boundary prediction.

## Not Yet Implemented

The following work remains for Day 3 or later:

- CRF feature extraction
- CRF model inference
- Public `tokenize()` API integration
- Full custom dictionary behavior across all engines
- CLI processing
- Evaluation metrics
- Performance benchmarks
- Packaging and release validation

## Day 2 Completion Status

Day 2 segmentation and BiMM work is implemented and verified. The completed
task file is archived at:

```text
docs/tasks/done/day-2-segmentation-and-bimm.md
```
