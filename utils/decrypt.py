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


def payload_includes_file(payload) -> bool:
    parsed_payload = _parse_payload(payload)
    return (
        "encrypted_file" in parsed_payload
        or "secret_file" in parsed_payload
    )


def decrypt_file_payload(file_payload: dict, gpg_key_path: str, passphrase: str) -> bytes | None:
    """Recover the original file bytes from its encrypted equation payload."""
    try:
        if not isinstance(file_payload, dict):
            raise ValueError("Invalid file payload.")

        encrypted_secret_key = file_payload.get("encrypted_data")
        equations = file_payload.get("equations")
        chunk_size = int(file_payload.get("chunk_size", 0) or 0)
        total_bytes = int(file_payload.get("total_bytes", 0) or 0)
        if not encrypted_secret_key or not isinstance(equations, list) or chunk_size <= 0:
            raise ValueError("File payload is missing its encrypted key or equations.")

        secret_key = gpg.decrypt_secret_key(encrypted_secret_key, gpg_key_path, passphrase)
        if not isinstance(secret_key, list) or len(secret_key) != total_bytes:
            raise ValueError("Decrypted file key does not match the expected file size.")

        expected_chunks = (total_bytes + chunk_size - 1) // chunk_size
        if len(equations) != expected_chunks:
            raise ValueError(
                f"File chunk mismatch: expected {expected_chunks} equations, got {len(equations)}."
            )

        x = sp.Symbol("x")
        recovered_values = []
        for chunk_index, equation_text in enumerate(equations):
            start = chunk_index * chunk_size
            end = min(start + chunk_size, total_bytes)
            expression = sp.sympify(equation_text).doit()
            for key in secret_key[start:end]:
                evaluated = expression.subs(x, sp.Rational(str(key))).doit()
                value = int(round(float(sp.N(evaluated))))
                if not 0 <= value <= 255:
                    raise ValueError(
                        f"Recovered file byte is out of range at index {len(recovered_values)}."
                    )
                recovered_values.append(value)

        return bytes(recovered_values)
    except Exception as exc:
        error_message = f"Failed to decrypt file payload: {exc}"
        print(error_message)
        log(error_message, "receiver_status_logger", text_color="#f54842")
        return None

def decrypt_payload(payload: str, gpg_key_path: str, passphrase: str) -> str | None:
    log("Starting decryption process...", "receiver_status_logger", text_color="#677D6A")

    try:
        parsed_payload = _parse_payload(payload)

        if not isinstance(parsed_payload, dict):
            raise ValueError("Payload is not a dictionary-like object.")

        encrypted_secret_key = parsed_payload.get("secret_key", parsed_payload.get("encrypted_data"))
        equation = parsed_payload.get("equation")
        equations = parsed_payload.get("equations")
        chunk_size = int(parsed_payload.get("chunk_size", 0) or 0)
        total_chars = int(parsed_payload.get("total_chars", 0) or 0)

        # Decrypt using private GPG key
        secret_key = gpg.decrypt_secret_key(encrypted_secret_key, gpg_key_path, passphrase)
        if secret_key is None:
            raise ValueError("Decrypted secret key is empty or invalid.")

        # An empty message is a valid sender payload. It has an empty key and no
        # equations, so there is nothing to evaluate during decryption.
        if not secret_key:
            if total_chars != 0 or equations or equation:
                raise ValueError("Empty secret key does not match the payload data.")
            log("", "decrypted_message_logger", text_color="#677D6A")
            log("Successfully decrypted the payload.", "receiver_status_logger", text_color="#677D6A")
            return ""

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

        return decrypted_message
    except Exception as exc:
        error_message = f"Failed to parse payload: {exc}"
        print(error_message)
        log(error_message, "receiver_status_logger", text_color="#f54842")
        return None


# receiver_status_logger
# decrypted_message_logger
