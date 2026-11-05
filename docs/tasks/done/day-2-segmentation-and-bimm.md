# Day 2 - Lexer, KCC Segmenter, Trie, and BiMM

## Objective

Build the deterministic segmentation foundation and a complete dictionary-based
fallback engine that can operate without the CRF model.

## Dependencies

- Day 1 normalization and constants.
- Chuon Nath dictionary input in `data/dictionaries/`.

## Tasks

### D2.1 Implement the pre-lexer

- Isolate URLs before punctuation handling.
- Isolate email addresses.
- Preserve Latin words and mixed-script spans.
- Preserve Arabic numbers, decimals such as `12.5`, and Khmer numerals.
- Preserve emojis, punctuation, and configured whitespace behavior.
- Return typed spans or an equivalent explicit representation so Khmer spans
  cannot be confused with passthrough spans.

### D2.2 Implement KCC chunking

- Implement deterministic KCC matching for Khmer consonants and independent
  vowels.
- Include register shifters, subscripts, dependent vowels, signs, and
  diacritics in the correct cluster.
- Handle at most the supported number of Coeng-subscript sequences without
  splitting valid clusters.
- Ensure malformed sequences terminate safely and remain observable to callers.

### D2.3 Implement the Trie

- Load the Chuon Nath dictionary.
- Build or load a prefix Trie keyed by KCC sequences.
- Support longest forward match lookup.
- Support custom word insertion and removal.
- Support loading custom words from `custom_dict_path`.
- Ensure custom entries take precedence over base dictionary entries.

### D2.4 Implement BiMM

- Implement forward maximal matching.
- Implement backward maximal matching.
- Resolve disagreements using the architecture rule:
  fewer total words first, then fewer single-KCC unknown tokens.
- Preserve non-Khmer spans without dictionary processing.

## Deliverables

- Lexer implementation.
- KCC segmenter implementation.
- Trie implementation and dictionary loading.
- BiMM engine with `engine="bimm"` support.
- Unit tests for KCC integrity, Trie matching, custom words, and BiMM choices.

## Acceptance Criteria

- `ប្រទេស` is represented as `["ប្រ", "ទេ", "ស"]`.
- No output token contains a dangling `U+17D2`.
- URLs, emails, numbers, Latin text, punctuation, and emojis survive unchanged.
- `.add_word()` preserves a registered word as one token.
- `.remove_word()` removes only the requested custom entry.
- BiMM reaches at least the PRD baseline of 84% Word F1 and 89% Boundary F1
  on the available evaluation subset, or records a documented reason and
  measured result if the corpus is unavailable.

## Verification

- Run KCC, Trie, and BiMM tests.
- Add malformed Unicode and repeated-Coeng cases.
- Run a small benchmark for dictionary lookup and BiMM throughput.

