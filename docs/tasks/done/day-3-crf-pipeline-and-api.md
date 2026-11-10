# Day 3 - CRF Pipeline, Overrides, and Public API

## Objective

Connect KCC sequences to BIES prediction and expose the supported library API.

## Dependencies

- Day 1 normalization.
- Day 2 lexer, KCC segmenter, Trie, and BiMM.
- CRF training data or a documented minimal model artifact.

## Tasks

### D3.1 Prepare KCC-level BIES data

- Convert word-segmented corpus entries into KCC sequences.
- Generate valid `B`, `I`, `E`, and `S` labels.
- Keep train, development, and test splits separate.
- Validate that every label sequence reconstructs the original words exactly.

### D3.2 Implement feature extraction

- Add KCC unigram, bigram, and trigram features.
- Add a `[-3, +3]` context window.
- Add base consonant series, subscript, dependent-vowel, and closing-sign
  indicators.
- Add Trie forward/current/backward match-length features.
- Add the ZWSP boundary feature.

### D3.3 Integrate the CRF engine

- Load the packaged CRF model.
- Predict valid BIES sequences.
- Expose controlled errors for missing, corrupt, or incompatible model files.
- Keep inference thread-safe by avoiding shared mutable request state.

### D3.4 Implement custom dictionary overrides

- Convert custom dictionary matches into locked `B-I-E` or `S` spans.
- Apply overrides consistently to both CRF and BiMM paths.
- Reject or report custom words that cannot be represented as valid KCC spans.

### D3.5 Implement token assembly and public API

- Reconstruct words from BIES tags.
- Preserve non-Khmer spans and optional whitespace behavior.
- Export `tokenize()` and `KhmerTokenizer`.
- Support the default CRF engine and explicit `engine="bimm"`.

## Deliverables

- Dataset conversion script.
- CRF feature extractor and engine wrapper.
- Custom override behavior.
- BIES assembler.
- Public package API.
- End-to-end tests for the canonical Khmer example.

## Acceptance Criteria

- The canonical example returns:
  `["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"]`.
- Invalid BIES transitions are handled deterministically and do not silently
  drop KCCs.
- Custom dictionary words remain intact with either engine.
- The default engine is CRF + Trie; BiMM is selectable explicitly.
- Missing or corrupt model artifacts produce a clear documented exception.
- Tokenizer instances are safe for concurrent read-only inference.

## Verification

- Run end-to-end tokenizer tests.
- Run dataset reconstruction checks.
- Run type checking and linting for all changed modules.
