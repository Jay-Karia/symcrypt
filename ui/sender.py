import customtkinter as ctk
from tkinter import filedialog, messagebox
import sympy as sp
import utils.encrypt
from logger import create_log_target

# Consistent Palette Definition
COLOR_ECLIPSE = "#0c1818"       # Deep dark window canvas
COLOR_CARD_BG = "#152422"       # Surface card background
COLOR_INPUT_BG = "#101d1c"      # Entry/Textbox inner background
COLOR_BORDER = "#2b3d37"        # Subtle hairline frame border
COLOR_BORDER_FOCUS = "#40534C"  # Active outline
COLOR_MATCHA_BREW = "#677D6A"   # Secondary text / accents / badges
COLOR_ALMOND = "#D6BD98"        # Primary typography / titles
COLOR_ACCENT_HOVER = "#859D88"  # Button hover state


def show_gpg_key_help():
    messagebox.showinfo(
        "GPG Key File",
        "Select the receiver's public GPG key file (.asc or .pub) to encrypt authorized point coordinates."
    )


def show_salt_equation_help():
    messagebox.showinfo(
        "Harmonic Masking (Salt)",
        "Injects a zero-crossing wave function into the calculus polynomial to disguise the carrier equation."
    )


def open_settings_modal(parent: ctk.CTk):
    """Opens a clean settings popup."""
    settings_win = ctk.CTkToplevel(parent)
    settings_win.title("Sender Configuration")
    settings_win.geometry("420x360")
    settings_win.configure(fg_color=COLOR_ECLIPSE)
    settings_win.transient(parent)
    settings_win.grab_set()

    content = ctk.CTkFrame(settings_win, fg_color=COLOR_CARD_BG, corner_radius=14, border_color=COLOR_BORDER, border_width=1)
    content.pack(fill="both", expand=True, padx=16, pady=16)

    title = ctk.CTkLabel(content, text="Preferences", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color=COLOR_ALMOND)
    title.pack(anchor="w", padx=16, pady=(16, 12))

    # Compression toggle
    comp_var = ctk.BooleanVar(value=True)
    comp_switch = ctk.CTkSwitch(
        content,
        text="Enable Payload Compression",
        variable=comp_var,
        font=ctk.CTkFont(family="Inter", size=13),
        text_color=COLOR_ALMOND,
        progress_color=COLOR_MATCHA_BREW
    )
    comp_switch.pack(anchor="w", padx=16, pady=8)

    # Verbose Math Logging toggle
    verb_var = ctk.BooleanVar(value=True)
    verb_switch = ctk.CTkSwitch(
        content,
        text="Full 2D Unicode Math Output",
        variable=verb_var,
        font=ctk.CTkFont(family="Inter", size=13),
        text_color=COLOR_ALMOND,
        progress_color=COLOR_MATCHA_BREW
    )
    verb_switch.pack(anchor="w", padx=16, pady=8)

    # Chunk size selector
    chunk_label = ctk.CTkLabel(content, text="Interpolation Chunk Size:", font=ctk.CTkFont(family="Inter", size=13), text_color=COLOR_MATCHA_BREW)
    chunk_label.pack(anchor="w", padx=16, pady=(12, 4))

    chunk_menu = ctk.CTkOptionMenu(
        content,
        values=["8 bytes / poly", "16 bytes / poly", "32 bytes / poly"],
        fg_color=COLOR_INPUT_BG,
        button_color=COLOR_BORDER,
        button_hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        dropdown_fg_color=COLOR_CARD_BG,
        corner_radius=8
    )
    chunk_menu.pack(anchor="w", padx=16, pady=(0, 16))

    close_btn = ctk.CTkButton(
        content,
        text="Save & Close",
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        corner_radius=8,
        command=settings_win.destroy
    )
    close_btn.pack(side="bottom", fill="x", padx=16, pady=(0, 16))


