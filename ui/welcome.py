import customtkinter as ctk


def clear_screen(root):
    for widget in root.winfo_children():
        widget.destroy()


def onModeButtonClick(mode: str, root: ctk.CTk):
    clear_screen(root)
    if mode == "Sender":
        from ui.sender import sender_screen

        sender_screen(root)
    elif mode == "Receiver":
        from ui.receiver import receiver_screen

        receiver_screen(root)


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def interpolate_color(start_hex: str, end_hex: str, factor: float) -> str:
    s_rgb = hex_to_rgb(start_hex)
    e_rgb = hex_to_rgb(end_hex)
    r = int(s_rgb[0] + (e_rgb[0] - s_rgb[0]) * factor)
    g = int(s_rgb[1] + (e_rgb[1] - s_rgb[1]) * factor)
    b = int(s_rgb[2] + (e_rgb[2] - s_rgb[2]) * factor)
    return rgb_to_hex((r, g, b))


def bind_smooth_hover(
    widget: ctk.CTkButton,
    root: ctk.CTk,
    idle_bg: str,
    hover_bg: str,
    idle_border: str,
    hover_border: str,
    steps: int = 8,
    delay_ms: int = 15,
):
    current_step = 0
    anim_id = None

    def animate(target_step: int):
        nonlocal current_step, anim_id
        if current_step < target_step:
            current_step += 1
        elif current_step > target_step:
            current_step -= 1

        factor = current_step / steps
        bg_col = interpolate_color(idle_bg, hover_bg, factor)
        border_col = interpolate_color(idle_border, hover_border, factor)

        widget.configure(fg_color=bg_col, border_color=border_col)

        if current_step != target_step:
            anim_id = root.after(delay_ms, lambda: animate(target_step))

    def on_enter(event):
        nonlocal anim_id
        if anim_id:
            root.after_cancel(anim_id)
        animate(steps)

    def on_leave(event):
        nonlocal anim_id
        if anim_id:
            root.after_cancel(anim_id)
        animate(0)

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


def welcome_screen(root: ctk.CTk):
    clear_screen(root)
    root.title("SymCrypt - Welcome")
    root.geometry("860x520")

    ctk.set_appearance_mode("dark")

    COLOR_ECLIPSE = "#0c1818"
    COLOR_FOREST_ROAST = "#2b3d37"
    COLOR_FOREST_HOVER = "#3a4f48"
    COLOR_BORDER_IDLE = "#40534C"
    COLOR_BORDER_HOVER = "#677D6A"
    COLOR_ALMOND = "#D6BD98"
    COLOR_SUBTITLE = "#677D6A"

    root.configure(fg_color=COLOR_ECLIPSE)

    frame = ctk.CTkFrame(root, fg_color="transparent")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    title = ctk.CTkLabel(
        frame,
        text="SymCrypt",
        font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
        text_color=COLOR_ALMOND,
    )
    title.pack(pady=(0, 4))

    subtitle = ctk.CTkLabel(
        frame,
        text="Select a mode to get started",
        font=ctk.CTkFont(family="Inter", size=14),
        text_color=COLOR_SUBTITLE,
    )
    subtitle.pack(pady=(0, 36))

    button_frame = ctk.CTkFrame(frame, fg_color="transparent")
    button_frame.pack()

    sender_button = ctk.CTkButton(
        button_frame,
        text="Sender",
        font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
        text_color=COLOR_ALMOND,
        fg_color=COLOR_FOREST_ROAST,
        hover_color=COLOR_FOREST_HOVER,
        border_color=COLOR_BORDER_IDLE,
        border_width=1,
        height=110,
        width=200,
        corner_radius=0,
        command=lambda: onModeButtonClick("Sender", root),
    )
    sender_button.grid(row=0, column=0, padx=16)

    receiver_button = ctk.CTkButton(
        button_frame,
        text="Receiver",
        font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
        text_color=COLOR_ALMOND,
        fg_color=COLOR_FOREST_ROAST,
        hover_color=COLOR_FOREST_HOVER,
        border_color=COLOR_BORDER_IDLE,
        border_width=1,
        height=110,
        width=200,
        corner_radius=0,
        command=lambda: onModeButtonClick("Receiver", root),
    )
    receiver_button.grid(row=0, column=1, padx=16)

    bind_smooth_hover(
        sender_button,
        root,
        COLOR_FOREST_ROAST,
        COLOR_FOREST_HOVER,
        COLOR_BORDER_IDLE,
        COLOR_BORDER_HOVER,
    )
    bind_smooth_hover(
        receiver_button,
        root,
        COLOR_FOREST_ROAST,
        COLOR_FOREST_HOVER,
        COLOR_BORDER_IDLE,
        COLOR_BORDER_HOVER,
    )

    footer = ctk.CTkLabel(
        frame,
        text="v1.0",
        font=ctk.CTkFont(family="DejaVu Sans Mono", size=11),
        text_color=COLOR_SUBTITLE,
    )
    footer.pack(pady=(36, 0))