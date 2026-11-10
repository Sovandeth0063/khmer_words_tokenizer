# Day 5 Report - Hardening and Release Readiness

## Overview

Day 5 prepares the Khmer tokenizer as a versioned, documented, CPU-only MVP.
The release keeps the deterministic Trie-backed BIES baseline clearly
separate from a trained CRF model.

## Completed Work

- Updated package version to `0.1.1`.
- Added MIT license and package author metadata.
- Added packaged model metadata with explicit baseline limitations.
- Updated the README with installation, API, CLI, benchmark, scope, and
  documentation guidance.
- Added release smoke tests for both CRF and BiMM engines.
- Kept dictionary and model artifacts configured as package data.
- Preserved explicit errors for malformed CRF model files.

## Artifact Metadata

The current model artifact is:

```text
strategy: trie-bies-baseline
training_status: deterministic baseline; not trained CRF weights
broken_cluster_rate: 0.0
```

Accuracy metrics remain `null` until a representative gold-standard corpus is
provided. This is documented rather than presented as a passing quality claim.

## Verification

Release checks completed:

```powershell
py -m pytest -q
py -m ruff check .
py -m build
```

Results:

```text
40 passed in 10.67s
All checks passed!
Successfully built khmer_tokenizer-0.1.1.tar.gz
Successfully built khmer_tokenizer-0.1.1-py3-none-any.whl
```

The wheel is 506,062 bytes and contains the tokenizer package, dictionary,
CRF artifact, normalization rules, and model metadata. No Python cache files
are included, and the wheel is below the 12 MB target.

The rebuilt wheel installed successfully in a clean virtual environment.
Both the Python API and the installed console script produced the canonical
tokenization.

The local mypy executable remains blocked by the Windows application-control
policy. The CI workflow still runs the configured type check.

## Scope

The project provides Khmer lexical word segmentation. POS tagging, spelling
correction, translation, sentiment analysis, and syntactic parsing are not
included.

## Day 5 Completion Status

Day 5 implementation is complete. Release publication remains intentionally
manual; the publish workflow only builds and uploads a package artifact when
started explicitly.
