import socket
import threading

from logger import log

is_server_running = False
_server_socket = None
_server_thread = None


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
      log(
        f"Sender connected from {client_address[0]}:{client_address[1]}.",
        "receiver_server_logger",
      )

      try:
        payload = client_socket.recv(4096)
      except OSError:
        continue

      if payload:
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
