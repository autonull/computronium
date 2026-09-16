"""``comp daemon`` — headless discovery engine with a lifecycle API (TODO30 8.9).

Same flags as ``comp continuous`` plus ``--port`` for the FastAPI/WS server.
``comp continuous`` remains as the legacy alias (one release).

Usage::

    comp daemon --target-cells 500 --limit-batches 30 --loop --sleep 15
    comp daemon --budget 5m --root artifacts/broad_map --port 8940
"""

from __future__ import annotations

import argparse
import logging

from computronium.autoscientist.daemon import (
    ContinuousDaemon,
    DaemonAlreadyRunningError,
)
from computronium.cli.continuous import _add_common_flags, _tee_log

logger = logging.getLogger("daemon")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="comp daemon", description=__doc__)
    _add_common_flags(parser)
    parser.add_argument(
        "--port",
        type=int,
        default=8940,
        help="port for the lifecycle/telemetry API server",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    logging.basicConfig(level=logging.INFO)
    if args.log_path is not None:
        _tee_log(args.log_path)
    try:
        daemon = ContinuousDaemon(args, port=args.port)
    except DaemonAlreadyRunningError:
        logger.exception("refusing to start: campaign root already owned")
        return 1
    daemon.serve()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
