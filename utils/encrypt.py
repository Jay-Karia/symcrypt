import random
import json
from concurrent.futures import ThreadPoolExecutor
import utils.gpg
import os
import utils.points
import sympy as sp
from logger import log
import server.client as client

x = sp.Symbol('x')
DEFAULT_CHUNK_SIZE = 8
MAX_WORKERS = min(32, max(1, os.cpu_count() or 1))
MAX_PREVIEW_CHUNKS = 20
MAX_DEBUG_CHUNKS = 50

def char_to_ascii(char):
    return ord(char)

def generate_secret_key(length):
    if length <= 0:
        return []

    # Use unique integer x-values to keep interpolation stable and unambiguous.
    # Rounded floats can create duplicate keys and break recovery.
    # Grow the pool with the input so large messages/files are not rejected by
    # a fixed key-space ceiling while every x-value remains unique.
    key_pool_size = max(10_000_000, length * 2)
    return random.sample(range(1, key_pool_size + 1), length)

def generate_base_salt_equation(secret_key):
    if not secret_key:
        return sp.Integer(0)

    base_salt_equation = sp.Integer(1)
    for key in secret_key:
        exact_key = sp.Rational(str(key))
        base_salt_equation *= (x - exact_key)

    return sp.expand(base_salt_equation)


def _apply_salt(base_salt_equation, salt_equation_type):
    if salt_equation_type == "Sine":
        return sp.sin(base_salt_equation)
    if salt_equation_type == "Cosine":
        return sp.cos(base_salt_equation) - 1
    if salt_equation_type == "Tan":
        return sp.tan(base_salt_equation)
    if salt_equation_type == "Square Root":
        return sp.sqrt(base_salt_equation)
    if salt_equation_type == "Log":
        return sp.log(base_salt_equation + 1)
    return base_salt_equation


def _build_chunk_equation(job):
    """Build one chunk independently so chunk work can run concurrently."""
    key_chunk, values, salt_equation_type, include_latex = job
    exact_key_chunk = [sp.Rational(str(key)) for key in key_chunk]
    points = utils.points.generate_points(exact_key_chunk, values)
    base_polynomial = sp.interpolate(points, x)
    calculus_wrapper = sp.Derivative(sp.integrate(base_polynomial, x), x)
    salt_equation = _apply_salt(
        generate_base_salt_equation(exact_key_chunk), salt_equation_type
    )
    expression = salt_equation + calculus_wrapper
    return str(expression), points, sp.latex(expression) if include_latex else None


def _build_chunk_equations(key_chunks, value_chunks, salt_equation_type, preview=False):
    jobs = (
        (key_chunk, values, salt_equation_type, preview and index < MAX_PREVIEW_CHUNKS)
        for index, (key_chunk, values) in enumerate(zip(key_chunks, value_chunks))
    )

    # ThreadPoolExecutor.map preserves input order, so equations remain aligned
    # with their keys even when chunks finish in a different order.
    if len(key_chunks) < 2:
        return [_build_chunk_equation(job) for job in jobs]

    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(key_chunks))) as executor:
        return list(executor.map(_build_chunk_equation, jobs))

