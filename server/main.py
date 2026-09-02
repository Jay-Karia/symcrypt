from logger import log

is_server_running = False

def start_server():
  global is_server_running

  if is_server_running:
    log("Server is already running.", "receiver_server_logger")
  else:
    print("Starting the server...")
    is_server_running = True
