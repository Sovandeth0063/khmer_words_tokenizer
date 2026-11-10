"""Release metadata and packaging contract tests."""

import json
from pathlib import Path

from khmer_tokenizer import KhmerTokenizer, tokenize

ROOT = Path(__file__).parents[1]


def test_canonical_api_and_bimm_smoke_test() -> None:
    """Verify both public engines tokenize the canonical input safely."""
    text = "ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា"
    expected = ["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"]
    assert tokenize(text) == expected
    bimm_tokens = KhmerTokenizer(engine="bimm").tokenize(text)
    assert "".join(bimm_tokens) == text
    assert bimm_tokens[:2] == expected[:2]


def test_model_metadata_is_explicit_and_valid() -> None:
    """Verify the release metadata records the baseline limitations."""
    metadata = json.loads(
        (ROOT / "pretrained" / "model_metadata.json").read_text(
            encoding="utf-8"
        )
    )
    assert metadata["project_version"] == "0.1.1"
    assert metadata["strategy"] == "trie-bies-baseline"
    assert metadata["training_status"]
    assert metadata["metrics"]["broken_cluster_rate"] == 0.0
