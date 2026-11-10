"""Tests for benchmark measurements and quality metrics."""

from scripts.benchmark import run_benchmark


def test_benchmark_reports_runtime_metrics() -> None:
    """Verify runtime metrics are present and non-negative."""
    result = run_benchmark("ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា", iterations=1)
    assert result["tokens"] > 0
    assert result["mean_latency_ms"] >= 0
    assert result["p95_latency_ms"] >= 0
    assert result["broken_cluster_rate"] == 0.0


def test_benchmark_reports_quality_metrics_with_gold_tokens() -> None:
    """Verify gold tokens enable precision, recall, and boundary metrics."""
    result = run_benchmark(
        "ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា",
        iterations=1,
        expected_tokens=["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"],
    )
    assert result["word_f1"] == 1.0
    assert result["boundary_f1"] == 1.0
