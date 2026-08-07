import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from src.mouseclicker.ipc import IPCServer, IPCClient


class TestIPCServer:
    """Tests for IPC Unix socket server."""

    def test_ipc_server_init(self):
        """Should initialize with socket path."""
        with tempfile.NamedTemporaryFile(suffix=".sock", delete=False) as f:
            socket_path = f.name

        try:
            server = IPCServer(socket_path)
            assert server.socket_path == socket_path
        finally:
            os.unlink(socket_path)

    def test_ipc_server_start(self):
        """Should start listening on socket."""
        with tempfile.NamedTemporaryFile(suffix=".sock", delete=False) as f:
            socket_path = f.name

        try:
            server = IPCServer(socket_path)
            server.start()
            assert server.is_running is True
            server.stop()
        finally:
            if os.path.exists(socket_path):
                os.unlink(socket_path)

    def test_ipc_server_stop(self):
        """Should stop listening on socket."""
        with tempfile.NamedTemporaryFile(suffix=".sock", delete=False) as f:
            socket_path = f.name

        try:
            server = IPCServer(socket_path)
            server.start()
            server.stop()
            assert server.is_running is False
        finally:
            if os.path.exists(socket_path):
                os.unlink(socket_path)

    def test_ipc_server_handle_start_command(self):
        """Should handle start command."""
        with tempfile.NamedTemporaryFile(suffix=".sock", delete=False) as f:
            socket_path = f.name

        try:
            server = IPCServer(socket_path)
            server.start()
            response = server.handle_command("start")
            assert response["status"] == "ok"
            assert response["action"] == "start"
            server.stop()
        finally:
            if os.path.exists(socket_path):
                os.unlink(socket_path)

    def test_ipc_server_handle_stop_command(self):
        """Should handle stop command."""
        with tempfile.NamedTemporaryFile(suffix=".sock", delete=False) as f:
            socket_path = f.name

        try:
            server = IPCServer(socket_path)
            server.start()
            response = server.handle_command("stop")
            assert response["status"] == "ok"
            assert response["action"] == "stop"
            server.stop()
        finally:
            if os.path.exists(socket_path):
                os.unlink(socket_path)

    def test_ipc_server_handle_status_command(self):
        """Should handle status command."""
        with tempfile.NamedTemporaryFile(suffix=".sock", delete=False) as f:
            socket_path = f.name

        try:
            server = IPCServer(socket_path)
            server.start()
            response = server.handle_command("status")
            assert response["status"] == "ok"
            assert "running" in response
            server.stop()
        finally:
            if os.path.exists(socket_path):
                os.unlink(socket_path)

    def test_ipc_server_handle_unknown_command(self):
        """Should return error for unknown command."""
        with tempfile.NamedTemporaryFile(suffix=".sock", delete=False) as f:
            socket_path = f.name

        try:
            server = IPCServer(socket_path)
            server.start()
            response = server.handle_command("unknown")
            assert response["status"] == "error"
            server.stop()
        finally:
            if os.path.exists(socket_path):
                os.unlink(socket_path)

    def test_ipc_server_handle_switch_profile(self):
        """Should handle switch_profile command."""
        with tempfile.NamedTemporaryFile(suffix=".sock", delete=False) as f:
            socket_path = f.name

        try:
            server = IPCServer(socket_path)
            server.start()
            response = server.handle_command("switch_profile gaming")
            assert response["status"] == "ok"
            server.stop()
        finally:
            if os.path.exists(socket_path):
                os.unlink(socket_path)


class TestIPCClient:
    """Tests for IPC Unix socket client."""

    def test_ipc_client_init(self):
        """Should initialize with socket path."""
        with tempfile.NamedTemporaryFile(suffix=".sock", delete=False) as f:
            socket_path = f.name

        try:
            client = IPCClient(socket_path)
            assert client.socket_path == socket_path
        finally:
            os.unlink(socket_path)

    @patch("socket.socket")
    def test_send_command(self, mock_socket):
        """Should send command and receive response."""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        mock_sock.recv.return_value = json.dumps({"status": "ok", "action": "start"}).encode()

        client = IPCClient("/tmp/test.sock")
        response = client.send_command("start")
        assert response["status"] == "ok"
        assert response["action"] == "start"

    @patch("socket.socket")
    def test_send_command_error(self, mock_socket):
        """Should handle connection error."""
        mock_socket.side_effect = ConnectionRefusedError()

        client = IPCClient("/tmp/test.sock")
        response = client.send_command("start")
        assert response["status"] == "error"
