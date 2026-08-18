import customtkinter
from ui.welcome import welcome_screen

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
customtkinter.deactivate_automatic_dpi_awareness()

root = customtkinter.CTk()
root.geometry("1100x700")
root.minsize(1100, 700)

def main():
    welcome_screen(root)
    root.mainloop()
