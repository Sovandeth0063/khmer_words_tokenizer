# Khmer Word Tokenizer

Lightweight, CPU-only Khmer text normalization and word-tokenization library.

Khmer text is commonly written without spaces between lexical words. This
project is designed to provide a production-ready tokenizer based on:

- Khmer Unicode normalization
- Khmer Character Cluster (KCC) preservation
- Trie dictionary matching
- Bi-Directional Maximal Matching (BiMM)
- Linear-Chain CRF BIES boundary prediction

## Project Status

Day 1 foundation is implemented:

- Unicode NFC normalization
- Split composite-vowel merging
- Register-shifter collision handling
- Deprecated Khmer character cleanup
- Zero-width-space boundary extraction
- Khmer cluster mark reordering
- Focused normalization tests

The remaining tokenizer engines, CLI behavior, model artifacts, and release
packaging are planned in the [five-day task plan](docs/tasks/README.md).

## Requirements

- Python 3.9 or newer
- No GPU or deep-learning framework is required

## Installation

Install the package in editable mode with development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

If the Python Launcher is used on Windows:

```powershell
py -m pip install -e ".[dev]"
```

## Current Normalization API

```python
from khmer_tokenizer import normalize

result = normalize("ក\u200bខ")
print(result.text)
print(result.zwsp_positions)
```

The result contains the cleaned normalized text and the positions where
zero-width spaces were found before cleanup.

## Run Tests

Run the Day 1 normalization tests:

```powershell
python -m pytest tests\test_normalizer.py -v
```

Or use `py` on Windows:

```powershell
py -m pytest tests\test_normalizer.py -v
```

## Project Structure

```text
khmer_tokenizer/   Library source
configs/           Normalization and model configuration
data/              Dictionaries and corpus data
docs/              Architecture, requirements, and implementation tasks
pretrained/        Model and lexicon artifacts
scripts/            Dataset, training, and benchmark scripts
tests/             Automated tests
```

## Documentation

- [Product requirements](docs/architecture/product_requirements_document.md)
- [System architecture](docs/architecture/system_architecture.md)
- [Implementation tasks](docs/tasks/README.md)

## Scope

This project focuses on Khmer lexical word segmentation. POS tagging,
syntactic parsing, spelling correction, translation, and sentiment analysis
are outside the project scope.