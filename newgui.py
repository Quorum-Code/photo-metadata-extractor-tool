import customtkinter
import time
import threading
import os
from PIL import Image
from customtkinter import filedialog


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


class HomePage:
    def __init__(self, parent):
        self.__parent = parent
        self.__file_character_limit = 30

        self.__photo_folder = "no folder selected"
        self.__sudoc_file = "no file selected"
        self.__file_icon_local_path = "icons\\folder-icon.png"
        # todo add error handling for no image found
        self.__file_icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.__file_icon_local_path)
        self.__file_icon = customtkinter.CTkImage(Image.open(self.__file_icon_path), size=(24, 24))

        self.home_frame = customtkinter.CTkFrame(self.__parent, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_text = customtkinter.CTkLabel(self.home_frame, text="Home Page",
                                                font=customtkinter.CTkFont(size=20, weight="bold"))
        self.home_text.grid(row=0, column=0, padx=20, pady=20)

        # Sub Home frame - Photo folder frame
        self.photo_folder_frame = customtkinter.CTkFrame(self.home_frame, corner_radius=0)
        self.photo_folder_frame.grid(row=1, column=0, padx=10, pady=10)

        self.photo_folder_name = customtkinter.CTkLabel(self.photo_folder_frame, text="Photo Folder", width=80)
        self.photo_folder_name.grid(row=0, column=0, padx=10, pady=10)

        self.select_photo_folder_button = customtkinter.CTkButton(self.photo_folder_frame,
                                                                  text="",
                                                                  image=self.__file_icon,
                                                                  height=10,
                                                                  width=10,
                                                                  border_spacing=0,
                                                                  corner_radius=0,
                                                                  fg_color="transparent",
                                                                  command=self.ask_photo_folder)
        self.select_photo_folder_button.grid(row=0, column=1, padx=10, pady=10)

        self.photo_folder_name = customtkinter.CTkLabel(self.photo_folder_frame, text=self.__photo_folder, anchor="w",
                                                        width=300)
        self.photo_folder_name.grid(row=0, column=2, padx=10, pady=10)

        # Process Subframe
        self.process_frame = customtkinter.CTkFrame(self.home_frame, corner_radius=0, fg_color="transparent")
        self.process_frame.grid(row=2, column=0, padx=10, pady=10)

        # Progress text
        self.progress_text = customtkinter.CTkLabel(self.process_frame, corner_radius=0, text="No Process Running")
        self.progress_text.grid(row=0, column=0)

        # Progress bar
        self.progress_bar = customtkinter.CTkProgressBar(self.process_frame, width=300)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, padx=10)

        self.process_photo_button = customtkinter.CTkButton(self.process_frame, text="Process Photos")
        self.process_photo_button.grid(row=2, column=0, padx=10, pady=20)

        # Sub Home frame - SuDoc file frame
        self.sudoc_file_frame = customtkinter.CTkFrame(self.home_frame, corner_radius=0)
        self.sudoc_file_frame.grid(row=3, column=0, padx=10, pady=10)

        self.sudoc_file_name = customtkinter.CTkLabel(self.sudoc_file_frame, text="SuDoc CSV", width=80)
        self.sudoc_file_name.grid(row=0, column=0, padx=10, pady=10)

        self.select_sudoc_file_button = customtkinter.CTkButton(self.sudoc_file_frame,
                                                                text="",
                                                                image=self.__file_icon,
                                                                height=10,
                                                                width=10,
                                                                border_spacing=0,
                                                                corner_radius=0,
                                                                fg_color="transparent",
                                                                command=parent.ask_sudoc_file)
        self.select_sudoc_file_button.grid(row=0, column=1, padx=10, pady=10)

        self.sudoc_file_name = customtkinter.CTkLabel(self.sudoc_file_frame, text=self.__sudoc_file, anchor="w",
                                                      width=300)
        self.sudoc_file_name.grid(row=0, column=2, padx=10, pady=10)

    def ask_photo_folder(self):
        foldername = filedialog.askdirectory()

        self.photo_folder_name.configure(text=foldername)

    def _trim_filename(self, filename: str) -> str:
        new_filename = ""
        if len(filename) > self.__file_character_limit:
            trim_index = len(filename) - self.__file_character_limit
            new_filename = "..."
            new_filename += filename[trim_index:]
        return new_filename


class SettingsPage:
    def __init__(self):
        pass


class ConfigurationPage:
    def __init__(self):
        pass


class InfoPage:
    def __init__(self):
        pass


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
                                                   text_color=("gray10", "gray90"),
                                                   anchor="w",
                                                   command=self.home_button_event)
        self.home_button.grid(row=0, column=0, sticky="ew")

        self.settings_button = customtkinter.CTkButton(self.navigation_frame,
                                                       corner_radius=0,
                                                       height=40,
                                                       border_spacing=10,
                                                       text="Settings",
                                                       fg_color="transparent",
                                                       text_color=("gray10", "gray90"),
                                                       anchor="w",
                                                       command=self.settings_button_event)
        self.settings_button.grid(row=1, column=0, sticky="ew")

        self.configuration_button = customtkinter.CTkButton(self.navigation_frame,
                                                            corner_radius=0,
                                                            height=40,
                                                            border_spacing=10,
                                                            text="Configuration",
                                                            fg_color="transparent",
                                                            text_color=("gray10", "gray90"),
                                                            anchor="w",
                                                            command=self.configuration_button_event)
        self.configuration_button.grid(row=2, column=0, sticky="ew")

        # Style menu
        self.style_menu = customtkinter.CTkOptionMenu(self.navigation_frame,
                                                      values=["Light", "Dark", "System"],
                                                      command=self.change_style_event)
        self.style_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # Initialize Home frame
        self.home = HomePage(self)
        self.process_folder = "None"
        self.sudoc_file = "None"

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

        self.grab_set()

    def select_frame_by_name(self, name: str):
        # Update navigation button colors
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")
        self.configuration_button.configure(fg_color=("gray75", "gray25") if name == "configuration" else "transparent")

        # Set or forget frames
        if name == "home":
            self.home.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home.home_frame.grid_forget()

        if name == "settings":
            self.settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.settings_frame.grid_forget()

        if name == "configuration":
            self.configuration_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.configuration_frame.grid_forget()

        if name == "info":
            self.configuration_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.info_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def settings_button_event(self):
        self.select_frame_by_name("settings")

    def configuration_button_event(self):
        self.select_frame_by_name("configuration")

    def info_button_event(self):
        self.select_frame_by_name("info")

    def ask_sudoc_file(self):
        self.home.sudoc_file_name.configure(text=filedialog.askopenfilename(filetypes=[("CSV", "*.csv")]))

    def change_style_event(self, style: str):
        customtkinter.set_appearance_mode(style)
        # todo set a var in settings config to style


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
        self.progressbar.set(self.progress)


if __name__ == "__main__":
    app = App()
    app.mainloop()
