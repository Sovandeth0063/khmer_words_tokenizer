"""
Module: benchmark.py
Purpose: Measure tokenizer latency and throughput as JSON.
Usage: python scripts\\benchmark.py --input data.txt --output benchmark.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import Counter
from pathlib import Path
from typing import Any, Optional

from tokenizer import KhmerTokenizer
from tokenizer.segmenter import segment_kcc


def _percentile(values: list[float], percentile: float) -> float:
    """Return a linear-interpolated percentile from measured values."""
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _f1(precision: float, recall: float) -> float:
    """Return the harmonic mean of precision and recall."""
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _word_metrics(predicted: list[str], expected: list[str]) -> dict[str, float]:
    """Calculate token precision, recall, and F1 using token counts."""
    predicted_counts = Counter(predicted)
    expected_counts = Counter(expected)
    correct = sum((predicted_counts & expected_counts).values())
    precision = correct / len(predicted) if predicted else 0.0
    recall = correct / len(expected) if expected else 0.0
    return {
        "word_precision": precision,
        "word_recall": recall,
        "word_f1": _f1(precision, recall),
    }


def _boundaries(tokens: list[str]) -> set[int]:
    """Return character offsets where token boundaries occur."""
    offset = 0
    result: set[int] = set()
    for token in tokens[:-1]:
        offset += len(token)
        result.add(offset)
    return result


def _boundary_f1(predicted: list[str], expected: list[str]) -> float:
    """Calculate F1 over predicted and expected character boundaries."""
    predicted_boundaries = _boundaries(predicted)
    expected_boundaries = _boundaries(expected)
    correct = len(predicted_boundaries & expected_boundaries)
    precision = correct / len(predicted_boundaries) if predicted_boundaries else 0.0
    recall = correct / len(expected_boundaries) if expected_boundaries else 0.0
    return _f1(precision, recall)


def _broken_cluster_rate(tokens: list[str]) -> float:
    """Return the fraction of tokens containing an unsafe Khmer cluster."""
    if not tokens:
        return 0.0
    broken = sum(
        any(cluster.endswith("\u17d2") for cluster in segment_kcc(token))
        for token in tokens
    )
    return broken / len(tokens)


def run_benchmark(
    text: str,
    engine: str = "crf",
    iterations: int = 5,
    expected_tokens: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Measure cold start, throughput, and P95 latency for one text."""
    if iterations < 1:
        raise ValueError("iterations must be at least 1")
    cold_start = time.perf_counter()
    tokenizer = KhmerTokenizer(engine=engine)
    cold_start_ms = (time.perf_counter() - cold_start) * 1000
    timings: list[float] = []
    token_count = 0
    for _ in range(iterations):
        started = time.perf_counter()
        tokens = tokenizer.tokenize(text)
        timings.append(time.perf_counter() - started)
        token_count = len(tokens)
    total_seconds = sum(timings)
    words_per_second = (
        token_count * iterations / total_seconds if total_seconds else 0.0
    )
    result: dict[str, Any] = {
        "engine": engine,
        "iterations": iterations,
        "characters": len(text),
        "tokens": token_count,
        "cold_start_ms": round(cold_start_ms, 3),
        "mean_latency_ms": round(statistics.mean(timings) * 1000, 3),
        "p95_latency_ms": round(_percentile(timings, 0.95) * 1000, 3),
        "words_per_second": round(words_per_second, 3),
        "word_precision": None,
        "word_recall": None,
        "word_f1": None,
        "boundary_f1": None,
        "broken_cluster_rate": _broken_cluster_rate(tokens),
        "quality_note": "Quality metrics require a gold-standard segmented corpus.",
    }
    if expected_tokens is not None:
        result.update(_word_metrics(tokens, expected_tokens))
        result["boundary_f1"] = _boundary_f1(tokens, expected_tokens)
        result["quality_note"] = "Metrics calculated against the supplied gold corpus."
    return result


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run the benchmark, and write JSON output."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--gold",
        type=Path,
        help="Optional gold file with one whitespace-separated tokenized line.",
    )
    parser.add_argument("--engine", choices=("crf", "bimm"), default="crf")
    parser.add_argument("--iterations", type=int, default=5)
    args = parser.parse_args(argv)
    text = args.input.read_text(encoding="utf-8-sig").rstrip("\r\n")
    expected_tokens = None
    if args.gold:
        gold_lines = args.gold.read_text(encoding="utf-8-sig").splitlines()
        expected_tokens = " ".join(gold_lines).split()
    result = run_benchmark(text, args.engine, args.iterations, expected_tokens)
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
