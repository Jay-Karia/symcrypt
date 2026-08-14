import customtkinter
from ui.welcome import welcome_screen

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.geometry("1100x700")

def main():
    welcome_screen(root)
    root.mainloop()
