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

Days 1-5 are implemented as a release-ready MVP:

- Unicode NFC normalization
- Split composite-vowel merging
- Register-shifter collision handling
- Deprecated Khmer character cleanup
- Zero-width-space boundary extraction
- Khmer cluster mark reordering
- Focused normalization tests
- KCC segmentation and BiMM dictionary matching
- Trie dictionary preparation from the raw CSV
- CRF + Trie BIES baseline
- Public `tokenize()` and `KhmerTokenizer` APIs
- Custom dictionary overrides
- Dataset preparation for KCC-level BIES training
- Streaming command-line interface
- Edge-case tests and JSON benchmark output
- CI test, lint, type-check, and package-build workflows
- Wheel and source distribution packaging

The current CRF artifact is a deterministic Trie-backed BIES baseline. It is
not a trained `python-crfsuite` weight file, so quality targets require a
representative gold-standard corpus before they can be certified.

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

Install the latest local wheel:

```powershell
py -m pip install dist\khmer_tokenizer-0.1.1-py3-none-any.whl
```

## Quickstart

```python
from khmer_tokenizer import tokenize

tokens = tokenize("ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា")
print(tokens)
# ["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"]
```

Whitespace is not returned as a token by default. Preserve it when needed:

```python
tokens = tokenize("ក ខ", keep_whitespace=True)
# ["ក", " ", "ខ"]
```

Use the alternative BiMM engine:

```python
from khmer_tokenizer import KhmerTokenizer

tokenizer = KhmerTokenizer(engine="bimm")
tokens = tokenizer.tokenize("ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា")
```

Add a custom word:

```python
tokenizer = KhmerTokenizer()
tokenizer.add_word("ប្រទេសកម្ពុជា")
assert tokenizer.tokenize("ប្រទេសកម្ពុជា") == ["ប្រទេសកម្ពុជា"]
```

## Command-Line Usage

Read from standard input and write space-separated tokens:

```powershell
py -m khmer_tokenizer.cli
```

Process a file with the BiMM engine and write another file:

```powershell
khmer-tokenizer `
  --input data\input.txt `
  --output data\output.txt `
  --engine bimm `
  --delimiter " "
```

The CLI processes one line at a time. Invalid arguments return a non-zero
status and display an error message.

For a quick one-sentence result, use the helper script:

```powershell
py scripts\tokenize_text.py "ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា"
```

Output:

```json
["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"]
```

You can also run it without text and enter the sentence when prompted:

```powershell
py scripts\tokenize_text.py
```

## Browser Interface

To use a visual HTML interface instead of the terminal:

```powershell
py scripts\web_app.py
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765) in a browser. Enter Khmer
text, choose CRF or BiMM, and click **Tokenize text**. Press `Ctrl+C` in the
server terminal to stop it.

## Benchmarking

Run a repeatable JSON benchmark:

```powershell
py scripts\benchmark.py `
  --input data\benchmark.txt `
  --gold data\benchmark.gold.txt `
  --iterations 5 `
  --output benchmark.json
```

The optional gold file contains whitespace-separated expected tokens. Without
it, runtime metrics are reported but accuracy metrics are left as `null`.

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
- [End-to-end example](docs/architecture/example_end_to_end.md)
- [Day 5 release report](docs/report/day-5-report.md)

## Scope

This project focuses on Khmer lexical word segmentation. POS tagging,
syntactic parsing, spelling correction, translation, and sentiment analysis
are outside the project scope.