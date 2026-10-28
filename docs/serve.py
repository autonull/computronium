"""Serve ``docs/`` as the site root.

``docs/index.html`` uses document-relative links, so the site is correct only
when ``docs/`` is the server root. This keeps the command short::

    uv run python docs/serve.py [--port 8000]

"""

from __future__ import annotations

import argparse
import contextlib
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DOCS = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="bind address")
    parser.add_argument("--port", type=int, default=8000, help="bind port")
    args = parser.parse_args(argv)

    handler = partial(SimpleHTTPRequestHandler, directory=str(DOCS))
    with ThreadingHTTPServer((args.host, args.port), handler) as server:
        print(f"serving {DOCS} at http://{args.host}:{args.port}/")
        with contextlib.suppress(KeyboardInterrupt):
            server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
