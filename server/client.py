"""Client for connecting to and sending payloads to the receiver's TCP server."""

import socket
import threading
from tkinter import messagebox

from logger import log


_client_socket = None
_is_connected = False
_monitor_stop_event = threading.Event()
_connection_monitor_thread = None

_APPROVAL_OK = b"APPROVED"
_APPROVAL_REJECTED = b"REJECTED"
_APPROVAL_TIMEOUT_SECONDS = 30


def _monitor_server_connection():
    global _client_socket, _is_connected

    while not _monitor_stop_event.is_set() and _is_connected and _client_socket is not None:
        try:
            data = _client_socket.recv(1)
        except socket.timeout:
            continue
        except OSError:
            break

        if not data:
            log(
                "Receiver stopped the server. Connection closed.",
                "server_status_logger",
            )
            break

    _is_connected = False
    _monitor_stop_event.set()


def _start_connection_monitor():
    global _connection_monitor_thread

    _monitor_stop_event.clear()
    _connection_monitor_thread = threading.Thread(
        target=_monitor_server_connection,
        daemon=True,
    )
    _connection_monitor_thread.start()


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

    if not messagebox.askyesno(
        "Connect to Receiver",
        f"A connection request will be sent to {host}. Continue?",
    ):
        log("Connection cancelled by sender.", "server_status_logger")
        return False

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
        _client_socket.settimeout(_APPROVAL_TIMEOUT_SECONDS)

        approval = _client_socket.recv(len(_APPROVAL_OK))
        if approval == _APPROVAL_REJECTED:
            raise socket.error("Connection was rejected by receiver.")
        if approval != _APPROVAL_OK:
            raise socket.error("Connection was not approved by receiver.")

        _client_socket.settimeout(1.0)
        _is_connected = True
        _start_connection_monitor()
        log(
            f"Connected to receiver at {host}:{port}",
            "server_status_logger",
        )
        return True
    except socket.error as exc:
        log(
            f"Failed to connect to receiver: {exc}",
            "server_status_logger",
        )
        return False


def send_payload(payload: bytes) -> bool:
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

    if not _is_connected:
        log("Not connected to receiver.", "server_status_logger")
        return

    _monitor_stop_event.set()

    if _client_socket is not None:
        try:
            _client_socket.close()
        except socket.error:
            pass

    _is_connected = False
    log("Disconnected from receiver.", "server_status_logger")
