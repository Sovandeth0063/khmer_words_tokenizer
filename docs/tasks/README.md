# Khmer Tokenizer - Five-Day Task Plan

This folder contains the implementation task breakdown for the `khmer-tokenizer`
project. The tasks are derived from:

- `docs/architecture/product_requirements_document.md`
- `docs/architecture/system_architecture.md`

The plan prioritizes a working core MVP within five days. Advanced packaging and
release work is included only after the tokenizer pipeline is functional.

## Task Files

| File | Focus | Expected result |
|---|---|---|
| [done/day-1-foundation-and-normalization.md](./done/day-1-foundation-and-normalization.md) | Project foundation and Unicode normalization | Completed: normalized Khmer text and reliable KCC-safe input |
| [done/day-2-segmentation-and-bimm.md](./done/day-2-segmentation-and-bimm.md) | Lexer, KCC segmenter, Trie, and BiMM | Completed: working dictionary-based tokenizer engine |
| [done/day-3-crf-pipeline-and-api.md](./done/day-3-crf-pipeline-and-api.md) | BIES features, CRF integration, and public API | Completed: default hybrid tokenizer pipeline |
| [done/day-4-cli-tests-and-performance.md](./done/day-4-cli-tests-and-performance.md) | CLI, edge cases, tests, and benchmarks | Implemented: CLI, tests, benchmarks, and CI |
| [done/day-5-hardening-and-release.md](./done/day-5-hardening-and-release.md) | Compatibility, packaging, documentation, and final verification | Implemented: release-ready MVP |

## Priority Rules

1. Complete all P0 requirements before optional P1 enhancements.
2. Preserve Khmer Character Clusters (KCC); no task may introduce dangling
   `U+17D2` Coeng marks or detached dependent vowels.
3. Keep the default runtime CPU-only and avoid PyTorch, TensorFlow, and CUDA.
4. Prefer deterministic behavior and explicit errors over silent fallback.
5. Record benchmark and evaluation results before claiming completion.

## Five-Day Definition of Done

- `tokenize("ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា")` returns
  `["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"]`.
- Unicode normalization handles NFC, split composite vowels, shifter rules,
  deprecated characters, canonical ordering, and ZWSP cues.
- KCC segmentation never breaks a Coeng sequence.
- URLs, emails, Latin text, punctuation, emojis, Arabic numbers, and Khmer
  numerals are preserved as atomic non-Khmer spans.
- The default CRF + Trie path and the BiMM fallback path are available.
- Custom dictionary words override statistical or dictionary segmentation.
- Public API, CLI, tests, packaging metadata, and documentation are present.
- Performance and memory measurements are captured against the PRD targets.
- Unsupported or malformed input produces a controlled, documented result.
