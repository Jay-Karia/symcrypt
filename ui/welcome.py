import customtkinter as ctk
from ui.sender import sender_screen
from ui.receiver import receiver_screen


# ---------------------------------------------------------------------------
# Palette — deep, muted blue → green wash (Apple dark-mode inspired)
# ---------------------------------------------------------------------------
GRADIENT_TOP = (16, 22, 34)         # deep midnight blue
GRADIENT_BOTTOM = (14, 28, 26)      # deep muted teal/green
PANEL_COLOR = "#1C1E24"             # dark "glass" panel
PANEL_BORDER = "#2C2F38"
CARD_COLOR = "#23262E"
CARD_COLOR_HOVER = "#272C3A"
CARD_BORDER = "#31343D"
CARD_BORDER_HOVER = "#0A84FF"
TEXT_PRIMARY = "#F5F5F7"
TEXT_SECONDARY = "#9A9CA5"
ACCENT = "#0A84FF"

FONT_FAMILY = "Helvetica Neue"  # falls back gracefully on non-macOS systems


def clear_screen(root):
    """Clear all widgets from the root window."""
    for widget in root.winfo_children():
        widget.destroy()


def onModeButtonClick(mode: str, root: ctk.CTk):
    clear_screen(root)
    if mode == "Sender":
        sender_screen(root)
    elif mode == "Receiver":
        receiver_screen(root)


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def _to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def _draw_gradient(canvas, width, height):
    """Paint a smooth vertical gradient across the canvas."""
    canvas.delete("gradient")
    step = 2  # px per band — smooth enough, cheap enough
    for y in range(0, height, step):
        t = y / max(height - 1, 1)
        color = _to_hex(_lerp_color(GRADIENT_TOP, GRADIENT_BOTTOM, t))
        canvas.create_rectangle(0, y, width, y + step, fill=color, outline=color, tags="gradient")
    canvas.tag_lower("gradient")


def _make_mode_card(parent, root, icon, title, subtitle, mode):
    card = ctk.CTkFrame(
        parent,
        width=210,
        height=190,
        corner_radius=20,
        fg_color=CARD_COLOR,
        border_width=1,
        border_color=CARD_BORDER,
    )
    card.pack_propagate(False)

    icon_label = ctk.CTkLabel(card, text=icon, font=(FONT_FAMILY, 34))
    icon_label.pack(pady=(28, 6))

    title_label = ctk.CTkLabel(card, text=title, font=(FONT_FAMILY, 16, "bold"), text_color=TEXT_PRIMARY)
    title_label.pack()

    subtitle_label = ctk.CTkLabel(
        card,
        text=subtitle,
        font=(FONT_FAMILY, 11),
        text_color=TEXT_SECONDARY,
        wraplength=165,
        justify="center",
    )
    subtitle_label.pack(pady=(4, 0))

    widgets = (card, icon_label, title_label, subtitle_label)

    def on_enter(_e=None):
        card.configure(fg_color=CARD_COLOR_HOVER, border_color=CARD_BORDER_HOVER)

    def on_leave(_e=None):
        card.configure(fg_color=CARD_COLOR, border_color=CARD_BORDER)

    def on_click(_e=None):
        onModeButtonClick(mode, root)

    for w in widgets:
        w.configure(cursor="hand2")
        w.bind("<Enter>", on_enter)
        w.bind("<Leave>", on_leave)
        w.bind("<Button-1>", on_click)

    return card


def welcome_screen(root: ctk.CTk):
    root.title("SymCrypt - Welcome")

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Full-window canvas that carries the gradient wash
    canvas = ctk.CTkCanvas(root, highlightthickness=0, bd=0)
    canvas.pack(expand=True, fill="both")

    # ---- Glass panel that holds all the content ----------------------------
    panel = ctk.CTkFrame(
        canvas,
        width=460,
        height=420,
        corner_radius=28,
        fg_color=PANEL_COLOR,
        border_width=1,
        border_color=PANEL_BORDER,
    )
    panel.pack_propagate(False)

    title = ctk.CTkLabel(panel, text="SymCrypt", font=(FONT_FAMILY, 26, "bold"), text_color=TEXT_PRIMARY)
    title.pack()

    tagline = ctk.CTkLabel(
        panel,
        text="Secure symmetric encryption, made simple.",
        font=(FONT_FAMILY, 12),
        text_color=TEXT_SECONDARY,
    )
    tagline.pack(pady=(2, 22))

    prompt = ctk.CTkLabel(panel, text="Select a mode to get started", font=(FONT_FAMILY, 13, "bold"), text_color=TEXT_PRIMARY)
    prompt.pack(pady=(0, 14))

    card_row = ctk.CTkFrame(panel, fg_color="transparent")
    card_row.pack()

    sender_card = _make_mode_card(card_row, root, "📤", "Sender", "Encrypt and send a message", "Sender")
    sender_card.grid(row=0, column=0, padx=12)

    receiver_card = _make_mode_card(card_row, root, "📥", "Receiver", "Receive and decrypt a message", "Receiver")
    receiver_card.grid(row=0, column=1, padx=12)

    footer = ctk.CTkLabel(
        panel,
        text="v1.0",
        font=(FONT_FAMILY, 9),
        text_color=TEXT_SECONDARY,
    )
    footer.pack(pady=(20, 0))

    panel_window = None

    def redraw(event=None):
        nonlocal panel_window
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width <= 1 or height <= 1:
            return
        _draw_gradient(canvas, width, height)
        if panel_window is None:
            panel_window = canvas.create_window(width // 2, height // 2, window=panel, anchor="center")
        else:
            canvas.coords(panel_window, width // 2, height // 2)

    canvas.bind("<Configure>", redraw)
    root.after(10, redraw)
