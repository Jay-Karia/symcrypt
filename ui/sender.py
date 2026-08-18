import customtkinter
from tkinter import filedialog, messagebox
import sympy as sp
import utils.encrypt
from logger import create_log_target

COLOR_ECLIPSE = "#0c1818"
COLOR_CARD_BG = "#152422"
COLOR_INPUT_BG = "#101d1c"
COLOR_BORDER = "#2b3d37"
COLOR_BORDER_FOCUS = "#40534C"
COLOR_MATCHA_BREW = "#677D6A"
COLOR_ALMOND = "#D6BD98"
COLOR_ACCENT_HOVER = "#859D88"


def show_gpg_key_help():
    messagebox.showinfo(
        "GPG Key File",
        "Select the receiver's public GPG key file for encryption."
    )


def show_salt_equation_help():
    messagebox.showinfo(
        "Salt Equation",
        "The salt equation is generated to improve the security of the equation."
    )


def open_settings_modal(parent: customtkinter.CTk):
    settings_win = customtkinter.CTkToplevel(parent)
    settings_win.title("Settings")
    settings_win.geometry("420x360")
    settings_win.configure(fg_color=COLOR_ECLIPSE)
    settings_win.transient(parent)
    settings_win.grab_set()

    content = customtkinter.CTkFrame(
        settings_win,
        fg_color=COLOR_CARD_BG,
        corner_radius=14,
        border_color=COLOR_BORDER,
        border_width=1,
    )
    content.pack(fill="both", expand=True, padx=16, pady=16)

    title = customtkinter.CTkLabel(
        content,
        text="Preferences",
        font=customtkinter.CTkFont(family="Inter", size=18, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    title.pack(anchor="w", padx=16, pady=(16, 12))

    comp_var = customtkinter.BooleanVar(value=True)
    comp_switch = customtkinter.CTkSwitch(
        content,
        text="Enable Payload Compression",
        variable=comp_var,
        font=customtkinter.CTkFont(family="Inter", size=13),
        text_color=COLOR_ALMOND,
        progress_color=COLOR_MATCHA_BREW,
    )
    comp_switch.pack(anchor="w", padx=16, pady=8)

    verb_var = customtkinter.BooleanVar(value=True)
    verb_switch = customtkinter.CTkSwitch(
        content,
        text="Full 2D Unicode Math Output",
        variable=verb_var,
        font=customtkinter.CTkFont(family="Inter", size=13),
        text_color=COLOR_ALMOND,
        progress_color=COLOR_MATCHA_BREW,
    )
    verb_switch.pack(anchor="w", padx=16, pady=8)

    chunk_label = customtkinter.CTkLabel(
        content,
        text="Interpolation Chunk Size:",
        font=customtkinter.CTkFont(family="Inter", size=13),
        text_color=COLOR_MATCHA_BREW,
    )
    chunk_label.pack(anchor="w", padx=16, pady=(12, 4))

    chunk_menu = customtkinter.CTkOptionMenu(
        content,
        values=["8 bytes / poly", "16 bytes / poly", "32 bytes / poly"],
        fg_color=COLOR_INPUT_BG,
        button_color=COLOR_BORDER,
        button_hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        dropdown_fg_color=COLOR_CARD_BG,
        corner_radius=8,
    )
    chunk_menu.pack(anchor="w", padx=16, pady=(0, 16))

    close_btn = customtkinter.CTkButton(
        content,
        text="Save & Close",
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        corner_radius=8,
        command=settings_win.destroy,
    )
    close_btn.pack(side="bottom", fill="x", padx=16, pady=(0, 16))


def sender_screen(root: customtkinter.CTk):
    from ui.welcome import welcome_screen

    root.title("SymCrypt - Sender")
    root.configure(fg_color=COLOR_ECLIPSE)

    math_font = customtkinter.CTkFont(family="DejaVu Sans Mono", size=12)

    top_bar = customtkinter.CTkFrame(root, fg_color="transparent", height=48)
    top_bar.pack(fill="x", padx=24, pady=(16, 8))

    settings_btn = customtkinter.CTkButton(
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
        font=customtkinter.CTkFont(family="Inter", size=12),
        command=lambda: open_settings_modal(root),
    )
    settings_btn.pack(side="right")

    main_frame = customtkinter.CTkScrollableFrame(root, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    card_conn = customtkinter.CTkFrame(
        main_frame,
        fg_color=COLOR_CARD_BG,
        corner_radius=12,
        border_color=COLOR_BORDER,
        border_width=1,
    )
    card_conn.pack(fill="x", pady=(0, 12))

    connectServerLabel = customtkinter.CTkLabel(
        card_conn,
        text="Connect to Receiver's Server",
        font=customtkinter.CTkFont(family="Inter", size=15, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    connectServerLabel.pack(anchor="w", padx=16, pady=(14, 8))

    connectionFrame = customtkinter.CTkFrame(card_conn, fg_color="transparent")
    connectionFrame.pack(fill="x", padx=16, pady=(0, 10))

    serverAddressEntry = customtkinter.CTkEntry(
        connectionFrame,
        placeholder_text="Server Address",
        font=customtkinter.CTkFont(family="DejaVu Sans Mono", size=13),
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=8,
        text_color=COLOR_ALMOND,
        height=36,
    )
    serverAddressEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))

    connectButton = customtkinter.CTkButton(
        connectionFrame,
        text="Connect",
        width=100,
        height=36,
        corner_radius=8,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="Inter", size=13, weight="bold"),
    )
    connectButton.pack(side="right")

    serverStatusBox = create_log_target(
        card_conn, "server_status_logger", height=42, fg_color=COLOR_INPUT_BG
    )
    serverStatusBox.pack(fill="x", padx=16, pady=(0, 14))

    card_sec = customtkinter.CTkFrame(
        main_frame,
        fg_color=COLOR_CARD_BG,
        corner_radius=12,
        border_color=COLOR_BORDER,
        border_width=1,
    )
    card_sec.pack(fill="x", pady=(0, 12))

    gpgKeyHeaderFrame = customtkinter.CTkFrame(
        card_sec, fg_color="transparent"
    )
    gpgKeyHeaderFrame.pack(fill="x", padx=16, pady=(14, 8))

    gpgKeyLabel = customtkinter.CTkLabel(
        gpgKeyHeaderFrame,
        text="GPG Key File",
        font=customtkinter.CTkFont(family="Inter", size=15, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    gpgKeyLabel.pack(side="left")

    gpgQuickInfoButton = customtkinter.CTkButton(
        gpgKeyHeaderFrame,
        text="?",
        width=24,
        height=24,
        corner_radius=12,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(size=12, weight="bold"),
        command=show_gpg_key_help,
    )
    gpgQuickInfoButton.pack(side="left", padx=(8, 0))

    gpgKeyFrame = customtkinter.CTkFrame(card_sec, fg_color="transparent")
    gpgKeyFrame.pack(fill="x", padx=16, pady=(0, 12))

    gpgKeyPathEntry = customtkinter.CTkEntry(
        gpgKeyFrame,
        placeholder_text="Select GPG key file",
        font=customtkinter.CTkFont(family="Inter", size=13),
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=8,
        text_color=COLOR_ALMOND,
        height=36,
    )
    gpgKeyPathEntry.pack(side="left", fill="x", expand=True, padx=(0, 10))
    gpgKeyPathEntry.configure(state="readonly")

    def browse_gpg_key_file():
        file_path = filedialog.askopenfilename(title="Select GPG Key File")
        if file_path:
            gpgKeyPathEntry.configure(state="normal")
            gpgKeyPathEntry.delete(0, "end")
            gpgKeyPathEntry.insert(0, file_path)
            gpgKeyPathEntry.configure(state="readonly")

    browseButton = customtkinter.CTkButton(
        gpgKeyFrame,
        text="Browse",
        width=100,
        height=36,
        corner_radius=8,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="Inter", size=13),
        command=browse_gpg_key_file,
    )
    browseButton.pack(side="right")

    saltEquationHeaderFrame = customtkinter.CTkFrame(
        card_sec, fg_color="transparent"
    )
    saltEquationHeaderFrame.pack(fill="x", padx=16, pady=(0, 14))

    saltEquationLabel = customtkinter.CTkLabel(
        saltEquationHeaderFrame,
        text="Salt Equation Type",
        font=customtkinter.CTkFont(family="Inter", size=13),
        text_color=COLOR_MATCHA_BREW,
    )
    saltEquationLabel.pack(side="left", padx=(0, 8))

    saltEquationQuickInfo = customtkinter.CTkButton(
        saltEquationHeaderFrame,
        text="?",
        width=20,
        height=20,
        corner_radius=10,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(size=11),
        command=show_salt_equation_help,
    )
    saltEquationQuickInfo.pack(side="left", padx=(0, 16))

    saltEquationTypeVar = customtkinter.StringVar(value="Sine")
    saltEquationTypeMenu = customtkinter.CTkOptionMenu(
        saltEquationHeaderFrame,
        values=["Sine", "Cosine", "Tan", "Square Root", "Log"],
        variable=saltEquationTypeVar,
        width=180,
        height=32,
        corner_radius=8,
        fg_color=COLOR_INPUT_BG,
        button_color=COLOR_BORDER,
        button_hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        dropdown_fg_color=COLOR_CARD_BG,
    )
    saltEquationTypeMenu.pack(side="right")

    card_msg = customtkinter.CTkFrame(
        main_frame,
        fg_color=COLOR_CARD_BG,
        corner_radius=12,
        border_color=COLOR_BORDER,
        border_width=1,
    )
    card_msg.pack(fill="x", pady=(0, 12))

    secretMessageLabel = customtkinter.CTkLabel(
        card_msg,
        text="Secret Message",
        font=customtkinter.CTkFont(family="Inter", size=15, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    secretMessageLabel.pack(anchor="w", padx=16, pady=(14, 8))

    secretMessageEntry = customtkinter.CTkTextbox(
        card_msg,
        height=140,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=8,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="DejaVu Sans Mono", size=13),
    )
    secretMessageEntry.pack(fill="x", padx=16, pady=(0, 10))

    loggerBox = create_log_target(
        card_msg, "encryption_logger", height=42, fg_color=COLOR_INPUT_BG
    )
    loggerBox.pack(fill="x", padx=16, pady=(0, 14))

    card_math = customtkinter.CTkFrame(
        main_frame,
        fg_color=COLOR_CARD_BG,
        corner_radius=12,
        border_color=COLOR_BORDER,
        border_width=1,
    )
    card_math.pack(fill="x", pady=(0, 16))

    math_header_row = customtkinter.CTkFrame(card_math, fg_color="transparent")
    math_header_row.pack(fill="x", padx=16, pady=(14, 8))

    mathEquationLabel = customtkinter.CTkLabel(
        math_header_row,
        text="Generated Math Equation",
        font=customtkinter.CTkFont(family="Inter", size=15, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    mathEquationLabel.pack(side="left")

    def open_expanded_math_modal():
        modal = customtkinter.CTkToplevel(root)
        modal.title("Generated Math Equation")
        modal.geometry("800x480")
        modal.configure(fg_color=COLOR_ECLIPSE)
        viewer = customtkinter.CTkTextbox(
            modal,
            font=math_font,
            wrap="none",
            activate_scrollbars=True,
            fg_color=COLOR_CARD_BG,
            text_color=COLOR_ALMOND,
            border_color=COLOR_BORDER,
            border_width=1,
        )
        viewer.pack(fill="both", expand=True, padx=16, pady=16)
        viewer.insert("1.0", mathEquationBox.get("1.0", "end"))

    expand_btn = customtkinter.CTkButton(
        math_header_row,
        text="Expand ⛶",
        width=70,
        height=24,
        corner_radius=6,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(size=11),
        command=open_expanded_math_modal,
    )
    expand_btn.pack(side="right")

    mathEquationBox = create_log_target(
        card_math,
        "math_equation_logger",
        height=140,
        fg_color=COLOR_INPUT_BG,
        font=math_font,
        wrap="none",
        activate_scrollbars=True,
    )
    mathEquationBox.pack(fill="x", padx=16, pady=(0, 14))

    encryptButton = customtkinter.CTkButton(
        main_frame,
        text="Encrypt and Send",
        font=customtkinter.CTkFont(family="Inter", size=16, weight="bold"),
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
            saltEquationTypeVar.get(),
        ),
    )
    encryptButton.pack(fill="x", pady=(0, 24))