def sender_screen(root: ctk.CTk):
    from ui.welcome import welcome_screen

    root.title("SymCrypt — Outbound Carrier Channel")
    root.configure(fg_color=COLOR_ECLIPSE)

    math_font = ctk.CTkFont(family="DejaVu Sans Mono", size=12)

    # 1. Top Navigation & Status Bar
    top_bar = ctk.CTkFrame(root, fg_color="transparent", height=48)
    top_bar.pack(fill="x", padx=24, pady=(16, 8))

    # Mode Tag
    mode_badge = ctk.CTkFrame(top_bar, fg_color=COLOR_CARD_BG, corner_radius=8, border_color=COLOR_BORDER, border_width=1)
    mode_badge.pack(side="left", padx=12)
    badge_lbl = ctk.CTkLabel(
        mode_badge,
        text="OUTBOUND TRANSMIT",
        font=ctk.CTkFont(family="DejaVu Sans Mono", size=11, weight="bold"),
        text_color=COLOR_MATCHA_BREW
    )
    badge_lbl.pack(padx=10, pady=4)

    # Settings action
    settings_btn = ctk.CTkButton(
        top_bar,
        text="⚙ Settings",
        width=90,
        height=32,
        corner_radius=8,
        fg_color=COLOR_CARD_BG,
        hover_color=COLOR_BORDER,
        border_color=COLOR_BORDER,
        border_width=1,
        text_color=COLOR_ALMOND,
        font=ctk.CTkFont(family="Inter", size=12),
        command=lambda: open_settings_modal(root)
    )
    settings_btn.pack(side="right")

    # 2. Main Scrollable View Area
    main_frame = ctk.CTkScrollableFrame(root, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    # --- CARD 1: Connection & Target Server ---
    card_conn = ctk.CTkFrame(main_frame, fg_color=COLOR_CARD_BG, corner_radius=12, border_color=COLOR_BORDER, border_width=1)
    card_conn.pack(fill="x", pady=(0, 12))

    conn_header = ctk.CTkLabel(card_conn, text="Receiver Target Socket", font=ctk.CTkFont(family="Inter", size=15, weight="bold"), text_color=COLOR_ALMOND)
    conn_header.pack(anchor="w", padx=16, pady=(14, 8))

    conn_row = ctk.CTkFrame(card_conn, fg_color="transparent")
    conn_row.pack(fill="x", padx=16, pady=(0, 10))

    serverAddressEntry = ctk.CTkEntry(
        conn_row,
        placeholder_text="127.0.0.1:8080",
        font=ctk.CTkFont(family="DejaVu Sans Mono", size=13),
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=8,
        text_color=COLOR_ALMOND,
        height=36
    )
    serverAddressEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))

    connectButton = ctk.CTkButton(
        conn_row,
        text="Connect",
        width=100,
        height=36,
        corner_radius=8,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=ctk.CTkFont(family="Inter", size=13, weight="bold")
    )
    connectButton.pack(side="right")

    serverStatusBox = create_log_target(card_conn, "server_status_logger", height=42, fg_color=COLOR_INPUT_BG)
    serverStatusBox.pack(fill="x", padx=16, pady=(0, 14))

    # --- CARD 2: GPG & Security Configuration ---
    card_sec = ctk.CTkFrame(main_frame, fg_color=COLOR_CARD_BG, corner_radius=12, border_color=COLOR_BORDER, border_width=1)
    card_sec.pack(fill="x", pady=(0, 12))

    sec_title_row = ctk.CTkFrame(card_sec, fg_color="transparent")
    sec_title_row.pack(fill="x", padx=16, pady=(14, 8))

    gpgKeyLabel = ctk.CTkLabel(sec_title_row, text="Public GPG Key", font=ctk.CTkFont(family="Inter", size=15, weight="bold"), text_color=COLOR_ALMOND)
    gpgKeyLabel.pack(side="left")

    gpgQuickInfo = ctk.CTkButton(
        sec_title_row,
        text="?",
        width=24,
        height=24,
        corner_radius=12,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=ctk.CTkFont(size=12, weight="bold"),
        command=show_gpg_key_help
    )
    gpgQuickInfo.pack(side="left", padx=(8, 0))

    gpg_row = ctk.CTkFrame(card_sec, fg_color="transparent")
    gpg_row.pack(fill="x", padx=16, pady=(0, 12))

    gpgKeyPathEntry = ctk.CTkEntry(
        gpg_row,
        placeholder_text="No key imported (click Browse)",
        font=ctk.CTkFont(family="Inter", size=13),
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=8,
        text_color=COLOR_ALMOND,
        height=36
    )
    gpgKeyPathEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))
    gpgKeyPathEntry.configure(state="readonly")

    def browse_gpg_key_file():
        file_path = filedialog.askopenfilename(
            title="Select Public GPG Key",
            filetypes=[("GPG Keys", "*.asc *.pub *.gpg"), ("All Files", "*.*")]
        )
        if file_path:
            gpgKeyPathEntry.configure(state="normal")
            gpgKeyPathEntry.delete(0, "end")
            gpgKeyPathEntry.insert(0, file_path)
            gpgKeyPathEntry.configure(state="readonly")

    browseButton = ctk.CTkButton(
        gpg_row,
        text="Browse...",
        width=100,
        height=36,
        corner_radius=8,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=ctk.CTkFont(family="Inter", size=13),
        command=browse_gpg_key_file
    )
    browseButton.pack(side="right")

    # Salt selector row inside security card
    salt_row = ctk.CTkFrame(card_sec, fg_color="transparent")
    salt_row.pack(fill="x", padx=16, pady=(0, 14))

    salt_title = ctk.CTkLabel(salt_row, text="Harmonic Camouflage Function:", font=ctk.CTkFont(family="Inter", size=13), text_color=COLOR_MATCHA_BREW)
    salt_title.pack(side="left", padx=(0, 8))

    saltQuickInfo = ctk.CTkButton(
        salt_row,
        text="?",
        width=20,
        height=20,
        corner_radius=10,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=ctk.CTkFont(size=11),
        command=show_salt_equation_help
    )
    saltQuickInfo.pack(side="left", padx=(0, 16))

    saltEquationTypeVar = ctk.StringVar(value="Sine")
    saltEquationTypeMenu = ctk.CTkOptionMenu(
        salt_row,
        values=["Sine", "Cosine", "Tan", "Square Root", "Log"],
        variable=saltEquationTypeVar,
        width=180,
        height=32,
        corner_radius=8,
        fg_color=COLOR_INPUT_BG,
        button_color=COLOR_BORDER,
        button_hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        dropdown_fg_color=COLOR_CARD_BG
    )
    saltEquationTypeMenu.pack(side="right")

    # --- CARD 3: Payload Text Input ---
    card_msg = ctk.CTkFrame(main_frame, fg_color=COLOR_CARD_BG, corner_radius=12, border_color=COLOR_BORDER, border_width=1)
    card_msg.pack(fill="x", pady=(0, 12))

    msg_header = ctk.CTkLabel(card_msg, text="Secret Payload Stream", font=ctk.CTkFont(family="Inter", size=15, weight="bold"), text_color=COLOR_ALMOND)
    msg_header.pack(anchor="w", padx=16, pady=(14, 8))

    secretMessageEntry = ctk.CTkTextbox(
        card_msg,
        height=140,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=8,
        text_color=COLOR_ALMOND,
        font=ctk.CTkFont(family="DejaVu Sans Mono", size=13)
    )
    secretMessageEntry.pack(fill="x", padx=16, pady=(0, 10))

    loggerBox = create_log_target(card_msg, "encryption_logger", height=42, fg_color=COLOR_INPUT_BG)
    loggerBox.pack(fill="x", padx=16, pady=(0, 14))

    # --- CARD 4: Generated Math Equation Preview ---
    card_math = ctk.CTkFrame(main_frame, fg_color=COLOR_CARD_BG, corner_radius=12, border_color=COLOR_BORDER, border_width=1)
    card_math.pack(fill="x", pady=(0, 16))

    math_header_row = ctk.CTkFrame(card_math, fg_color="transparent")
    math_header_row.pack(fill="x", padx=16, pady=(14, 8))

    mathEquationLabel = ctk.CTkLabel(math_header_row, text="Generated Mathematical Carrier Expression", font=ctk.CTkFont(family="Inter", size=15, weight="bold"), text_color=COLOR_ALMOND)
    mathEquationLabel.pack(side="left")

    def open_expanded_math_modal():
        modal = ctk.CTkToplevel(root)
        modal.title("Carrier Equation Viewer")
        modal.geometry("800x480")
        modal.configure(fg_color=COLOR_ECLIPSE)
        viewer = ctk.CTkTextbox(
            modal,
            font=math_font,
            wrap="none",
            activate_scrollbars=True,
            fg_color=COLOR_CARD_BG,
            text_color=COLOR_ALMOND,
            border_color=COLOR_BORDER,
            border_width=1
        )
        viewer.pack(fill="both", expand=True, padx=16, pady=16)
        viewer.insert("1.0", mathEquationBox.get("1.0", "end"))

    expand_btn = ctk.CTkButton(
        math_header_row,
        text="Expand ⛶",
        width=70,
        height=24,
        corner_radius=6,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=ctk.CTkFont(size=11),
        command=open_expanded_math_modal
    )
    expand_btn.pack(side="right")

    mathEquationBox = create_log_target(
        card_math,
        "math_equation_logger",
        height=140,
        fg_color=COLOR_INPUT_BG,
        font=math_font,
        wrap="none",
        activate_scrollbars=True
    )
    mathEquationBox.pack(fill="x", padx=16, pady=(0, 14))

    # --- TRANSMIT ACTION BUTTON ---
    encryptButton = ctk.CTkButton(
        main_frame,
        text="Interpolate & Transmit Function →",
        font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        border_color=COLOR_MATCHA_BREW,
        border_width=1,
        text_color=COLOR_ALMOND,
        height=48,
        corner_radius=12,
        command=lambda: utils.encrypt.encryptMessage(
            secretMessageEntry.get("1.0", "end-1c"),
            gpgKeyPathEntry.get(),
            saltEquationTypeVar.get()
        )
    )
    encryptButton.pack(fill="x", pady=(0, 24))