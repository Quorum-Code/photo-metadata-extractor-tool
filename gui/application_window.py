import customtkinter
import gui.home_page
import gui.settings_page
import gui.config_page
from file_handler import FileHandler


class App(customtkinter.CTk):
    def __init__(self, filehandler: FileHandler):
        super().__init__()
        self.filehandler = filehandler

        # Window settings
        self.title("Photo Metadata Extractor Tool")
        self.geometry("800x600")

        # Side button setup
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        """ **************
        Nav Bar Frame 
        ************** """
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
        style = self.filehandler.get_style()
        self.style_menu.set(style)
        self.change_style_event(style)
        self.style_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # Initialize Home frame
        self.home = gui.home_page.HomePage(self)
        self.process_folder = "None"
        self.sudoc_file = "None"

        # Initialize Settings frame
        self.settings = gui.settings_page.SettingsPage(self, self.filehandler)

        # Initialize Configuration frame
        self.configuration = gui.config_page.ConfigurationPage(self, self.filehandler)

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

        # Clear focus
        self.focus()

        # Set or forget frames
        if name == "home":
            self.home.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home.home_frame.grid_forget()

        if name == "settings":
            self.settings.settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.settings.settings_frame.grid_forget()

        if name == "configuration":
            self.configuration.configuration_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.configuration.configuration_frame.grid_forget()

        if name == "info":
            self.configuration.configuration_frame.grid(row=0, column=1, sticky="nsew")
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

    def change_style_event(self, style: str):
        print(f"NEW STYLE: {style}")
        customtkinter.set_appearance_mode(style)
        self.filehandler.save_style(style)
