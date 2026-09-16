"""Client for connecting to and sending payloads to the receiver's TCP server."""

import socket
import threading
from logger import log


_client_socket = None
_is_connected = False
_connection_thread = None


def connect_to_server(host: str, port: int = 5000):
    """
    Connect to the receiver's TCP server.

    Args:
        host: Receiver's IP address (e.g., "192.168.1.100" or "127.0.0.1:5000")
        port: Port number (default 5000)

    Returns:
        True if connected, False otherwise.
    """
    global _client_socket, _is_connected

    if _is_connected:
        log("Already connected to receiver.", "server_status_logger")
        return False

    # Parse host:port format if provided
    if ":" in host:
        host, port_str = host.rsplit(":", 1)
        try:
            port = int(port_str)
        except ValueError:
            log(f"Invalid port in address: {port_str}", "server_status_logger")
            return False

    try:
        _client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _client_socket.connect((host, port))
        _is_connected = True
        log(
            f"Connected to receiver at {host}:{port}",
            "server_status_logger",
        )
        return True
    except socket.error as exc:
        log(
            f"Failed to connect to {host}:{port}: {exc}",
            "server_status_logger",
        )
        return False


def send_payload(payload: bytes) -> bool:
    """
    Send encrypted payload to the connected receiver.

    Args:
        payload: Raw bytes to send

    Returns:
        True if sent, False otherwise.
    """
    global _client_socket, _is_connected

    if not _is_connected or _client_socket is None:
        log("Not connected to receiver. Connect first.", "server_status_logger")
        return False

    try:
        _client_socket.sendall(payload)
        log(
            f"Sent {len(payload)} bytes to receiver.",
            "server_status_logger",
        )
        return True
    except socket.error as exc:
        log(
            f"Failed to send payload: {exc}",
            "server_status_logger",
        )
        _is_connected = False
        return False


def disconnect():
    """Disconnect from the receiver's server."""
    global _client_socket, _is_connected

    if _client_socket is not None:
        try:
            _client_socket.close()
        except socket.error:
            pass

    _is_connected = False
    log("Disconnected from receiver.", "server_status_logger")
