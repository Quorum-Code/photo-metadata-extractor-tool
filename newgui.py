import customtkinter
from customtkinter import CTkProgressBar, IntVar
import time
import threading


def main():
    gui = GUI(False)
    return

def login():
    print("Logged in!!")

def start_long_process():
    proc = threading.Thread(target=long_process)
    proc.start()

def long_process():
    progress = 0
    while progress < 3:
        progress += .5
        print(f"Progress: {progress}")
        time.sleep(.5)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Window settings
        self.title("Photo Metadata Extractor Tool")
        self.geometry("800x600")

        # Side button setup
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Navigation bar
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(3, weight=1)

        # Navigation buttons
        self.home_button = customtkinter.CTkButton(self.navigation_frame,
                                                   corner_radius=0,
                                                   height=40,
                                                   border_spacing=10,
                                                   text="Home",
                                                   fg_color="transparent",
                                                   anchor="w",
                                                   command=self.home_button_event)
        self.home_button.grid(row=0, column=0, sticky="ew")

        self.settings_button = customtkinter.CTkButton(self.navigation_frame,
                                                   corner_radius=0,
                                                   height=40,
                                                   border_spacing=10,
                                                   text="Settings",
                                                   fg_color="transparent",
                                                   anchor="w",
                                                   command=self.settings_button_event)
        self.settings_button.grid(row=1, column=0, sticky="ew")

        self.configuration_button = customtkinter.CTkButton(self.navigation_frame,
                                                   corner_radius=0,
                                                   height=40,
                                                   border_spacing=10,
                                                   text="Configuration",
                                                   fg_color="transparent",
                                                   anchor="w",
                                                   command=self.configuration_button_event)
        self.configuration_button.grid(row=2, column=0, sticky="ew")

        # Style menu
        self.style_menu = customtkinter.CTkOptionMenu(self.navigation_frame,
                                                      values=["Light", "Dark", "System"])
        self.style_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # Initialize Home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_text = customtkinter.CTkLabel(self.home_frame, text="Home page...")
        self.home_text.grid(row=0, column=0, padx=20, pady=20)

        # Initialize Settings frame
        self.settings_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.settings_text = customtkinter.CTkLabel(self.settings_frame, text="Settings page...")
        self.settings_text.grid(row=0, column=0, padx=20, pady=20)

        # Initialize Configuration frame
        self.configuration_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # Initialize Info frame
        self.info_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # Load home frame
        self.select_frame_by_name("home")

    def select_frame_by_name(self, name: str):
        # Update navigation button colors
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")
        self.configuration_button.configure(fg_color=("gray75", "gray25") if name == "configuration" else "transparent")

        # Set or forget frames
        if name == "home": self.home_frame.grid(row=0, column=1, sticky="nsew")
        else: self.home_frame.grid_forget()

        if name == "settings": self.settings_frame.grid(row=0, column=1, sticky="nsew")
        else: self.settings_frame.grid_forget()

        if name == "configuration": self.configuration_frame.grid(row=0, column=1, sticky="nsew")
        else: self.configuration_frame.grid_forget()

        if name == "info": self.configuration_frame.grid(row=0, column=1, sticky="nsew")
        else: self.info_frame.grid_forget()


    def home_button_event(self):
        self.select_frame_by_name("home")

    def settings_button_event(self):
        self.select_frame_by_name("settings")

    def configuration_button_event(self):
        self.select_frame_by_name("configuration")

    def info_button_event(self):
        self.select_frame_by_name("info")


class GUI:
    def __init__(self, light: bool = True):
        # Graphic Theme
        if light: customtkinter.set_appearance_mode("light")
        else: customtkinter.set_appearance_mode("dark")

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
        self.progressbar.set(self.progress)

if __name__ == "__main__":
    app = App()
    app.mainloop()
