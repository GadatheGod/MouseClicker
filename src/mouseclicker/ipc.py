"""IPC mechanism using Unix domain sockets."""

from __future__ import annotations

import json
import os
import socket
import threading
from typing import Any


class IPCServer:
    """Unix socket IPC server for Daemon communication.

    Attributes:
        socket_path: Path to the Unix socket file.
        is_running: Whether the server is currently listening.
    """

    def __init__(self, socket_path: str | None = None) -> None:
        self.socket_path = socket_path or "/tmp/mouseclicker.sock"
        self._server_socket: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._running = False
        self._handlers: dict[str, Any] = {}

    @property
    def is_running(self) -> bool:
        """Whether the server is currently running."""
        return self._running

    def start(self) -> None:
        """Start the IPC server."""
        if self._running:
            return

        # Clean up old socket file
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server_socket.bind(self.socket_path)
        self._server_socket.listen(1)
        self._server_socket.settimeout(1.0)
        self._running = True

        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the IPC server."""
        self._running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

    def handle_command(self, command: str) -> dict[str, Any]:
        """Handle an IPC command.

        Args:
            command: The command string (e.g. 'start', 'stop', 'status').

        Returns:
            Response dictionary.
        """
        parts = command.strip().split()
        action = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        if action == "start":
            return {"status": "ok", "action": "start"}
        elif action == "stop":
            return {"status": "ok", "action": "stop"}
        elif action == "status":
            return {"status": "ok", "running": self._running}
        elif action == "switch_profile":
            return {"status": "ok", "action": "switch_profile", "profile": args[0] if args else ""}
        elif action == "load_script":
            return {"status": "ok", "action": "load_script", "script": args[0] if args else ""}
        elif action == "set_jitter":
            return {"status": "ok", "action": "set_jitter", "args": args}
        elif action == "set_hotkey":
            return {"status": "ok", "action": "set_hotkey", "hotkey": args[0] if args else ""}
        else:
            return {"status": "error", "message": f"Unknown command: {action}"}

    def _accept_loop(self) -> None:
        """Accept incoming connections and handle commands."""
        while self._running:
            try:
                conn, _ = self._server_socket.accept()
                data = conn.recv(4096).decode("utf-8")
                if data:
                    response = self.handle_command(data)
                    conn.sendall(json.dumps(response).encode("utf-8"))
                conn.close()
            except (OSError, ConnectionError):
                continue


class IPCClient:
    """Unix socket IPC client for sending commands to the Daemon.

    Attributes:
        socket_path: Path to the Unix socket file.
    """

    def __init__(self, socket_path: str | None = None) -> None:
        self.socket_path = socket_path or "/tmp/mouseclicker.sock"

    def send_command(self, command: str) -> dict[str, Any]:
        """Send a command to the Daemon.

        Args:
            command: The command string.

        Returns:
            Response dictionary.
        """
        try:
            client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client_socket.connect(self.socket_path)
            client_socket.sendall(command.encode("utf-8"))
            response = client_socket.recv(4096).decode("utf-8")
            client_socket.close()
            return json.loads(response)
        except (ConnectionRefusedError, FileNotFoundError, OSError):
            return {"status": "error", "message": "Cannot connect to Daemon"}
