"""Tests for the local web tokenizer API."""

from __future__ import annotations

import json
from email.message import Message
from io import BytesIO
from typing import Optional

from scripts.web_app import TokenizerHandler


class _FakeTokenizerHandler(TokenizerHandler):
    """In-memory TokenizerHandler harness requiring no network sockets."""

    def __init__(self, path: str, body: bytes = b"") -> None:
        self.path = path
        headers = Message()
        headers["Content-Length"] = str(len(body))
        self.headers = headers
        self.rfile = BytesIO(body)
        self.wfile = BytesIO()
        self.status: Optional[int] = None
        self.response_headers: dict[str, str] = {}

    def send_response(self, code: int, message: Optional[str] = None) -> None:
        self.status = code

    def send_header(self, keyword: str, value: str) -> None:
        self.response_headers[keyword] = value

    def end_headers(self) -> None:
        pass


def _call_post(payload: dict[str, object]) -> tuple[Optional[int], dict[str, object]]:
    """Invoke TokenizerHandler.do_POST with a JSON payload."""
    handler = _FakeTokenizerHandler(
        "/api/tokenize", json.dumps(payload).encode("utf-8")
    )
    handler.do_POST()
    return handler.status, json.loads(handler.wfile.getvalue().decode("utf-8"))


def test_web_api_supports_khmer_only_option() -> None:
    """Verify /api/tokenize honors khmer_only and validates its type."""
    status, body = _call_post(
        {"text": "ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា !", "engine": "crf"}
    )
    assert status == 200
    assert body["tokens"] == ["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា", "!"]

    status, body = _call_post(
        {
            "text": "ខ្ញុំស្រឡាញ់ប្រទេសកម្ពុជា !",
            "engine": "crf",
            "khmer_only": True,
        }
    )
    assert status == 200
    assert body["tokens"] == ["ខ្ញុំ", "ស្រឡាញ់", "ប្រទេស", "កម្ពុជា"]

    status, body = _call_post(
        {"text": "ក", "engine": "crf", "khmer_only": "yes"}
    )
    assert status == 400
    assert "error" in body
