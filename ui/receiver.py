import customtkinter
from tkinter import filedialog, messagebox
import socket
import threading
from logger import create_log_target, log
from server.main import register_connection_prompt, register_payload_received_callback, start_server, stop_server
from utils import decrypt

COLOR_ECLIPSE = "#0d1818"
COLOR_CARD_BG = "#152422"
COLOR_INPUT_BG = "#0f1c1a"
COLOR_BORDER = "#2b3d37"
COLOR_MATCHA_BREW = "#677D6A"
COLOR_ALMOND = "#D6BD98"
COLOR_ALMOND_HOVER = "#e5d3b8"


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def show_private_key_help():
    messagebox.showinfo(
        "Private GPG Key",
        "Select your private GPG key file and enter its passphrase to decrypt the secret key.",
    )


def receiver_screen(root: customtkinter.CTk):
    root.title("SymCrypt - Receiver")
    root.configure(fg_color=COLOR_ECLIPSE)
    root.geometry("1080x680")
    root.minsize(960, 600)

    top_bar = customtkinter.CTkFrame(root, fg_color="transparent", height=40)
    top_bar.pack(fill="x", padx=20, pady=(10, 4))

    mode_badge = customtkinter.CTkFrame(
        top_bar,
        fg_color=COLOR_CARD_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=0,
    )
    mode_badge.pack(side="left")

    mode_badge_lbl = customtkinter.CTkLabel(
        mode_badge,
        text="RECEIVER MODE",
        font=customtkinter.CTkFont(family="DejaVu Sans Mono", size=11, weight="bold"),
        text_color=COLOR_MATCHA_BREW,
    )
    mode_badge_lbl.pack(padx=10, pady=3)

    dashboard = customtkinter.CTkFrame(root, fg_color="transparent")
    dashboard.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    # --- 1. FULL-WIDTH TOP BAR: Server Management & Configuration ---
    card_server_banner = customtkinter.CTkFrame(
        dashboard,
        fg_color=COLOR_CARD_BG,
        corner_radius=0,
        border_color=COLOR_BORDER,
        border_width=1,
    )
    card_server_banner.pack(side="top", fill="x", pady=(0, 10))

    server_inner = customtkinter.CTkFrame(card_server_banner, fg_color="transparent")
    server_inner.pack(fill="x", padx=14, pady=8)

    server_label = customtkinter.CTkLabel(
        server_inner,
        text="Run the server on ",
        font=customtkinter.CTkFont(family="Inter", size=12),
        text_color=COLOR_ALMOND,
    )
    server_label.pack(side="left", padx=(0, 0))

    # IP address box with distinct styling and copy functionality
    ip_box = customtkinter.CTkFrame(
        server_inner,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_MATCHA_BREW,
        border_width=2,
        corner_radius=4,
    )
    ip_box.pack(side="left", padx=(0, 10))

    ip_text = f"{get_local_ip()}:5000"

    ip_label = customtkinter.CTkLabel(
        ip_box,
        text=ip_text,
        font=customtkinter.CTkFont(family="DejaVu Sans Mono", size=12, weight="bold"),
        text_color=COLOR_MATCHA_BREW,
    )
    ip_label.pack(side="left", padx=8, pady=4)

    def copy_ip():
        root.clipboard_clear()
        root.clipboard_append(ip_text)
        root.update()

    copy_btn = customtkinter.CTkButton(
        ip_box,
        text="📋",
        width=24,
        height=24,
        corner_radius=2,
        fg_color=COLOR_MATCHA_BREW,
        hover_color=COLOR_ALMOND,
        text_color=COLOR_ECLIPSE,
        font=customtkinter.CTkFont(size=11),
        command=copy_ip,
    )
    copy_btn.pack(side="left", padx=(0, 6), pady=4)

    server_toggle_btn = customtkinter.CTkButton(
        server_inner,
        text="Start Server",
        width=110,
        height=32,
        corner_radius=0,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="Inter", size=12, weight="bold"),
        command=lambda: start_server()
    )
    server_toggle_btn.pack(side="left")

    end_server_btn = customtkinter.CTkButton(
        server_inner,
        text="End Server",
        width=110,
        height=32,
        corner_radius=0,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="Inter", size=12, weight="bold"),
        command=lambda: (
            stop_server()
            if messagebox.askyesno(
                "Stop Receiver Server",
                "Do you want to stop the receiver server?",
            )
            else None
        ),
    )
    end_server_btn.pack(side="left", padx=(8, 0))

    rx_server_log = create_log_target(
        server_inner, "receiver_server_logger", height=42, fg_color=COLOR_INPUT_BG
    )
    rx_server_log.pack(side="right", fill="x", expand=True, padx=(16, 0))

    def confirm_incoming_connection(client_address):
        approval_event = threading.Event()
        approval_result = {"value": False}

        def show_prompt():
            approval_result["value"] = messagebox.askyesno(
                "Incoming Connection",
                f"Someone is trying to connect from {client_address[0]}:{client_address[1]}. Allow it?",
            )
            approval_event.set()

        root.after(0, show_prompt)
        approval_event.wait()
        return approval_result["value"]

    register_connection_prompt(confirm_incoming_connection)

    # --- 2. MAIN SPLIT VIEW ---
    workbench = customtkinter.CTkFrame(dashboard, fg_color="transparent")
    workbench.pack(side="top", fill="both", expand=True)

    # --- LEFT PANE: GPG Credentials & Incoming Stream ---
    left_pane = customtkinter.CTkFrame(workbench, fg_color="transparent")
    left_pane.pack(side="left", fill="both", expand=True, padx=(0, 6))

    card_sec = customtkinter.CTkFrame(
        left_pane,
        fg_color=COLOR_CARD_BG,
        corner_radius=0,
        border_color=COLOR_BORDER,
        border_width=1,
    )
    card_sec.pack(side="top", fill="x", pady=(0, 10))

    sec_header = customtkinter.CTkFrame(card_sec, fg_color="transparent")
    sec_header.pack(fill="x", padx=14, pady=(8, 4))

    sec_label = customtkinter.CTkLabel(
        sec_header,
        text="GPG Private Key",
        font=customtkinter.CTkFont(family="Inter", size=13, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    sec_label.pack(side="left")

    help_btn = customtkinter.CTkButton(
        sec_header,
        text="?",
        width=18,
        height=18,
        corner_radius=0,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(size=11, weight="bold"),
        command=show_private_key_help,
    )
    help_btn.pack(side="left", padx=(8, 0))

    key_input_frame = customtkinter.CTkFrame(card_sec, fg_color="transparent")
    key_input_frame.pack(fill="x", padx=14, pady=(0, 6))

    priv_key_path_entry = customtkinter.CTkEntry(
        key_input_frame,
        placeholder_text="Select private GPG key...",
        font=customtkinter.CTkFont(family="Inter", size=12),
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=0,
        text_color=COLOR_ALMOND,
        height=32,
    )
    priv_key_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
    priv_key_path_entry.configure(state="readonly")

    def browse_priv_key():
        file_path = filedialog.askopenfilename(title="Select Private GPG Key File")
        if file_path:
            priv_key_path_entry.configure(state="normal")
            priv_key_path_entry.delete(0, "end")
            priv_key_path_entry.insert(0, file_path)
            priv_key_path_entry.configure(state="readonly")

    browse_btn = customtkinter.CTkButton(
        key_input_frame,
        text="Browse",
        width=75,
        height=32,
        corner_radius=0,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="Inter", size=12),
        command=browse_priv_key,
    )
    browse_btn.pack(side="right")

    passphrase_entry = customtkinter.CTkEntry(
        card_sec,
        placeholder_text="Passphrase",
        show="•",
        font=customtkinter.CTkFont(family="DejaVu Sans Mono", size=12),
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=0,
        text_color=COLOR_ALMOND,
        height=32,
    )
    passphrase_entry.pack(fill="x", padx=14, pady=(0, 10))

    # Incoming Raw Stream Box (Scrollable 2D & Read-Only)
    card_raw = customtkinter.CTkFrame(
        left_pane,
        fg_color=COLOR_CARD_BG,
        corner_radius=0,
        border_color=COLOR_BORDER,
        border_width=1,
    )
    card_raw.pack(side="top", fill="both", expand=True)

    raw_header = customtkinter.CTkFrame(card_raw, fg_color="transparent")
    raw_header.pack(fill="x", padx=14, pady=(8, 2))

    raw_title = customtkinter.CTkLabel(
        raw_header,
        text="Incoming Payload",
        font=customtkinter.CTkFont(family="Inter", size=13, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    raw_title.pack(side="left")

    raw_status = customtkinter.CTkLabel(
        raw_header,
        text="idle",
        font=customtkinter.CTkFont(family="DejaVu Sans Mono", size=11),
        text_color=COLOR_MATCHA_BREW,
    )
    raw_status.pack(side="right")

    raw_payload_box = create_log_target(
        card_raw,
        "incoming_payload_logger",
        height=180,
        fg_color=COLOR_INPUT_BG,
        wrap="word",
        activate_scrollbars=True,
    )
    raw_payload_box.configure(state="disabled")
    raw_payload_box.pack(fill="both", expand=True, padx=14, pady=(0, 10))

    def show_incoming_payload(payload_text: str):
        raw_payload_box.configure(state="normal")
        raw_payload_box.delete("1.0", "end")
        raw_payload_box.insert("end", payload_text)
        raw_payload_box.configure(state="disabled")
        raw_status.configure(text="received")

    register_payload_received_callback(show_incoming_payload)

    # --- RIGHT PANE: Output Inspector & Direct Action ---
    right_pane = customtkinter.CTkFrame(workbench, fg_color="transparent")
    right_pane.pack(side="right", fill="both", expand=True, padx=(6, 0))

    decrypt_btn = customtkinter.CTkButton(
        right_pane,
        text="Decrypt Payload",
        font=customtkinter.CTkFont(family="Inter", size=14, weight="bold"),
        fg_color=COLOR_ALMOND,
        hover_color=COLOR_ALMOND_HOVER,
        border_color=COLOR_BORDER,
        border_width=1,
        text_color=COLOR_ECLIPSE,
        height=36,
        corner_radius=0,
    )

    def decrypt_current_payload():
        payload = raw_payload_box.get("1.0", "end-1c")
        key_path = priv_key_path_entry.get().strip()
        passphrase = passphrase_entry.get()

        if not key_path:
            messagebox.showwarning("Missing Private Key", "Please select your private GPG key file first.")
            return

        if not passphrase.strip():
            messagebox.showwarning("Missing Passphrase", "Please enter the passphrase for the private GPG key.")
            return

        decrypted_message = decrypt.decrypt_payload(payload, key_path, passphrase)
        if decrypted_message is None:
            return

        has_file_equation = decrypt.payload_includes_file(payload)
        dec_file_path_entry.configure(state="normal")
        dec_file_path_entry.delete(0, "end")
        if has_file_equation:
            dec_file_path_entry.insert(
                0, "Encrypted file equation received — file decryption coming soon"
            )
        dec_file_path_entry.configure(state="readonly")

    decrypt_btn.configure(command=decrypt_current_payload)
    decrypt_btn.pack(side="bottom", fill="x")

    card_result = customtkinter.CTkFrame(
        right_pane,
        fg_color=COLOR_CARD_BG,
        corner_radius=0,
        border_color=COLOR_BORDER,
        border_width=1,
    )
    card_result.pack(side="top", fill="both", expand=True, pady=(0, 10))

    dec_header = customtkinter.CTkFrame(card_result, fg_color="transparent")
    dec_header.pack(fill="x", padx=14, pady=(8, 2))

    dec_title = customtkinter.CTkLabel(
        dec_header,
        text="Decrypted Output",
        font=customtkinter.CTkFont(family="Inter", size=13, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    dec_title.pack(side="left")

    decrypted_msg_box = create_log_target(
        card_result, "decrypted_message_logger", height=100, fg_color=COLOR_INPUT_BG
    )
    decrypted_msg_box.configure(state="disabled")
    decrypted_msg_box.pack(fill="both", expand=True, padx=14, pady=(0, 6))

    # --- Decrypted File Output Box ---
    dec_file_frame = customtkinter.CTkFrame(card_result, fg_color="transparent")
    dec_file_frame.pack(fill="x", padx=14, pady=(0, 6))

    dec_file_path_entry = customtkinter.CTkEntry(
        dec_file_frame,
        placeholder_text="No decrypted file received",
        font=customtkinter.CTkFont(family="Inter", size=12),
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=0,
        text_color=COLOR_ALMOND,
        height=32,
    )
    dec_file_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
    dec_file_path_entry.configure(state="readonly")

    def save_decrypted_file():
        file_path = filedialog.asksaveasfilename(title="Save Decrypted File")
        if file_path:
            log(f"Decrypted file saved to: {file_path}", "receiver_status_logger")

    save_btn = customtkinter.CTkButton(
        dec_file_frame,
        text="Save File",
        width=75,
        height=32,
        corner_radius=0,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="Inter", size=12),
        command=save_decrypted_file,
    )
    save_btn.pack(side="right")

    rx_status_box = create_log_target(
        card_result, "receiver_status_logger", height=50, fg_color=COLOR_INPUT_BG
    )
    rx_status_box.pack(fill="x", padx=14, pady=(0, 10))
