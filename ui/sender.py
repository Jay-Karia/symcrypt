import customtkinter
from tkinter import filedialog, messagebox, Canvas, Scrollbar
import sympy as sp
import utils.encrypt
from logger import create_log_target, log
from server.client import connect_to_server, disconnect

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms

COLOR_ECLIPSE = "#0d1818"
COLOR_CARD_BG = "#152422"
COLOR_INPUT_BG = "#0f1c1a"
COLOR_BORDER = "#2b3d37"
COLOR_MATCHA_BREW = "#677D6A"
COLOR_ALMOND = "#D6BD98"
COLOR_ALMOND_HOVER = "#e5d3b8"


def show_gpg_key_help():
    messagebox.showinfo(
        "GPG Key File",
        "Select the receiver's public GPG key file for encryption."
    )


def show_secret_file_help():
    messagebox.showinfo(
        "Secret File",
        "Optionally select a file whose contents will be read and encrypted."
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
        corner_radius=0,
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
        button_color=COLOR_ALMOND,
        button_hover_color=COLOR_ALMOND_HOVER,
        corner_radius=0,
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
        button_color=COLOR_ALMOND,
        button_hover_color=COLOR_ALMOND_HOVER,
        corner_radius=0,
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
        dropdown_text_color=COLOR_ALMOND,
        corner_radius=0,
    )
    chunk_menu.pack(anchor="w", padx=16, pady=(0, 16))

    close_btn = customtkinter.CTkButton(
        content,
        text="Save & Close",
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="Inter", size=13, weight="bold"),
        corner_radius=0,
        command=settings_win.destroy,
    )
    close_btn.pack(side="bottom", fill="x", padx=16, pady=(0, 16))


def render_latex(fig, ax, canvas, scroll_canvas, scroll_x, scroll_y, latex_expr: str, f_size=12):
    if not canvas.get_tk_widget().winfo_exists():
        return

    ax.clear()
    ax.set_facecolor(COLOR_INPUT_BG)
    fig.patch.set_facecolor(COLOR_INPUT_BG)
    ax.axis("off")

    clean_str = latex_expr.strip()

    if not clean_str:
        formatted_latex = r"$\mathrm{No\ message\ entered}$"
    elif not (clean_str.startswith("$") and clean_str.endswith("$")):
        formatted_latex = f"${clean_str}$"
    else:
        formatted_latex = clean_str

    trans = mtransforms.blended_transform_factory(fig.dpi_scale_trans, ax.transAxes)

    try:
        t = ax.text(
            0.15,
            0.5,
            formatted_latex,
            fontsize=f_size,
            color=COLOR_ALMOND,
            ha="left",
            va="center",
            transform=trans,
        )
    except Exception:
        t = ax.text(
            0.15,
            0.5,
            clean_str,
            fontsize=f_size - 1,
            color=COLOR_ALMOND,
            ha="left",
            va="center",
            transform=trans,
        )

    canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox = t.get_window_extent(renderer=renderer)

    view_w = max(scroll_canvas.winfo_width(), 400)
    view_h = max(scroll_canvas.winfo_height(), 60)

    needed_width = max(int(bbox.x1 + 60), view_w)
    needed_height = max(int(bbox.height + 25), view_h)

    fig.set_size_inches(needed_width / 100, needed_height / 100)
    canvas.draw()

    canvas_widget = canvas.get_tk_widget()
    canvas_widget.configure(width=needed_width, height=needed_height)
    scroll_canvas.configure(scrollregion=(0, 0, needed_width, needed_height))

    if needed_width > view_w + 5:
        scroll_x.pack(side="bottom", fill="x")
    else:
        scroll_x.pack_forget()

    if needed_height > view_h + 5:
        scroll_y.pack(side="right", fill="y")
    else:
        scroll_y.pack_forget()


