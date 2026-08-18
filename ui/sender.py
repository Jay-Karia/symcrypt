import customtkinter
from tkinter import filedialog, messagebox
import sympy as sp
import utils.encrypt
from logger import create_log_target

def show_gpg_key_help():
        messagebox.showinfo(
            "GPG Key File",
            "Select the receiver's public GPG key file for encryption."
        )

def show_salt_equation_help():
    messagebox.showinfo(
        "Salt Equation",
        "The salt equation is generated to improve the security of the equation."
    )


def sender_screen(root: customtkinter.CTk):
    root.title("SymCrypt - Sender")
    math_font = customtkinter.CTkFont(family="DejaVu Sans Mono", size=12)

    # Create a scrollable frame for the entire content
    main_frame = customtkinter.CTkScrollableFrame(root, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=0, pady=0)

    # Connect to Server
    connectServerLabel = customtkinter.CTkLabel(main_frame, text="Connect to Receiver's Server", font=("Arial", 16))
    connectServerLabel.pack(pady=(12, 2), anchor="w", padx=(20, 0))

    connectionFrame = customtkinter.CTkFrame(main_frame)
    connectionFrame.pack(pady=(0, 5), anchor="w", padx=(20, 0))

    serverAddressEntry = customtkinter.CTkEntry(connectionFrame, placeholder_text="Server Address", width=300)
    serverAddressEntry.grid(row=0, column=0, padx=(0, 10), pady=5)

    connectButton = customtkinter.CTkButton(connectionFrame, text="Connect", width=100)
    connectButton.grid(row=0, column=2, padx=(10, 0), pady=5)

    serverStatusBox = create_log_target(main_frame, "server_status_logger", width=600, height=40, fg_color="#2b2b2b")
    serverStatusBox.pack(pady=(0, 10), anchor="w", padx=(20, 0))

    # GPG Key Input
    gpgKeyHeaderFrame = customtkinter.CTkFrame(main_frame)
    gpgKeyHeaderFrame.pack(pady=(12, 2), anchor="w", padx=(20, 0))

    gpgKeyLabel = customtkinter.CTkLabel(gpgKeyHeaderFrame, text="GPG Key File", font=("Arial", 16))
    gpgKeyLabel.grid(row=0, column=0, padx=(0, 8))

    gpgQuickInfoButton = customtkinter.CTkButton(gpgKeyHeaderFrame, text="?", width=30, command=show_gpg_key_help)
    gpgQuickInfoButton.grid(row=0, column=1)

    gpgKeyFrame = customtkinter.CTkFrame(main_frame)
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
    secretMessageLabel = customtkinter.CTkLabel(main_frame, text="Secret Message", font=("Arial", 16))
    secretMessageLabel.pack(pady=(12, 2), anchor="w", padx=(20, 0))

    secretMessageEntry = customtkinter.CTkTextbox(main_frame, width=600, height=200, fg_color="#333333")
    secretMessageEntry.pack(pady=(0, 5), anchor="w", padx=(20, 0))

    loggerBox = create_log_target(main_frame, "encryption_logger", width=600, height=40, fg_color="#2b2b2b")
    loggerBox.pack(pady=(0, 10), anchor="w", padx=(20, 0))

    # Salt equation settings
    saltEquationHeaderFrame = customtkinter.CTkFrame(main_frame)
    saltEquationHeaderFrame.pack(pady=(12, 2), anchor="w", padx=(20, 0))

    saltEquationLabel = customtkinter.CTkLabel(saltEquationHeaderFrame, text="Salt Equation Type", font=("Arial", 16))
    saltEquationLabel.grid(row=0, column=0, padx=(0, 8))

    saltEquationQuickInfo = customtkinter.CTkButton(saltEquationHeaderFrame, text="?", width=30, command=show_salt_equation_help)
    saltEquationQuickInfo.grid(row=0, column=1)

    saltEquationTypeVar = customtkinter.StringVar(value="Sine")
    saltEquationTypeMenu = customtkinter.CTkOptionMenu(
        main_frame,
        values=["Sine", "Cosine", "Tan", "Square Root", "Log"],
        variable=saltEquationTypeVar,
        width=220,
        fg_color="#4E4E4E",
        button_color="#C0C0C0",
        button_hover_color="#B0B0B0",
    )
    saltEquationTypeMenu.pack(pady=(10, 10), anchor="w", padx=(20, 0))

    # Math equation
    mathEquationLabel = customtkinter.CTkLabel(main_frame, text="Generated Math Equation", font=("Arial", 16))
    mathEquationLabel.pack(pady=(12, 2), anchor="w", padx=(20, 0))

    mathEquationBox = create_log_target(
        main_frame,
        "math_equation_logger",
        width=600,
        height=180,  # Increase height for multi-line 2D expressions
        fg_color="#2b2b2b",
        font=math_font,
        wrap="none",  # Prevents equation folding
        activate_scrollbars=True,
    )
    mathEquationBox.pack(pady=(0, 10), anchor="w", padx=(20, 0))

    # Encrypt Button
    encryptButton = customtkinter.CTkButton(main_frame, text="Encrypt", width=600, command=lambda: utils.encrypt.encryptMessage(secretMessageEntry.get("1.0", "end-1c"), gpgKeyPathEntry.get(), saltEquationTypeVar.get()))
    encryptButton.pack(pady=(10, 20), anchor="w", padx=(20, 0))
