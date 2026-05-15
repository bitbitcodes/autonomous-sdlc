"""Real-time SDLC dashboard — WebSocket server + file watcher."""

from __future__ import annotations

import asyncio
import json
import logging
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread

from .dashboard_html import DASHBOARD_HTML

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# State reader — reads all .sdlc/ files into a single JSON-serializable dict
# ---------------------------------------------------------------------------


def read_state(sdlc_dir: Path) -> dict:
    """Read all .sdlc/ state files into a single payload."""

    def _read_json(rel: str) -> dict | list | None:
        p = sdlc_dir / rel
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def _read_lines(rel: str, head: int | None = None, tail: int | None = None) -> list[str]:
        p = sdlc_dir / rel
        if not p.exists():
            return []
        try:
            lines = p.read_text(encoding="utf-8").strip().splitlines()
        except OSError:
            return []
        if tail and len(lines) > tail:
            lines = lines[-tail:]
        if head and len(lines) > head:
            lines = lines[:head]
        return lines

    orch = _read_json("state/orchestrator.json") or {}
    trace = _read_json("state/agent-trace.json") or {"traces": []}

    pending = _read_json("queue/pending.json")
    active = _read_json("queue/active.json")
    completed = _read_json("queue/completed.json")

    model_config = _read_json("model-config.json") or {}

    return {
        "orchestrator": orch,
        "trace": trace,
        "queue": {
            "pending": len(pending) if isinstance(pending, list) else 0,
            "active": len(active) if isinstance(active, list) else 0,
            "completed": len(completed) if isinstance(completed, list) else 0,
        },
        "activity_log": _read_lines("state/activity-log.md", tail=30),
        "continuity": _read_lines("CONTINUITY.md", head=20),
        "model_config": model_config,
    }


# ---------------------------------------------------------------------------
# File change detector — polls mtime of watched files
# ---------------------------------------------------------------------------

WATCHED_FILES = [
    "state/orchestrator.json",
    "state/agent-trace.json",
    "state/activity-log.md",
    "queue/pending.json",
    "queue/active.json",
    "queue/completed.json",
    "CONTINUITY.md",
    "model-config.json",
]


def get_mtimes(sdlc_dir: Path) -> dict[str, float]:
    """Return a dict of file -> mtime for all watched files."""
    mtimes: dict[str, float] = {}
    for rel in WATCHED_FILES:
        p = sdlc_dir / rel
        try:
            mtimes[rel] = p.stat().st_mtime if p.exists() else 0.0
        except OSError:
            mtimes[rel] = 0.0
    return mtimes


# ---------------------------------------------------------------------------
# HTTP server — serves the single-page dashboard HTML
# ---------------------------------------------------------------------------


def _make_handler(ws_port: int) -> type:
    """Create an HTTP handler class with the WS port baked in."""

    class DashboardHTTPHandler(SimpleHTTPRequestHandler):
        """Serve the dashboard HTML for any request path."""

        def do_GET(self) -> None:  # noqa: N802
            html = DASHBOARD_HTML.replace(
                "/*WS_PORT*/8421", str(ws_port)
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        def log_message(self, format: str, *args: object) -> None:  # noqa: A002
            # Silence HTTP access logs
            pass

    return DashboardHTTPHandler


def start_http_server(port: int, ws_port: int) -> HTTPServer:
    """Start the HTTP server in a daemon thread."""
    handler_cls = _make_handler(ws_port)
    server = HTTPServer(("127.0.0.1", port), handler_cls)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


# ---------------------------------------------------------------------------
# WebSocket server — pushes state updates to connected browsers
# ---------------------------------------------------------------------------


async def ws_handler(
    websocket: object,
    sdlc_dir: Path,
    clients: set,
) -> None:
    """Handle a single WebSocket connection."""
    clients.add(websocket)
    try:
        # Send initial state immediately
        state = read_state(sdlc_dir)
        await websocket.send(json.dumps(state))
        # Keep connection alive — listen for pings/close
        async for _ in websocket:
            pass
    finally:
        clients.discard(websocket)


async def watch_and_broadcast(
    sdlc_dir: Path,
    clients: set,
    interval: float = 1.0,
) -> None:
    """Poll .sdlc/ files and broadcast state to all clients on change."""
    last_mtimes = get_mtimes(sdlc_dir)
    last_payload: str | None = None

    while True:
        await asyncio.sleep(interval)

        current_mtimes = get_mtimes(sdlc_dir)
        if current_mtimes == last_mtimes:
            continue
        last_mtimes = current_mtimes

        state = read_state(sdlc_dir)
        payload = json.dumps(state)

        # Only broadcast if the payload actually changed
        if payload == last_payload:
            continue
        last_payload = payload

        if clients:
            await asyncio.gather(
                *[c.send(payload) for c in clients.copy()],
                return_exceptions=True,
            )


async def run_dashboard(
    sdlc_dir: Path,
    http_port: int,
    ws_port: int,
    open_browser: bool = True,
) -> None:
    """Main async entry point — starts HTTP + WebSocket servers."""
    import websockets

    # Start HTTP server (serves HTML)
    start_http_server(http_port, ws_port)
    logger.info("HTTP server on http://127.0.0.1:%d", http_port)

    clients: set = set()

    # Start WebSocket server
    async with websockets.serve(
        lambda ws: ws_handler(ws, sdlc_dir, clients),
        "127.0.0.1",
        ws_port,
    ):
        logger.info("WebSocket server on ws://127.0.0.1:%d", ws_port)

        # Open browser in a background thread (non-blocking)
        if open_browser:
            Thread(
                target=lambda: webbrowser.open(f"http://127.0.0.1:{http_port}"),
                daemon=True,
            ).start()

        # Run file watcher loop
        await watch_and_broadcast(sdlc_dir, clients)


def serve(sdlc_dir: Path, port: int = 8420, open_browser: bool = True) -> None:
    """Blocking entry point — run the dashboard servers."""
    ws_port = port + 1
    try:
        asyncio.run(run_dashboard(sdlc_dir, port, ws_port, open_browser))
    except KeyboardInterrupt:
        pass
