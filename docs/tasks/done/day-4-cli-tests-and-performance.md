# Day 4 - CLI, Edge Cases, Tests, and Performance

> **Status: Implemented.** Runtime and quality measurements are available. The
> PRD performance and quality targets still require a representative benchmark
> corpus before they can be certified.

## Objective

Make the tokenizer usable from the command line, cover production edge cases,
and measure the required quality and resource targets.

## Dependencies

- Completed API and both tokenizer engines from Day 3.
- Test corpus and dictionary/model artifacts.

## Tasks

### D4.1 Implement the CLI

- Support stdin and stdout streaming.
- Support `--input` and `--output` files.
- Support configurable `--delimiter`.
- Support engine selection.
- Support large-file processing without loading the complete corpus into memory.
- Add the documented multi-core processing option only if it preserves output
  order and safe tokenizer isolation.
- Return non-zero exit codes with useful error messages for invalid arguments.

### D4.2 Complete edge-case coverage

- Mixed Khmer and Latin text.
- URLs and email addresses.
- Arabic and Khmer numerals, including decimals.
- Emojis and Khmer punctuation.
- ZWSP and other zero-width controls.
- Repeated Coeng marks and incomplete clusters.
- Empty input, whitespace-only input, and very long input.
- OOV words and proper nouns.

### D4.3 Add evaluation and benchmark tooling

- Measure Word Precision, Word Recall, Word F1, Boundary F1, and Broken Cluster
  Rate.
- Measure CRF and BiMM throughput.
- Measure P95 latency for a 1,000-character paragraph.
- Measure cold-start time, active RSS memory, and wheel size where available.
- Emit machine-readable benchmark output for repeatability.

### D4.4 Add CI checks

- Run tests, lint, and type checks.
- Validate supported Python versions as available in CI.
- Ensure model and dictionary artifacts are included in test/package builds.

## Deliverables

- CLI implementation and CLI tests.
- Edge-case test suite.
- Evaluation and benchmark scripts.
- CI workflow configuration.
- Initial performance and quality report stored as test/benchmark output.

## Acceptance Criteria

- CLI output is deterministic and matches library output.
- Streaming mode handles input larger than available working memory.
- Broken Cluster Rate is 0% on the edge-case suite.
- CRF and BiMM measurements are reported against their respective PRD targets:
  25,000 and 60,000 words/sec.
- CRF quality is measured against 95% Word F1 and 97.5% Boundary F1 targets.
- Failures are visible through test failures, exit codes, or explicit errors.

## Verification

- Run the complete test suite.
- Run CLI tests through stdin, stdout, and file input/output.
- Run the benchmark suite at least twice and record stable results.

## Implementation Notes

- `khmer_tokenizer.cli` streams input line by line from stdin or a file.
- `scripts/benchmark.py` reports JSON runtime metrics and accepts an optional
  whitespace-segmented `--gold` file for quality metrics.
- Edge cases and CLI behavior are covered by `tests/test_edge_cases.py` and
  `tests/test_cli.py`.
- CI runs tests, Ruff, and mypy on supported Python versions.
