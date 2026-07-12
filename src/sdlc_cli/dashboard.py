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


def _read_json_file(p: Path) -> dict | list | None:
    """Read a JSON file with resilient parsing for extra data."""
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        try:
            obj, _ = json.JSONDecoder().raw_decode(p.read_text(encoding="utf-8"))
            return obj
        except (json.JSONDecodeError, OSError):
            return None
    except OSError:
        return None


def _read_lines_file(p: Path, head: int | None = None, tail: int | None = None) -> list[str]:
    """Read lines from a text file."""
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


def read_state(run_dir: Path, sdlc_dir: Path | None = None) -> dict:
    """Read all state files into a single payload.

    run_dir: the active run directory (e.g. .sdlc/ or .sdlc/runs/<slug>/)
    sdlc_dir: the root .sdlc/ directory (for shared files like model-config.json)
    """
    if sdlc_dir is None:
        sdlc_dir = run_dir

    orch = _read_json_file(run_dir / "state" / "orchestrator.json") or {}
    trace = _read_json_file(run_dir / "state" / "agent-trace.json") or {"traces": []}

    pending = _read_json_file(run_dir / "queue" / "pending.json")
    active = _read_json_file(run_dir / "queue" / "active.json")
    completed = _read_json_file(run_dir / "queue" / "completed.json")

    model_config = _read_json_file(sdlc_dir / "model-config.json") or {}

    # Phase enablement (phase-config.json lives at the shared .sdlc/ root).
    enabled_map: dict[str, bool] = {}
    try:
        from .phases import (
            load_config as load_phase_config,
            load_custom_agents,
            phase_enabled_map,
        )

        phase_cfg = load_phase_config(sdlc_dir)
        custom = load_custom_agents(sdlc_dir)
        enabled_map = phase_enabled_map(phase_cfg, custom)
    except Exception:
        enabled_map = {}

    # Generate Mermaid diagram
    try:
        from .mermaid import generate_mermaid

        mermaid_src = generate_mermaid(orch, trace, model_config, enabled_map)
    except Exception:
        mermaid_src = ""

    return {
        "orchestrator": orch,
        "trace": trace,
        "queue": {
            "pending": len(pending) if isinstance(pending, list) else 0,
            "active": len(active) if isinstance(active, list) else 0,
            "completed": len(completed) if isinstance(completed, list) else 0,
        },
        "activity_log": _read_lines_file(run_dir / "state" / "activity-log.md", tail=30),
        "continuity": _read_lines_file(run_dir / "CONTINUITY.md", head=20),
        "model_config": model_config,
        "phase_enabled": enabled_map,
        "mermaid_src": mermaid_src,
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
    "STATUS.md",
    "model-config.json",
    "phase-config.json",
]

# Files that live at the shared .sdlc/ root rather than the run dir.
SHARED_ROOT_FILES = {"model-config.json", "phase-config.json"}


def get_mtimes(run_dir: Path, sdlc_dir: Path | None = None) -> dict[str, float]:
    """Return a dict of file -> mtime for all watched files."""
    if sdlc_dir is None:
        sdlc_dir = run_dir
    mtimes: dict[str, float] = {}
    for rel in WATCHED_FILES:
        # Shared config files live at sdlc root; everything else in run_dir
        base = sdlc_dir if rel in SHARED_ROOT_FILES else run_dir
        p = base / rel
        try:
            mtimes[rel] = p.stat().st_mtime if p.exists() else 0.0
        except OSError:
            mtimes[rel] = 0.0
    # Scan state/ and queue/ dirs for any additional modified files
    for subdir in ("state", "queue"):
        dp = run_dir / subdir
        if dp.is_dir():
            try:
                for f in dp.iterdir():
                    if f.is_file():
                        rp = f"{subdir}/{f.name}"
                        if rp not in mtimes:
                            mtimes[rp] = f.stat().st_mtime
            except OSError:
                pass
    return mtimes


# ---------------------------------------------------------------------------
# HTTP server — serves the single-page dashboard HTML
# ---------------------------------------------------------------------------


def _make_handler(ws_port: int) -> type:
    """Create an HTTP handler class with the WS port baked in."""

    class DashboardHTTPHandler(SimpleHTTPRequestHandler):
        """Serve the dashboard HTML for any request path."""

        def do_GET(self) -> None:  # noqa: N802
            if self.path.startswith("/static/"):
                # Serve static files from the 'static' subdirectory
                try:
                    # Build the full path to the requested file
                    static_dir = Path(__file__).parent / "static"
                    filepath = static_dir / self.path[8:]

                    if filepath.is_file():
                        self.send_response(200)
                        if self.path.endswith(".js"):
                            self.send_header("Content-Type", "application/javascript")
                        else:
                            self.send_header("Content-Type", self.guess_type(str(filepath)))
                        self.end_headers()
                        with open(filepath, 'rb') as f:
                            self.wfile.write(f.read())
                    else:
                        self.send_error(404, "File not found")
                except Exception as e:
                    self.send_error(500, f"Server error: {e}")
            else:
                # Serve the main dashboard HTML
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
    run_dir: Path,
    sdlc_dir: Path | None,
    clients: set,
) -> None:
    """Handle a single WebSocket connection."""
    clients.add(websocket)
    try:
        # Send initial state immediately
        state = read_state(run_dir, sdlc_dir)
        await websocket.send(json.dumps(state))
        # Keep connection alive — listen for pings/close
        async for _ in websocket:
            pass
    finally:
        clients.discard(websocket)


async def watch_and_broadcast(
    run_dir: Path,
    sdlc_dir: Path | None,
    clients: set,
    interval: float = 0.5,
) -> None:
    """Poll state files and broadcast to all clients on change."""
    last_mtimes = get_mtimes(run_dir, sdlc_dir)
    last_payload: str | None = None

    while True:
        await asyncio.sleep(interval)

        current_mtimes = get_mtimes(run_dir, sdlc_dir)
        if current_mtimes == last_mtimes:
            continue
        last_mtimes = current_mtimes

        state = read_state(run_dir, sdlc_dir)
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
    run_dir: Path,
    sdlc_dir: Path | None,
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
        lambda ws: ws_handler(ws, run_dir, sdlc_dir, clients),
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
        await watch_and_broadcast(run_dir, sdlc_dir, clients)


def serve(
    run_dir: Path,
    sdlc_dir: Path | None = None,
    port: int = 8420,
    open_browser: bool = True,
) -> None:
    """Blocking entry point — run the dashboard servers."""
    ws_port = port + 1
    try:
        asyncio.run(run_dashboard(run_dir, sdlc_dir, port, ws_port, open_browser))
    except KeyboardInterrupt:
        pass