def sender_screen(root: customtkinter.CTk):
    root.title("SymCrypt - Sender")
    root.configure(fg_color=COLOR_ECLIPSE)
    root.geometry("1080x680")
    root.minsize(960, 600)

    def on_app_destroy(event):
        if event.widget == root:
            plt.close('all')
    root.bind("<Destroy>", on_app_destroy, add="+")

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
        text="SENDER MODE",
        font=customtkinter.CTkFont(family="DejaVu Sans Mono", size=11, weight="bold"),
        text_color=COLOR_MATCHA_BREW,
    )
    mode_badge_lbl.pack(padx=10, pady=3)

    settings_btn = customtkinter.CTkButton(
        top_bar,
        text="⚙ Settings",
        width=95,
        height=30,
        corner_radius=0,
        fg_color=COLOR_CARD_BG,
        hover_color=COLOR_BORDER,
        border_color=COLOR_BORDER,
        border_width=1,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="Inter", size=12),
        command=lambda: open_settings_modal(root),
    )
    settings_btn.pack(side="right")

    dashboard = customtkinter.CTkFrame(root, fg_color="transparent")
    dashboard.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    # --- LEFT COLUMN ---
    left_col = customtkinter.CTkFrame(dashboard, fg_color="transparent", width=380)
    left_col.pack(side="left", fill="both", padx=(0, 12))
    left_col.pack_propagate(False)

    card_conn = customtkinter.CTkFrame(
        left_col,
        fg_color=COLOR_CARD_BG,
        corner_radius=0,
        border_color=COLOR_BORDER,
        border_width=1,
    )
    card_conn.pack(side="top", fill="x", pady=(0, 10))

    connectServerLabel = customtkinter.CTkLabel(
        card_conn,
        text="Connect to Receiver's Server",
        font=customtkinter.CTkFont(family="Inter", size=14, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    connectServerLabel.pack(anchor="w", padx=14, pady=(10, 6))

    connectionFrame = customtkinter.CTkFrame(card_conn, fg_color="transparent")
    connectionFrame.pack(fill="x", padx=14, pady=(0, 8))

    serverAddressEntry = customtkinter.CTkEntry(
        connectionFrame,
        placeholder_text="Server Address",
        font=customtkinter.CTkFont(family="DejaVu Sans Mono", size=12),
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=0,
        text_color=COLOR_ALMOND,
        height=34,
    )
    serverAddressEntry.pack(side="left", fill="x", expand=True, padx=(0, 8))

    disconnectButton = customtkinter.CTkButton(
        connectionFrame,
        text="Disconnect",
        width=95,
        height=34,
        corner_radius=0,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="Inter", size=12, weight="bold"),
        command=lambda: (
            disconnect()
            if messagebox.askyesno(
                "Disconnect from Receiver",
                "Do you want to disconnect from the receiver's server?",
            )
            else None
        ),
    )
    disconnectButton.pack(side="right", padx=(0, 8))

    connectButton = customtkinter.CTkButton(
        connectionFrame,
        text="Connect",
        width=80,
        height=34,
        corner_radius=0,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="Inter", size=12, weight="bold"),
        command=lambda: connect_to_server(serverAddressEntry.get()),
    )
    connectButton.pack(side="right", padx=(0, 12))

    serverStatusBox = create_log_target(
        card_conn, "server_status_logger", height=42, fg_color=COLOR_INPUT_BG
    )
    serverStatusBox.pack(fill="x", padx=14, pady=(0, 10))

    card_sec = customtkinter.CTkFrame(
        left_col,
        fg_color=COLOR_CARD_BG,
        corner_radius=0,
        border_color=COLOR_BORDER,
        border_width=1,
    )
    card_sec.pack(side="top", fill="both", expand=True)

    gpg_header = customtkinter.CTkFrame(card_sec, fg_color="transparent")
    gpg_header.pack(fill="x", padx=14, pady=(10, 6))

    gpgKeyLabel = customtkinter.CTkLabel(
        gpg_header,
        text="GPG Key File",
        font=customtkinter.CTkFont(family="Inter", size=14, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    gpgKeyLabel.pack(side="left")

    gpgQuickInfoButton = customtkinter.CTkButton(
        gpg_header,
        text="?",
        width=20,
        height=20,
        corner_radius=0,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(size=11, weight="bold"),
        command=show_gpg_key_help,
    )
    gpgQuickInfoButton.pack(side="left", padx=(8, 0))

    gpgKeyFrame = customtkinter.CTkFrame(card_sec, fg_color="transparent")
    gpgKeyFrame.pack(fill="x", padx=14, pady=(0, 10))

    gpgKeyPathEntry = customtkinter.CTkEntry(
        gpgKeyFrame,
        placeholder_text="Select GPG key file",
        font=customtkinter.CTkFont(family="Inter", size=12),
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=0,
        text_color=COLOR_ALMOND,
        height=34,
    )
    gpgKeyPathEntry.pack(side="left", fill="x", expand=True, padx=(0, 8))
    gpgKeyPathEntry.configure(state="readonly")

    def browse_gpg_key_file():
        file_path = filedialog.askopenfilename(title="Select GPG Key File")
        if file_path:
            gpgKeyPathEntry.configure(state="normal")
            gpgKeyPathEntry.delete(0, "end")
            gpgKeyPathEntry.insert(0, file_path)
            gpgKeyPathEntry.configure(state="readonly")

    browseGpgButton = customtkinter.CTkButton(
        gpgKeyFrame,
        text="Browse",
        width=80,
        height=34,
        corner_radius=0,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="Inter", size=12),
        command=browse_gpg_key_file,
    )
    browseGpgButton.pack(side="right")

    salt_header = customtkinter.CTkFrame(card_sec, fg_color="transparent")
    salt_header.pack(fill="x", padx=14, pady=(0, 4))

    saltEquationLabel = customtkinter.CTkLabel(
        salt_header,
        text="Salt Equation Type",
        font=customtkinter.CTkFont(family="Inter", size=13, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    saltEquationLabel.pack(side="left")

    saltEquationQuickInfo = customtkinter.CTkButton(
        salt_header,
        text="?",
        width=18,
        height=18,
        corner_radius=0,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(size=11),
        command=show_salt_equation_help,
    )
    saltEquationQuickInfo.pack(side="left", padx=(8, 0))

    saltEquationTypeVar = customtkinter.StringVar(value="Sine")
    saltEquationTypeMenu = customtkinter.CTkOptionMenu(
        card_sec,
        values=["Sine", "Cosine", "Tan", "Square Root", "Log"],
        variable=saltEquationTypeVar,
        height=32,
        corner_radius=0,
        fg_color=COLOR_INPUT_BG,
        button_color=COLOR_BORDER,
        button_hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        dropdown_fg_color=COLOR_CARD_BG,
        dropdown_text_color=COLOR_ALMOND,
    )
    saltEquationTypeMenu.pack(fill="x", padx=14, pady=(0, 10))

    # --- RIGHT COLUMN ---
    right_col = customtkinter.CTkFrame(dashboard, fg_color="transparent")
    right_col.pack(side="right", fill="both", expand=True)

    right_col.grid_columnconfigure(0, weight=1)
    right_col.grid_rowconfigure(0, weight=1)
    right_col.grid_rowconfigure(1, weight=2)
    right_col.grid_rowconfigure(2, weight=0)

    # --- Message & Secret File Card ---
    card_msg = customtkinter.CTkFrame(
        right_col,
        fg_color=COLOR_CARD_BG,
        corner_radius=0,
        border_color=COLOR_BORDER,
        border_width=1,
    )
    card_msg.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

    msg_header = customtkinter.CTkFrame(card_msg, fg_color="transparent")
    msg_header.pack(fill="x", padx=14, pady=(8, 2))

    secretMessageLabel = customtkinter.CTkLabel(
        msg_header,
        text="Secret Message",
        font=customtkinter.CTkFont(family="Inter", size=14, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    secretMessageLabel.pack(side="left")

    counter_label = customtkinter.CTkLabel(
        msg_header,
        text="0 chars",
        font=customtkinter.CTkFont(family="DejaVu Sans Mono", size=11),
        text_color=COLOR_MATCHA_BREW,
    )
    counter_label.pack(side="right")

    secretMessageEntry = customtkinter.CTkTextbox(
        card_msg,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=0,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="DejaVu Sans Mono", size=13),
    )
    secretMessageEntry.pack(fill="both", expand=True, padx=14, pady=(0, 6))

    def update_char_count(event=None):
        text_len = len(secretMessageEntry.get("1.0", "end-1c"))
        counter_label.configure(text=f"{text_len} chars")

    secretMessageEntry.bind("<KeyRelease>", update_char_count)

    # --- Secret File Input ---
    secret_file_header = customtkinter.CTkFrame(card_msg, fg_color="transparent")
    secret_file_header.pack(fill="x", padx=14, pady=(4, 2))

    secretFileLabel = customtkinter.CTkLabel(
        secret_file_header,
        text="Secret File",
        font=customtkinter.CTkFont(family="Inter", size=13, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    secretFileLabel.pack(side="left")

    secretFileQuickInfo = customtkinter.CTkButton(
        secret_file_header,
        text="?",
        width=18,
        height=18,
        corner_radius=0,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(size=11, weight="bold"),
        command=show_secret_file_help,
    )
    secretFileQuickInfo.pack(side="left", padx=(8, 0))

    secretFileFrame = customtkinter.CTkFrame(card_msg, fg_color="transparent")
    secretFileFrame.pack(fill="x", padx=14, pady=(0, 8))

    secretFilePathEntry = customtkinter.CTkEntry(
        secretFileFrame,
        placeholder_text="Select secret file (optional)",
        font=customtkinter.CTkFont(family="Inter", size=12),
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=0,
        text_color=COLOR_ALMOND,
        height=32,
    )
    secretFilePathEntry.pack(side="left", fill="x", expand=True, padx=(0, 8))
    secretFilePathEntry.configure(state="readonly")

    def browse_secret_file():
        file_path = filedialog.askopenfilename(title="Select Secret File")
        if file_path:
            secretFilePathEntry.configure(state="normal")
            secretFilePathEntry.delete(0, "end")
            secretFilePathEntry.insert(0, file_path)
            secretFilePathEntry.configure(state="readonly")

    browseSecretFileButton = customtkinter.CTkButton(
        secretFileFrame,
        text="Browse",
        width=80,
        height=32,
        corner_radius=0,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(family="Inter", size=12),
        command=browse_secret_file,
    )
    browseSecretFileButton.pack(side="right")

    loggerBox = create_log_target(
        card_msg, "encryption_logger", height=100, fg_color=COLOR_INPUT_BG
    )
    loggerBox.pack(fill="x", padx=14, pady=(0, 10))

    # --- Math Card ---
    card_math = customtkinter.CTkFrame(
        right_col,
        fg_color=COLOR_CARD_BG,
        corner_radius=0,
        border_color=COLOR_BORDER,
        border_width=1,
    )
    card_math.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

    math_header = customtkinter.CTkFrame(card_math, fg_color="transparent")
    math_header.pack(fill="x", padx=14, pady=(6, 2))

    mathEquationLabel = customtkinter.CTkLabel(
        math_header,
        text="Generated Math Equation",
        font=customtkinter.CTkFont(family="Inter", size=14, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    mathEquationLabel.pack(side="left")

    latest_latex_state = [r"\text{}"]

    def open_expanded_math_modal():
        modal = customtkinter.CTkToplevel(root)
        modal.title("Generated Math Equation")
        modal.geometry("850x380")
        modal.configure(fg_color=COLOR_ECLIPSE)

        m_container = customtkinter.CTkFrame(
            modal, fg_color=COLOR_INPUT_BG, border_color=COLOR_BORDER, border_width=1, corner_radius=0
        )
        m_container.pack(fill="both", expand=True, padx=16, pady=16)

        m_scroll_canvas = Canvas(m_container, bg=COLOR_INPUT_BG, highlightthickness=0)
        m_scroll_x = Scrollbar(m_container, orient="horizontal", command=m_scroll_canvas.xview, width=16)
        m_scroll_y = Scrollbar(m_container, orient="vertical", command=m_scroll_canvas.yview, width=16)
        m_scroll_canvas.configure(xscrollcommand=m_scroll_x.set, yscrollcommand=m_scroll_y.set)

        m_scroll_canvas.pack(side="left", fill="both", expand=True)

        m_fig, m_ax = plt.subplots(figsize=(10, 3), dpi=100)
        m_fig.patch.set_facecolor(COLOR_INPUT_BG)
        m_ax.set_facecolor(COLOR_INPUT_BG)
        m_ax.axis("off")

        m_canvas = FigureCanvasTkAgg(m_fig, master=m_scroll_canvas)
        m_canvas_widget = m_canvas.get_tk_widget()
        m_scroll_canvas.create_window((0, 0), window=m_canvas_widget, anchor="nw")

        render_latex(m_fig, m_ax, m_canvas, m_scroll_canvas, m_scroll_x, m_scroll_y, latest_latex_state[0], f_size=15)

    expand_btn = customtkinter.CTkButton(
        math_header,
        text="Expand ⛶",
        width=70,
        height=18,
        corner_radius=0,
        fg_color=COLOR_BORDER,
        hover_color=COLOR_MATCHA_BREW,
        text_color=COLOR_ALMOND,
        font=customtkinter.CTkFont(size=11),
        command=open_expanded_math_modal,
    )
    expand_btn.pack(side="right")

    canvas_outer_box = customtkinter.CTkFrame(
        card_math,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=1,
        corner_radius=0,
    )
    canvas_outer_box.pack(fill="both", expand=True, padx=14, pady=(0, 10))

    scroll_canvas = Canvas(canvas_outer_box, bg=COLOR_INPUT_BG, highlightthickness=0)
    scroll_x = Scrollbar(canvas_outer_box, orient="horizontal", command=scroll_canvas.xview, width=16)
    scroll_y = Scrollbar(canvas_outer_box, orient="vertical", command=scroll_canvas.yview, width=16)
    scroll_canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

    scroll_canvas.pack(side="left", fill="both", expand=True)

    fig, ax = plt.subplots(figsize=(5, 0.8), dpi=100)
    fig.patch.set_facecolor(COLOR_INPUT_BG)
    ax.set_facecolor(COLOR_INPUT_BG)
    ax.axis("off")

    fig_canvas = FigureCanvasTkAgg(fig, master=scroll_canvas)
    fig_canvas_widget = fig_canvas.get_tk_widget()
    scroll_canvas.create_window((0, 0), window=fig_canvas_widget, anchor="nw")

    def initial_render():
        if scroll_canvas.winfo_exists():
            render_latex(fig, ax, fig_canvas, scroll_canvas, scroll_x, scroll_y, latest_latex_state[0], f_size=12)
    root.after(100, initial_render)

    # --- Encrypt Button ---
    def trigger_encryption():
        msg = secretMessageEntry.get("1.0", "end-1c")
        secret_file = secretFilePathEntry.get()
        gpg_key = gpgKeyPathEntry.get()
        salt_type = saltEquationTypeVar.get()

        payload = utils.encrypt.encryptMessage(msg, gpg_key, salt_type)

        if secret_file and payload:
            file_eq = utils.encrypt.encrypt_file(secret_file, gpg_key, salt_type)
            if file_eq:
                payload["encrypted_file"] = file_eq

        if payload:
            utils.encrypt.send_payload(payload)

        if payload and "latex" in payload:
            latest_latex_state[0] = payload["latex"]
            render_latex(fig, ax, fig_canvas, scroll_canvas, scroll_x, scroll_y, payload["latex"], f_size=12)

    encryptButton = customtkinter.CTkButton(
        right_col,
        text="Encrypt and Send",
        font=customtkinter.CTkFont(family="Inter", size=14, weight="bold"),
        fg_color=COLOR_ALMOND,
        hover_color=COLOR_ALMOND_HOVER,
        border_color=COLOR_BORDER,
        border_width=1,
        text_color=COLOR_ECLIPSE,
        height=38,
        corner_radius=0,
        command=trigger_encryption,
    )
    encryptButton.grid(row=2, column=0, sticky="ew")
