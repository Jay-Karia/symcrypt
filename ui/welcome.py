import customtkinter as ctk
from ui.sender import sender_screen
from ui.receiver import receiver_screen

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

def welcome_screen(root: ctk.CTk):
    root.title("SymCrypt - Welcome")

    frame = ctk.CTkFrame(root, fg_color="transparent")
    frame.pack(expand=True, fill="both")

    # Welcome label
    label = ctk.CTkLabel(frame, text="Welcome to SymCrypt!", font=("Arial", 16))
    label.pack(pady=20)

    # Select mode label
    modeLabel = ctk.CTkLabel(frame, text="Select Mode:", font=("Arial", 14))
    modeLabel.pack(pady=10)

    # Button frame for horizontal layout
    button_frame = ctk.CTkFrame(frame, fg_color="transparent")
    button_frame.pack(pady=20)

    # Sender mode button
    sender_button = ctk.CTkButton(button_frame, text="Sender", command=lambda: onModeButtonClick("Sender", root), bg_color="transparent", height=120, width=220)
    sender_button.grid(row=0, column=0, padx=45)

    # Receiver mode button
    receiver_button = ctk.CTkButton(button_frame, text="Receiver", command=lambda: onModeButtonClick("Receiver", root), bg_color="transparent", height=120, width=220)
    receiver_button.grid(row=0, column=1, padx=45)