def encryptMessage(message, gpg_key_path, salt_equation_type):
    """Build a message payload, including a deliberately empty message."""
    if message is None:
        message = ""

    try:
        ascii_values = [char_to_ascii(char) for char in message]
        total_chars = len(ascii_values)
        secret_key = generate_secret_key(total_chars)

        gpg_key = utils.gpg.read_gpg_file(gpg_key_path)

        if gpg_key is not None:
            encrypted_secret_key = utils.gpg.encrypt_secret_key(secret_key, gpg_key)
            key_chunks = chunk_bytes(secret_key, DEFAULT_CHUNK_SIZE)
            ascii_chunks = chunk_bytes(ascii_values, DEFAULT_CHUNK_SIZE)
            chunk_results = _build_chunk_equations(
                key_chunks, ascii_chunks, salt_equation_type, preview=True
            )
            equations = [equation for equation, _, _ in chunk_results]
            latex_blocks = [latex for _, _, latex in chunk_results if latex]

            # log("Encryption process completed successfully.", "encryption_logger", text_color="#677D6A")

            payload = {
                "encrypted_data": encrypted_secret_key,
                "equations": equations,
                "chunk_size": DEFAULT_CHUNK_SIZE,
                "total_chars": total_chars,
                "equation": equations[0] if equations else "",
                # This is UI-only. Matplotlib mathtext cannot parse literal
                # ``\\n`` separators between full LaTeX expressions.
                "latex": latex_blocks[0] if latex_blocks else "",
            }

            return payload
    except Exception as e:
        log(f"Error during encryption: {str(e)}", "encryption_logger", text_color="#f54842")
        return None


def encrypt_file(file_path: str, salt_equation_type: str = "Sine"):
    try:
        if not file_path:
            return None

        if not os.path.exists(file_path):
            log(f"Secret file not found: {file_path}", "encryption_logger", text_color="#f54842")
            return None

        # Convert the file into bytes and split into chunks
        bytes_data = read_file_bytes(file_path)
        if bytes_data is None:
            return None

        chunks = chunk_bytes(bytes_data, DEFAULT_CHUNK_SIZE)
        flat_secret_key = generate_secret_key(len(bytes_data))
        secret_key = [
            flat_secret_key[index * DEFAULT_CHUNK_SIZE:index * DEFAULT_CHUNK_SIZE + len(chunk)]
            for index, chunk in enumerate(chunks)
        ]
        chunk_results = _build_chunk_equations(
            secret_key, [list(chunk) for chunk in chunks], salt_equation_type
        )
        equations = [equation for equation, _, _ in chunk_results]

        if len(secret_key) <= MAX_DEBUG_CHUNKS:
            print(f"Secret file key: {secret_key}")
        else:
            print(
                f"Secret file key (first {MAX_DEBUG_CHUNKS} of {len(secret_key)} chunks): "
                f"{secret_key[:MAX_DEBUG_CHUNKS]}"
            )

        for chunk_index, (equation, points, _) in enumerate(chunk_results[:MAX_DEBUG_CHUNKS]):
            print(f"Secret file chunk {chunk_index + 1} points: {points}")
            print(f"Secret file chunk {chunk_index + 1} equation: {equation}")
        if len(chunk_results) > MAX_DEBUG_CHUNKS:
            print(f"... {len(chunk_results) - MAX_DEBUG_CHUNKS} additional file chunks omitted from debug output.")

        # File recovery is intentionally not implemented yet.  Preserve the
        # generated equations in the transport payload so the receiver can
        # identify that a file was included and reserve a place for it.
        return {
            "equations": equations,
            "chunk_size": DEFAULT_CHUNK_SIZE,
            "total_bytes": len(bytes_data),
            "equation": equations[0] if equations else "",
        }
    except Exception as exc:
        log(f"Failed to build secret file equation: {exc}", "encryption_logger", text_color="#f54842")
        return None


def read_file_bytes(file_path: str) -> bytes | None:
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        log(f"Secret file not found: {file_path}", "encryption_logger", text_color="#f54842")
        return None
    except Exception as exc:
        log(f"Error reading file {file_path}: {exc}", "encryption_logger", text_color="#f54842")
        return None


def chunk_bytes(data: bytes, chunk_size: int = DEFAULT_CHUNK_SIZE):
    if not data:
        return []
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def send_payload(payload: dict) -> bool:
    """Send the complete message/file payload after all optional parts exist."""
    try:
        return client.send_payload(json.dumps(payload).encode("utf-8"))
    except Exception as exc:
        log("Error sending payload", "encryption_logger", text_color="#f54842")
        print(f"Error sending payload: {exc}")
        return False
