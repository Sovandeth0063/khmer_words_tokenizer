"""
Module: web_app.py
Purpose: Serve the local Khmer tokenizer web interface.
Usage: py scripts\\web_app.py
"""
from __future__ import annotations

import argparse
import json
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).parents[1]
WEB_ROOT = ROOT / "web"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tokenizer import KhmerTokenizer


class TokenizerHandler(BaseHTTPRequestHandler):
    """Serve the web page and tokenize JSON requests."""

    def _send(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        """Send an HTTP response with its content type."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        """Serve the HTML page and stylesheet."""
        path = urlparse(self.path).path
        files = {
            "/": ("tokenizer.html", "text/html; charset=utf-8"),
            "/tokenizer.html": ("tokenizer.html", "text/html; charset=utf-8"),
            "/tokenizer.css": ("tokenizer.css", "text/css; charset=utf-8"),
        }
        if path not in files:
            self._send(HTTPStatus.NOT_FOUND, b"Not found", "text/plain; charset=utf-8")
            return
        filename, content_type = files[path]
        self._send(HTTPStatus.OK, (WEB_ROOT / filename).read_bytes(), content_type)

    def do_POST(self) -> None:
        """Tokenize JSON input and return JSON output."""
        if urlparse(self.path).path != "/api/tokenize":
            self._send(HTTPStatus.NOT_FOUND, b"Not found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload: dict[str, Any] = json.loads(self.rfile.read(length))
            text = payload["text"]
            engine = payload.get("engine", "crf")
            khmer_only = payload.get("khmer_only", False)
            if (
                not isinstance(text, str)
                or not isinstance(engine, str)
                or not isinstance(khmer_only, bool)
            ):
                raise TypeError(
                    "text and engine must be strings; khmer_only must be a boolean"
                )
            tokens = KhmerTokenizer(engine=engine).tokenize(
                text, khmer_only=khmer_only
            )
            body = json.dumps({"tokens": tokens}, ensure_ascii=False).encode("utf-8")
            self._send(HTTPStatus.OK, body, "application/json; charset=utf-8")
        except (TypeError, ValueError, KeyError, json.JSONDecodeError) as error:
            body = json.dumps({"error": str(error)}).encode("utf-8")
            self._send(HTTPStatus.BAD_REQUEST, body, "application/json; charset=utf-8")

    def log_message(self, format: str, *args: object) -> None:
        """Keep the local server output quiet."""


def main() -> None:
    """Start the local web server."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), TokenizerHandler)
    print(f"Open http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
