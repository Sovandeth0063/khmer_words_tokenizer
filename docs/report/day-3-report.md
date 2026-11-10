# Day 3 Report - CRF Pipeline, Overrides, and Public API

## Overview

Day 3 connected KCC sequences to BIES prediction and exposed the public
tokenizer API. The project now supports a default CRF + Trie path, an explicit
BiMM path, custom dictionary overrides, BIES assembly, and lightweight model
validation without adding heavy machine-learning dependencies.

## Completed Files

### CRF Components

#### `khmer_tokenizer/models/crf/features.py`

Extracts features for every KCC, including:

- Context from three KCCs before and after the current KCC
- Unigrams, bigrams, and trigrams
- Coeng presence
- Dependent-vowel presence
- Closing-sign indicators
- Trie forward and backward match lengths
- ZWSP boundary indicators

#### `khmer_tokenizer/models/crf/crf_engine.py`

Provides the BIES prediction engine. It:

- Validates the lightweight model artifact format
- Raises `MalformedModelError` for missing or corrupt explicit models
- Uses Trie matches to produce deterministic BIES tags
- Penalizes long phrase entries so lexical words are preferred
- Keeps inference state local and read-only

#### `khmer_tokenizer/models/crf/__init__.py`

Exports:

- `CRFEngine`
- `extract_features`

#### `pretrained/crf_khmer_base.crfsuite`

Contains the validated baseline model metadata used by the default public
tokenizer. The current model strategy is a lightweight Trie-backed BIES
baseline.

### Token Assembly

#### `khmer_tokenizer/postprocessor/assembler.py`

Converts KCC and BIES sequences into lexical tokens. It preserves clusters when
tags are incomplete or invalid instead of silently dropping them.

#### `khmer_tokenizer/postprocessor/__init__.py`

Exports `assemble_tokens`.

### Public API

#### `khmer_tokenizer/__init__.py`

Adds:

- `KhmerTokenizer`
- `tokenize()`
- `engine="crf"`
- `engine="bimm"`
- `add_word()`
- `remove_word()`
- `custom_dict_path`
- `model_path`

The canonical example now returns:

```python
["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"]
```

### Dataset Preparation

#### `scripts/build_kcc_dataset.py`

Converts space-segmented Khmer text into KCC-level BIES rows for future model
training.

Example:

```powershell
py scripts\build_kcc_dataset.py `
  --input data\corpora\raw\train.txt `
  --output data\corpora\processed\train.tsv
```

### Model Interface

#### `khmer_tokenizer/models/base.py`

Defines the abstract `BaseTokenizer` interface shared by tokenizer engines.

### Tests

#### `tests/test_crf_tokenizer.py`

Tests:

- BIES token assembly
- Invalid BIES sequence safety
- Canonical Khmer tokenization
- Custom dictionary overrides
- Engine selection
- Missing and corrupt model errors
- JSON model loading

## Current Usage

Use the default CRF + Trie engine:

```python
from khmer_tokenizer import tokenize

tokens = tokenize("ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា")
```

Use a tokenizer instance:

```python
from khmer_tokenizer import KhmerTokenizer

tokenizer = KhmerTokenizer()
tokenizer.add_word("ពាក្យផ្ទាល់ខ្លួន")
tokens = tokenizer.tokenize("ពាក្យផ្ទាល់ខ្លួន")
```

Select BiMM explicitly:

```python
tokenizer = KhmerTokenizer(engine="bimm")
```

## Test Result

The complete test suite passes:

```text
29 passed
```

Ruff also passes:

```text
All checks passed!
```

## Known Limitation

The current CRF implementation is a lightweight Trie-backed BIES baseline. It
does not yet load learned `python-crfsuite` weights or provide trained model
quality metrics. Full CRF training and benchmark evaluation remain later work.

## Day 3 Completion Status

Day 3 pipeline, overrides, and public API work is implemented and verified.
