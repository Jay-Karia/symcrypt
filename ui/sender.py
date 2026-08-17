import customtkinter
from tkinter import filedialog, messagebox
import utils.encrypt
from logger import create_log_target


def show_gpg_key_help():
        messagebox.showinfo(
            "GPG Key File",
            "Select the receiver's public GPG key file for encryption."
        )


def sender_screen(root: customtkinter.CTk):
    root.title("SymCrypt - Sender")

    # Connect to Server
    connectServerLabel = customtkinter.CTkLabel(root, text="Connect to Receiver's Server", font=("Arial", 16))
    connectServerLabel.pack(pady=(12, 2), anchor="w", padx=(20, 0))

    connectionFrame = customtkinter.CTkFrame(root)
    connectionFrame.pack(pady=(0, 5), anchor="w", padx=(20, 0))

    serverAddressEntry = customtkinter.CTkEntry(connectionFrame, placeholder_text="Server Address", width=300)
    serverAddressEntry.grid(row=0, column=0, padx=(0, 10), pady=5)

    connectButton = customtkinter.CTkButton(connectionFrame, text="Connect", width=100)
    connectButton.grid(row=0, column=2, padx=(10, 0), pady=5)

    # GPG Key Input
    gpgKeyHeaderFrame = customtkinter.CTkFrame(root)
    gpgKeyHeaderFrame.pack(pady=(12, 2), anchor="w", padx=(20, 0))

    gpgKeyLabel = customtkinter.CTkLabel(gpgKeyHeaderFrame, text="GPG Key File", font=("Arial", 16))
    gpgKeyLabel.grid(row=0, column=0, padx=(0, 8))

    gpgQuickInfoButton = customtkinter.CTkButton(gpgKeyHeaderFrame, text="?", width=30, command=show_gpg_key_help)
    gpgQuickInfoButton.grid(row=0, column=1)

    gpgKeyFrame = customtkinter.CTkFrame(root)
    gpgKeyFrame.pack(pady=(0, 5), anchor="w", padx=(20, 0))

    gpgKeyPathEntry = customtkinter.CTkEntry(gpgKeyFrame, placeholder_text="Select GPG key file", width=500)
    gpgKeyPathEntry.grid(row=0, column=0, padx=(0, 10), pady=5)
    gpgKeyPathEntry.configure(state="readonly")

    def browse_gpg_key_file():
        file_path = filedialog.askopenfilename(title="Select GPG Key File")
        if file_path:
            gpgKeyPathEntry.configure(state="normal")
            gpgKeyPathEntry.delete(0, "end")
            gpgKeyPathEntry.insert(0, file_path)
            gpgKeyPathEntry.configure(state="readonly")

    browseButton = customtkinter.CTkButton(gpgKeyFrame, text="Browse", width=100, command=browse_gpg_key_file)
    browseButton.grid(row=0, column=2, pady=5)

    # Secret Message
    secretMessageLabel = customtkinter.CTkLabel(root, text="Secret Message", font=("Arial", 16))
    secretMessageLabel.pack(pady=(12, 2), anchor="w", padx=(20, 0))

    secretMessageEntry = customtkinter.CTkTextbox(root, width=600, height=200, fg_color="#333333")
    secretMessageEntry.pack(pady=(0, 5), anchor="w", padx=(20, 0))

    loggerBox = create_log_target(root, "encryption_logger", width=600, height=40, fg_color="#2b2b2b")
    loggerBox.pack(pady=(0, 10), anchor="w", padx=(20, 0))

    encryptButton = customtkinter.CTkButton(root, text="Encrypt", width=200, command=lambda: utils.encrypt.encryptMessage(secretMessageEntry.get("1.0", "end-1c"), gpgKeyPathEntry.get()))
    encryptButton.pack(pady=(10, 20), anchor="w", padx=(20, 0))
