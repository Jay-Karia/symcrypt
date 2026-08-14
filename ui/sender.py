import customtkinter

def sender_screen(root: customtkinter.CTk):
    root.title("SymCrypt - Sender")
    label = customtkinter.CTkLabel(root, text="Sender Screen", font=("Arial", 16))
    label.pack(pady=20)
