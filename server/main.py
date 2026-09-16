import socket
import threading

from logger import log

is_server_running = False
_server_socket = None
_server_thread = None
_connection_prompt_callback = None

APPROVAL_OK = b"APPROVED"
APPROVAL_REJECTED = b"REJECTED"


def register_connection_prompt(callback):
  global _connection_prompt_callback
  _connection_prompt_callback = callback


def create_server(host="0.0.0.0", port=5000):
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server_socket.bind((host, port))
  server_socket.listen(1)
  server_socket.settimeout(1.0)
  return server_socket


def _run_server(server_socket, host, port):
  global is_server_running

  log(f"TCP server listening on {host}:{port}.", "receiver_server_logger")

  while is_server_running:
    try:
      client_socket, client_address = server_socket.accept()
    except socket.timeout:
      continue
    except OSError:
      break

    with client_socket:
      if _connection_prompt_callback is not None:
        try:
          approved = bool(_connection_prompt_callback(client_address))
        except Exception as exc:
          log(
            f"Connection approval prompt failed: {exc}",
            "receiver_server_logger",
          )
          approved = False

        if not approved:
          log(
            "Incoming connection rejected by receiver.",
            "receiver_server_logger",
          )
          try:
            client_socket.sendall(APPROVAL_REJECTED)
          except OSError:
            pass
          continue

      log(
        f"Sender connected from {client_address[0]}:{client_address[1]}.",
        "receiver_server_logger",
      )

      try:
        client_socket.sendall(APPROVAL_OK)
      except OSError:
        log(
          "Could not send approval response to sender.",
          "receiver_server_logger",
        )
        continue

      log(
        "Incoming connection approved by receiver.",
        "receiver_server_logger",
      )

      while is_server_running:
        try:
          payload = client_socket.recv(4096)
        except OSError:
          break

        if not payload:
          log(
            "Sender disconnected from receiver.",
            "receiver_server_logger",
          )
          break

        log(
          f"Received {len(payload)} bytes from sender.",
          "receiver_server_logger",
        )

  try:
    server_socket.close()
  except OSError:
    pass


def start_server(host="0.0.0.0", port=5000):
  global is_server_running, _server_socket, _server_thread

  if is_server_running:
    log("Server is already running.", "receiver_server_logger")
    return

  try:
    _server_socket = create_server(host, port)
  except OSError as exc:
    log(
      f"Failed to start TCP server on {host}:{port}: {exc}",
      "receiver_server_logger",
    )
    return

  is_server_running = True
  _server_thread = threading.Thread(
    target=_run_server,
    args=(_server_socket, host, port),
    daemon=True,
  )
  _server_thread.start()


def stop_server():
  global is_server_running, _server_socket, _server_thread

  if not is_server_running:
    log("Server is not running.", "receiver_server_logger")
    return

  is_server_running = False

  if _server_socket is not None:
    try:
      _server_socket.close()
    except OSError:
      pass
    _server_socket = None

  _server_thread = None
  log("Server stopped.", "receiver_server_logger")
