"""Local read-only KORA trace viewer, bound to loopback only."""
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlsplit

from .viewer import discover_runs, render_html


def create_handler(base_dir: Path, *, run_ids=None):
    """Handler factory for testing; exposes no filesystem writes or directory browsing."""
    base_dir = Path(base_dir)
    initial_html = render_html([], live=True).encode("utf-8")

    class TraceHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/":
                self._send(200, initial_html, "text/html; charset=utf-8")
            elif path == "/api/traces":
                runs, warnings = discover_runs(base_dir, run_ids=run_ids)
                data = json.dumps({"runs": runs, "warnings": warnings,
                                   "updated_utc": datetime.now(timezone.utc).isoformat()},
                                  ensure_ascii=False, allow_nan=False).encode("utf-8")
                self._send(200, data, "application/json; charset=utf-8")
            else:
                self._send(404, b"Not found", "text/plain; charset=utf-8")

        def _send(self, status, content, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy",
                             "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self';")
            self.end_headers()
            self.wfile.write(content)

        def do_POST(self):
            self._send(405, b"Read only", "text/plain; charset=utf-8")

        def log_message(self, fmt, *args):
            pass

    return TraceHandler


def serve_trace_explorer(base_dir: Path, *, port: int = 8765, run_ids=None) -> None:
    """Run until interrupted. No external access: loopback is not configurable."""
    if not 1 <= port <= 65535:
        raise ValueError("--port must be 1..65535")
    server = ThreadingHTTPServer(("127.0.0.1", port), create_handler(base_dir, run_ids=run_ids))
    print(f"KORA Trace Explorer: http://127.0.0.1:{port}", flush=True)
    print(f"Read-only trace directory: {base_dir}", flush=True)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
