import random
import utils.gpg
import utils.points
import sympy as sp
from logger import log
import server.client as client

x = sp.Symbol('x')
DEFAULT_CHUNK_SIZE = 32

def char_to_ascii(char):
    return ord(char)

def generate_secret_key(length):
    if length <= 0:
        return []

    # Use unique integer x-values to keep interpolation stable and unambiguous.
    # Rounded floats can create duplicate keys and break recovery.
    max_pool = 10_000_000
    if length > max_pool:
        raise ValueError("Message is too large for the current secret key pool.")

    return random.sample(range(1, max_pool + 1), length)

def generate_base_salt_equation(secret_key):
    if not secret_key:
        return sp.Integer(0)

    base_salt_equation = sp.Integer(1)
    for key in secret_key:
        exact_key = sp.Rational(str(key))
        base_salt_equation *= (x - exact_key)

    return sp.expand(base_salt_equation)

def encryptMessage(message, gpg_key_path, salt_equation_type):
    try:
        ascii_values = [char_to_ascii(char) for char in message]
        total_chars = len(ascii_values)
        secret_key = generate_secret_key(total_chars)

        gpg_key = utils.gpg.read_gpg_file(gpg_key_path)

        if gpg_key is not None:
            encrypted_data = utils.gpg.encrypt_secret_key(secret_key, gpg_key)
            equations = []
            latex_blocks = []

            for start in range(0, total_chars, DEFAULT_CHUNK_SIZE):
                end = min(start + DEFAULT_CHUNK_SIZE, total_chars)
                key_chunk = secret_key[start:end]
                ascii_chunk = ascii_values[start:end]

                exact_key_chunk = [sp.Rational(str(key)) for key in key_chunk]
                points = utils.points.generate_points(exact_key_chunk, ascii_chunk)
                base_polynomial = sp.interpolate(points, x)
                integral = sp.integrate(base_polynomial, x)
                calculus_wrapper = sp.Derivative(integral, x)

                base_salt_equation = generate_base_salt_equation(exact_key_chunk)
                if salt_equation_type == "Sine":
                    salt_equation = sp.sin(base_salt_equation)
                elif salt_equation_type == "Cosine":
                    salt_equation = sp.cos(base_salt_equation) - 1
                elif salt_equation_type == "Tan":
                    salt_equation = sp.tan(base_salt_equation)
                elif salt_equation_type == "Square Root":
                    salt_equation = sp.sqrt(base_salt_equation)
                elif salt_equation_type == "Log":
                    salt_equation = sp.log(base_salt_equation + 1)
                else:
                    salt_equation = base_salt_equation

                sym_expression = salt_equation + calculus_wrapper
                equations.append(str(sym_expression))
                latex_blocks.append(sp.latex(sym_expression))

            # log("Encryption process completed successfully.", "encryption_logger", text_color="#677D6A")

            payload = {
                "encrypted_data": encrypted_data,
                "equations": equations,
                "chunk_size": DEFAULT_CHUNK_SIZE,
                "total_chars": total_chars,
                "equation": equations[0] if equations else "",
                "latex": "\\n\\n".join(latex_blocks)
            }

            try:
                client.send_payload(str(payload).encode('utf-8'))
                log("Payload sent to receiver successfully.", "encryption_logger", text_color="#677D6A")
            except Exception as e:
                log(f"Error sending payload", "encryption_logger", text_color="#f54842")
                print(f"Error sending payload: {str(e)}")

            return payload
    except Exception as e:
        log(f"Error during encryption: {str(e)}", "encryption_logger", text_color="#f54842")
        return None
