from logger import log

def decrypt_payload(payload: str, gpg_key_path: str, passphrase: str) -> str:
    log("Starting decryption process...", "receiver_status_logger", text_color="#677D6A")
    print(f"Decrypting payload: {payload}")
    print(f"Using GPG key path: {gpg_key_path}")
    print(f"Using passphrase: {passphrase}")

# receiver_status_logger
# decrypted_message_logger
