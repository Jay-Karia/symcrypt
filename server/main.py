is_server_running = False

def start_server():
  global is_server_running

  if is_server_running:
    print("Server is already running.")
  else:
    print("Starting server...")
    is_server_running = True
