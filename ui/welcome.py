import customtkinter
from ui.sender import sender_screen
from ui.receiver import receiver_screen

def clear_screen(root):
    """Clear all widgets from the root window."""
    for widget in root.winfo_children():
        widget.destroy()

def onModeButtonClick(mode: str, root: customtkinter.CTk):
    clear_screen(root)
    if mode == "Sender":
        sender_screen(root)
    elif mode == "Receiver":
        receiver_screen(root)

def welcome_screen(root: customtkinter.CTk):
    root.title("SymCrypt - Welcome")
    label = customtkinter.CTkLabel(root, text="Welcome to SymCrypt!", font=("Arial", 16))
    label.pack(pady=20)

    modeLabel = customtkinter.CTkLabel(root, text="Select Mode:", font=("Arial", 14))
    modeLabel.pack(pady=10)

    sender_button = customtkinter.CTkButton(root, text="Sender", command=lambda: onModeButtonClick("Sender", root))
    sender_button.pack(pady=5)

    receiver_button = customtkinter.CTkButton(root, text="Receiver", command=lambda: onModeButtonClick("Receiver", root))
    receiver_button.pack(pady=5)
