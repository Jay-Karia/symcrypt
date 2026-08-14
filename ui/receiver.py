import customtkinter

def receiver_screen(root: customtkinter.CTk):
    root.title("SymCrypt - Receiver")
    label = customtkinter.CTkLabel(root, text="Receiver Screen", font=("Arial", 16))
    label.pack(pady=20)
