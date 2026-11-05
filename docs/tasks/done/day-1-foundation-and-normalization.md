# Day 1 - Foundation and Khmer Unicode Normalization

## Objective

Create the project foundation and implement the normalization contract required
by every later segmentation component.

## Dependencies

- Existing project tree from the architecture document.
- No dependency on the CRF model or external training data.

## Tasks

### D1.1 Configure the Python package

- Define package metadata and supported Python versions in `pyproject.toml`.
- Configure the console entry point for `khmer-tokenizer`.
- Keep runtime dependencies lightweight and CPU-only.
- Configure test, lint, and type-check commands.

### D1.2 Define shared constants and errors

- Define Khmer Unicode ranges and relevant Khmer symbols.
- Define BIES tags and zero-width/control-character constants.
- Define explicit exceptions for invalid configuration, malformed model data,
  and tokenizer setup failures.

### D1.3 Implement normalization

- Apply Unicode NFC normalization.
- Merge `U+17C1 + U+17B6` into `U+17C4`.
- Merge `U+17C1 + U+17B8` into `U+17BE`.
- Resolve the documented `U+17BB` register-shifter collision rules.
- Remove or replace deprecated characters:
  - Strip `U+17B4` and `U+17B5`.
  - Replace `U+17A3` with `U+17A2`.
  - Replace `U+17A4` with `U+17A2 + U+17B6`.
- Extract ZWSP (`U+200B`) boundary cues before removing zero-width and
  invisible control characters.
- Reorder each Khmer cluster into the documented canonical sequence.

### D1.4 Add configuration data

- Store normalization tables in `configs/normalizer_rules.json`.
- Keep transformation rules data-driven where practical.
- Validate configuration at load time and report invalid rules explicitly.

## Deliverables

- Working package metadata and command configuration.
- Implemented files under `khmer_tokenizer/normalizer/`.
- Shared constants and exception definitions.
- Normalizer rule configuration.
- Unit tests for every mandatory normalization transformation.

## Acceptance Criteria

- NFC-equivalent input produces identical normalized output.
- Split composite vowels are merged correctly.
- Deprecated Khmer characters are handled exactly as specified.
- ZWSP positions are retained as boundary metadata while ZWSP is absent from
  normalized text.
- Reordering does not detach a Coeng sequence or dependent vowel.
- Repeated or incomplete marks do not raise an unhandled exception.

## Verification

- Run focused normalizer tests.
- Run the configured formatter/linter on changed Python files.
- Run the configured type checker.

