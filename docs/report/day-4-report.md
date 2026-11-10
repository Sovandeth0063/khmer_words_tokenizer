# Day 4 Report - CLI, Edge Cases, Tests, and Performance

## Overview

Day 4 is implemented. The project now provides a streaming CLI, production
edge-case coverage, benchmark JSON output, optional gold-corpus quality
metrics, and CI checks.

## Current Status

### Implemented

- `khmer_tokenizer/cli.py` supports stdin/stdout, files, delimiters, and CRF or
  BiMM selection.
- `scripts/benchmark.py` reports cold start, mean latency, P95 latency,
  throughput, broken-cluster rate, and optional precision/recall/F1 metrics.
- `tests/test_edge_cases.py` covers mixed text, controls, empty input, and
  malformed Coeng input.
- `tests/test_cli.py` covers streaming, file I/O, engine selection, and invalid
  arguments.
- `.github/workflows/test.yml` runs tests, Ruff, and mypy.
- `.github/workflows/publish.yml` builds and uploads the package artifact.

### Remaining Measurement Work

The benchmark tooling is ready, but PRD targets such as 95% Word F1,
97.5% Boundary F1, and the throughput targets need a representative
gold-standard corpus and repeated benchmark runs. They are not claimed based
on the small smoke test.

## Verification

The existing project checks were run successfully:

```text
py -m pytest -q
38 passed in 8.34s
```

```text
py -m ruff check .
All checks passed!
```

The benchmark smoke test produced runtime JSON including throughput,
P95 latency, and broken-cluster rate. The local mypy command could not run
because the installed mypy extension was blocked by the Windows application
control policy; CI will run the configured type check.

## Day 4 Completion Status

Day 4 task tracking is archived in
[`docs/tasks/done/day-4-cli-tests-and-performance.md`](../tasks/done/day-4-cli-tests-and-performance.md).
Implementation is complete. Performance and quality certification remain
data-dependent follow-up work.
