# SymCrypt
A secure file transfer and messaging tool that hides data inside mathematical equations and transfers it seamlessly over TCP sockets.

## Features

- **Secure message and file transfers** — send text or arbitrary files to a receiver over TCP.
- **Equation-based payloads** — represents encrypted message and file data as mathematical equations.
- **GPG-protected keys** — encrypts the generated secret key with the recipient's GPG public key.
- **Sender and receiver interfaces** — connect to a receiver, approve incoming connections, inspect payloads, decrypt messages, and save recovered files.
- **Equation preview** — view generated equations in the sender before sharing a payload.

### Welcome Screen
![Welcome Screen](/public/welcome.png)

### Sender Mode
![Sender Mode](/public/sender.png)

### Receiver Mode
![Receiver Mode](/public/receiver.png)

## Setup

1. Install `uv` from [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
2. Clone the repository and navigate to the project directory
3. Install dependencies:
   ```bash
   uv sync
   ```
4. Run the application:
   ```bash
   uv run main.py
   ```

## Contributing

Read the [contributing guidelines](CONTRIBUTING.md) for more information.

### Architecture

![FigJam Image](/public/figjam.png)
