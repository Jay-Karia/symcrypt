import ast
import json
import re
from utils import gpg
import sympy as sp
from logger import log


def _sanitize_payload_string(cleaned: str) -> str:
    """
    Remove fields that are not valid Python literals (e.g., unquoted sympy_expr)
    so the payload can still be parsed for encrypted_data/equation.
    """
    pattern = r",\s*['\"]sympy_expr['\"]\s*:\s*.*\}\s*$"
    if re.search(pattern, cleaned, flags=re.DOTALL):
        return re.sub(pattern, "}", cleaned, flags=re.DOTALL)
    return cleaned


def _parse_payload(payload):
    if payload is None:
        raise ValueError("Payload is empty.")

    if isinstance(payload, bytes):
        payload = payload.decode("utf-8", errors="replace")

    if isinstance(payload, dict):
        return payload

    if isinstance(payload, str):
        cleaned = payload.strip()

        if cleaned.startswith("{") and cleaned.endswith("}"):
            try:
                return ast.literal_eval(cleaned)
            except (SyntaxError, ValueError):
                try:
                    sanitized = _sanitize_payload_string(cleaned)
                    return ast.literal_eval(sanitized)
                except (SyntaxError, ValueError):
                    pass

                try:
                    return json.loads(cleaned)
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"Invalid payload object string: {exc}") from exc

    raise ValueError("Payload is not a dictionary-like object.")

def decrypt_payload(payload: str, gpg_key_path: str, passphrase: str) -> str:
    log("Starting decryption process...", "receiver_status_logger", text_color="#677D6A")

    try:
        parsed_payload = _parse_payload(payload)

        if not isinstance(parsed_payload, dict):
            raise ValueError("Payload is not a dictionary-like object.")

        encrypted_secret_key = parsed_payload.get("secret_key", parsed_payload.get("encrypted_data"))
        equation = parsed_payload.get("equation")
        equations = parsed_payload.get("equations")
        chunk_size = int(parsed_payload.get("chunk_size", 0) or 0)

        # Decrypt using private GPG key
        secret_key = gpg.decrypt_secret_key(encrypted_secret_key, gpg_key_path, passphrase)
        if not secret_key:
            raise ValueError("Decrypted secret key is empty or invalid.")
        if not equations and not equation:
            raise ValueError("Equation field is missing in payload.")

        # Get the ASCII values of the message
        x = sp.Symbol("x")
        ascii_values = []

        if equations and chunk_size > 0:
            if not isinstance(equations, list):
                raise ValueError("Invalid equations format; expected a list.")

            expected_chunks = (len(secret_key) + chunk_size - 1) // chunk_size
            if len(equations) != expected_chunks:
                raise ValueError(
                    f"Chunk mismatch: expected {expected_chunks} equations, got {len(equations)}."
                )

            for chunk_index, equation_text in enumerate(equations):
                start = chunk_index * chunk_size
                end = min(start + chunk_size, len(secret_key))
                key_chunk = secret_key[start:end]
                expression = sp.sympify(equation_text).doit()

                for key in key_chunk:
                    exact_key = sp.Rational(str(key))
                    evaluated_val = expression.subs(x, exact_key).doit()
                    numeric_expr = sp.N(evaluated_val)

                    if hasattr(numeric_expr, "is_real") and numeric_expr.is_real is False:
                        raise ValueError(f"Non-real value encountered for key {key}: {numeric_expr}")

                    numeric_result = float(numeric_expr)
                    integer_result = int(round(numeric_result))
                    ascii_values.append(integer_result)
        else:
            expression = sp.sympify(equation).doit()
            for key in secret_key:
                exact_key = sp.Rational(str(key))
                evaluated_val = expression.subs(x, exact_key).doit()
                numeric_expr = sp.N(evaluated_val)

                if hasattr(numeric_expr, "is_real") and numeric_expr.is_real is False:
                    raise ValueError(f"Non-real value encountered for key {key}: {numeric_expr}")

                numeric_result = float(numeric_expr)
                integer_result = int(round(numeric_result))
                ascii_values.append(integer_result)

        # Convert ASCII values back to characters
        decrypted_chars = []
        for index, value in enumerate(ascii_values):
            if not (0 <= value <= 0x10FFFF):
                raise ValueError(
                    f"Recovered code point out of Unicode range at index {index}: {value}"
                )
            decrypted_chars.append(chr(value))

        decrypted_message = ''.join(decrypted_chars)

        log(decrypted_message, "decrypted_message_logger", text_color="#677D6A")
        log("Successfully decrypted the payload.", "receiver_status_logger", text_color="#677D6A")

        return str(equation or "")
    except Exception as exc:
        error_message = f"Failed to parse payload: {exc}"
        print(error_message)
        log(error_message, "receiver_status_logger", text_color="#f54842")
        return ""


# receiver_status_logger
# decrypted_message_logger
