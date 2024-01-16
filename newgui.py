import gui.application_window


"""
class GUI:
    def __init__(self, light: bool = True):
        # Graphic Theme
        if light:
            customtkinter.set_appearance_mode("light")
        else:
            customtkinter.set_appearance_mode("dark")

        # Interactable color
        customtkinter.set_default_color_theme("blue")

        # Window setup
        self.root = customtkinter.CTk()
        self.root.geometry("800x600")

        self.progress = 0.0

        # Frame setup
        self.frame = customtkinter.CTkFrame(master=self.root)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        # label
        self.label = customtkinter.CTkLabel(master=self.frame, text="Login System")
        self.label.pack(pady=12, padx=10)

        # Interactable Elements
        self.entry1 = customtkinter.CTkEntry(master=self.frame, placeholder_text="Username")
        self.entry1.pack(pady=12, padx=10)

        self.entry2 = customtkinter.CTkEntry(master=self.frame, placeholder_text="Password", show="*")
        self.entry2.pack(pady=12, padx=10)

        self.button = customtkinter.CTkButton(master=self.frame, text="Login", command=login)
        self.button.pack(pady=12, padx=10)

        self.button = customtkinter.CTkButton(master=self.frame, text="Long Process", command=start_long_process)
        self.button.pack(pady=12, padx=10)

        self.button = customtkinter.CTkButton(master=self.frame, text="Inc!", command=self.increment_progress)
        self.button.pack(pady=12, padx=10)

        self.checkbox = customtkinter.CTkCheckBox(master=self.frame, text="Remember Me")
        self.checkbox.pack(pady=12, padx=10)

        # Progress bar
        self.progressbar = customtkinter.CTkProgressBar(master=self.frame, width=200)
        self.progressbar.pack(pady=12, padx=10)
        self.progressbar.set(0)

        self.root.mainloop()

        return

    def increment_progress(self):
        self.progress += .1
        self.progressbar.set(self.progress)"""


if __name__ == "__main__":
    app = gui.application_window.App()
    app.mainloop()
