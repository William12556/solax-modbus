# Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
"""
HTTP telemetry server for Solax inverter monitoring.

Provides a read-only HTTP interface to live inverter telemetry. The server reads
from a thread-safe shared state populated by the polling loop; it never contacts
the inverter directly.

Design: design-9b7e2c4a-component_presentation_server.md
"""

from __future__ import annotations

import ipaddress
import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Default HTTP port for telemetry server (non-privileged, avoids common conflict)
DEFAULT_HTTP_PORT: int = 8181

# Default RFC 1918 private networks plus link-local (USB-gadget direct path)
DEFAULT_ALLOWED_NETWORKS: List[ipaddress.IPv4Network] = [
    ipaddress.IPv4Network("10.0.0.0/8"),
    ipaddress.IPv4Network("172.16.0.0/12"),
    ipaddress.IPv4Network("192.168.0.0/16"),
    ipaddress.IPv4Network("169.254.0.0/16"),
]


class StateHolder:
    """
    Thread-safe holder for the latest telemetry snapshot.

    The Application domain instantiates this class and shares it between the
    polling loop (writer) and the HTTP server (reader). All access is guarded
    by a single lock.
    """

    def __init__(self) -> None:
        """Initialize with an empty snapshot and a lock."""
        self._lock = threading.Lock()
        self._snapshot: Dict[str, Any] = {}

    def get(self) -> Dict[str, Any]:
        """
        Return a copy of the most recent telemetry snapshot.

        Returns:
            Shallow copy of the snapshot dictionary.
        """
        with self._lock:
            return self._snapshot.copy()

    def set(self, data: Dict[str, Any]) -> None:
        """
        Replace the telemetry snapshot.

        Args:
            data: New telemetry dictionary from poll_inverter().
        """
        with self._lock:
            self._snapshot = data.copy()


class TelemetryRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for telemetry endpoints.

    Routes:
        /               - Static dashboard HTML
        /api/telemetry  - Current telemetry snapshot as JSON
        /api/history    - Downsampled rollup series as JSON (30-day window)
        /api/history/12mo - Daily rollup series as JSON (365-day window)
        Other paths     - 404 Not Found
        Disallowed IP   - 403 Forbidden
    """

    # Suppress default stderr logging
    def log_message(self, format: str, *args: Any) -> None:
        """Route HTTP logs through the module logger."""
        logger.debug("HTTP %s - %s", self.address_string(), format % args)

    def do_GET(self) -> None:
        """Handle GET requests with IP filtering and routing."""
        try:
            # Check source IP against allowlist
            if not self._client_allowed():
                logger.warning(
                    "Rejected request from disallowed IP: %s", self.client_address[0]
                )
                self._send_error(403, "Forbidden")
                return

            # Route request
            if self.path == "/":
                self._serve_dashboard()
            elif self.path == "/api/telemetry":
                self._serve_telemetry()
            elif self.path == "/api/history":
                self._serve_history()
            elif self.path == "/api/history/12mo":
                self._serve_history_12mo()
            else:
                self._send_error(404, "Not Found")

        except Exception as e:
            logger.error("Unhandled error in request handler: %s", e, exc_info=True)
            self._send_error(500, "Internal Server Error")

    def _client_allowed(self) -> bool:
        """Check if the client IP is in any allowed network."""
        try:
            client_ip = ipaddress.IPv4Address(self.client_address[0])
            allowed_networks = getattr(self.server, "allowed_networks", [])
            return any(client_ip in network for network in allowed_networks)
        except (ValueError, TypeError) as e:
            logger.debug("Could not parse client address: %s", e)
            return False

    def _serve_dashboard(self) -> None:
        """Serve the static dashboard HTML."""
        template_path: Path = getattr(self.server, "template_path", None)
        if template_path is None or not template_path.exists():
            logger.error("Dashboard template not found: %s", template_path)
            self._send_error(500, "Dashboard template not found")
            return

        try:
            content = template_path.read_text(encoding="utf-8")
            self._send_response(200, "text/html", content.encode("utf-8"))
        except Exception as e:
            logger.error("Error reading dashboard template: %s", e, exc_info=True)
            self._send_error(500, "Error reading dashboard")

    def _serve_telemetry(self) -> None:
        """Serve the current telemetry snapshot as JSON."""
        state: StateHolder = getattr(self.server, "state", None)
        if state is None:
            self._send_error(500, "State holder not configured")
            return

        try:
            snapshot = state.get()
            content = json.dumps(snapshot, indent=2)
            self._send_response(200, "application/json", content.encode("utf-8"))
        except (TypeError, ValueError) as e:
            logger.error("JSON serialization failed: %s", e, exc_info=True)
            self._send_error(500, "Serialization error")

    def _serve_history(self) -> None:
        """Serve downsampled rollup series as JSON for all primary metrics."""
        # Metrics to include in the history response
        metrics = ("pv_power", "battery_power", "battery_soc", "grid_power_total")
        # 30-day window in seconds
        window_seconds = 30 * 24 * 3600

        store = getattr(self.server, "store", None)

        # Build the response object with all metrics
        result: Dict[str, List[Dict[str, Any]]] = {}

        for metric in metrics:
            if store is None:
                result[metric] = []
            else:
                try:
                    result[metric] = store.query_history(metric, window_seconds)
                except ValueError as e:
                    logger.warning("query_history failed for %s: %s", metric, e)
                    result[metric] = []
                except Exception as e:
                    logger.error(
                        "Unexpected error in query_history for %s: %s",
                        metric,
                        e,
                        exc_info=True,
                    )
                    result[metric] = []

        try:
            content = json.dumps(result)
            self._send_response(200, "application/json", content.encode("utf-8"))
        except (TypeError, ValueError) as e:
            logger.error("History JSON serialization failed: %s", e, exc_info=True)
            self._send_error(500, "Serialization error")

    def _serve_history_12mo(self) -> None:
        """Serve daily rollup series as JSON for all primary metrics (365-day window)."""
        # Metrics to include in the history response
        metrics = ("pv_power", "battery_power", "battery_soc", "grid_power_total")

        store = getattr(self.server, "store", None)

        # Build the response object with all metrics
        result: Dict[str, List[Dict[str, Any]]] = {}

        for metric in metrics:
            if store is None:
                result[metric] = []
            else:
                try:
                    result[metric] = store.query_history_12mo(metric)
                except ValueError as e:
                    logger.warning("query_history_12mo failed for %s: %s", metric, e)
                    result[metric] = []
                except Exception as e:
                    logger.error(
                        "Unexpected error in query_history_12mo for %s: %s",
                        metric,
                        e,
                        exc_info=True,
                    )
                    result[metric] = []

        try:
            content = json.dumps(result)
            self._send_response(200, "application/json", content.encode("utf-8"))
        except (TypeError, ValueError) as e:
            logger.error("History 12mo JSON serialization failed: %s", e, exc_info=True)
            self._send_error(500, "Serialization error")

    def _send_response(self, status: int, content_type: str, body: bytes) -> None:
        """Send an HTTP response with headers and body."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, message: str) -> None:
        """Send an error response."""
        body = message.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class TelemetryServer:
    """
    Background HTTP server for telemetry endpoints.

    Owns the ThreadingHTTPServer lifecycle on a dedicated thread. The server
    reads telemetry from shared state; it never contacts the inverter.
    """

    def __init__(
        self,
        state: StateHolder,
        bind_host: str = "0.0.0.0",
        port: int = DEFAULT_HTTP_PORT,
        allowed_networks: Optional[List[ipaddress.IPv4Network]] = None,
        store: Optional[Any] = None,
    ) -> None:
        """
        Initialize the telemetry server.

        Args:
            state: Shared, lock-guarded telemetry snapshot holder.
            bind_host: Interface to bind (default all interfaces).
            port: TCP port (non-privileged default 8181).
            allowed_networks: Permitted source ranges (None = DEFAULT_ALLOWED_NETWORKS).
            store: Optional TimeSeriesStore for /api/history (None yields empty series).
        """
        self.state = state
        self.bind_host = bind_host
        self.port = port
        self.allowed_networks = (
            allowed_networks if allowed_networks is not None else DEFAULT_ALLOWED_NETWORKS
        )
        self.store = store

        # Resolve dashboard template path relative to this module
        self.template_path = Path(__file__).parent / "templates" / "dashboard.html"

        self._httpd: Optional[ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """
        Bind the server and begin serving on a background thread.

        Raises:
            OSError: Port unavailable. Logged; the polling loop should continue.
        """
        try:
            self._httpd = ThreadingHTTPServer(
                (self.bind_host, self.port), TelemetryRequestHandler
            )
            # Attach context for the handler to access
            self._httpd.state = self.state  # type: ignore[attr-defined]
            self._httpd.allowed_networks = self.allowed_networks  # type: ignore[attr-defined]
            self._httpd.template_path = self.template_path  # type: ignore[attr-defined]
            self._httpd.store = self.store  # type: ignore[attr-defined]

            self._thread = threading.Thread(
                target=self._httpd.serve_forever, name="TelemetryServer", daemon=True
            )
            self._thread.start()
            logger.info(
                "Telemetry server started on http://%s:%d/", self.bind_host, self.port
            )
        except OSError as e:
            logger.error(
                "Failed to bind telemetry server on port %d: %s",
                self.port,
                e,
                exc_info=True,
            )
            raise

    def stop(self) -> None:
        """
        Stop serving and release the socket.

        Calls httpd.shutdown() then httpd.server_close(), then joins the server
        thread. Idempotent; safe if not started.
        """
        if self._httpd is not None:
            logger.info("Stopping telemetry server...")
            try:
                self._httpd.shutdown()
                self._httpd.server_close()
            except Exception as e:
                logger.error("Error during server shutdown: %s", e, exc_info=True)

        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=5.0)
            if self._thread.is_alive():
                logger.warning("Telemetry server thread did not stop within timeout")

        self._httpd = None
        self._thread = None
        logger.info("Telemetry server stopped")
