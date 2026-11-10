# Day 5 - Hardening, Documentation, and Release Readiness

> **Status: Implemented.** Publication remains manual and requires explicit
> approval.

## Completed

- Correctness and malformed-input behavior reviewed.
- Both CRF and BiMM public paths verified.
- Model metadata and package resources finalized.
- Installation, API, CLI, benchmark, scope, and limitation documentation
  completed.
- Versioned package metadata and MIT license added.
- Release smoke tests added.
- CI and package-build workflows prepared.

## Known Limitations

- The CRF artifact is a deterministic Trie-backed BIES baseline, not trained
  `python-crfsuite` weights.
- Accuracy targets require a representative gold-standard corpus.
- Performance targets require repeated runs on the target benchmark corpus.

## Verification

```powershell
py -m pytest -q
py -m ruff check .
py -m build
```
