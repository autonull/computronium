"""SEC Watch: Monitor SEC loop progress via HTTP.

Run:
    uv run python -m computronium.experiment.sec_watch --port 8080 --dir results/sec
"""

from __future__ import annotations

import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


class WatchHandler(BaseHTTPRequestHandler):
    """HTTP handler for SEC watch endpoint."""

    watch_dir: Path = Path("results/sec")

    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
            return

        if self.path == "/portfolio":
            self._serve_json(self.watch_dir / "portfolio.json")
            return

        if self.path == "/map":
            self._serve_json(self.watch_dir / "map.json")
            return

        if self.path == "/census":
            self._serve_json(self.watch_dir / "census.json")
            return

        if self.path == "/cells":
            self._serve_jsonl(self.watch_dir / "cells.jsonl")
            return

        if self.path == "/":
            self._serve_dashboard()
            return

        self.send_response(404)
        self.end_headers()

    def _serve_json(self, path: Path) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if path.exists():
            self.wfile.write(path.read_bytes())
        else:
            self.wfile.write(b"{}")

    def _serve_jsonl(self, path: Path) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if path.exists():
            lines = path.read_text().strip().split("\n")
            data = [json.loads(line) for line in lines if line.strip()]
            self.wfile.write(json.dumps(data).encode())
        else:
            self.wfile.write(b"[]")

    def _serve_dashboard(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        html = self._generate_dashboard()
        self.wfile.write(html.encode())

    def _generate_dashboard(self) -> str:
        portfolio_path = self.watch_dir / "portfolio.json"
        map_path = self.watch_dir / "map.json"
        cells_path = self.watch_dir / "cells.jsonl"

        portfolio = json.loads(portfolio_path.read_text()) if portfolio_path.exists() else {}
        map_data = json.loads(map_path.read_text()) if map_path.exists() else {}
        cells = []
        if cells_path.exists():
            for line in cells_path.read_text().strip().split("\n"):
                if line.strip():
                    cells.append(json.loads(line))

        # Track status
        tracks_html = ""
        for track in portfolio.get("tracks", []):
            tracks_html += f"""
            <tr>
                <td>{track['track']}</td>
                <td>{track['rank']}</td>
                <td>{track['last_result']}</td>
                <td>{track['kill_rule']}</td>
                <td>cells: {track['budget_used'].get('cells', 0)}, seeds: {track['budget_used'].get('seeds', 0)}</td>
                <td>{'⚠️' if track['contention'] else '✅'}</td>
            </tr>
            """

        # Recent cells
        recent_cells = cells[-20:] if cells else []
        cells_html = ""
        for cell in recent_cells:
            status = cell.get("status", cell.get("verdict", "?"))
            val_acc = cell.get("val_acc", cell.get("metrics", {}).get("val_acc", "N/A"))
            if isinstance(val_acc, float):
                val_acc = f"{val_acc:.4f}"
            cells_html += f"""
            <tr>
                <td>{cell.get('track', '?')}</td>
                <td>{cell.get('credit', cell.get('primitive', '?'))}</td>
                <td>{cell.get('seed', '?')}</td>
                <td>{status}</td>
                <td>{val_acc}</td>
                <td>{cell.get('walltime_s', 0):.1f}s</td>
            </tr>
            """

        # Map summary
        primitives = map_data.get("primitives", {})
        status_counts = {}
        for p in primitives.values():
            s = p.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1

        map_html = ""
        for status, count in sorted(status_counts.items()):
            map_html += f"<li>{status}: {count}</li>"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SEC Watch Dashboard</title>
            <meta http-equiv="refresh" content="10">
            <style>
                body {{ font-family: monospace; margin: 20px; background: #1a1a1a; color: #e0e0e0; }}
                h1 {{ color: #4ec9b0; }}
                h2 {{ color: #dcdcaa; border-bottom: 1px solid #333; padding-bottom: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #333; padding: 8px; text-align: left; }}
                th {{ background: #2d2d2d; color: #4ec9b0; }}
                tr:nth-child(even) {{ background: #252526; }}
                .status-claim {{ color: #4ec9b0; font-weight: bold; }}
                .status-coordinate {{ color: #dcdcaa; }}
                .status-defect {{ color: #f44747; }}
                .status-pass {{ color: #4ec9b0; }}
                .status-unavailable {{ color: #808080; }}
                .surprise {{ color: #dcdcaa; font-weight: bold; }}
                .refresh-note {{ color: #808080; font-size: 0.8em; }}
            </style>
        </head>
        <body>
            <h1>🔬 SEC Loop Watch Dashboard</h1>
            <p class="refresh-note">Auto-refreshes every 10s | {time.strftime('%Y-%m-%d %H:%M:%S')}</p>

            <h2>📊 Portfolio</h2>
            <p>Session: {portfolio.get('session_count', 0)} | Active: {portfolio.get('active_track', 'R1')} | Last: {portfolio.get('last_session', 'never')}</p>
            <table>
                <tr><th>Track</th><th>Rank</th><th>Last Result</th><th>Kill Rule</th><th>Budget Used</th><th>Contention</th></tr>
                {tracks_html}
            </table>

            <h2>🗺️ Capability Map</h2>
            <p>Total primitives tracked: {len(primitives)}</p>
            <ul>{map_html}</ul>

            <h2>📋 Recent Cells (last 20)</h2>
            <table>
                <tr><th>Track</th><th>Primitive/Credit</th><th>Seed</th><th>Status</th><th>Val Acc</th><th>Walltime</th></tr>
                {cells_html}
            </table>

            <h2>🔗 API Endpoints</h2>
            <ul>
                <li><a href="/portfolio">/portfolio</a> - Portfolio JSON</li>
                <li><a href="/map">/map</a> - Capability Map JSON</li>
                <li><a href="/census">/census</a> - Census JSON</li>
                <li><a href="/cells">/cells</a> - All Cells JSON</li>
                <li><a href="/health">/health</a> - Health check</li>
            </ul>
        </body>
        </html>
        """


def run_watch_server(port: int, watch_dir: Path) -> None:
    """Run the watch HTTP server."""
    WatchHandler.watch_dir = watch_dir
    server = HTTPServer(("", port), WatchHandler)
    print(f"SEC Watch server running on http://localhost:{port}")
    print(f"Watching directory: {watch_dir}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="SEC Watch - monitor SEC loop progress")
    parser.add_argument("--port", type=int, default=8080, help="Port to serve on")
    parser.add_argument("--dir", type=Path, default=Path("results/sec"), help="Directory to watch")
    args = parser.parse_args()

    run_watch_server(args.port, args.dir)


if __name__ == "__main__":
    main()