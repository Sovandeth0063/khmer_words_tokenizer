# Day 5 - Hardening, Documentation, and Release Readiness

## Objective

Resolve defects found during validation and prepare a reproducible, documented
MVP release without expanding into non-goal features.

## Dependencies

- All Day 1 through Day 4 deliverables.
- Fresh test, benchmark, and packaging results.

## Tasks

### D5.1 Fix correctness and reliability defects

- Address all failing P0 tests.
- Verify normalization before segmentation on every public path.
- Verify custom dictionary precedence on both engines.
- Verify no KCC loss or duplication during malformed-input handling.
- Verify thread-safe concurrent inference.
- Remove accidental heavy dependencies and unused runtime dependencies.

### D5.2 Finalize artifacts

- Generate the bundled Trie artifact.
- Generate or validate the CRF model artifact.
- Write accurate model metadata, training date, version, and measured metrics.
- Confirm dictionary and model files are packaged in the wheel.

### D5.3 Complete documentation

- Document installation and quickstart.
- Document `tokenize()`, `KhmerTokenizer`, engine selection, custom dictionary
  APIs, CLI options, and error behavior.
- Document supported Python versions and platform expectations.
- Document benchmark methodology and known limitations.
- Explicitly state that POS tagging, spelling correction, and translation are
  outside the project scope.

### D5.4 Package and release checks

- Build source and wheel distributions.
- Verify wheel contents and size against the 12 MB target.
- Run the package from a clean environment.
- Validate the console script after installation.
- Prepare the publish workflow without publishing unless explicitly approved.

### D5.5 Final sign-off

- Compare measured results with every PRD acceptance criterion.
- Record unmet targets as known limitations rather than claiming success.
- Confirm no secrets, local paths, corpora with restricted redistribution, or
  generated caches are included.

## Deliverables

- Hardened implementation.
- Complete user and API documentation.
- Validated model and lexicon artifacts.
- Buildable source and wheel distributions.
- Final acceptance checklist and benchmark results.

## Acceptance Criteria

- All P0 requirements pass.
- No unhandled malformed-input crashes occur in the supported API or CLI.
- Canonical example, custom dictionary behavior, and mixed-script behavior pass.
- Package installs cleanly on the supported Python range available for testing.
- Wheel contents, metadata, and entry point are correct.
- Any missed performance or accuracy target is clearly documented.

## Verification

- Run the full test, lint, and type-check suite.
- Build and install the wheel in a clean environment.
- Run the smoke test through both the Python API and CLI.
- Review the final diff for unrelated files and generated artifacts.

