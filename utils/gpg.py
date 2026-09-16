from gnupg import GPG
import json
from logger import log, clear_log

def validate_gpg_key(gpg_key):
    # Check if the GPG key is empty
    if not gpg_key:
        return False

    # Trim whitespace from the GPG key
    gpg_key = gpg_key.strip()

    # Check if the GPG key starts with the expected header
    if not gpg_key.startswith("-----BEGIN PGP PUBLIC KEY BLOCK-----"):
        return False

    # Check if the GPG key ends with the expected footer
    if not gpg_key.endswith("-----END PGP PUBLIC KEY BLOCK-----"):
        return False

    return True

def read_gpg_file(path):
    try:
        with open(path, 'r') as file:
            gpg_key = file.read()
        valid = validate_gpg_key(gpg_key)
        if not valid:
            log(f"Error: Invalid GPG key format in file '{path}'.", "encryption_logger", text_color="#f54842")
            return None

        clear_log("encryption_logger")
        return gpg_key
    except FileNotFoundError:
        log(f"Error: GPG key file '{path}' not found.", "encryption_logger", text_color="#f54842")
        return None

def encrypt_secret_key(secret_key, gpg_key):
    gpg = GPG()
    secret_key_payload = json.dumps(secret_key)

    # Import the GPG key
    import_result = gpg.import_keys(gpg_key)
    if not import_result.fingerprints:
        log("Failed to import key.", "encryption_logger", text_color="#f54842")
        return None

    # Extract the fingerprint of the imported key
    key_fingerprint = import_result.fingerprints[0]

    # Encrypt
    encryption_status = gpg.encrypt(
        secret_key_payload,
        recipients=[key_fingerprint],
        always_trust=True
    )

    if not encryption_status.ok:
        log(f"Encryption failed: {encryption_status.status}", "encryption_logger", text_color="#f54842")
        return None

    return encryption_status.data.decode("utf-8")

def decrypt_secret_key(encrypted_secret_key, gpg_key_path, passphrase):
    gpg = GPG()
    # Import the GPG key
    with open(gpg_key_path, 'r') as key_file:
        gpg_key = key_file.read()
    import_result = gpg.import_keys(gpg_key)
    if not import_result.fingerprints:
        log("Failed to import key.", "receiver_status_logger", text_color="#f54842")
        return None

    # Decrypt
    decryption_status = gpg.decrypt(encrypted_secret_key, passphrase=passphrase)

    if not decryption_status.ok:
        log(f"Decryption failed: {decryption_status.status}", "receiver_status_logger", text_color="#f54842")
        return None

    try:
        decrypted_secret_key = json.loads(decryption_status.data.decode("utf-8"))
        return decrypted_secret_key
    except json.JSONDecodeError as e:
        log(f"Failed to decode decrypted secret key: {e}", "receiver_status_logger", text_color="#f54842")
        return None
