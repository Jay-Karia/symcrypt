import ast
import json
import re

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

        secret_key = parsed_payload.get("secret_key", parsed_payload.get("encrypted_data"))
        equation = parsed_payload.get("equation")

        print("Secret key:", secret_key)
        print("Equation:", equation)
        print("Private Key Path:", gpg_key_path)
        print("Passphrase:", passphrase)

        return str(equation or "")
    except Exception as exc:
        error_message = f"Failed to parse payload: {exc}"
        print(error_message)
        log(error_message, "receiver_status_logger", text_color="#f54842")
        return ""


# receiver_status_logger
# decrypted_message_logger
